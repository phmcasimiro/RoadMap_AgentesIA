# Decoradores para Agentes de IA

## O que são Decoradores?

**Definição Simples:** Decoradores são funções que **modificam o comportamento** de outras funções sem alterar o código original delas.

**Sintaxe:**
```python
@decorador
def minha_funcao():
    pass

# É equivalente a:
minha_funcao = decorador(minha_funcao)
```

---

## Por que são CRÍTICOS para Agentes de IA?

Agentes de IA precisam de **funcionalidades transversais** que se aplicam a muitas funções:

1. **Logging e Monitoramento**
   - Registrar todas as chamadas de ferramentas
   - Rastrear o que o agente está fazendo

2. **Medição de Performance**
   - Quanto tempo cada operação leva?
   - Onde estão os gargalos?

3. **Validação de Dados**
   - Garantir que inputs sejam válidos
   - Evitar erros em runtime

4. **Cache de Resultados**
   - Evitar chamar APIs repetidamente
   - Economizar tempo e dinheiro

5. **Tratamento de Erros**
   - Retry automático em caso de falha
   - Graceful degradation (sistema continuar funcionando mesmo se algo der errado)

### **Problema sem decoradores:**
```python
# Código repetitivo em TODAS as funções
def consultar_api(query):
    logger.info(f"Consultando API: {query}")
    inicio = time.time()
    
    resultado = requests.get(f"api.com?q={query}")
    
    duracao = time.time() - inicio
    logger.info(f"Completou em {duracao}s")
    return resultado

def processar_texto(texto):
    logger.info(f"Processando texto: {texto}")
    inicio = time.time()
    
    resultado = modelo.processar(texto)
    
    duracao = time.time() - inicio
    logger.info(f"Completou em {duracao}s")
    return resultado

# Tudo se repete!
```

### **Solução com decoradores:**
```python
# Código limpo e reutilizável
@log_e_medir_tempo
def consultar_api(query):
    return requests.get(f"api.com?q={query}")

@log_e_medir_tempo
def processar_texto(texto):
    return modelo.processar(texto)

# Muito mais limpo! 
```

---

## Anatomia de um Decorador

### Estrutura Básica

```python
import functools

def meu_decorador(func):
    """
    func: função que será decorada
    """
    @functools.wraps(func)  # IMPORTANTE: preserva metadados da função original
    def wrapper(*args, **kwargs):
        # ANTES: Código executado ANTES da função original
        print(f"Antes de chamar {func.__name__}")
        
        # EXECUÇÃO: Chama a função original
        resultado = func(*args, **kwargs)
        
        # DEPOIS: Código executado DEPOIS da função original
        print(f"Depois de chamar {func.__name__}")
        
        return resultado
    
    return wrapper

# Uso
@meu_decorador
def saudar(nome):
    return f"Olá, {nome}!"

print(saudar("Pedro"))
# Saída:
# Antes de chamar saudar
# Depois de chamar saudar
# Olá, Pedro!
```

**Por que `@functools.wraps(func)`?**
```python
# SEM @functools.wraps
def decorador_ruim(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@decorador_ruim
def minha_funcao():
    """Documentação importante"""
    pass

print(minha_funcao.__name__)  # "wrapper"
print(minha_funcao.__doc__)   # None

# COM @functools.wraps
def decorador_bom(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@decorador_bom
def minha_funcao():
    """Documentação importante"""
    pass

print(minha_funcao.__name__)  # "minha_funcao"
print(minha_funcao.__doc__)   # "Documentação importante"
```

---

## Explicação Detalhada dos Decoradores do Código

### 1. Decorador de Logging

```python
import functools
import time
from typing import Callable
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO) # INFO é o nível de severidade dos logs
logger = logging.getLogger(__name__) # __name__ é o nome do módulo (no caso, "__main__")

def log_chamada(func: Callable) -> Callable: # Callable é um tipo de dado que representa uma função
    """Loga chamadas de funções do agente"""
    @functools.wraps(func) # Preserva metadados da função original
    def wrapper(*args, **kwargs): # *args e **kwargs são argumentos posicionais e nomeados
        # ANTES: Registra início da chamada
        logger.info(f"Chamando {func.__name__}") # __name__ é o nome da função
        inicio = time.time() # time.time() retorna o tempo atual em segundos
        
        # EXECUTA: Função original
        resultado = func(*args, **kwargs) # *args e **kwargs são argumentos posicionais e nomeados
        
        # DEPOIS: Registra conclusão e duração
        duracao = time.time() - inicio # time.time() retorna o tempo atual em segundos
        logger.info(f"{func.__name__} completou em {duracao:.2f}s") # __name__ é o nome da função
        
        return resultado # Retorna o resultado da função original
    return wrapper # Retorna o wrapper
```

**O que faz:**
- Registra quando uma função é chamada
- Mede quanto tempo levou
- Útil para debugar e monitorar agentes

**Uso:**
```python
@log_chamada
def consultar_base_conhecimento(query):
    time.sleep(2)
    return "Resposta"

resultado = consultar_base_conhecimento("O que é IA?")
# INFO:__main__: Chamando consultar_base_conhecimento
# INFO:__main__: consultar_base_conhecimento completou em 2.00s
```

---

### 2. Decorador de Medição de Tempo

```python
def medir_tempo(func: Callable) -> Callable: # Callable é um tipo de dado que representa uma função
    """Mede tempo de execução"""
    @functools.wraps(func) # Preserva metadados da função original
    def wrapper(*args, **kwargs): # *args e **kwargs são argumentos posicionais e nomeados
        inicio = time.time() # time.time() retorna o tempo atual em segundos
        resultado = func(*args, **kwargs) # *args e **kwargs são argumentos posicionais e nomeados
        fim = time.time() # time.time() retorna o tempo atual em segundos
        
        print(f"{func.__name__} levou {fim - inicio:.2f}s") # __name__ é o nome da função
        return resultado # Retorna o resultado da função original
    return wrapper # Retorna o wrapper
```

**O que faz:**
- Mede tempo de execução de forma simples
- Imprime diretamente no console (diferente do logger)

**Uso:**
```python
@medir_tempo
def gerar_embeddings(textos):
    time.sleep(1.5)
    return [0.1, 0.2, 0.3]

embeddings = gerar_embeddings(["texto1", "texto2"])
# gerar_embeddings levou 1.50s
```

---

### 3. Decorador de Validação de Entrada

```python
def validar_entrada(tipos: dict):
    """Valida tipos dos argumentos"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Combina args posicionais e kwargs em um dicionário
            todos_args = kwargs.copy()
            for i, arg in enumerate(args):
                nome_param = list(func.__annotations__.keys())[i]
                todos_args[nome_param] = arg
            
            # Valida tipos
            for param, tipo_esperado in tipos.items():
                if param in todos_args:
                    valor = todos_args[param]
                    if not isinstance(valor, tipo_esperado):
                        raise TypeError(
                            f"Parâmetro '{param}' deve ser {tipo_esperado.__name__}, "
                            f"recebeu {type(valor).__name__}"
                        )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

**O que faz:**
- Valida tipos dos parâmetros antes de executar a função
- Levanta `TypeError` se tipo estiver incorreto
- Previne bugs difíceis de encontrar

**Uso:**
```python
@validar_entrada({"texto": str, "temperatura": float})
def gerar_resposta(texto: str, temperatura: float):
    return f"Gerando com temp={temperatura}"

# Correto
gerar_resposta("Olá", 0.7)

# Erro: TypeError
gerar_resposta("Olá", "0.7")  # String em vez de float!
# TypeError: Parâmetro 'temperatura' deve ser float, recebeu str
```

---

### 4. Decorador de Cache

```python
def cache_resultado(tempo_expiracao: int = 300):
    """Cache simples com expiração em segundos"""
    def decorator(func: Callable) -> Callable:
        cache = {}  # Dicionário para armazenar resultados
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Cria chave única baseada nos argumentos
            chave = str(args) + str(sorted(kwargs.items()))
            
            # Verifica se está no cache e não expirou
            if chave in cache:
                resultado, timestamp = cache[chave]
                if time.time() - timestamp < tempo_expiracao:
                    print(f"Usando cache para {func.__name__}")
                    return resultado
            
            # Se não está em cache ou expirou, executa função
            resultado = func(*args, **kwargs)
            cache[chave] = (resultado, time.time())
            return resultado
        return wrapper
    return decorator
```

**O que faz:**
- Armazena resultados de chamadas anteriores
- Se mesmos argumentos forem passados novamente, retorna do cache
- Cache expira após `tempo_expiracao` segundos

**Uso:**
```python
@cache_resultado(tempo_expiracao=10)
def consultar_api_cara(query):
    print("Fazendo chamada cara à API...")
    time.sleep(2)
    return f"Resultado para: {query}"

# Primeira chamada - chama API
print(consultar_api_cara("Python"))
# Fazendo chamada cara à API...
# Resultado para: Python

# Segunda chamada (mesmos argumentos) - usa cache!
print(consultar_api_cara("Python"))
# Usando cache para consultar_api_cara
# Resultado para: Python
```

---

## Decoradores Empilhados (Stacked Decorators)

Você pode aplicar **múltiplos decoradores** na mesma função:

```python
class AgenteDecorado:
    @log_chamada
    @medir_tempo
    @cache_resultado(tempo_expiracao=60)
    def processar_complexo(self, texto: str) -> str:
        time.sleep(1)
        return f"Processado: {texto}"
```

**Ordem de execução:**
```
@decorador1
@decorador2
@decorador3
def funcao():
    pass

# É equivalente a:
funcao = decorador1(decorador2(decorador3(funcao)))

# Execução:
decorador1 -> ANTES
  decorador2 -> ANTES
    decorador3 -> ANTES
      funcao() executa
    decorador3 -> DEPOIS
  decorador2 -> DEPOIS
decorador1 -> DEPOIS
```

---

## Exemplo Completo

```python
import functools
import time
from typing import Callable
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Decorador 1: Logging
def log_chamada(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"Chamando {func.__name__}")
        inicio = time.time()
        resultado = func(*args, **kwargs)
        duracao = time.time() - inicio
        logger.info(f"{func.__name__} completou em {duracao:.2f}s")
        return resultado
    return wrapper

# Decorador 2: Medição de tempo
def medir_tempo(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        inicio = time.time()
        resultado = func(*args, **kwargs)
        fim = time.time()
        print(f"{func.__name__} levou {fim - inicio:.2f}s")
        return resultado
    return wrapper

# Decorador 3: Validação
def validar_entrada(tipos: dict):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            todos_args = kwargs.copy()
            for i, arg in enumerate(args):
                nome_param = list(func.__annotations__.keys())[i]
                todos_args[nome_param] = arg
            
            for param, tipo_esperado in tipos.items():
                if param in todos_args:
                    valor = todos_args[param]
                    if not isinstance(valor, tipo_esperado):
                        raise TypeError(
                            f"Parâmetro '{param}' deve ser {tipo_esperado.__name__}, "
                            f"recebeu {type(valor).__name__}"
                        )
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Decorador 4: Cache
def cache_resultado(tempo_expiracao: int = 300):
    def decorator(func: Callable) -> Callable:
        cache = {}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            chave = str(args) + str(sorted(kwargs.items()))
            
            if chave in cache:
                resultado, timestamp = cache[chave]
                if time.time() - timestamp < tempo_expiracao:
                    print(f"🔄 Usando cache para {func.__name__}")
                    return resultado
            
            resultado = func(*args, **kwargs)
            cache[chave] = (resultado, time.time())
            return resultado
        return wrapper
    return decorator

# Classe do Agente
class AgenteDecorado:
    def __init__(self, nome: str):
        self.nome = nome
    
    @log_chamada
    @medir_tempo
    def processar(self, texto: str) -> str:
        """Processa texto"""
        time.sleep(0.5)
        return f"Processado: {texto}"
    
    @validar_entrada({"texto": str, "tamanho": int})
    def resumir(self, texto: str, tamanho: int) -> str:
        """Resume texto com validação de tipos"""
        return texto[:tamanho] + "..."
    
    @cache_resultado(tempo_expiracao=10)
    def consultar_conhecimento(self, pergunta: str) -> str:
        """Consulta conhecimento (com cache)"""
        print(f"🤔 Consultando base de conhecimento...")
        time.sleep(1)
        return f"Resposta para: {pergunta}"

# Testes
agente = AgenteDecorado("Assistente")

# Teste 1: Cache
print("\n=== Teste de Cache ===")
print(agente.consultar_conhecimento("O que são agentes?"))
print(agente.consultar_conhecimento("O que são agentes?"))  # Cache!

# Teste 2: Validação
print("\n=== Teste de Validação ===")
try:
    agente.resumir("Texto longo", "10")  # Erro: '10' é string, não int
except TypeError as e:
    print(f"Erro capturado: {e}")

# Teste 3: Processamento
print("\n=== Teste de Processamento ===")
resultado = agente.processar("mensagem importante")
print(resultado)
```

**Saída:**
```
=== Teste de Cache ===
Consultando base de conhecimento...
Resposta para: O que são agentes?
🔄 Usando cache para consultar_conhecimento
Resposta para: O que são agentes?

=== Teste de Validação ===
Erro capturado: Parâmetro 'tamanho' deve ser int, recebeu str

=== Teste de Processamento ===
INFO:__main__:Chamando processar
processar levou 0.50s
INFO:__main__:processar completou em 0.50s
Processado: mensagem importante
```

---

## Decoradores Pré-prontos Úteis

### 1. `@retry` - Retry Automático

```python
import functools
import time

def retry(max_tentativas: int = 3, delay: float = 1.0):
    """Tenta novamente em caso de erro"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for tentativa in range(max_tentativas):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if tentativa == max_tentativas - 1:
                        raise
                    print(f"Tentativa {tentativa + 1} falhou, tentando novamente...")
                    time.sleep(delay)
        return wrapper
    return decorator

@retry(max_tentativas=3, delay=2.0)
def chamar_api_instavel():
    import random
    if random.random() < 0.7:  # 70% de chance de falhar
        raise Exception("API indisponível")
    return "Sucesso!"
```

### 2. `@deprecar` - Avisar sobre funções antigas

```python
import warnings
import functools

def deprecar(mensagem: str):
    """Avisa que função está depreciada"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"{func.__name__} está depreciada. {mensagem}",
                category=DeprecationWarning,
                stacklevel=2
            )
            return func(*args, **kwargs)
        return wrapper
    return decorator

@deprecar("Use consultar_conhecimento_v2() em vez disso")
def consultar_conhecimento_v1(query):
    return "Resultado antigo"
```

---

## Boas Práticas

1. **Sempre use `@functools.wraps`**
   - Preserva metadados da função original

2. **Decoradores devem ser genéricos**
   - Funcionam com qualquer função
   - Use `*args, **kwargs`

3. **Nomeie decoradores de forma descritiva**
   - `@log_chamada`
   - `@d1`

4. **Cuidado com a ordem dos decoradores**
   - A ordem importa!
   - Decoradores de logging geralmente vão por fora

5. **Use type hints**
   - `func: Callable` → Deixa claro que é um decorador

---

## Resumo

**Decoradores:**
- Modificam funções sem alterar código original
- Reutilizáveis em múltiplas funções
- Essenciais para logging, cache, validação
- Tornam código de agentes mais limpo e profissional

**Sintaxe:**
```python
@decorador
def funcao():
    pass
```

**Decoradores úteis para Agentes:**
- `@log_chamada` - Logging
- `@medir_tempo` - Performance
- `@validar_entrada` - Validação
- `@cache_resultado` - Cache
- `@retry` - Resiliência

**Agentes modernos DEVEM usar decoradores!**