import json
import math

from app.schemas.ai_response import Intent
from app.utils.date_validation import converter_para_datetime
from app.utils.validation_limits import (
    MAX_AI_DATA_COLLECTION_ITEMS,
    MAX_AI_DATA_DEPTH,
    MAX_AI_DATA_FIELDS,
    MAX_AI_DATA_JSON_LENGTH,
    MAX_CARGA_LENGTH,
    MAX_ORIGEM_DESTINO_LENGTH,
    MAX_RESOURCE_ID,
)


CAMPOS_PERMITIDOS_POR_INTENT = {
    Intent.REGISTRAR_KM: {
        "quilometros",
        "viagem_id",
    },
    Intent.REGISTRAR_ABASTECIMENTO: {
        "valor",
        "litros",
        "viagem_id",
    },
    Intent.REGISTRAR_VIAGEM: {
        "origem",
        "destino",
        "quilometros",
        "valor_frete",
        "carga",
        "data_inicio",
        "data_fim",
        "gastos",
        "empresa_id",
    },
    Intent.CONSULTAR_KM: {
        "data_inicio",
        "data_fim",
    },
    Intent.CONSULTAR_VIAGENS: {
        "data_inicio",
        "data_fim",
    },
    Intent.CONVERSA: set(),
    Intent.AJUDA: set(),
}


LIMITES_TEXTUAIS = {
    "origem": MAX_ORIGEM_DESTINO_LENGTH,
    "destino": MAX_ORIGEM_DESTINO_LENGTH,
    "carga": MAX_CARGA_LENGTH,
}


CAMPOS_NUMERICOS = {
    "quilometros",
    "valor",
    "litros",
    "valor_frete",
    "gastos",
}


CAMPOS_DE_DATA = {
    "data_inicio",
    "data_fim",
}


CAMPOS_DE_ID = {
    "viagem_id",
    "empresa_id",
}


def validar_dados_da_ia(intent: Intent, dados: dict) -> dict:
    """
    Valida a estrutura e os tipos básicos dos dados produzidos pela IA.

    As regras de negócio específicas continuam nos Use Cases.
    """

    try:
        intent = Intent(intent)
    except ValueError as exc:
        raise ValueError("Intent inválido.") from exc

    if not isinstance(dados, dict):
        raise ValueError("Os dados da IA devem ser um objeto JSON.")

    _validar_tamanho_e_estrutura(dados)

    campos_permitidos = CAMPOS_PERMITIDOS_POR_INTENT[intent]

    campos_desconhecidos = set(dados.keys()) - campos_permitidos

    if campos_desconhecidos:
        raise ValueError(
            f"Campos não permitidos para o intent: "
            f"{', '.join(sorted(campos_desconhecidos))}."
        )

    for campo, valor in dados.items():
        _validar_campo(campo, valor)

    return dict(dados)


def _validar_tamanho_e_estrutura(valor, profundidade: int = 0):
    if profundidade > MAX_AI_DATA_DEPTH:
        raise ValueError(
            "Os dados da IA possuem profundidade excessiva."
        )

    if isinstance(valor, dict):
        if len(valor) > MAX_AI_DATA_FIELDS:
            raise ValueError(
                "Os dados da IA possuem campos em excesso."
            )

        for chave, item in valor.items():
            if not isinstance(chave, str):
                raise ValueError(
                    "As chaves dos dados da IA devem ser strings."
                )

            _validar_tamanho_e_estrutura(item, profundidade + 1)

    elif isinstance(valor, list):
        if len(valor) > MAX_AI_DATA_COLLECTION_ITEMS:
            raise ValueError(
                "Os dados da IA possuem itens em excesso."
            )

        for item in valor:
            _validar_tamanho_e_estrutura(item, profundidade + 1)

    try:
        tamanho_json = len(
            json.dumps(
                valor,
                ensure_ascii=False,
                allow_nan=False,
                separators=(",", ":"),
            )
        )
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "Os dados da IA não possuem estrutura JSON válida."
        ) from exc

    if tamanho_json > MAX_AI_DATA_JSON_LENGTH:
        raise ValueError(
            "Os dados da IA excedem o tamanho máximo permitido."
        )


def _validar_campo(campo: str, valor):
    if campo in LIMITES_TEXTUAIS:
        _validar_texto(campo, valor, LIMITES_TEXTUAIS[campo])
        return

    if campo in CAMPOS_NUMERICOS:
        _validar_numero(campo, valor)
        return

    if campo in CAMPOS_DE_DATA:
        _validar_data(campo, valor)
        return

    if campo in CAMPOS_DE_ID:
        _validar_id(campo, valor)
        return

    raise ValueError(
        f"O campo '{campo}' não possui validação definida."
    )


def _validar_texto(campo: str, valor, limite: int):
    if not isinstance(valor, str):
        raise ValueError(
            f"O campo '{campo}' deve ser uma string."
        )

    if not valor.strip():
        raise ValueError(
            f"O campo '{campo}' não pode estar vazio."
        )

    if len(valor) > limite:
        raise ValueError(
            f"O campo '{campo}' excede o tamanho máximo permitido."
        )


def _validar_numero(campo: str, valor):
    if isinstance(valor, bool):
        raise ValueError(
            f"O campo '{campo}' deve ser numérico."
        )

    if not isinstance(valor, (int, float)):
        raise ValueError(
            f"O campo '{campo}' deve ser numérico."
        )

    if isinstance(valor, float) and not math.isfinite(valor):
        raise ValueError(
            f"O campo '{campo}' possui um valor numérico inválido."
        )


def _validar_data(campo: str, valor):
    if not isinstance(valor, str):
        raise ValueError(
            f"O campo '{campo}' deve ser uma data em formato textual."
        )

    if not valor.strip():
        raise ValueError(
            f"O campo '{campo}' não pode estar vazio."
        )

    if converter_para_datetime(valor) is None:
        raise ValueError(
            f"O campo '{campo}' possui formato de data inválido."
        )


def _validar_id(campo: str, valor):
    if isinstance(valor, bool):
        raise ValueError(
            f"O campo '{campo}' deve ser um identificador inteiro."
        )

    if not isinstance(valor, int):
        raise ValueError(
            f"O campo '{campo}' deve ser um identificador inteiro."
        )

    if valor <= 0 or valor > MAX_RESOURCE_ID:
        raise ValueError(
            f"O campo '{campo}' possui um identificador inválido."
        )