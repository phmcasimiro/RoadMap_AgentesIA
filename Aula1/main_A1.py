"""
Engenharia de Agentes
Aula 1 - Lógica de Programação e Python Intermediário/Avançado para Engenharia de Agentes de IA
"""

# ============================================================================
# Importações
# ============================================================================

from typing import List, Dict, Optional, Any
from datetime import datetime
import asyncio
import json
import os
import re
from dataclasses import dataclass, field
from enum import Enum

from dotenv import load_dotenv
import google.generativeai as genai

# Define diretório base do script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Carrega variáveis de ambiente (procura .env na raiz do projeto, um nível acima)
dotenv_path = os.path.join(BASE_DIR, "..", ".env")
load_dotenv(dotenv_path)

# Configura Gemini
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError(
        f"GOOGLE_API_KEY não encontrada no arquivo .env (buscado em: {dotenv_path})"
    )

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# ============================================================================
# MODELOS DE DADOS
# ============================================================================


class Role(Enum):
    """Papéis possíveis em uma conversa"""

    SYSTEM = "system"  # SYSTEM é a mensagem que define o comportamento do agente
    USER = "user"  # USER é a mensagem do usuário
    ASSISTANT = "assistant"  # ASSISTANT é a mensagem do agente
    TOOL = "tool"  # TOOL é a mensagem que define a ferramenta que o agente pode usar


@dataclass  # @dataclass é um decorador que cria uma classe com métodos especiais
class Mensagem:  # Mensagem é uma classe que representa uma mensagem na conversa
    """Representa uma mensagem na conversa"""

    role: Role  # Role é o papel do autor da mensagem
    content: str  # Content é o conteúdo da mensagem
    timestamp: datetime = field(
        default_factory=datetime.now
    )  # Timestamp é a data e hora da mensagem
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )  # Metadata é um dicionário de metadados

    def to_dict(
        self,
    ) -> Dict[
        str, Any
    ]:  # to_dict é um método que converte a mensagem para um dicionário, formato que a API entende
        """Converte para formato da API"""
        return {
            "role": self.role.value,  # Role é o papel do autor da mensagem
            "content": self.content,  # Content é o conteúdo da mensagem
        }


@dataclass  # @dataclass é um decorador que cria uma classe com métodos especiais
class Ferramenta:  # Ferramenta é uma classe que representa uma ferramenta que o agente pode usar
    """Representa uma ferramenta que o agente pode usar"""

    nome: str  # Nome da ferramenta
    descricao: str  # Descrição da ferramenta
    func: callable  # Função que a ferramenta executa

    def __call__(self, **kwargs) -> Any:
        """Executa a ferramenta"""
        print(f"Usando ferramenta: {self.nome}")
        return self.func(**kwargs)


# ========== AGENTE PRINCIPAL ==========


class MeuPrimeiroAgente:  # MeuPrimeiroAgente é uma classe que representa um agente de IA simples
    """Agente de IA simples para aprendizado"""

    def __init__(
        self,
        nome: str,  # Nome do agente
        modelo: str = "gemini-2.0-flash",  # Modelo de IA a ser usado
        temperatura: float = 0.5,
    ):
        self.nome = nome  # Nome do agente
        self.modelo = modelo  # Modelo de IA a ser usado
        self.client = genai.GenerativeModel(modelo)  # Cliente Gemini
        self.temperatura = self._validar_temperatura(
            temperatura
        )  # Temperatura do agente
        self._historico: List[Mensagem] = []  # Histórico de mensagens
        self._ferramentas: Dict[str, Ferramenta] = {}  # Ferramentas do agente
        self._limite_contexto = 4096  # Limite de contexto do agente

        # Mensagem de sistema padrão
        self.adicionar_mensagem(
            Role.SYSTEM,  # Role.SYSTEM é o papel do autor da mensagem
            f"Você é {nome}, um assistente de IA útil e amigável.",
        )

    def _validar_temperatura(self, valor: float) -> float:
        """Valida temperatura entre 0 e 1"""
        if not 0 <= valor <= 1:
            raise ValueError("Temperatura deve estar entre 0 e 1")
        return valor

    @property  # @property é um decorador que permite que um método seja acessado como um atributo
    def historico(self) -> List[Mensagem]:
        """Retorna cópia do histórico"""
        return self._historico.copy()

    @property  # @property é um decorador que permite que um método seja acessado como um atributo
    def tokens_estimados(self) -> int:
        """Estima tokens usados"""
        return sum(len(msg.content.split()) for msg in self._historico)

    def adicionar_mensagem(self, role: Role, content: str):
        """Adiciona mensagem ao histórico"""
        msg = Mensagem(role, content)
        self._historico.append(msg)

        # Log simples
        print(f"[{role.value.upper()}] {content[:50]}...")

    def registrar_ferramenta(self, ferramenta: Ferramenta):
        """Registra uma ferramenta para o agente usar"""
        self._ferramentas[ferramenta.nome] = ferramenta
        print(f"Ferramenta registrada: {ferramenta.nome}")

    async def processar_mensagem(
        self, mensagem: str, usar_ferramentas: bool = True
    ) -> str:
        """
        Processa mensagem do usuário usando Google Gemini
        """
        # Adiciona mensagem do usuário
        self.adicionar_mensagem(Role.USER, mensagem)
        print(f"{self.nome} está pensando...")

        contexto_ferramenta = ""

        # Lógica Simples de Ferramentas (ReAct simplificado)
        if usar_ferramentas:
            if "calcular" in mensagem.lower():
                if "calcular" in self._ferramentas:
                    try:
                        resultado = self._ferramentas["calcular"](expressao=mensagem)
                        contexto_ferramenta = f"\n[SISTEMA] O usuário pediu um cálculo. Resultado da ferramenta: {resultado}. Use isso para responder."
                    except Exception as e:
                        contexto_ferramenta = f"\n[SISTEMA] Erro ao calcular: {str(e)}"

            elif "pesquisar" in mensagem.lower():
                if "buscar" in self._ferramentas:
                    termos = mensagem.replace("pesquisar", "").strip()
                    resultado = self._ferramentas["buscar"](termo=termos)
                    contexto_ferramenta = f"\n[SISTEMA] Resultado da busca: {resultado}. Use isso para responder."

        # Constrói o histórico para o prompt
        prompt_completo = ""
        for msg in self._historico:
            prompt_completo += f"{msg.role.value}: {msg.content}\n"

        prompt_completo += contexto_ferramenta
        prompt_completo += "\nassistant:"

        try:
            # Gera resposta com Gemini
            response = await self.client.generate_content_async(prompt_completo)
            resposta_texto = response.text
        except Exception as e:
            resposta_texto = f"Erro ao contatar a IA: {str(e)}"

        # Adiciona resposta ao histórico
        self.adicionar_mensagem(Role.ASSISTANT, resposta_texto)

        return resposta_texto

    def salvar_conversa(self, arquivo: str):
        """Salva histórico em arquivo"""
        dados = [
            {
                "role": msg.role.value,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
            }
            for msg in self._historico
        ]

        with open(arquivo, "w") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
        print(f"Conversa salva em {arquivo}")

    def carregar_conversa(self, arquivo: str):
        """Carrega histórico de arquivo"""
        with open(arquivo, "r") as f:
            dados = json.load(f)

        self._historico = []
        for item in dados:
            msg = Mensagem(
                role=Role(item["role"]),
                content=item["content"],
                timestamp=datetime.fromisoformat(item["timestamp"]),
            )
            self._historico.append(msg)

        print(f"Conversa carregada: {len(self._historico)} mensagens")

    def __str__(self) -> str:
        return (
            f"Agente '{self.nome}' | Modelo: {self.modelo} | Temp: {self.temperatura}"
        )

    def __len__(self) -> int:
        return len(self._historico)


# ========== FERRAMENTAS DE EXEMPLO ==========


def ferramenta_calcular(expressao: str) -> float:
    """Calcula expressão matemática simples de forma segura"""
    try:
        # Tenta encontrar uma expressão matemática válida na string
        # Padrão: números seguidos de operadores/números/espaços
        match = re.search(r"([\d\.\s\(\)]*[\+\-\*\/][\d\.\s\(\)\+\-\*\/]*)", expressao)

        if not match:
            # Tenta apenas um número se não houver operadores (ex: "calcular 10")
            match_num = re.search(r"(\d+)", expressao)
            if match_num:
                return float(match_num.group(1))
            return "Erro: Nenhuma expressão matemática encontrada."

        expressao_encontrada = match.group(1).strip()

        # Avalia a expressão encontrada
        resultado = eval(expressao_encontrada)
        return resultado
    except Exception:
        return "Erro no cálculo"


def ferramenta_buscar(termo: str) -> str:
    """Simula busca na web"""
    return f"Resultados da busca por '{termo}'"


# ========== EXEMPLO DE USO ==========


async def main():
    print("=" * 50)
    print("Iniciando Meu Primeiro Agente")
    print("=" * 50)

    # Cria agente
    agente = MeuPrimeiroAgente(
        nome="Assistente de IA N1", modelo="gemini-2.0-flash", temperatura=0.5
    )
    print(agente)

    # Registra ferramentas
    agente.registrar_ferramenta(
        Ferramenta("calcular", "Calcula expressões matemáticas", ferramenta_calcular)
    )
    agente.registrar_ferramenta(
        Ferramenta("buscar", "Busca informações na web", ferramenta_buscar)
    )

    # Conversa
    resposta = await agente.processar_mensagem("Olá, tudo bem?")
    print(f"Resposta: {resposta}")

    resposta = await agente.processar_mensagem("Calcule 10+2+5?")
    print(f"Resposta: {resposta}")

    # Estatísticas
    print(f"\nEstatísticas:")
    print(f"- Total mensagens: {len(agente)}")
    print(f"- Tokens estimados: {agente.tokens_estimados}")

    # Salva conversa
    # Salva conversa no diretório da aula
    json_path = os.path.join(BASE_DIR, "minha_conversa.json")
    agente.salvar_conversa(json_path)

    print("=" * 50)


# Executar
if __name__ == "__main__":
    asyncio.run(main())
