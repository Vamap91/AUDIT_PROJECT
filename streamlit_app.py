import streamlit as st
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import pandas as pd
import json
import tempfile

st.set_page_config(page_title="Comparador de PDF Fiscal", layout="centered")
st.title("📄 Comparador de Campos de Notas Fiscais")

# Lista de campos esperados
fields = {
    "FiscalDocumentNumber": "Número da NF",
    "FiscalDocumentIssuerCNPJ": "CNPJ Emitente",
    "FiscalDocumentCarglassCNPJ": "CNPJ Destinatário",
    "FiscalDocumentNCM": "NCM",
    "FiscalDocumentCFOP": "CFOP",
    "FiscalDocumentTotal": "Valor",
    "FiscalDocumentIPI": "IPI",
    "FiscalDocumentST": "ICMS ST",
    "FiscalDocumentDesconto": "Desconto",
    "FiscalDocumentICMS": "ICMS",
    "FiscalDocumentType": "Tipo"
}

# Função robusta de busca por campo
def find_field_value(keyword, text):
    if not keyword or not isinstance(keyword, str):
        return "Chave inválida"

    if not text or not isinstance(text, str):
        return "Texto inválido"

    lines = text.split("\n")

    for line in lines:
        if isinstance(line, str) and keyword.lower() in line.lower():
            parts = line.split(":")
            if len(parts) > 1:
                return parts[1].strip()
            else:
                return line.strip()

    return "Não encontrado"

# Função de extração de texto (OCR + texto embutido)
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
            raise ValueError("PDF pode estar em imagem. Tentando OCR...")

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
                if isinstance(ocr_text, str):
                    text += ocr_text
            except Exception:
                continue
        return text

# Upload do PDF
uploaded_file = st.file_uploader("📎 Faça upload da Nota Fiscal (PDF)", type=["pdf"])

if uploaded_file:
    st.success("✅ PDF carregado com sucesso!")

    extracted_text = extract_text_from_pdf(uploaded_file)

    if not extracted_text.strip():
        st.error("❌ Não foi possível extrair o texto do PDF.")
    else:
        extracted_data = []
        for field, label in fields.items():
            try:
                value = find_field_value(label, extracted_text)
            except Exception:
                value = "Erro ao extrair"
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
