# Engenharia de Agentes de IA: Roteiro para Iniciantes

## **Temas Fundamentais (Ordem Progressiva)**

### **1. Fundamentos de Programação e Python**
- Python intermediário/avançado para Agentes de IA
- Estruturas de dados complexas
- Programação assíncrona
- APIs REST e GraphQL
- Manipulação de arquivos JSON/YAML

#### Material Didático e Exercícios
1. FundamentosPythonIA.ipynb
2. TypeHints&Docs.md
3. GerenciamentoContexto.md
4. ProgramacaoAssincrona.md
5. DecoradoresAgentesIA.md
6. main_A1.py (Simulação de Chat com Agente de IA Básico)

#### Visão Geral doAssistente de IA N1

No script `main_A1.py` foi criado um agente que, a partir de ferramentas (calcular e buscar), utiliza a API do Google Gemini para gerar respostas.

- **Biblioteca:** Uso da google.generativeai.
- **Modelo:** Configurado para usar gemini-2.0-flash.
- **Autenticação:** Carregamento seguro da chave de API via .env
- **Lógica:** O método `processar_mensagem` envia o histórico e o contexto das ferramentas para o Gemini, que gera a resposta final em linguagem natural.

### **2. Inteligência Artificial e Machine Learning**
- Conceitos básicos de ML
- Modelos de linguagem (LLMs)
- Embeddings e representações vetoriais
- Fine-tuning de modelos
- APIs de LLMs (OpenAI, Anthropic, open-source)

### **3. Frameworks para Agentes de IA**
- **LangChain** (padrão da indústria)
- **AutoGen** (Microsoft)
- **CrewAI** (para agentes colaborativos)
- **Semantic Kernel** (Microsoft)
- **Haystack** (para sistemas de perguntas e respostas)

### **4. Arquitetura de Sistemas de Agentes**
- Arquitetura de agentes (ReAct, ToT, etc.)
- Memória de agentes (curto/longo prazo)
- Ferramentas e function calling
- Orquestração de múltiplos agentes
- RAG (Retrieval Augmented Generation)

### **5. Bancos de Dados Especializados**
- Vector databases (Pinecone, Chroma, Weaviate)
- Bancos para memória (Redis, SQLite)
- Armazenamento de logs e traços

### **6. Deployment e Monitoramento**
- Containers (Docker)
- APIs (FastAPI, Flask)
- Monitoramento e logging
- Avaliação de performance de agentes

### **7. Tópicos Avançados**
- Agentic workflows
- Autonomous agents
- Human-in-the-loop systems
- Segurança e alignment