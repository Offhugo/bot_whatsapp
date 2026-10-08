import pytest

from app.schemas.ai_response import Intent
from app.utils.ai_data_validation import validar_dados_da_ia


def test_aceita_campo_permitido():
    dados = {
        "quilometros": 430
    }

    resultado = validar_dados_da_ia(
        Intent.REGISTRAR_KM,
        dados,
    )

    assert resultado == dados


def test_rejeita_campo_desconhecido():
    dados = {
        "quilometros": 430,
        "placa": "ABC1234",
    }

    with pytest.raises(ValueError):
        validar_dados_da_ia(
            Intent.REGISTRAR_KM,
            dados,
        )


def test_rejeita_string_vazia():
    dados = {
        "origem": "   "
    }

    with pytest.raises(ValueError):
        validar_dados_da_ia(
            Intent.REGISTRAR_VIAGEM,
            dados,
        )


def test_rejeita_string_excessivamente_longa():
    dados = {
        "origem": "A" * 151
    }

    with pytest.raises(ValueError):
        validar_dados_da_ia(
            Intent.REGISTRAR_VIAGEM,
            dados,
        )


def test_rejeita_tipo_incorreto_para_quilometros():
    dados = {
        "quilometros": "430"
    }

    with pytest.raises(ValueError):
        validar_dados_da_ia(
            Intent.REGISTRAR_KM,
            dados,
        )


def test_rejeita_tipo_incorreto_para_valor():
    dados = {
        "valor": "500.00"
    }

    with pytest.raises(ValueError):
        validar_dados_da_ia(
            Intent.REGISTRAR_ABASTECIMENTO,
            dados,
        )


def test_rejeita_estrutura_aninhada_em_campo_simples():
    dados = {
        "carga": {
            "tipo": "soja"
        }
    }

    with pytest.raises(ValueError):
        validar_dados_da_ia(
            Intent.REGISTRAR_VIAGEM,
            dados,
        )


def test_aceita_dados_vazios_para_conversa():
    resultado = validar_dados_da_ia(
        Intent.CONVERSA,
        {},
    )

    assert resultado == {}


def test_aceita_dados_vazios_para_ajuda():
    resultado = validar_dados_da_ia(
        Intent.AJUDA,
        {},
    )

    assert resultado == {}


def test_rejeita_dados_para_conversa():
    dados = {
        "quilometros": 430
    }

    with pytest.raises(ValueError):
        validar_dados_da_ia(
            Intent.CONVERSA,
            dados,
        )


def test_rejeita_data_invalida():
    dados = {
        "data_inicio": "data-que-nao-existe"
    }

    with pytest.raises(ValueError):
        validar_dados_da_ia(
            Intent.CONSULTAR_KM,
            dados,
        )


def test_rejeita_id_invalido():
    dados = {
        "viagem_id": "123"
    }

    with pytest.raises(ValueError):
        validar_dados_da_ia(
            Intent.REGISTRAR_KM,
            dados,
        )


def test_rejeita_muitos_campos():
    dados = {
        "origem": "Aracaju",
        "destino": "Salvador",
        "quilometros": 500,
        "valor_frete": 1000,
        "carga": "Soja",
        "data_inicio": "2026-08-01",
        "data_fim": "2026-08-02",
        "gastos": 100,
        "empresa_id": 1,
        "viagem_id": 2,
        "campo_extra_1": "x",
        "campo_extra_2": "y",
    }

    with pytest.raises(ValueError):
        validar_dados_da_ia(
            Intent.REGISTRAR_VIAGEM,
            dados,
        )


def test_rejeita_estrutura_muito_profunda():
    dados = {
        "carga": {
            "nivel_1": {
                "nivel_2": {
                    "nivel_3": "valor"
                }
            }
        }
    }

    with pytest.raises(ValueError):
        validar_dados_da_ia(
            Intent.REGISTRAR_VIAGEM,
            dados,
        )


def test_rejeita_json_excessivamente_grande():
    dados = {
        "carga": "A" * 9000
    }

    with pytest.raises(ValueError):
        validar_dados_da_ia(
            Intent.REGISTRAR_VIAGEM,
            dados,
        )