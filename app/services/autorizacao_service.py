class AutorizacaoService:

    def pode_acessar_viagem(self, usuario, viagem) -> bool:
        """
        Verifica se o usuário pode acessar uma viagem.
        """

        if usuario.perfil == "motorista":
            return viagem.usuario_id == usuario.id

        if usuario.perfil == "gerente":
            return self._pode_acessar_empresa(
                usuario,
                viagem.empresa_id
            )

        return False

    def pode_acessar_registro(self, usuario, registro) -> bool:
        """
        Verifica se o usuário pode acessar um registro.
        """

        if usuario.perfil == "motorista":
            return registro.usuario_id == usuario.id

        if usuario.perfil == "gerente":
            return self._pode_acessar_empresa(
                usuario,
                registro.empresa_id
            )

        return False

    def _pode_acessar_empresa(self, usuario, empresa_id) -> bool:
        """
        Gerentes só acessam empresas nas quais possuem
        vínculo ativo.
        """

        if empresa_id is None:
            return False

        return any(
            vinculo.empresa_id == empresa_id and vinculo.ativo
            for vinculo in usuario.empresas_vinculos
        )