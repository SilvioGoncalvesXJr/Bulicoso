from dotenv import load_dotenv
from langchain_chroma.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI #Responde o chat de mensagens

CAMINHO_DB = r'C:\Extensão3\db'
load_dotenv()

prompt_template = '''
Responda a pergunta do usuário:
{pergunta}

com base nessas informações abaixo:
{base_conhecimento}
'''
def perguntar(): 
    pergunta = input("Escreva sua pergunta: ")#Isso pode vir através de forntend, usando as rotas, tudo certinho

    #carregar banco de dados
    funcao_embedding = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001"
    )
    db = Chroma(
        persist_directory=CAMINHO_DB,
        embedding_function=funcao_embedding
    )# vai precisar de 2 informações, onde está o banco de dados e função que fez o embedding do bd


    #Comparar a pergunta do usuário (embedding) com o meu banco de dados, retornando uma lista com vários resultados
    '''
    Nesse ponto o modelo irá analisar o bd e depois retornará algumas possíveis respostas no formato lista de tuplas,  e podemos delimitar a porcentagem
    das repostas que estão mais dentro do escopo da pergunta, indo de 0 a 1 (como 0 a 100%), e temos que ir testando os 
    melhores valores. Se deixar muito abrangente, fica complicado para encontrar, da mesma forma se form muito restritivo. Geralmente a primeira
    tupla(primeiro é o documento e o segundo é o score [doc][score]) é a que tem a melhor correlação, mas pode ser que não tenha um bom score e por isso precisamos filtrar
    '''
    resultados = db.similarity_search_with_relevance_scores(pergunta, k=3)#Quanto maior o k, mais contexto ao modelo. k é o nº de respostas com maiores correspondencias. Quanto mais passa, mais chances de achar a resposta, mas também aumenta o custo de tokens
    if len(resultados) == 0  or resultados[0][1] < 0.7:
        print("Não conseguiu encontrar uma informação relevante na base")
        return
    
    texto_resultado = []
    for resultado in resultados:
        texto = resultado[0].page_content #Page_content é onde tem a resposta em si
        texto_resultado.append(texto)

    #Para devolver as melhores respostas de forma organizada, juntando todos os elementos da lista com esses elementos de separação de linhas
    base_conhecimento = "\n\n----\n\n".join(texto_resultado) 
    prompt = ChatPromptTemplate.from_template(prompt_template)#mandar o prompt para o modelo
    prompt = prompt.invoke({"pergunta":pergunta,"base_conhecimento": base_conhecimento})

    modelo = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash"
    )
    texto_resposta = modelo.invoke(prompt).content
    print("Reposta da IA:", texto_resposta)

perguntar()