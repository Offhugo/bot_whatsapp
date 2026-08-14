from datetime import datetime

from sqlalchemy.orm import Session

from app.repositories.registro_repository import RegistroRepository
from app.schemas.ai_response import AIResponseDTO


class ConsultarKMUseCase:

    # Inicialização da classe
    def __init__(self, registro_repository: RegistroRepository):
        self.registro_repository = registro_repository

    # Assinaturas do método
    def executar(
        self,
        resposta: AIResponseDTO,
        usuario_id: int,
        db: Session
    ):
        dados = resposta.dados

        data_inicio = dados.get("data_inicio")
        data_fim = dados.get("data_fim")

        # Validação caso haja falta de data
        if data_inicio is None or data_fim is None:
            return {
                "sucesso": False,
                "mensagem": "Preciso saber qual período você deseja consultar."
            }

        # Caso hajam datas válidas, chama o metodo para buscar os registros
        registros = self.registro_repository.buscar_por_tipo_e_periodo(
            usuario_id=usuario_id,
            tipo="km",
            data_inicio=data_inicio,
            data_fim=data_fim,
            db=db
        )

        # Parte responsavel por contabilizar o toal de kms
        total_km = sum(
            registro.dados.get("quilometros", 0)
            for registro in registros
        )

        return {
            "sucesso": True,
            "total_km": total_km
        }