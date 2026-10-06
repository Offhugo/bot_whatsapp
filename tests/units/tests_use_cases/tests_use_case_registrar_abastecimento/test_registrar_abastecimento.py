from unittest.mock import MagicMock

from app.schemas.ai_response import AIResponseDTO
from app.use_cases.registrar_abastecimento import (
    RegistrarAbastecimentoUseCase
)
from app.utils.validation_limits import (
    MAX_LITROS_ABASTECIMENTO,
    MAX_VALOR_ABASTECIMENTO,
)


def criar_resposta(valor, litros=None):
    dados = {
        "valor": valor
    }

    if litros is not None:
        dados["litros"] = litros

    return AIResponseDTO(
        intent="registrar_abastecimento",
        dados=dados,
        resposta="Abastecimento registrado."
    )


def criar_use_case():
    repository = MagicMock()
    use_case = RegistrarAbastecimentoUseCase(repository)

    return use_case, repository


def test_registrar_abastecimento_com_valor_valido():
    use_case, repository = criar_use_case()

    resposta = criar_resposta(350.50)

    resultado = use_case.executar(
        resposta,
        usuario_id=1,
        db=MagicMock()
    )

    assert resultado["sucesso"] is True
    repository.salvar.assert_called_once()


def test_registrar_abastecimento_rejeita_valor_ausente():
    use_case, repository = criar_use_case()

    resposta = AIResponseDTO(
        intent="registrar_abastecimento",
        dados={},
        resposta="Informe o valor."
    )

    resultado = use_case.executar(
        resposta,
        usuario_id=1,
        db=MagicMock()
    )

    assert resultado["sucesso"] is False
    assert resultado["mensagem"] == (
        "Qual foi o valor do abastecimento?"
    )
    repository.salvar.assert_not_called()


def test_registrar_abastecimento_rejeita_string():
    use_case, repository = criar_use_case()

    resposta = criar_resposta("300")

    resultado = use_case.executar(
        resposta,
        usuario_id=1,
        db=MagicMock()
    )

    assert resultado["sucesso"] is False
    repository.salvar.assert_not_called()


def test_registrar_abastecimento_rejeita_zero():
    use_case, repository = criar_use_case()

    resposta = criar_resposta(0)

    resultado = use_case.executar(
        resposta,
        usuario_id=1,
        db=MagicMock()
    )

    assert resultado["sucesso"] is False
    repository.salvar.assert_not_called()


def test_registrar_abastecimento_rejeita_valor_negativo():
    use_case, repository = criar_use_case()

    resposta = criar_resposta(-100)

    resultado = use_case.executar(
        resposta,
        usuario_id=1,
        db=MagicMock()
    )

    assert resultado["sucesso"] is False
    repository.salvar.assert_not_called()


def test_registrar_abastecimento_rejeita_booleano():
    use_case, repository = criar_use_case()

    resposta = criar_resposta(True)

    resultado = use_case.executar(
        resposta,
        usuario_id=1,
        db=MagicMock()
    )

    assert resultado["sucesso"] is False
    repository.salvar.assert_not_called()


def test_registrar_abastecimento_rejeita_nan():
    use_case, repository = criar_use_case()

    resposta = criar_resposta(float("nan"))

    resultado = use_case.executar(
        resposta,
        usuario_id=1,
        db=MagicMock()
    )

    assert resultado["sucesso"] is False
    repository.salvar.assert_not_called()


def test_registrar_abastecimento_rejeita_infinito():
    use_case, repository = criar_use_case()

    resposta = criar_resposta(float("inf"))

    resultado = use_case.executar(
        resposta,
        usuario_id=1,
        db=MagicMock()
    )

    assert resultado["sucesso"] is False
    repository.salvar.assert_not_called()


def test_registrar_abastecimento_rejeita_valor_acima_do_limite():
    use_case, repository = criar_use_case()

    resposta = criar_resposta(
        MAX_VALOR_ABASTECIMENTO + 1
    )

    resultado = use_case.executar(
        resposta,
        usuario_id=1,
        db=MagicMock()
    )

    assert resultado["sucesso"] is False
    repository.salvar.assert_not_called()


def test_registrar_abastecimento_aceita_litros_validos():
    use_case, repository = criar_use_case()

    resposta = criar_resposta(
        350.50,
        litros=300
    )

    resultado = use_case.executar(
        resposta,
        usuario_id=1,
        db=MagicMock()
    )

    assert resultado["sucesso"] is True
    repository.salvar.assert_called_once()


def test_registrar_abastecimento_rejeita_litros_string():
    use_case, repository = criar_use_case()

    resposta = criar_resposta(
        350.50,
        litros="300"
    )

    resultado = use_case.executar(
        resposta,
        usuario_id=1,
        db=MagicMock()
    )

    assert resultado["sucesso"] is False
    repository.salvar.assert_not_called()


def test_registrar_abastecimento_rejeita_litros_booleano():
    use_case, repository = criar_use_case()

    resposta = criar_resposta(
        350.50,
        litros=True
    )

    resultado = use_case.executar(
        resposta,
        usuario_id=1,
        db=MagicMock()
    )

    assert resultado["sucesso"] is False
    repository.salvar.assert_not_called()


def test_registrar_abastecimento_rejeita_litros_zero():
    use_case, repository = criar_use_case()

    resposta = criar_resposta(
        350.50,
        litros=0
    )

    resultado = use_case.executar(
        resposta,
        usuario_id=1,
        db=MagicMock()
    )

    assert resultado["sucesso"] is False
    repository.salvar.assert_not_called()


def test_registrar_abastecimento_rejeita_litros_negativo():
    use_case, repository = criar_use_case()

    resposta = criar_resposta(
        350.50,
        litros=-20
    )

    resultado = use_case.executar(
        resposta,
        usuario_id=1,
        db=MagicMock()
    )

    assert resultado["sucesso"] is False
    repository.salvar.assert_not_called()


def test_registrar_abastecimento_rejeita_litros_nan():
    use_case, repository = criar_use_case()

    resposta = criar_resposta(
        350.50,
        litros=float("nan")
    )

    resultado = use_case.executar(
        resposta,
        usuario_id=1,
        db=MagicMock()
    )

    assert resultado["sucesso"] is False
    repository.salvar.assert_not_called()


def test_registrar_abastecimento_rejeita_litros_infinito():
    use_case, repository = criar_use_case()

    resposta = criar_resposta(
        350.50,
        litros=float("inf")
    )

    resultado = use_case.executar(
        resposta,
        usuario_id=1,
        db=MagicMock()
    )

    assert resultado["sucesso"] is False
    repository.salvar.assert_not_called()


def test_registrar_abastecimento_rejeita_litros_acima_do_limite():
    use_case, repository = criar_use_case()

    resposta = criar_resposta(
        350.50,
        litros=MAX_LITROS_ABASTECIMENTO + 1
    )

    resultado = use_case.executar(
        resposta,
        usuario_id=1,
        db=MagicMock()
    )

    assert resultado["sucesso"] is False
    repository.salvar.assert_not_called()