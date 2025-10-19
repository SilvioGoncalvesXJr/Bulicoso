import os
import re
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# === Configurações ===
DB_DIR = "./chroma_bulas_local"
COLLECTION_NAME = "bulas_local"
BATCH_DIR = "batches"


# === Funções auxiliares ===
def clean_text(text):
    return re.sub(r"\s+", " ", text).strip()


# =LÓGICA CORRIGIDA=================================
def extract_fields(med_text):
    """Extrai os campos do medicamento em um dicionário."""
    fields = {
        "Nome Comercial": "", "Forma de Apresentação": "", "Administração": "",
        "Dose": "", "Ação": "", "Reação Adversa": "", "Interação": ""
    }
    for field in fields.keys():

        # [REGEX CORRIGIDO]
        # Este regex (baseado no seu original) procura pelo próximo campo
        # (ex: "Ação:") ou pelo fim do texto (\Z).
        # Esta é a versão correta que captura todos os campos.
        pattern = rf"{re.escape(field)}\s*:\s*(.*?)(?=\s*[A-ZÁÉÍÓÚÂÊÔÃÕÇ]+\s*:|\Z)"

        match = re.search(pattern, med_text, re.IGNORECASE | re.DOTALL)
        if match:
            fields[field] = clean_text(match.group(1))

    return fields


# =FIM DA CORREÇÃO=================================


def split_medications_to_docs(batch_text):
    """
    Encontra cada medicamento e cria UM Documento (grande) por medicamento,
    com o texto formatado.
    """
    # Este padrão encontra o "1.42 DIPIRONA SÓDICA"
    pattern = re.compile(r"\d+\.\d+\s+([A-ZÁÉÍÓÚÂÊÔÃÕÇ0-9\s\-\(\)]+)(?=\n| Nome comercial:)")
    matches = list(pattern.finditer(batch_text))
    docs = []

    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(batch_text)

        med_block = batch_text[start:end].strip()
        med_block_cleaned = re.sub(r"^\d+\.\d+\s+", "", med_block).strip()
        med_name = clean_text(match.group(1))

        # 1. Extrai os campos do bloco (usando a função corrigida)
        fields = extract_fields(med_block_cleaned)

        # [DEBUG OPCIONAL] Descomente a linha abaixo para ver no terminal
        # se todos os campos estão sendo extraídos corretamente.
        # print(f"\n[DEBUG] Campos extraídos para {med_name}:\n{fields}")

        # 2. Monta o page_content formatado
        content_parts = [f"Medicamento: {med_name}"]
        for field_name, content in fields.items():
            if content:
                content_parts.append(f"{field_name}: {content}")

        if content_parts:
            content_parts[-1] = re.sub(r"-\s*\d+\s*-$", "", content_parts[-1]).strip()

        full_content_string = "\n\n".join(content_parts)

        # 4. Cria UM Documento por medicamento
        doc = Document(
            page_content=full_content_string,
            metadata={"title": med_name}
        )
        docs.append(doc)

    return docs


# === Inicializa embeddings e Chroma ===
print("[INFO] Carregando modelo de embeddings...")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectordb = Chroma(
    persist_directory=DB_DIR,
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings
)

# === Inicializa o Text Splitter ===
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150,
    length_function=len,
    separators=["\n\n", "\n", ". ", " ", ""]
)

# === Itera sobre batches ===
batch_files = sorted(
    [f for f in os.listdir(BATCH_DIR) if f.endswith(".txt")],
    key=lambda x: int(re.findall(r'\d+', x)[0])
)
print(f"[INFO] Encontrados {len(batch_files)} arquivos na pasta '{BATCH_DIR}'.")

all_docs_full = []
for batch_file in batch_files:
    batch_path = os.path.join(BATCH_DIR, batch_file)
    print(f"\n[PROCESSANDO] {batch_path} ...")
    with open(batch_path, "r", encoding="utf-8") as f:
        text = f.read()

    docs_from_file = split_medications_to_docs(text)
    print(f"  -> Encontrados {len(docs_from_file)} medicamentos.")
    all_docs_full.extend(docs_from_file)

# [ETAPA FINAL]
if all_docs_full:
    print(f"\n[INFO] Total de {len(all_docs_full)} medicamentos encontrados.")

    print(f"[INFO] Dividindo medicamentos em chunks de ~{text_splitter._chunk_size} caracteres...")
    final_chunks = text_splitter.split_documents(all_docs_full)

    print(f"[INFO] {len(all_docs_full)} medicamentos geraram {len(final_chunks)} chunks para vetorização.")

    print(f"\n[INFO] Adicionando {len(final_chunks)} chunks ao ChromaDB (salvando automaticamente)...")
    vectordb.add_documents(final_chunks)

    print("\n✅ Vetorização completa!")
else:
    print("\n⚠️ Nenhum documento foi encontrado para vetorizar.")