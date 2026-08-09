from sqlalchemy.orm import Session

from app.repositories.registro_repository import RegistroRepository
from app.schemas.ai_response import AIResponseDTO


class RegistrarKMUseCase:

    def __init__(self):
        self.registro_repository = RegistroRepository()

    # Recebe dados da IA, no caso um JSON com a intent interpretada pela IA
    def executar(
        self,
        resposta: AIResponseDTO,
        usuario_id: int,
        db: Session
    ):

        # Pega puramente o dado a ser trabalhado, sabendo já quem é esse dado por causa da própria classe
        dados = resposta.dados

        quilometros = dados.get("quilometros")

        # Verificação do dado e aplicação de uma regra simples
        if quilometros is None:
            return {
                "sucesso": False,
                "mensagem": "Quantos quilômetros foram percorridos?"
            }

        # Dado devidamente registrado
        registro = {
            "quilometros": quilometros
        }

        # Informações sendo salvas corretamente
        self.registro_repository.salvar(
            usuario_id=usuario_id,
            tipo="km",
            dados=registro,
            db=db
        )

        # Retorno informativo
        return {
            "sucesso": True,
            "mensagem": resposta.resposta
        }