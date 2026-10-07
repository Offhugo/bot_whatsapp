from datetime import timedelta

from sqlalchemy.orm import Session

from app.repositories.registro_repository import RegistroRepository
from app.schemas.ai_response import AIResponseDTO
from app.utils.date_validation import converter_para_datetime
from app.utils.validation_limits import MAX_PERIODO_CONSULTA_DIAS


class ConsultarKMUseCase:

    def __init__(self, registro_repository: RegistroRepository):
        self.registro_repository = registro_repository

    def executar(
        self,
        resposta: AIResponseDTO,
        usuario_id: int,
        db: Session
    ):
        dados = resposta.dados

        data_inicio = dados.get("data_inicio")
        data_fim = dados.get("data_fim")

        if data_inicio is None or data_fim is None:
            return {
                "sucesso": False,
                "mensagem": "Preciso saber qual período você deseja consultar."
            }

        data_inicio = converter_para_datetime(data_inicio)
        data_fim = converter_para_datetime(data_fim)

        if data_inicio is None or data_fim is None:
            return {
                "sucesso": False,
                "mensagem": "O período informado é inválido."
            }

        if data_inicio > data_fim:
            return {
                "sucesso": False,
                "mensagem": "A data de início não pode ser posterior à data de fim."
            }

        if data_fim - data_inicio > timedelta(
            days=MAX_PERIODO_CONSULTA_DIAS
        ):
            return {
                "sucesso": False,
                "mensagem": "O período consultado excede o limite permitido."
            }

        registros = self.registro_repository.buscar_por_tipo_e_periodo(
            usuario_id=usuario_id,
            tipo="km",
            data_inicio=data_inicio,
            data_fim=data_fim,
            db=db
        )

        total_km = sum(
            registro.dados.get("quilometros", 0)
            for registro in registros
        )

        return {
            "sucesso": True,
            "total_km": total_km
        }