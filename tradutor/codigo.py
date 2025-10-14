import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser 
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
#SystemMessage é como deseja se comunicar com o modelo, o que ele deve fazer
#HumanMessage já é o input do usuário

load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")

# Agora você pode verificar se as chaves foram carregadas (opcional, bom para depuração)
if not os.getenv("LANGSMITH_API_KEY"):
    print("Chave da API LangSmith não encontrada. Verifique seu arquivo .env")
if not os.getenv("GOOGLE_API_KEY"):
    print("Chave da API do Google não encontrada. Verifique seu arquivo .env")

try:
        # 2. Passe a variável diretamente para o construtor usando o parâmetro 'google_api_key'
        model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=google_api_key
        )
        # # Exemplo de uso
        # print("Enviando pergunta para o Gemini...")
        # response = model.invoke("Olá, como você está?")
        # print("Resposta do Gemini:")
        # print(response.content)

except Exception as e:
    print(f"Ocorreu um erro: {e}")

'''
Quando recebemos o output do modelo, vem, além da resposta, várias outras informações, como o número de tokes, etc
O parse faz uma filtragem para que apareça apenas a resposta
'''
parser = StrOutputParser() 
# chain = model | parser
'''
o chain é uma das principais ferramentas do langchain, que cria um pipeline de execução
O input passa para o modelo e a sua resposta é encaminhada para o parser que processará e assim por diante
podendo incluir vários elementos na cadeia
Ai inves de ter que fazer isso:

resposta = model.invoke(mensagens)
texto = parser.invoke(resposta)

basta acionar a chain
'''

'''
Ao invés de precisar passar uma lista de mensagens fixas, hardcoded, pode estruturar um templat de prompt para 
deixar mais flexível e adaptado a interação com o usuário. Asssim, ao invés de fazer isso: 

mensagens = [
    SystemMessage("Traduza o texto a seguir para o inglês"),
    HumanMessage("Olá. Meu nome é Silvio e estou fazendo um teste de API e construção de modelo de LLM")
]

basta criar um template, como segue abaixo
'''
template_message = ChatPromptTemplate.from_messages([ #Construído a base de tuplas
    ("system", "Traduza o texto a seguir para {idioma}"), #mensagem para o sistema
    ("user", "{texto}") #Será passado o texto do usário
])
#Passar um dicionário com os parâmetros do template. Aqui pode ser o que o usuário quiser, delimitando por variável
#Com o acrescimo do template, podemos alterar a chain para incluir como elemento inicializador
chain = template_message | model | parser
#mensagens_formatadas = chain.invoke({"idioma": "francês", "texto": "Olá. Meu nome é Silvio e estou fazendo um teste de API e construção de modelo de LLM"})

#print(mensagens_formatadas)