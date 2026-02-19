# PROGRAMAÇÃO ASSÍNCRONA

## O que é Programação Assíncrona?

- **Definição Simples:** Programação assíncrona é o que permite que seu código execute múltiplas tarefas ao mesmo tempo sem bloquear a execução enquanto espera por operações lentas (como chamadas de API, leitura de arquivos, consultas a banco de dados).

- **Analogia do Restaurante**
  - Garçom **Síncrono** (Tradicional): 
    - 1. Vai até mesa 1
    - 2. Anota pedido
    - 3. Vai até cozinha
    - 4. FICA PARADO esperando comida ficar pronta (5 min) ⏰
    - 5. Leva para mesa 1
    - 6. Vai até mesa 2... (repete tudo)

  - Garçom **Assíncrono**
    - 1. Vai até mesa 1, anota pedido, envia para cozinha
    - 2. Enquanto cozinha prepara, vai até mesa 2, anota pedido
    - 3. Enquanto cozinha prepara, vai até mesa 3, anota pedido
    - 4. Comida da mesa 1 fica pronta → entrega
    - 5. Comida da mesa 2 fica pronta → entrega
    - 6. Comida da mesa 3 fica pronta → entrega

- Por que essa é uma capacidade crítica para Agentes de IA?
  - Resposta Simples: Porque os agentes de IA fazem muitas chamadas, por exemplo, chamadas de API, leitura de arquivos, consultas a banco de dados, etc. e precisam lidar com essas operações lentas e bloqueantes.

```python
# Agente Síncrono (LENTO)
def agente_sincrono():
    r1 = consultar_openai("pergunta 1")      # Espera 2s
    r2 = consultar_google("pesquisa 1")      # Espera 1s
    r3 = consultar_wikipedia("termo 1")      # Espera 1.5s
    r4 = consultar_banco_dados("query 1")    # Espera 0.5s
    # TOTAL: 2 + 1 + 1.5 + 0.5 = 5 segundos 🐌

# Agente Assíncrono (RÁPIDO)
async def agente_assincrono():
    '''async def define uma função assíncrona'''
    resultados = await asyncio.gather(
        consultar_openai("pergunta 1"),
        consultar_google("pesquisa 1"),
        consultar_wikipedia("termo 1"),
        consultar_banco_dados("query 1")
    )
    '''asyncio.gather() executa todas as chamadas ao mesmo tempo'''
    # TOTAL: max(2, 1, 1.5, 0.5) = 2 segundos 
```

### Casos de Uso em Agentes de IA:

- **Multi-Agent Systems (CrewAI, AutoGen)**
  - Vários agentes trabalhando simultaneamente
  - Cada agente fazendo suas próprias pesquisas
- **RAG (Retrieval Augmented Generation)**
  - Buscar em múltiplos bancos vetoriais ao mesmo tempo
  - Consultar várias fontes de conhecimento
- **Tool Calling Paralelo**
  - Agente decide usar 5 ferramentas diferentes
  - Executa todas em paralelo
- **Batch Processing**
  - Processar 1000 documentos
  -Fazer embeddings de forma paralela

### Conceitos Fundamentais

1. `async` e `await`
- Use `async def` para declarar função assíncrona
- Use `await` para chamar função assíncrona
- Só pode usar `await` dentro de funções async

```python
# Função normal (síncrona)
def funcao_normal():
    return "resultado"

# Função assíncrona (coroutine)
async def funcao_assincrona():
    return "resultado"

# Como chamar
resultado = funcao_normal()  # Chamada direta

# ERRADO
resultado = funcao_assincrona()  # Retorna coroutine, não executa!

# CORRETO
resultado = await funcao_assincrona()  # Espera e retorna resultado
```

2. `asyncio.gather()` - Paralelização

- Executa múltiplas chamadas assíncronas ao mesmo tempo

```python
# Executa múltiplas coroutines em PARALELO
# Se uma tarefa falhar, não cancela as outras
resultados = await asyncio.gather(
    tarefa1(),
    tarefa2(),  # Pode dar erro
    tarefa3(),
    return_exceptions=True  # Retorna Exception em vez de levantar erro
)
# resultados = [resultado1, resultado2, resultado3]
```

3. `asyncio.run()` - Ponto de Entrada

- Executa a função assíncrona principal
- Inicializa o loop de eventos
- Fecha o loop de eventos

```python
async def main():
    """Função principal assíncrona"""
    # Código assíncrono aqui
    resultado = await funcao_assincrona()
    print(resultado)

# Executa o event loop
asyncio.run(main())  # ← Ponto de entrada do código assíncrono
```

4. Context Managers Assíncronos

- Usado para gerenciar recursos assíncronos
- Similar ao `with` em blocos síncronos
- Implementa `__aenter__` e `__aexit__`

```python
class RecursoAssincrono:
    async def __aenter__(self):
        """Chamado ao entrar no async with"""
        # Setup assíncrono
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Chamado ao sair do async with"""
        # Cleanup assíncrono
        pass

# Uso
async with RecursoAssincrono() as recurso:
    await recurso.fazer_algo()
```
#### Partes de um Código

- **Parte 1:** Classe do Agente Assíncrono
  - Por que `session = None`?
  - `aiohttp.ClientSession()` deve ser criado dentro de um event loop assíncrono
  - Não podemos criar no `__init__` (que é síncrono)
  - Vamos criar no `__aenter__` (assíncrono)

```python
import asyncio
import aiohttp  # Biblioteca HTTP assíncrona (equivalente ao requests)
from typing import List, Dict
import time

class AgenteAssincrono:
    """Agente que faz chamadas paralelas para múltiplas fontes"""
    
    def __init__(self, nome: str):
        self.nome = nome
        self.session = None  # Sessão HTTP reutilizável
```

- **Parte 2:** Context Manager Assíncrono
  - `__aenter__` cria conexão HTTP reutilizável (mais eficiente que criar/fechar a cada request)
  - `__aexit__` sempre fecha a sessão (evita memory leaks)
  - Como usar: `async with AgenteAssincrono("nome") as agente:`

```python
    async def __aenter__(self): # Cria conexão HTTP reutilizável
        """Context manager assíncrono"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb): # Fecha a sessão
        await self.session.close()  # Importante: fecha conexões HTTP
```

- **Parte 3:** Consulta Assíncrona

```python
    async def consultar_api(self, url: str, query: str) -> Dict:
        """Consulta uma API assincronamente"""
        # Simula latência de rede (em produção, seria uma chamada HTTP real)
        await asyncio.sleep(1)  # NÃO bloqueia! Permite outras tarefas executarem
        
        return {
            "fonte": url,
            "query": query,
            "resultado": f"Dados de {url} sobre {query}",
            "status": "sucesso"
        }
```

- Diferença Crucial entre síncrono e assíncrono

```python
# Síncrono - BLOQUEIA tudo por 1 segundo
time.sleep(1)

# Assíncrono - Permite outras tarefas executarem durante 1 segundo
await asyncio.sleep(1)
```

- **Parte 4:** Pesquisa Paralela (O Coração!)

```python
    async def pesquisar_multiplas_fontes(self, 
                                         query: str, 
                                         fontes: List[str]) -> List[Dict]:
        """Pesquisa em múltiplas fontes em paralelo"""
        print(f"🔍 {self.nome} pesquisando: {query}")
        
        # Cria lista de coroutines (não executa ainda!)
        tarefas = [
            self.consultar_api(fonte, query)
            for fonte in fontes
        ]
        
        # Executa TODAS em paralelo e espera TODAS terminarem
        resultados = await asyncio.gather(*tarefas, return_exceptions=True)
        
        return resultados
```

- Fluxo de Execução

```python
fontes = ["wikipedia", "arxiv", "medium"]

# 1. Cria 3 tarefas (ainda não executadas)
tarefas = [
    consultar_api("wikipedia", "IA"),
    consultar_api("arxiv", "IA"),
    consultar_api("medium", "IA")
]

# 2. asyncio.gather() inicia TODAS ao mesmo tempo
# Tempo 0.0s: Todas começam
# Tempo 1.0s: Todas terminam (porque dormem 1s cada)
# Total: 1 segundo (não 3!)
```

- **Parte 5:** Processamento em Lote

```python
    async def processar_em_lote(self, queries: List[str]) -> List[str]:
        """Processa múltiplas queries em sequência (cada uma paralelizada)"""
        resultados = []
        
        for query in queries:  # SEQUENCIAL (uma query de cada vez)
            fontes = ["google", "bing", "duckduckgo", "yahoo"]
            # Mas cada query pesquisa em 4 fontes EM PARALELO
            resultados_query = await self.pesquisar_multiplas_fontes(query, fontes)
            
            resumo = f"Query '{query}': {len(resultados_query)} fontes consultadas"
            resultados.append(resumo)
        
        return resultados
```

- ESTRUTURA:
  - Query "LangChain" → [google, bing, duckduckgo, yahoo] em PARALELO → 1s
  - Query "AutoGen"   → [google, bing, duckduckgo, yahoo] em PARALELO → 1s
  - Query "CrewAI"    → [google, bing, duckduckgo, yahoo] em PARALELO → 1s
  - TOTAL: 3 segundos (não 12!)



#### Código Completo Detalhado

```python
import asyncio
import time
from typing import List, Dict

class AgenteAssincrono: # Agente Assíncrono
    def __init__(self, nome: str): # Inicializa o agente
        self.nome = nome # Nome do agente
    
    async def consultar_api(self, url: str, query: str) -> Dict:
        """Simula consulta a API com latência"""
        print(f"  Consultando {url}...")
        await asyncio.sleep(1)  # Simula latência da rede
        print(f"  {url} respondeu!")
        return {
            "fonte": url,
            "resultado": f"Dados de {url} sobre '{query}'"
        } # Retorna os resultados
    
    async def pesquisar_paralelo(self, query: str, fontes: List[str]) -> List[Dict]: 
        """Pesquisa em todas as fontes simultaneamente"""
        print(f"\n🔍 Iniciando pesquisa paralela: '{query}'")
        
        # Cria todas as tarefas
        tarefas = [self.consultar_api(fonte, query) for fonte in fontes]
        
        # Executa em paralelo
        inicio = time.time() # Inicia o timer
        resultados = await asyncio.gather(*tarefas) # Retorna lista de resultados
        duracao = time.time() - inicio # Calcula a duração
        
        print(f"⚡ Concluído em {duracao:.2f}s ({len(fontes)} fontes)")
        return resultados # Retorna os resultados

async def main(): # Função principal
    agente = AgenteAssincrono("PesquisadorTurbo") # Cria o agente
    
    # Pesquisa em 4 fontes ao mesmo tempo
    resultados = await agente.pesquisar_paralelo(
        query="Agentes de IA",
        fontes=["Wikipedia", "ArXiv", "Medium", "GitHub"]
    ) # Pesquisa em paralelo
    
    print("\nResultados:") # Imprime os resultados
    for r in resultados:
        print(f"  - {r['resultado']}")

# Executa
asyncio.run(main())
```

#### Saída do Código Completo Detalhado
Iniciando pesquisa paralela: 'Agentes de IA'
  Consultando Wikipedia...
  Consultando ArXiv...
  Consultando Medium...
  Consultando GitHub...
  Wikipedia respondeu!
  ArXiv respondeu!
  Medium respondeu!
  GitHub respondeu!
Concluído em 1.00s (4 fontes)  ← 4x mais rápido que síncrono!

Resultados:
  - Dados de Wikipedia sobre 'Agentes de IA'
  - Dados de ArXiv sobre 'Agentes de IA'
  - Dados de Medium sobre 'Agentes de IA'
  - Dados de GitHub sobre 'Agentes de IA'

#### Comparação de Agentes Síncronos e Assíncronos

```python
import time
import asyncio

# ========== VERSÃO SÍNCRONA ==========
def consultar_sincrono():
    time.sleep(1)  # Bloqueia tudo!
    return "resultado"

def teste_sincrono():
    print("\nTeste Síncrono:")
    inicio = time.time()
    
    for i in range(5):
        resultado = consultar_sincrono()
        print(f"Chamada {i+1} concluída")
    
    duracao = time.time() - inicio
    print(f"Total: {duracao:.2f}s")

# ========== VERSÃO ASSÍNCRONA ==========
async def consultar_assincrono():
    await asyncio.sleep(1)  # NÃO bloqueia!
    return "resultado"

async def teste_assincrono():
    print("\n⚡ Teste Assíncrono:")
    inicio = time.time()
    
    # Cria 5 tarefas
    tarefas = [consultar_assincrono() for _ in range(5)]
    
    # Executa todas em paralelo
    resultados = await asyncio.gather(*tarefas)
    
    for i, _ in enumerate(resultados):
        print(f"Chamada {i+1} concluída")
    
    duracao = time.time() - inicio
    print(f"Total: {duracao:.2f}s")

# Executar
teste_sincrono()
asyncio.run(teste_assincrono())
```

#### Saída da Comparação

Teste Síncrono:
  Chamada 1 concluída
  Chamada 2 concluída
  Chamada 3 concluída
  Chamada 4 concluída
  Chamada 5 concluída
Total: 5.00s

Teste Assíncrono:
  Chamada 1 concluída
  Chamada 2 concluída
  Chamada 3 concluída
  Chamada 4 concluída
  Chamada 5 concluída
Total: 1.00s  ← 5x mais rápido!

### Boas Práticas de Programação Assíncrona para Agentes de IA

1. Use sempre `async with` para recursos HTTP
2. Trate erros em operações paralelas com `return_exceptions=True`
3. Use semáforos para limitar concorrência
4. Use timeouts para evitar travamentos

1. Use sempre `async with` para recursos HTTP

```python
# CORRETO
async with aiohttp.ClientSession() as session:
    async with session.get(url) as response:
        data = await response.json()

# ERRADO (vazamento de conexões)
session = aiohttp.ClientSession()
response = await session.get(url)
# session nunca é fechado!
```

2. Trate erros em operações paralelas com `return_exceptions=True`

```python
# CORRETO - Não cancela tudo se uma falhar
resultados = await asyncio.gather(
    tarefa1(),
    tarefa2(),
    tarefa3(),
    return_exceptions=True  # Retorna Exception em vez de propagar
)

# Verifica resultados
for i, r in enumerate(resultados):
    if isinstance(r, Exception):
        print(f"Tarefa {i} falhou: {r}")
    else:
        print(f"Tarefa {i} sucesso: {r}")
```

3. Use semáforos para limitar concorrência

```python
# Limita a 10 requests simultâneos (evita sobrecarregar APIs)
semaforo = asyncio.Semaphore(10)

async def consultar_com_limite(url):
    async with semaforo:  # Limita acesso
        return await consultar_api(url)

# Mesmo que tenha 1000 URLs, só 10 executam por vez
tarefas = [consultar_com_limite(url) for url in urls]
resultados = await asyncio.gather(*tarefas)
```

4. Use timeouts para evitar travamentos

```python
try:
    # Aborta se demorar mais de 5 segundos
    resultado = await asyncio.wait_for(
        consultar_api_lenta(),
        timeout=5.0
    )
except asyncio.TimeoutError:
    print("API demorou muito!")
```

### Resumo de Programação Assíncrona:

- Executa múltiplas tarefas simultaneamente
- Essencial para agentes modernos (até 10x mais rápido)
- Não bloqueia enquanto espera I/O (APIs, arquivos, BD)

- Palavras-chave importantes:

- `async def` - Define função assíncrona
- `await` - Espera resultado assíncrono
- `asyncio.gather()` - Executa múltiplas tarefas em paralelo
- `asyncio.run()` - Ponto de entrada
- `async with` - Context manager assíncrono

Quando usar:

- Chamadas de API (OpenAI, Google, etc.)
- Leitura/escrita de arquivos
- Consultas a banco de dados
- Operações de rede
- Cálculos intensivos de CPU (use multiprocessing)
