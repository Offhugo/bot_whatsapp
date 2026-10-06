import math

from sqlalchemy.orm import Session

from app.repositories.registro_repository import RegistroRepository
from app.schemas.ai_response import AIResponseDTO
from app.utils.validation_limits import (
    MAX_LITROS_ABASTECIMENTO,
    MAX_VALOR_ABASTECIMENTO,
)


class RegistrarAbastecimentoUseCase:

    def __init__(self, registro_repository: RegistroRepository):
        self.registro_repository = registro_repository

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

        if (
            isinstance(valor, bool)
            or not isinstance(valor, (int, float))
        ):
            return {
                "sucesso": False,
                "mensagem": "O valor do abastecimento informado é inválido."
            }

        if (
            isinstance(valor, float)
            and not math.isfinite(valor)
        ):
            return {
                "sucesso": False,
                "mensagem": "O valor do abastecimento informado é inválido."
            }

        if valor <= 0:
            return {
                "sucesso": False,
                "mensagem": "O valor do abastecimento deve ser maior que zero."
            }

        if valor > MAX_VALOR_ABASTECIMENTO:
            return {
                "sucesso": False,
                "mensagem": "O valor do abastecimento informado excede o limite permitido."
            }

        litros = dados.get("litros")

        if litros is not None:

            if (
                isinstance(litros, bool)
                or not isinstance(litros, (int, float))
            ):
                return {
                    "sucesso": False,
                    "mensagem": "A quantidade de litros informada é inválida."
                }

            if (
                isinstance(litros, float)
                and not math.isfinite(litros)
            ):
                return {
                    "sucesso": False,
                    "mensagem": "A quantidade de litros informada é inválida."
                }

            if litros <= 0:
                return {
                    "sucesso": False,
                    "mensagem": "A quantidade de litros deve ser maior que zero."
                }

            if litros > MAX_LITROS_ABASTECIMENTO:
                return {
                    "sucesso": False,
                    "mensagem": "A quantidade de litros informada excede o limite permitido."
                }

        registro = {
            "valor": valor
        }

        if litros is not None:
            registro["litros"] = litros

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