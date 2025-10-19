import os
import re
import sys
from langchain_community.document_loaders import PyPDFLoader

PDF_PATH = "guia-medicamentos.pdf"
BATCH_MEDICAMENTOS = 1
START_PAGE = 22

# === Carregar PDF ===
loader = PyPDFLoader(PDF_PATH)
pages = loader.load_and_split()
total_pages = len(pages)
print(f"[INFO] Total de páginas no PDF: {total_pages}")

# === Juntar texto das páginas úteis ===
text = "\n".join([p.page_content for p in pages[START_PAGE:]])

# === Regex robusto para identificar medicamentos ===
pattern = re.compile(r"\d+\.\d+\s*\n?[A-ZÁÉÍÓÚÂÊÔÃÕÇ0-9\s\-\(\)]+(?=\n)")
matches = list(pattern.finditer(text))
print(f"[INFO] Medicamentos detectados: {len(matches)}")

if not matches:
    print("[ERRO] Nenhum medicamento detectado. Verifique o regex ou o texto.")
    sys.exit(1)

# === Criar diretório para batches ===
os.makedirs("batches", exist_ok=True)

# === Gerar batches (sem vetorizar ainda) ===
for i in range(0, len(matches), BATCH_MEDICAMENTOS):
    batch_start = matches[i].start()
    batch_end = matches[i + BATCH_MEDICAMENTOS].start() if i + BATCH_MEDICAMENTOS < len(matches) else len(text)
    batch_text = text[batch_start:batch_end].strip()

    # Evitar salvar lotes vazios
    if len(batch_text.strip()) < 30:
        print(f"[AVISO] Lote {i+1} parece vazio, ignorando.")
        continue

    batch_file = f"batches/batch_{i+1}_{min(i+BATCH_MEDICAMENTOS, len(matches))}.txt"
    with open(batch_file, "w", encoding="utf-8") as f:
        f.write(batch_text)

    # Mostra nome detectado
    preview = " ".join(batch_text.split("\n")[:2]).strip()
    print(f"[INFO] Lote salvo: {batch_file} | Preview: {preview[:120]}...")

print(f"\n✅ Todos os batches foram gerados em: {os.path.abspath('batches')}")
print("Agora execute o script 'vectorize_batches.py' para vetorizar cada batch.")
