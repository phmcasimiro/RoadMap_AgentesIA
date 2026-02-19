# Context Managers para Agentes de IA: Gerenciando Recursos

## O que é Gerenciamento de Contexto (Context Managers)?

- **Definição Simples:** Gereciamento de Contexto é implementado por meio de estruturas que garantem que recursos sejam adquiridos e liberados corretamente, mesmo em caso de erros.

- **Analogia:** É como uma porta automática:
    - Quando você entra → Porta abre (adquire recurso)
    - Quando você sai → Porta fecha (libera recurso)
    - Mesmo se você tropeçar → Porta ainda fecha!

## Por que são CRÍTICOS para Agentes de IA?

- Agentes de IA trabalham com recursos que DEVEM ser liberados:
    - Conexões com APIs (OpenAI, Anthropic, etc.)
        - Se não fechar, pode atingir limite de conexões
        - Pode vazar tokens de autenticação
    - Arquivos de log/histórico
        - Se não salvar, perde conversas importantes
        - Pode corromper dados
    - Sessões de banco de dados
        - Se não fechar, tranca tabelas
        - Desperdiça conexões
    - Recursos computacionais
        - Memória, GPU, processamento
        - Monitoramento de performance e custos

### Exemplo Simples de Gerenciamento de Contexto

```python
# PERIGOSO!
arquivo = open("conversa.json", "w")
arquivo.write(dados)
# E se der erro aqui? ↓
processar_algo_que_pode_falhar()
arquivo.close()  # ← Nunca executa se houver erro!
```

```python
# SEGURO!
with open("conversa.json", "w") as arquivo:
    arquivo.write(dados)
    processar_algo_que_pode_falhar()
# arquivo.close() é SEMPRE chamado, mesmo com erro!
```

## @Decorator: Forma Pytônica de criar Gerenciamento de Contexto

- Função com decorator `@contextmanager`
- `@contextmanager` forma mais simples e pythônica para Gerenciamento de Contexto de Função única

```python
from contextlib import contextmanager
from time import time

@contextmanager
def monitorar_performance(nome_agente: str):
    """Monitora performance de um agente"""
    
    # ===== PARTE 1: SETUP (equivalente ao __enter__) =====
    print(f"Iniciando monitoramento do {nome_agente}")
    inicio = time()
    
    try:
        yield  # ← PONTO CRUCIAL! Código do with executa aqui
        # ===== PARTE 2: CLEANUP NORMAL =====
    finally:
        # ===== PARTE 3: CLEANUP (equivalente ao __exit__) =====
        duracao = time() - inicio
        print(f"{nome_agente} executou em {duracao:.2f}s")
```

```python
with monitorar_performance("AgentePesquisa"):
    # 1. Executa: print("Iniciando...")
    # 2. Executa: inicio = time()
    # 3. yield pausa aqui ↓
    
    import time
    time.sleep(1.5)  # ← Código do usuário executa
    
    # 4. Retorna ao yield ↑
    # 5. Executa finally: duracao = time() - inicio
    # 6. Executa: print(" ... executou em 1.50s")

# Saída:
# Iniciando monitoramento do AgentePesquisa
# AgentePesquisa executou em 1.50s
```

## Gerenciamento de Contexto para Agentes de IA

### Aplicaçao 1: Gerenciar Conexão com API OpenAI

```python
from contextlib import contextmanager
import openai

@contextmanager
def sessao_openai(api_key: str):
    """Gerencia sessão com OpenAI"""
    print("Conectando à OpenAI...")
    openai.api_key = api_key
    
    try:
        yield openai
    finally:
        print("Limpando credenciais...")
        openai.api_key = None  # Remove API key da memória

# Uso
with sessao_openai("sk-...") as client:
    response = client.ChatCompletion.create(...)
# API key é removida automaticamente!
```

### Aplicaçao 2: Controlar Custos de IA

```python
@contextmanager
def limite_custo(max_dolares: float): # Define limite de custo
    """Monitora custo e aborta se ultrapassar limite"""
    custo_total = 0
    
    class MonitorCusto: # Classe para monitorar custo
        def adicionar(self, tokens: int): # Adiciona custo
            nonlocal custo_total # Permite modificar a variável externa
            custo_por_token = 0.00002  # Exemplo: 2 centavos por token
            custo_total += tokens * custo_por_token # Adiciona custo
            
            if custo_total > max_dolares: # Aborta se ultrapassar limite
                raise ValueError(f"Limite de ${max_dolares} ultrapassado!")
    
    monitor = MonitorCusto() # Instancia monitor
    
    try: # Tenta executar código
        yield monitor # Retorna monitor
    finally: # Sempre executa
        print(f"Custo total: ${custo_total:.4f}") # Exibe custo total


with limite_custo(max_dolares=1.0) as monitor: # Abre contexto
    for i in range(10): # Executa 10 chamadas
        # Simula chamada de API
        monitor.adicionar(tokens=1000) # Simula a chamada de API com 1000 tokens
# Aborta automaticamente se ultrapassar $1
```

### Aplicaçao 3: Gerenciamento de Contexto Aninhado (Monitorar Performance e Custos)

```python
with monitorar_performance("Sistema Completo"): # Monitora performance
    with GerenciadorSessaoIA("log.json") as sessao: # Gerencia sessão
        with limite_custo(5.0) as monitor: # Limita custo
            resposta = sessao.conversar("Pesquise sobre IA") # Executa chamada de API
            monitor.adicionar(500) # Adiciona custo
# Todos os recursos são liberados na ordem inversa!
# 1. sessao.close()
# 2. monitor.close()
```

#### Boas Práticas para Agentes de IA
    - Sempre use context managers para:
    - Conexões com APIs (OpenAI, Anthropic, etc.)
    - Arquivos de log/histórico
    - Sessões de banco de dados
    - Monitoramento de custos
    - Medição de performance

No `__exit__` ou finally:
    - Sempre libere recursos (feche conexões, arquivos)
    - Salve dados importantes
    - Registre métricas (tempo, custo, tokens)

Tratamento de erros:
    - Use try/except no `__enter__` para inicialização
    - Use finally no `__exit__` para cleanup garantido
    - Retorne False no `__exit__` para propagar exceções

#### Resumo sobre Gerenciamento de Contexto:

- Garantem limpeza de recursos mesmo com erros
- Carregam/salvam dados automaticamente
- Monitoram custos e performance
- Gerenciam conexões com APIs

Duas formas:
- Decorador: @contextmanager com yield (para casos simples)
- Classe: __enter__ e __exit__ (para casos complexos)