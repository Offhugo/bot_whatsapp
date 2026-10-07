from datetime import datetime


def converter_para_datetime(valor):
    if isinstance(valor, datetime):
        return valor

    if not isinstance(valor, str):
        return None

    try:
        return datetime.fromisoformat(valor)
    except ValueError:
        return None