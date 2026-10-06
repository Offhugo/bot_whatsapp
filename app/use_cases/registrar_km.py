import math

from sqlalchemy.orm import Session

from app.repositories.registro_repository import RegistroRepository
from app.schemas.ai_response import AIResponseDTO
from app.utils.validation_limits import MAX_QUILOMETROS_POR_REGISTRO


class RegistrarKMUseCase:

    def __init__(self, registro_repository: RegistroRepository):
        self.registro_repository = registro_repository

    def executar(
        self,
        resposta: AIResponseDTO,
        usuario_id: int,
        db: Session
    ):
        dados = resposta.dados

        quilometros = dados.get("quilometros")

        if quilometros is None:
            return {
                "sucesso": False,
                "mensagem": "Quantos quilômetros foram percorridos?"
            }

        if (
            isinstance(quilometros, bool)
            or not isinstance(quilometros, (int, float))
        ):
            return {
                "sucesso": False,
                "mensagem": "O valor dos quilômetros informado é inválido."
            }

        # Inteiros não podem ser NaN ou infinito.
        # Para floats, fazemos a verificação explicitamente.
        if (
            isinstance(quilometros, float)
            and not math.isfinite(quilometros)
        ):
            return {
                "sucesso": False,
                "mensagem": "O valor dos quilômetros informado é inválido."
            }

        if quilometros <= 0:
            return {
                "sucesso": False,
                "mensagem": "O valor dos quilômetros deve ser maior que zero."
            }

        if quilometros > MAX_QUILOMETROS_POR_REGISTRO:
            return {
                "sucesso": False,
                "mensagem": "O valor dos quilômetros informado excede o limite permitido."
            }

        registro = {
            "quilometros": quilometros
        }

        self.registro_repository.salvar(
            usuario_id=usuario_id,
            tipo="km",
            dados=registro,
            db=db
        )

        return {
            "sucesso": True,
            "mensagem": resposta.resposta
        }