import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import json
import re

st.set_page_config(page_title="Comparador de Campos de Notas Fiscais", layout="centered")

st.title("📄 Comparador de Campos de Notas Fiscais")
st.caption("📂 Faça upload da Nota Fiscal (PDF)")

# Upload do PDF
pdf_file = st.file_uploader("Drag and drop file here", type=["pdf"])

# Dicionário de palavras-chave para extração
field_keywords = {
    "FiscalDocumentNumber": ["Nº", "NUMERO", "NF", "NOTA FISCAL"],
    "FiscalDocumentIssuerCNPJ": ["CNPJ", "CNPJ EMITENTE"],
    "FiscalDocumentCarglassCNPJ": ["CNPJ DESTINATÁRIO", "DESTINATÁRIO", "RAZÃO SOCIAL"],
    "FiscalDocumentNCM": ["NCM"],
    "FiscalDocumentCFOP": ["CFOP"],
    "FiscalDocumentTotal": ["VALOR TOTAL DA NOTA", "VALOR TOTAL DOS SERVIÇOS", "TOTAL DA NOTA", "VALOR TOTAL"],
    "FiscalDocumentIPI": ["IPI", "VALOR TOTAL DO IPI"],
    "FiscalDocumentST": ["ICMS ST", "ICMS SUBST", "BASE DE CALCULO DO ICMS ST"],
    "FiscalDocumentDesconto": ["DESCONTO"],
    "FiscalDocumentICMS": ["ICMS", "BASE DE CALCULO DO ICMS"]
}

def extract_text_from_pdf(pdf_file):
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        text = ""
        for page in doc:
            text += page.get_text()
    return text

def find_field_value(keywords, text):
    for line in text.split("\n"):
        for keyword in keywords:
            if keyword.lower() in line.lower():
                match = re.search(r'([\d.,/-]+)', line)
                return match.group(0) if match else line.strip()
    return "Não encontrado"

if pdf_file:
    st.success("✅ PDF carregado com sucesso!")

    pdf_text = extract_text_from_pdf(pdf_file)

    results = []
    for field_name, keywords in field_keywords.items():
        value = find_field_value(keywords, pdf_text)
        results.append({"Campo": field_name, "Valor PDF": value})

    df = pd.DataFrame(results)

    st.subheader("📊 Resultado da Comparação")
    st.dataframe(df, use_container_width=True)

    # Baixar como JSON
    json_data = json.dumps(results, indent=2, ensure_ascii=False)
    st.download_button("📥 Baixar resultado em JSON", data=json_data, file_name="resultado.json", mime="application/json")
