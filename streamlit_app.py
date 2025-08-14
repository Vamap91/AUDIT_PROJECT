import streamlit as st
import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import json
import pandas as pd
import io

st.set_page_config(page_title="Comparador de PDFs", layout="wide")
st.title("📄 Comparador de Campos Fiscais em PDF")

# 📥 Upload
pdf_file = st.file_uploader("Selecione o PDF para análise", type=["pdf"])

# 📚 Carregar referência
def load_reference():
    with open("reference.json", encoding="utf-8") as f:
        return json.load(f)

# 🧾 Tenta extrair texto do PDF diretamente
def extract_text_from_pdf(pdf_bytes):
    text = ""
    doc = fitz.open("pdf", pdf_bytes)
    for page in doc:
        text += page.get_text()
    return text.strip()

# 🖼️ Se falhar, tenta OCR página a página
def extract_text_with_ocr(pdf_bytes):
    images = convert_from_bytes(pdf_bytes)
    text = ""
    for img in images:
        gray = img.convert("L")  # grayscale
        text += pytesseract.image_to_string(gray, lang="por")
    return text

# 🔍 Função para buscar valores com base em palavras-chave
def find_field_value(keyword, content):
    lines = content.split("\n")
    for line in lines:
        if keyword.lower() in line.lower():
            parts = line.split(":")
            if len(parts) > 1:
                return parts[-1].strip()
            return line.strip()
    return "Não encontrado"

if pdf_file:
    reference = load_reference()
    pdf_bytes = pdf_file.read()

    # Tentativa principal
    text = extract_text_from_pdf(pdf_bytes)

    # Se nada for extraído, fallback OCR
    if not text.strip():
        st.warning("Texto não encontrado via extração direta. Utilizando OCR...")
        text = extract_text_with_ocr(pdf_bytes)

    # Comparar campos
    results = []
    for field_key, keyword in reference.items():
        value = find_field_value(keyword, text)
        results.append({"Campo": field_key, "Valor PDF": value})

    df_result = pd.DataFrame(results)

    # 🧾 Mostrar resultados
    st.subheader("📋 Resultado da Comparação")
    st.dataframe(df_result, use_container_width=True)

    # 💾 Download em JSON
    json_data = json.dumps(results, indent=2, ensure_ascii=False)
    st.download_button("📥 Baixar resultado em JSON", json_data, file_name="resultado_comparacao.json", mime="application/json")
