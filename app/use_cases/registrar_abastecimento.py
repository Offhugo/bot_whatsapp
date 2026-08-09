from sqlalchemy.orm import Session

from app.repositories.registro_repository import RegistroRepository
from app.schemas.ai_response import AIResponseDTO


class RegistrarAbastecimentoUseCase:

    def __init__(self):
        self.registro_repository = RegistroRepository()

    def executar(
        self,
        resposta: AIResponseDTO,
        usuario_id: int,
        db: Session
    ):

        dados = resposta.dados

        valor = dados.get("valor")

        if valor is None:
            return {
                "sucesso": False,
                "mensagem": "Qual foi o valor do abastecimento?"
            }

        registro = {
            "valor": valor
        }

        if "litros" in dados:
            registro["litros"] = dados["litros"]

        if "caminhao" in dados:
            registro["caminhao"] = dados["caminhao"]

        self.registro_repository.salvar(
            usuario_id=usuario_id,
            tipo="abastecimento",
            dados=registro,
            db=db
        )

        return {
            "sucesso": True,
            "mensagem": resposta.resposta
        }