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
