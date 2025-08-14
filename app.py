import streamlit as st
import json
from extractor import extract_fields_from_pdf
from comparator import compare_fields

st.set_page_config(page_title="Comparador de NF", layout="wide")
st.title("📄 Comparador de Nota Fiscal - MVP1")

st.markdown("Faça upload de um **PDF da Nota Fiscal** e um **JSON Espelho** com os dados corretos.")

# Upload dos arquivos
pdf_file = st.file_uploader("📤 Envie o PDF da Nota Fiscal", type=["pdf"])
json_file = st.file_uploader("📤 Envie o JSON Espelho", type=["json"])

if pdf_file and json_file:
    # Extração do PDF
    with st.spinner("🔍 Extraindo dados do PDF..."):
        pdf_text = pdf_file.read()
        extracted_data = extract_fields_from_pdf(pdf_text)

    # Leitura do JSON Espelho
    try:
        json_data = json.load(json_file)
        expected_data = json_data.get("fiscalDocument", {})
    except Exception as e:
        st.error(f"Erro ao ler o JSON: {e}")
        st.stop()

    # Comparação
    with st.spinner("🧠 Comparando campos..."):
        comparison_result = compare_fields(extracted_data, expected_data)

    # Resultado
    st.subheader("🧾 Resultado da Comparação")
    st.table(comparison_result)

    # JSON gerado (opcional download)
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
