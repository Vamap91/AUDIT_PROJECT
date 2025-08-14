import streamlit as st
import fitz  # PyMuPDF
import json
import re
import pandas as pd

st.set_page_config(page_title="Comparador de Campos de Notas Fiscais", layout="centered")

st.markdown("## 🧾 Comparador de Campos de Notas Fiscais")
st.markdown("📎 Faça upload da Nota Fiscal (PDF)")

uploaded_file = st.file_uploader("Drag and drop file here", type="pdf")

# Palavras-chave por campo
field_keywords = {
    "FiscalDocumentNumber": ["NF", "NF-e", "Nota Fiscal", "Número NF"],
    "FiscalDocumentIssuerCNPJ": ["Emitente", "CNPJ Emitente"],
    "FiscalDocumentCarglassCNPJ": ["Destinatário", "CNPJ Destinatário"],
    "FiscalDocumentNCM": ["NCM"],
    "FiscalDocumentCFOP": ["CFOP"],
    "FiscalDocumentTotal": ["VALOR TOTAL", "TOTAL DA NOTA", "VALOR TOTAL DOS SERVIÇOS"],
    "FiscalDocumentIPI": ["IPI", "VALOR TOTAL DO IPI"],
    "FiscalDocumentST": ["ICMS ST", "BASE DE CALCULO DO ICMS ST"],
    "FiscalDocumentDesconto": ["DESCONTO"],
    "FiscalDocumentICMS": ["ICMS", "BASE DE CALCULO DO ICMS"]
}

# Função inteligente para extrair valores por campo
def find_field_value(field_name, text):
    lines = text.split("\n")

    if field_name == "FiscalDocumentNumber":
        match = re.search(r"\b(?:NF[-: ]?|NF-e[-: ]?)\s*(\d{3,})", text, re.IGNORECASE)
        if match:
            return match.group(1)

    if field_name == "FiscalDocumentIssuerCNPJ":
        matches = re.findall(r"\d{2}[./]?\d{3}[./]?\d{3}[./]?\d{4}[-]?\d{2}", text)
        if matches:
            return matches[0]

    if field_name == "FiscalDocumentCarglassCNPJ":
        matches = re.findall(r"\d{2}[./]?\d{3}[./]?\d{3}[./]?\d{4}[-]?\d{2}", text)
        if len(matches) > 1:
            return matches[1]

    if field_name == "FiscalDocumentNCM":
        match = re.search(r"\bNCM[: ]+(\d{8})", text, re.IGNORECASE)
        if match:
            return match.group(1)

    # Fallback com palavras-chave
    keywords = field_keywords.get(field_name, [])
    for keyword in keywords:
        for line in lines:
            if not isinstance(line, str):
                continue
            if keyword.lower() in line.lower():
                parts = line.split(":")
                if len(parts) > 1:
                    return parts[1].strip()
                return line.strip()

    return "Não encontrado"

# Extrai texto do PDF
def extract_text_from_pdf(file):
    text = ""
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

if uploaded_file:
    st.success("✅ PDF carregado com sucesso!")

    extracted_text = extract_text_from_pdf(uploaded_file)

    results = []
    for field in field_keywords:
        value = find_field_value(field, extracted_text)
        results.append({"Campo": field, "Valor PDF": value})

    df = pd.DataFrame(results)

    st.markdown("### 📊 Resultado da Comparação")
    st.dataframe(df, use_container_width=True)

    # Botão para baixar como JSON
    json_result = json.dumps(results, indent=2, ensure_ascii=False)
    st.download_button(
        label="📥 Baixar resultado em JSON",
        data=json_result,
        file_name="resultado_comparacao.json",
        mime="application/json"
    )
