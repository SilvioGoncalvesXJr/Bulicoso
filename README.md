## Extensão3

Projeto com dois módulos independentes e complementares:

- tradutor_LangChain: API de tradução baseada em LangChain + Gemini.
- Embedding_Gemini: pipeline RAG simples (criação de base vetorial com PDF e consulta via Gemini).


### Requisitos gerais
- Python 3.12
- Conta e chave de API do Google AI Studio (variável `GOOGLE_API_KEY`)
- Windows PowerShell (as instruções abaixo assumem Windows)

### Instalação das dependências
Instale todas as dependências necessárias usando o arquivo `requirements.txt`:

```powershell
cd C:\Extensão3
pip install -r requirements.txt
```


### Variáveis de ambiente
Crie um arquivo `.env` na raiz do projeto (ou em cada subpasta, se preferir) contendo:

```
GOOGLE_API_KEY=coloque_sua_chave_aqui
```

Se você tiver uma chave do LangSmith, pode adicioná-la também (opcional):

```
LANGSMITH_API_KEY=sua_chave_langsmith
```


## tradutor_LangChain

### Visão geral
Serviço de tradução exposto via FastAPI com LangServe. Ele publica uma rota `/tradutor` que recebe `{ idioma, texto }` e retorna o texto traduzido usando o modelo Gemini.

Arquivos principais:
- `tradutor_LangChain/codigo.py`: define a cadeia (`chain`) de tradução usando `ChatGoogleGenerativeAI` e `ChatPromptTemplate`.
- `tradutor_LangChain/serve.py`: sobe uma API FastAPI e registra a rota com LangServe.
- `tradutor_LangChain/cliente.py`: exemplo de consumo remoto da cadeia via HTTP.

### Instalação
Certifique-se de ter instalado as dependências do `requirements.txt` e o arquivo `.env` com `GOOGLE_API_KEY` disponível (na raiz ou dentro de `tradutor_LangChain/`).

### Execução do servidor

```powershell
cd C:\Extensão3\tradutor_LangChain
python serve.py
```

Isso iniciará o servidor em `http://localhost:8000`. Para testar no playground do LangServe:

- Abra `http://localhost:8000/tradutor/playground/` no navegador.

### Exemplo de cliente

Com o servidor rodando, em outro terminal:

```powershell
cd C:\Extensão3\tradutor_LangChain
python cliente.py
```

O cliente faz uma chamada remota à rota `/tradutor`, enviando `{ idioma, texto }` e imprime a tradução.


## Embedding_Gemini (RAG texto)

### Visão geral
Pipeline simples de RAG que:
1) Lê PDFs em `Embedding_Gemini/rag_texto/base/`.
2) Quebra em chunks (tamanho e overlap configuráveis).
3) Gera embeddings com `GoogleGenerativeAIEmbeddings` e persiste no ChromaDB em `Embedding_Gemini/rag_texto/db/`.
4) Consulta a base vetorial comparando a pergunta do usuário e monta um contexto para o modelo Gemini responder.

Arquivos principais:
- `Embedding_Gemini/rag_texto/criar_db.py`: cria o banco vetorial a partir dos PDFs.
- `Embedding_Gemini/rag_texto/main.py`: realiza a consulta (pergunta) usando o banco vetorial.
- `Embedding_Gemini/rag_texto/requirements.txt`: dependências mínimas para este módulo (use o `requirements.txt` da raiz).

### Instalação
Certifique-se de ter instalado as dependências do `requirements.txt` e o arquivo `.env` com `GOOGLE_API_KEY` disponível (na raiz ou dentro de `Embedding_Gemini/rag_texto/`).

Coloque seus PDFs em `Embedding_Gemini\rag_texto\base\` (ex.: `FAQ Python Video YouTube.pdf`).

### Criar a base vetorial (Chroma)

```powershell
cd C:\Extensão3\Embedding_Gemini\rag_texto
python criar_db.py
```

Ao final, a pasta `db/` será criada/preenchida com os vetores persistidos.

### Consultar a base (perguntas)

O script `main.py` solicita a pergunta no console, busca os chunks mais relevantes no Chroma e envia um prompt ao Gemini:

```powershell
cd C:\Extensão3\Embedding_Gemini\rag_texto
python main.py
```

Notas importantes:
- O caminho do banco no exemplo de código está definido como `C:\Extensão3\db`. Se você permanecer usando o `criar_db.py` como fornecido, o Chroma salva em `Embedding_Gemini/rag_texto/db`. Ajuste `CAMINHO_DB` em `main.py` para `Embedding_Gemini\rag_texto\db` se quiser reutilizar a base criada por `criar_db.py`:

```python
CAMINHO_DB = r"C:\\Extensão3\\Embedding_Gemini\\rag_texto\\db"
```

- Ajuste `k` e o limiar de relevância em `main.py` conforme sua necessidade (ex.: `k=3` e score mínimo `0.7`).

### Modelo de Embedding (obrigatório)
É obrigatório usar exatamente o modelo abaixo para que o embedding funcione corretamente. Outros nomes (por exemplo, `gemini-embedding-1.0` ou `gemini-embedding-001` sem o prefixo `models/`) não funcionaram nos testes.

```python
from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)
```


## Dicas e resolução de problemas
- Sem `GOOGLE_API_KEY` no `.env`, os scripts irão falhar de forma explícita.
- Se o LangServe não abrir o playground, verifique se o servidor está de pé em `localhost:8000` e se não há conflito de portas.
- Ao trabalhar com PDFs grandes, ajuste `chunk_size` e `chunk_overlap` em `criar_db.py` para qualidade/velocidade.
- Se mudar caminhos no Windows, use strings raw (`r"..."`) ou duplique barras.


## Estrutura relevante
- `tradutor_LangChain/`: API de tradução com LangServe.
- `Embedding_Gemini/rag_texto/`: criação e consulta de base vetorial (RAG).
- `venv/`: ambiente virtual Python com executáveis (inclui `uvicorn.exe`).


