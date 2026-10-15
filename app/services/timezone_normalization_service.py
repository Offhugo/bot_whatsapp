"""
Serviço para normalização e conversão de timezones.

Item 10: Implementa estratégia de UTC no banco + timezone preferido do usuário.
"""

import logging
from datetime import datetime
from sqlalchemy.orm import Session
import pytz

import app.models as models

logger = logging.getLogger(__name__)


class TimezoneNormalizationService:
    """
    Normaliza e converte timezones entre UTC e timezone preferido do usuário.

    Estratégia:
    - Armazenar sempre em UTC no banco de dados
    - Cada usuário tem um timezone preferido
    - Converter apenas na apresentação ao usuário
    """

    DEFAULT_TIMEZONE = "America/Fortaleza"

    def obter_timezone_usuario(
        self,
        usuario_id: int,
        db: Session
    ) -> str:
        """
        Obtém o timezone preferido do usuário.

        Args:
            usuario_id: ID do usuário
            db: Sessão do banco de dados

        Returns:
            Timezone em formato IANA (ex: "America/Fortaleza")
        """
        try:
            usuario = db.query(models.Usuario).get(usuario_id)
            if not usuario:
                logger.warning(f"Usuário {usuario_id} não encontrado")
                return self.DEFAULT_TIMEZONE

            timezone = usuario.timezone or self.DEFAULT_TIMEZONE
            return timezone

        except Exception as e:
            logger.error(f"Erro ao obter timezone do usuário: {e}")
            return self.DEFAULT_TIMEZONE

    def atualizar_timezone_usuario(
        self,
        usuario_id: int,
        timezone: str,
        db: Session
    ) -> bool:
        """
        Atualiza o timezone preferido do usuário.

        Args:
            usuario_id: ID do usuário
            timezone: Novo timezone (IANA format)
            db: Sessão do banco de dados

        Returns:
            True se sucesso, False caso contrário
        """
        try:
            # Validar timezone
            try:
                pytz.timezone(timezone)
            except pytz.exceptions.UnknownTimeZoneError:
                logger.error(f"Timezone inválido: {timezone}")
                return False

            usuario = db.query(models.Usuario).get(usuario_id)
            if not usuario:
                logger.warning(f"Usuário {usuario_id} não encontrado")
                return False

            usuario.timezone = timezone
            db.commit()

            logger.info(f"Timezone atualizado para usuário {usuario_id}: {timezone}")
            return True

        except Exception as e:
            logger.error(f"Erro ao atualizar timezone: {e}")
            db.rollback()
            return False

    def agora_utc(self) -> datetime:
        """
        Retorna data/hora atual em UTC.

        Returns:
            datetime em UTC (sem tzinfo para compatibilidade com banco)
        """
        return datetime.now(pytz.UTC).replace(tzinfo=None)

    def agora_usuario(
        self,
        usuario_id: int,
        db: Session
    ) -> datetime:
        """
        Retorna data/hora atual no timezone do usuário.

        Args:
            usuario_id: ID do usuário
            db: Sessão do banco de dados

        Returns:
            datetime no timezone do usuário (com tzinfo)
        """
        try:
            timezone_str = self.obter_timezone_usuario(usuario_id, db)
            tz = pytz.timezone(timezone_str)
            return datetime.now(tz)

        except Exception as e:
            logger.error(f"Erro ao obter data/hora do usuário: {e}")
            return datetime.now(pytz.UTC)

    def converter_para_usuario(
        self,
        timestamp_iso: str,
        usuario_id: int,
        db: Session,
        formato: str = "%d/%m/%Y %H:%M"
    ) -> str:
        """
        Converte timestamp ISO para timezone do usuário (formatado).

        Args:
            timestamp_iso: ISO 8601 string (ex: "2026-10-15T02:30:00Z")
            usuario_id: ID do usuário
            db: Sessão do banco de dados
            formato: Formato de saída (Python strftime)

        Returns:
            String formatada no timezone do usuário
        """
        try:
            # Parse ISO 8601
            if timestamp_iso.endswith('Z'):
                timestamp_iso = timestamp_iso.replace('Z', '+00:00')

            dt_utc = datetime.fromisoformat(timestamp_iso)

            # Obter timezone do usuário
            timezone_str = self.obter_timezone_usuario(usuario_id, db)
            tz = pytz.timezone(timezone_str)

            # Se o datetime não tem timezone, assumir UTC
            if dt_utc.tzinfo is None:
                dt_utc = pytz.UTC.localize(dt_utc)

            # Converter para timezone do usuário
            dt_usuario = dt_utc.astimezone(tz)

            # Formatar
            return dt_usuario.strftime(formato)

        except Exception as e:
            logger.warning(f"Erro ao converter timestamp: {e}")
            return timestamp_iso

    def converter_para_usuario_dict(
        self,
        timestamp_iso: str,
        usuario_id: int,
        db: Session
    ) -> dict:
        """
        Converte timestamp ISO para múltiplos formatos no timezone do usuário.

        Args:
            timestamp_iso: ISO 8601 string
            usuario_id: ID do usuário
            db: Sessão do banco de dados

        Returns:
            Dict com múltiplos formatos:
            {
                "utc": "2026-10-15T02:30:00Z",
                "usuario": "15/10/2026 23:30",  # Localizado
                "data": "15/10/2026",
                "hora": "23:30",
                "timestamp": 1726353000
            }
        """
        try:
            # Parse ISO
            if timestamp_iso.endswith('Z'):
                timestamp_iso_parse = timestamp_iso.replace('Z', '+00:00')
            else:
                timestamp_iso_parse = timestamp_iso

            dt_utc = datetime.fromisoformat(timestamp_iso_parse)

            # Obter timezone do usuário
            timezone_str = self.obter_timezone_usuario(usuario_id, db)
            tz = pytz.timezone(timezone_str)

            # Se não tem timezone, assumir UTC
            if dt_utc.tzinfo is None:
                dt_utc = pytz.UTC.localize(dt_utc)

            # Converter
            dt_usuario = dt_utc.astimezone(tz)

            return {
                "utc": timestamp_iso,
                "usuario": dt_usuario.strftime("%d/%m/%Y %H:%M"),
                "data": dt_usuario.strftime("%d/%m/%Y"),
                "hora": dt_usuario.strftime("%H:%M"),
                "timestamp": int(dt_utc.timestamp())
            }

        except Exception as e:
            logger.warning(f"Erro ao converter timestamp para dict: {e}")
            return {"utc": timestamp_iso}

    def converter_lista_mensagens(
        self,
        mensagens: list,
        usuario_id: int,
        db: Session
    ) -> list:
        """
        Converte timestamps de todas as mensagens para timezone do usuário.

        Args:
            mensagens: Lista de dicts com campo 'timestamp'
            usuario_id: ID do usuário
            db: Sessão do banco de dados

        Returns:
            Lista de mensagens com timestamps convertidos adicionados
        """
        resultado = []

        for msg in mensagens:
            msg_copia = msg.copy()

            if "timestamp" in msg_copia:
                try:
                    msg_copia["timestamp_usuario"] = self.converter_para_usuario(
                        msg_copia["timestamp"],
                        usuario_id,
                        db
                    )
                    # Também adicionar dict completo
                    msg_copia["timestamp_info"] = self.converter_para_usuario_dict(
                        msg_copia["timestamp"],
                        usuario_id,
                        db
                    )
                except Exception as e:
                    logger.warning(f"Erro ao converter timestamp da mensagem: {e}")

            resultado.append(msg_copia)

        return resultado

    def validar_timezone(self, timezone: str) -> bool:
        """
        Valida se um timezone é válido.

        Args:
            timezone: Timezone em formato IANA

        Returns:
            True se válido, False caso contrário
        """
        try:
            pytz.timezone(timezone)
            return True
        except pytz.exceptions.UnknownTimeZoneError:
            return False

    def listar_timezones_brasil(self) -> list:
        """
        Lista todos os timezones do Brasil.

        Returns:
            Lista de timezones IANA para Brasil
        """
        timezones_brasil = [
            'America/Fortaleza',      # UTC-3 (Ceará, RN, PB, PE, AL, SE)
            'America/Recife',         # UTC-3 (Pernambuco - alias)
            'America/Araguaina',      # UTC-3 (Tocantins)
            'America/Maceio',         # UTC-3 (Alagoas - alias)
            'America/Bahia',          # UTC-3 (Bahia)
            'America/Sao_Paulo',      # UTC-3 (SP, RJ, ES, MG, PR, SC, RS)
            'America/Campo_Grande',   # UTC-4 (Mato Grosso do Sul)
            'America/Cuiaba',         # UTC-4 (Mato Grosso)
            'America/Belem',          # UTC-3 (Pará, AP)
            'America/Manaus',         # UTC-4 (Amazonas, RR)
            'America/Boa_Vista',      # UTC-4 (Roraima - alias)
            'America/Porto_Velho',    # UTC-4 (Rondônia)
            'America/Eirunepe',       # UTC-5 (Acre - western)
            'America/Rio_Branco',     # UTC-5 (Acre)
        ]

        return sorted(timezones_brasil)
