'''
Caso eu queira usar esse API do modelo em outra aplicação, basta eu instaurar este arquivo de cliente
no código do cliente importando um RemoteRunnable, importando a chain que está ativa/no ar
'''
from langserve import RemoteRunnable

chain_remota = RemoteRunnable("http://localhost:8000/tradutor")
texto = chain_remota.invoke({"idioma": "espanhol", "texto": "Já deu like no vídeo? Se não, dá agora"})
print(texto)

#python cliente.py