# Type Hints e Documentação para Agentes de IA

### Por que isso é CRÍTICO para Agentes de IA?

- Entender o que está sendo feito por outro programador é um problema comum em scritps
- O uso de Documentação, Type Hints e Validações são a maneira mais recomendada de resolver esse tipo de problema

- No código abaixo, 
  - O que é msg? String? Dicionário? Objeto?
  - O que é hist? Lista? Dict? Lista de quê?
  - O que é temp? Float? Int? String?

- Em agentes de IA, isso é um PESADELO porque:
  - Agentes se comunicam com LLMs (OpenAI, Anthropic) que exigem formatos específicos
  - Agentes usam múltiplos tipos de dados, isto é, Mensagens, ferramentas, contextos, embeddings...
  - Não documentar e não usar Type Hints torna o Debugg mais difícil, por exemplo, quando algo errado acontece é necessário saber exatamente o que cada função espera
  - Documentar e usar Type Hynts ajuda no trabalho em equipe, ou seja, outros desenvolvedores ou Gemini e Claude precisam entender seu código
  - A IDE vai ajudar MUITO mais com type hints

```python
# Código sem type hints
def processar(msg, hist, temp):
    pass
```

#### Criação de um Agente de IA com boas práticas (Type Hints, Validação e Documentação)

```python
from typing import List, Optional
from datetime import datetime


class Agente:
    """
    Representa um agente de IA com suas configurações e ferramentas.
    
    Attributes:
        nome: Nome identificador do agente
        ferramentas: Lista de ferramentas disponíveis para o agente
        modelo: Nome do modelo de IA (ex: "gpt-4", "claude-3")
        temperatura: Controla aleatoriedade das respostas (0.0 = determinístico, 1.0 = criativo)
    """
    
    def __init__(self,
                 nome: str,
                 ferramentas: List[str],
                 modelo: str = "gpt-4",
                 temperatura: float = 0.7):
        """
        Inicializa um agente de IA.
        
        Args:
            nome: Nome do agente (ex: "Assistente de Vendas")
            ferramentas: Lista de ferramentas disponíveis (ex: ["search", "calculator"])
            modelo: Modelo de IA a ser usado (padrão: "gpt-4")
            temperatura: Float entre 0 e 1 (padrão: 0.7)
        
        Raises:
            ValueError: Se temperatura não estiver entre 0 e 1
        """
        # Validação da temperatura
        if not 0.0 <= temperatura <= 1.0:
            raise ValueError(f"Temperatura deve estar entre 0 e 1. Recebido: {temperatura}")
        
        self.nome: str = nome
        self.ferramentas: List[str] = ferramentas
        self.modelo: str = modelo
        self.temperatura: float = temperatura
        self.criado_em: datetime = datetime.now()
    
    def __repr__(self) -> str:
        """Representação string do agente para debugging."""
        return (f"Agente(nome='{self.nome}', modelo='{self.modelo}', "
                f"temperatura={self.temperatura}, ferramentas={len(self.ferramentas)})")
    
    def adicionar_ferramenta(self, ferramenta: str) -> None:
        """
        Adiciona uma nova ferramenta ao agente.
        
        Args:
            ferramenta: Nome da ferramenta a adicionar
        """
        if ferramenta not in self.ferramentas:
            self.ferramentas.append(ferramenta)
    
    def remover_ferramenta(self, ferramenta: str) -> bool:
        """
        Remove uma ferramenta do agente.
        
        Args:
            ferramenta: Nome da ferramenta a remover
        
        Returns:
            True se removeu com sucesso, False se ferramenta não existe
        """
        if ferramenta in self.ferramentas:
            self.ferramentas.remove(ferramenta)
            return True
        return False
    
    def tem_ferramenta(self, ferramenta: str) -> bool:
        """
        Verifica se o agente possui uma ferramenta específica.
        
        Args:
            ferramenta: Nome da ferramenta a verificar
        
        Returns:
            True se possui a ferramenta, False caso contrário
        """
        return ferramenta in self.ferramentas
    
    def to_dict(self) -> dict:
        """
        Converte o agente para dicionário (útil para APIs e serialização).
        
        Returns:
            Dicionário com todas as informações do agente
        """
        return {
            "nome": self.nome,
            "ferramentas": self.ferramentas,
            "modelo": self.modelo,
            "temperatura": self.temperatura,
            "criado_em": self.criado_em.isoformat()
        }


# EXEMPLOS DE USO

# Criando agentes
agente1 = Agente(
    nome="Assistente de Vendas",
    ferramentas=["search_web", "send_email", "consultar_estoque"],
    modelo="gpt-4",
    temperatura=0.7
)

agente2 = Agente(
    nome="Analista de Dados",
    ferramentas=["executar_sql", "gerar_grafico", "exportar_excel"],
    modelo="gpt-4-turbo",
    temperatura=0.3  # Mais determinístico para análises
)

agente3 = Agente(
    nome="Assistente Criativo",
    ferramentas=["gerar_imagem", "editar_texto"],
    modelo="claude-3-opus",
    temperatura=0.9  # Mais criativo
)

# Testando
print(agente1)
# Agente(nome='Assistente de Vendas', modelo='gpt-4', temperatura=0.7, ferramentas=3)

print(f"\nAgente 1 tem a ferramenta 'search_web'? {agente1.tem_ferramenta('search_web')}")
# True

# Adicionando ferramenta
agente1.adicionar_ferramenta("calcular_desconto")
print(f"Ferramentas do Agente 1: {agente1.ferramentas}")
# ['search_web', 'send_email', 'consultar_estoque', 'calcular_desconto']

# Convertendo para dicionário
print(f"\nAgente 2 como dict:")
print(agente2.to_dict())

# Testando validação (vai dar erro!)
try:
    agente_invalido = Agente(
        nome="Agente Inválido",
        ferramentas=["tool1"],
        temperatura=1.5  # Maior que 1!
    )
except ValueError as e:
    print(f"\nErro capturado: {e}")
    # Temperatura deve estar entre 0 e 1. Recebido: 1.5
```

#### Criação de um Agente de IA com validação usando Pydantic, Documentação e Type Hints

```python
from pydantic import BaseModel, Field, validator
from typing import List

class AgenteAvancado(BaseModel):
    """Agente com validação automática usando Pydantic"""
    
    nome: str = Field(..., min_length=1, description="Nome do agente")
    ferramentas: List[str] = Field(default_factory=list)
    modelo: str = Field(default="gpt-4", description="Modelo de IA")
    temperatura: float = Field(default=0.7, ge=0.0, le=1.0, description="Temperatura (0-1)")
    
    @validator('temperatura')
    def validar_temperatura(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Temperatura deve estar entre 0 e 1')
        return v

# Uso
agente = AgenteAvancado(
    nome="Meu Agente",
    ferramentas=["search"],
    temperatura=0.5
)
```