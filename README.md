# Buliçoso | Seu Assistente de Saúde Inteligente
Buliçoso é um projeto para a cadeira de Extensão 3 com o intuíto de desenvolver um Produto Mínimo Viável (MVP) que utiliza Large Language Model (LLM) e Geração Aumentada por Recuperação (RAG) para transformar o cuidado com a medicação, tornando-o simples e seguro para todos, com foco especial no público sênior.

🎯 Propósito do Projeto
Milhões de pessoas, especialmente idosos, enfrentam dois grandes desafios na rotina de saúde: a confusão com bulas complexas e o esquecimento de horários de medicamentos. O Buliçoso resolve ambos, utilizando o poder do Google Gemini para desburocratizar a informação e automatizar os lembretes.

✨ Planejamento inicial do MVP
O Buliçoso atua em duas frentes principais:

1. 📖 Simplificação de Bulas (Módulo RAG Híbrido)
O usuário insere o nome de um medicamento e o sistema busca por sua bula.

Gemini (via RAG) extrai as informações críticas e as resume em linguagem simples e amigável, focando em dosagem, efeitos colaterais e modo de uso.

Utilizamos uma arquitetura RAG Híbrida que prioriza a velocidade: busca na nossa Base Curada (ChromaDB) para medicamentos comuns ou na Web para medicamentos raros.

2. ⏰ Lembretes e Organização (Módulo Tool-Calling)
O usuário informa a medicação, a frequência e a duração do tratamento em linguagem natural.

O Gemini atua como um Agente, interpretando a intenção e acionando uma função de integração.

O sistema cria automaticamente lembretes recorrentes na Google Agenda do usuário (via API), garantindo que nenhuma dose seja esquecida.

🛠️ Stack Tecnológico Planejado (Para Apresentação)
Nosso projeto é baseado em uma arquitetura de ponta para garantir precisão e escalabilidade.

O Google Gemini API é o motor de inteligência central, responsável pelo raciocínio (simplificação de texto) e por atuar como nosso Agente Roteador (Tool-Calling). 

A orquestração do fluxo de trabalho é realizada pelo framework LangChain, que conecta o LLM às nossas bases de dados. Para a Base de Conhecimento Rápida (os 100-200 medicamentos mais comuns), utilizamos o ChromaDB como nosso Vector Store local. 

Por fim, a funcionalidade de agendamento é integrada através da API do Google Agenda, que recebe os comandos do Agente Gemini para criar os lembretes.