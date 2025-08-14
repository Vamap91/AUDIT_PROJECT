import re
import fitz  # PyMuPDF

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
