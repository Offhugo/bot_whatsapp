from sqlalchemy.orm import Session

from app.repositories.registro_repository import RegistroRepository
from app.schemas.ai_response import AIResponseDTO


class RegistrarViagemUseCase:

    # Carrega a classe
    def __init__(self, registro_repository: RegistroRepository):
        self.registro_repository = registro_repository

    # assinaturas do metodo de execução
    def executar(
        self,
        resposta: AIResponseDTO,
        usuario_id: int,
        db: Session
    ):
        dados = resposta.dados     # Extração de dados importantes

        origem = dados.get("origem")
        destino = dados.get("destino")

        # Pequena validação(No caso dos testes de ausencia de valor, é aqui esse trecho que testamos se está funcionando de maneira correta)
        if origem is None or destino is None:
            return {
                "sucesso": False,
                "mensagem": "Preciso saber a origem e o destino da viagem."
            }

        # caso passe, salvamos as datas
        registro = {
            "origem": origem,
            "destino": destino
        }

        # Adicionamos somente os dados que a IA conseguiu identificar.
        campos_opcionais = [
            "quilometros",
            "valor_frete",
            "carga",
            "data_inicio",
            "data_fim",
            "gastos"
        ]

        # Loop para inserir N dados opcionais no registro
        for campo in campos_opcionais:
            if campo in dados:
                registro[campo] = dados[campo]

        # Efetivamente salva o registro no banco
        self.registro_repository.salvar(
            usuario_id=usuario_id,
            tipo="viagem",
            dados=registro,
            db=db
        )

        # Resposta de sucesso caso tudo de certo
        return {
            "sucesso": True,
            "mensagem": resposta.resposta
        }