import streamlit as st
import json
import re
import fitz  # PyMuPDF

# ======== FUNÇÕES AUXILIARES ========

def extract_fields_from_pdf(pdf_bytes) -> dict:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()

    def find(pattern, default="Não encontrado", flags=0):
        match = re.search(pattern, text, flags)
        return match.group(1).strip() if match else default

    return {
        "FiscalDocumentNumber": find(r"NFe\s+(\d+)", default="0"),
        "FiscalDocumentIssuerCNPJ": find(r"Emitente.*?CNPJ[:\s]*([\d./-]+)", flags=re.DOTALL),
        "FiscalDocumentCarglassCNPJ": find(r"Destinatário.*?CNPJ[:\s]*([\d./-]+)", flags=re.DOTALL),
        "FiscalDocumentNCM": find(r"NCM[:\s]*([\d]+)"),
        "FiscalDocumentCFOP": find(r"CFOP[:\s]*([\d]+)"),
        "FiscalDocumentTotal": find(r"Valor\s+Total[:\s]*R?\$?\s?([\d.,]+)"),
        "FiscalDocumentType": "NotaProduto",
        "FiscalDocumentIPI": find(r"IPI[:\s]*([\d.,]+)"),
        "FiscalDocumentST": find(r"ICMS ST[:\s]*([\d.,]+)"),
        "FiscalDocumentDesconto": find(r"Desconto[:\s]*R?\$?\s?([\d.,]+)"),
        "FiscalDocumentICMS": find(r"ICMS[:\s]*([\d.,]+)")
    }

def normalize(value):
    if isinstance(value, str):
        return value.replace(".", "").replace(",", ".").replace("/", "").replace("-", "").strip()
    if isinstance(value, float):
        return round(value, 2)
    return str(value).strip()

def compare_fields(extracted: dict, expected: dict) -> list:
    result = []
    for key in expected:
        val_extr = normalize(extracted.get(key, ""))
        val_esp = normalize(expected.get(key, ""))

        match = val_extr == val_esp
        result.append({
            "Campo": key,
            "Valor PDF": extracted.get(key, "Não encontrado"),
            "Valor Esperado": expected.get(key, "Não informado"),
            "Igual?": "✅ Sim" if match else "❌ Não"
        })
    return result

# ======== STREAMLIT APP ========

st.set_page_config(page_title="Comparador de NF", layout="wide")
st.title("📄 Comparador de Nota Fiscal - MVP")

st.markdown("Faça upload de um **PDF da Nota Fiscal** e um **JSON Espelho** com os dados corretos.")

pdf_file = st.file_uploader("📤 Envie o PDF da Nota Fiscal", type=["pdf"])
json_file = st.file_uploader("📤 Envie o JSON Espelho", type=["json"])

if pdf_file and json_file:
    with st.spinner("🔍 Extraindo dados do PDF..."):
        pdf_bytes = pdf_file.read()
        extracted_data = extract_fields_from_pdf(pdf_bytes)

    try:
        json_data = json.load(json_file)
        expected_data = json_data.get("fiscalDocument", {})
    except Exception as e:
        st.error(f"Erro ao ler o JSON: {e}")
        st.stop()

    with st.spinner("🧠 Comparando campos..."):
        comparison_result = compare_fields(extracted_data, expected_data)

    st.subheader("🧾 Resultado da Comparação")
    st.table(comparison_result)

    result_json = {
        "pdfExtracted": extracted_data,
        "expected": expected_data,
        "comparison": comparison_result
    }

    st.download_button(
        label="📥 Baixar resultado em JSON",
        data=json.dumps(result_json, indent=2),
        file_name="resultado_comparacao.json",
        mime="application/json"
    )
