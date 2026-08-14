from datetime import datetime

from sqlalchemy.orm import Session

from app.repositories.registro_repository import RegistroRepository
from app.schemas.ai_response import AIResponseDTO


class ConsultarViagensUseCase:


    def __init__(self, registro_repository: RegistroRepository):
        self.registro_repository = registro_repository

    def executar(
        self,
        resposta: AIResponseDTO,
        usuario_id: int,
        db: Session
    ):
        # guarda as informações importantes vindas da IA
        dados = resposta.dados

        # guarda as datas de inicio e fim registradas pela IA
        data_inicio = dados.get("data_inicio")
        data_fim = dados.get("data_fim")

        # validação caso haja falta de datas
        if data_inicio is None or data_fim is None:
            return {
                "sucesso": False,
                "mensagem": "Preciso saber qual período você deseja consultar."
            }

        # caso as datas estejam corretas, é feita a busca dentro do periodo determinado
        registros = self.registro_repository.buscar_por_tipo_e_periodo(
            usuario_id=usuario_id,
            tipo="viagem",
            data_inicio=data_inicio,
            data_fim=data_fim,
            db=db
        )

        return {
            "sucesso": True,
            "viagens": registros
        }