import math
from datetime import datetime

from sqlalchemy.orm import Session

from app.repositories.registro_repository import RegistroRepository
from app.schemas.ai_response import AIResponseDTO
from app.utils.date_validation import converter_para_datetime
from app.utils.validation_limits import (
    MAX_GASTOS_VIAGEM,
    MAX_ORIGEM_DESTINO_LENGTH,
    MAX_QUILOMETROS_POR_REGISTRO,
    MAX_VALOR_FRETE,
)


class RegistrarViagemUseCase:

    def __init__(self, registro_repository: RegistroRepository):
        self.registro_repository = registro_repository

    def executar(
        self,
        resposta: AIResponseDTO,
        usuario_id: int,
        db: Session
    ):
        dados = resposta.dados

        origem = dados.get("origem")
        destino = dados.get("destino")

        if origem is None or destino is None:
            return {
                "sucesso": False,
                "mensagem": "Preciso saber a origem e o destino da viagem."
            }

        for nome, valor in (
            ("origem", origem),
            ("destino", destino)
        ):
            if not isinstance(valor, str):
                return {
                    "sucesso": False,
                    "mensagem": f"O campo {nome} informado é inválido."
                }

            if not valor.strip():
                return {
                    "sucesso": False,
                    "mensagem": f"O campo {nome} não pode estar vazio."
                }

            if len(valor) > MAX_ORIGEM_DESTINO_LENGTH:
                return {
                    "sucesso": False,
                    "mensagem": f"O campo {nome} excede o limite permitido."
                }

        quilometros = dados.get("quilometros")

        if quilometros is not None:

            if (
                isinstance(quilometros, bool)
                or not isinstance(quilometros, (int, float))
            ):
                return {
                    "sucesso": False,
                    "mensagem": "O valor dos quilômetros informado é inválido."
                }

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

        valor_frete = dados.get("valor_frete")

        if valor_frete is not None:

            if (
                isinstance(valor_frete, bool)
                or not isinstance(valor_frete, (int, float))
            ):
                return {
                    "sucesso": False,
                    "mensagem": "O valor do frete informado é inválido."
                }

            if (
                isinstance(valor_frete, float)
                and not math.isfinite(valor_frete)
            ):
                return {
                    "sucesso": False,
                    "mensagem": "O valor do frete informado é inválido."
                }

            if valor_frete < 0:
                return {
                    "sucesso": False,
                    "mensagem": "O valor do frete não pode ser negativo."
                }

            if valor_frete > MAX_VALOR_FRETE:
                return {
                    "sucesso": False,
                    "mensagem": "O valor do frete informado excede o limite permitido."
                }

        gastos = dados.get("gastos")

        if gastos is not None and isinstance(gastos, (int, float)):

            if isinstance(gastos, bool):
                return {
                    "sucesso": False,
                    "mensagem": "O valor dos gastos informado é inválido."
                }

            if isinstance(gastos, float) and not math.isfinite(gastos):
                return {
                    "sucesso": False,
                    "mensagem": "O valor dos gastos informado é inválido."
                }

            if gastos < 0:
                return {
                    "sucesso": False,
                    "mensagem": "O valor dos gastos não pode ser negativo."
                }

            if gastos > MAX_GASTOS_VIAGEM:
                return {
                    "sucesso": False,
                    "mensagem": "O valor dos gastos informado excede o limite permitido."
                }

        for nome in ("data_inicio", "data_fim"):

            if nome not in dados:
                continue

            data = converter_para_datetime(dados[nome])

            if data is None:
                return {
                    "sucesso": False,
                    "mensagem": f"A data {nome} informada é inválida."
                }

        data_inicio = dados.get("data_inicio")
        data_fim = dados.get("data_fim")

        if data_inicio is not None and data_fim is not None:

            inicio = converter_para_datetime(data_inicio)
            fim = converter_para_datetime(data_fim)

            if inicio is None or fim is None:
                return {
                    "sucesso": False,
                    "mensagem": "O período informado é inválido."
                }

            if inicio > fim:
                return {
                    "sucesso": False,
                    "mensagem": "A data de início não pode ser posterior à data de fim."
                }

        registro = {
            "origem": origem,
            "destino": destino
        }

        campos_opcionais = [
            "quilometros",
            "valor_frete",
            "carga",
            "data_inicio",
            "data_fim",
            "gastos"
        ]

        for campo in campos_opcionais:
            if campo in dados:
                registro[campo] = dados[campo]

        self.registro_repository.salvar(
            usuario_id=usuario_id,
            tipo="viagem",
            dados=registro,
            db=db
        )

        return {
            "sucesso": True,
            "mensagem": resposta.resposta
        }