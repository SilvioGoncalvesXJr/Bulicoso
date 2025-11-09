# Buliçoso Backend API

Backend FastAPI para o projeto Buliçoso - Assistente de Saúde Inteligente.

## 🚀 Início Rápido

### 1. Instalação

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual (Windows)
.\venv\Scripts\Activate.ps1

# Ativar ambiente virtual (Linux/Mac)
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 2. Configuração

Copie o arquivo `.env.example` para `.env` e configure as variáveis:

```bash
cp .env.example .env
```

Edite o arquivo `.env` e configure:

- `GOOGLE_API_KEY`: Sua chave da API do Google Gemini (obrigatório)
- `CHROMA_DB_DIR`: Caminho para o diretório do ChromaDB (padrão: `./chroma_bulas_db`)
- `CHROMA_COLLECTION_NAME`: Nome da coleção no ChromaDB (padrão: `bulas_poc`)

### 3. Executar

```bash
# Desenvolvimento (com hot-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Ou usando o script Python
python -m app.main
```

A API estará disponível em:
- **API**: http://localhost:8000
- **Documentação Swagger**: http://localhost:8000/docs
- **Documentação ReDoc**: http://localhost:8000/redoc

## 📁 Estrutura do Projeto

```
Backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Aplicação FastAPI principal
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Configurações (Pydantic Settings)
│   │   └── dependencies.py     # Dependências para injeção
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── api.py           # Router principal da API v1
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── bulas.py    # Endpoints de bulas
│   │           └── lembretes.py # Endpoints de lembretes
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── bula.py             # Schemas Pydantic para bulas
│   │   └── lembrete.py         # Schemas Pydantic para lembretes
│   └── services/
│       ├── __init__.py
│       ├── rag_service.py      # Serviço RAG (ChromaDB + Gemini)
│       └── calendar_service.py # Serviço Google Calendar
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 📚 Endpoints da API

### Bulas

#### `POST /api/v1/bulas/consultar`

Consulta informações sobre um medicamento usando RAG.

**Request Body:**
```json
{
  "medicamento": "Dormec",
  "pergunta": "Quais são os efeitos colaterais?"
}
```

**Response:**
```json
{
  "medicamento": "Dormec",
  "resposta": "O Dormec pode causar...",
  "fonte": "Base Curada",
  "tempo_resposta": 1.23
}
```

#### `GET /api/v1/bulas/buscar/{medicamento}`

Busca documentos relacionados ao medicamento (sem processamento LLM).

### Lembretes

#### `POST /api/v1/lembretes/criar`

Cria lembretes de medicamento no Google Calendar.

**Request Body:**
```json
{
  "medicamento": "Dormec",
  "frequencia": "3 vezes ao dia",
  "duracao": "por 7 dias",
  "horario_inicio": "08:00",
  "observacoes": "Tomar após as refeições"
}
```

**Response:**
```json
{
  "sucesso": true,
  "mensagem": "Lembretes configurados com sucesso",
  "evento_id": "abc123xyz",
  "medicamento": "Dormec",
  "proximo_lembrete": "2024-01-15T08:00:00"
}
```

## 🔧 Desenvolvimento

### Adicionar Novos Endpoints

1. Crie o schema em `app/schemas/`
2. Crie o serviço em `app/services/` (se necessário)
3. Crie o endpoint em `app/api/v1/endpoints/`
4. Registre o router em `app/api/v1/api.py`

### Testes

```bash
# Instalar dependências de teste
pip install pytest pytest-asyncio httpx

# Executar testes
pytest
```

## 🐛 Troubleshooting

### Erro: "GOOGLE_API_KEY not set"

Configure a variável `GOOGLE_API_KEY` no arquivo `.env`.

### Erro: "ChromaDB collection not found"

Certifique-se de que o ChromaDB foi inicializado com os dados. Execute o script de inicialização (se disponível) ou verifique o caminho em `CHROMA_DB_DIR`.

### Erro: "Module not found"

Ative o ambiente virtual e instale as dependências:
```bash
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 📝 Notas

- O serviço de lembretes (`CalendarService`) atualmente retorna dados simulados. A integração real com Google Calendar API precisa ser implementada.
- O modelo de embeddings `all-MiniLM-L6-v2` será baixado automaticamente na primeira execução.
- A API usa CORS configurável via `CORS_ORIGINS` no `.env`.

## 📄 Licença

Este projeto faz parte do Buliçoso - Extensão 3.

