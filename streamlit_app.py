import streamlit as st
import fitz
import pytesseract
from PIL import Image
import io
import pandas as pd
import json
import tempfile

st.set_page_config(page_title="Comparador de PDF Fiscal", layout="centered")
st.title("📄 Comparador de Campos de Notas Fiscais")

# Mapeamento com múltiplos sinônimos por campo
field_keywords = {
    "FiscalDocumentNumber": ["Número da NF", "NF-e", "NF:", "Nota Fiscal"],
    "FiscalDocumentIssuerCNPJ": ["CNPJ Emitente", "Emitente CNPJ", "CNPJ do Emitente"],
    "FiscalDocumentCarglassCNPJ": ["CNPJ Destinatário", "Destinatário CNPJ", "CNPJ do Destinatário"],
    "FiscalDocumentNCM": ["NCM", "Código NCM"],
    "FiscalDocumentCFOP": ["CFOP", "Código CFOP"],
    "FiscalDocumentTotal": ["Valor Total", "Total da Nota", "VALOR TOTAL DOS SERVIÇOS"],
    "FiscalDocumentIPI": ["IPI", "VALOR TOTAL DO IPI"],
    "FiscalDocumentST": ["ICMS ST", "BASE DE CALCULO DO ICMS ST"],
    "FiscalDocumentDesconto": ["Desconto"],
    "FiscalDocumentICMS": ["ICMS", "BASE DE CALCULO DO ICMS"],
    "FiscalDocumentType": ["Tipo de Documento", "Modelo"]
}

# Busca com múltiplas opções por campo
def find_field_value(keywords, text):
    lines = text.split("\n")

    for keyword in keywords:
        for line in lines:
            if not isinstance(line, str): continue
            if keyword.lower() in line.lower():
                parts = line.split(":")
                if len(parts) > 1:
                    return parts[1].strip()
                return line.strip()
    return "Não encontrado"

# OCR + fallback para texto embutido
def extract_text_from_pdf(uploaded_file):
    text = ""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = tmp_file.name

        pdf_document = fitz.open(tmp_path)
        for page in pdf_document:
            text += page.get_text()

        if text.strip() == "":
            raise ValueError("Sem texto embutido")

        return text

    except Exception:
        st.warning("🔍 Conteúdo textual não encontrado, aplicando OCR...")
        text = ""
        pdf_document = fitz.open("pdf", uploaded_file.read())
        for page in pdf_document:
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            try:
                ocr_text = pytesseract.image_to_string(img)
                text += ocr_text
            except:
                continue
        return text

# Upload
uploaded_file = st.file_uploader("📎 Faça upload da Nota Fiscal (PDF)", type=["pdf"])

if uploaded_file:
    st.success("✅ PDF carregado com sucesso!")

    extracted_text = extract_text_from_pdf(uploaded_file)

    if not extracted_text.strip():
        st.error("❌ Não foi possível extrair texto do PDF.")
    else:
        extracted_data = []
        for field, keywords in field_keywords.items():
            try:
                value = find_field_value(keywords, extracted_text)
            except Exception:
                value = "Erro"
            extracted_data.append({"Campo": field, "Valor PDF": value})

        df_result = pd.DataFrame(extracted_data)

        st.subheader("📊 Resultado da Comparação")
        st.dataframe(df_result, use_container_width=True)

        st.download_button(
            "📥 Baixar resultado em JSON",
            data=json.dumps(extracted_data, indent=2),
            file_name="resultado.json",
            mime="application/json"
        )
