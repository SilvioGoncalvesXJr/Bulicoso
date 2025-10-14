'''
O LangServe serve para criar uma API de acesso rapido e direto a cadeia criada
através da utilização de FastAPI
'''
from codigo import chain
from fastapi import FastAPI
from langserve import add_routes #rotas a serem adicionadas

app = FastAPI(title="TradutorLLM", description="Traduza o texto que desejar para qualquer lingua")

#De forma simples, configurar a rota
add_routes(app, chain, path="/tradutor")

#Colocar a API no ar
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)

#Link de acesso: http://localhost:8000/tradutor/playground/