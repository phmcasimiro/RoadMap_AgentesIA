# Context Managers para Agentes de IA: Gerenciando Recursos

## O que são Context Managers?

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

```python
# ❌ PERIGOSO!
arquivo = open("conversa.json", "w")
arquivo.write(dados)
# E se der erro aqui? ↓
processar_algo_que_pode_falhar()
arquivo.close()  # ← Nunca executa se houver erro!
```

```python
# ✅ SEGURO!
with open("conversa.json", "w") as arquivo:
    arquivo.write(dados)
    processar_algo_que_pode_falhar()
# arquivo.close() é SEMPRE chamado, mesmo com erro!
```
