import json
import re
import sys
from pathlib import Path
import fitz  # PyMuPDF
from tqdm import tqdm


ROOT = Path(__file__).parent
TEMPLATE_FILE = ROOT / "test.json"
OUTPUT_FILE = ROOT / "data.json"


def load_template():
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_text_from_pdf(path: Path) -> str:
    try:
        doc = fitz.open(path)
    except Exception:
        return ""
    texts = []
    for page in doc:
        try:
            texts.append(page.get_text())
        except Exception:
            continue
    return "\n".join(texts)


def find_first_regex(text, patterns):
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return ""


def extract_fields(text: str) -> dict:
    out = {}
    # nomor_perkara
    out["nomor_perkara"] = find_first_regex(text, [r"Nomor[:\s]*([\w\./\-\s]+)", r"No\.?[:\s]*([\w\./\-\s]+)"])
    # tanggal_putusan (Indonesian date simple)
    out["tanggal_putusan"] = find_first_regex(text, [r"(\d{1,2}\s+\w+\s+\d{4})"])
    # lokasi (Pengadilan Negeri / PN)
    out["lokasi"] = find_first_regex(text, [r"Pengadilan Negeri[\s:,-]*([A-Za-z0-9\s]+)", r"PN\s+([A-Za-z0-9\s]+)"])

    # nama_file and url will be filled by caller

    # Terdakwa: try to capture blocks following the word 'Terdakwa' or 'Terdakwa :' up to a blank line
    terdakwa_list = []
    for m in re.finditer(r"Terdakwa[:\s]*\n?([\s\S]{0,400}?)(?:\n\n|\n\r\n|$)", text, re.IGNORECASE):
        block = m.group(1).strip()
        # try to extract name and umur
        name = find_first_regex(block, [r"Nama[:\s]*([A-Za-z\s\-']+)", r"([A-Z][A-Za-z\s\-']{3,})"]) or block.splitlines()[0]
        umur = find_first_regex(block, [r"Umur[:\s]*(\d{1,3})", r"umur[:\s]*(\d{1,3})"]) or ""
        terdakwa_list.append({"nama": name.strip(), "umur": umur})
    out["terdakwa"] = terdakwa_list

    # hakim: try to find Ketua and Anggota
    hakim = []
    ketua = find_first_regex(text, [r"Ketua[:\s]*([A-Za-z\s]+)", r"Ketua Majelis[:\s]*([A-Za-z\s]+)"])
    if ketua:
        hakim.append({"ketua": ketua, "anggota": []})
        # anggota: find subsequent lines with 'Anggota' or list of names
        anggota_matches = re.findall(r"Anggota[:\s]*([A-Za-z,\s\n]+)", text)
        if anggota_matches:
            names = re.split(r"[,\n]", anggota_matches[0])
            hakim[0]["anggota"] = [{"nama": n.strip()} for n in names if n.strip()]

    out["hakim"] = hakim

    out["panitera"] = find_first_regex(text, [r"Panitera[:\s]*([A-Za-z\s]+)"])
    out["penuntut_umum"] = find_first_regex(text, [r"Penuntut Umum[:\s]*([A-Za-z\s]+)", r"Jaksa[:\s]*([A-Za-z\s]+)"])

    return out


def main():
    template = load_template()

    # find pdf files
    pdf_paths = list(ROOT.glob("pn-*/pdf/*.pdf"))
    if not pdf_paths:
        print("No PDFs found in pn-*/pdf folders.")
        return

    results = []
    for p in tqdm(pdf_paths, desc="Processing PDFs"):
        text = extract_text_from_pdf(p)
        data = extract_fields(text)
        # merge with template structure minimally
        entry = template.copy()
        # overwrite simple scalar fields if found
        for k in ["nomor_perkara", "tanggal_putusan", "lokasi", "panitera", "penuntut_umum"]:
            if data.get(k):
                entry[k] = data[k]
        entry["terdakwa"] = data.get("terdakwa", []) or []
        entry["hakim"] = data.get("hakim", []) or []
        entry["nama_file"] = p.name
        entry["url"] = str(p.resolve())
        results.append(entry)

    # write output
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(results)} entries to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
