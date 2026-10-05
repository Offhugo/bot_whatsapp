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

    def pode_registrar(self, usuario) -> bool:
        """
        Operações de registro pertencem ao motorista no MVP.
        """

        return usuario.perfil == "motorista"

    def pode_registrar_em_empresa(
        self,
        usuario,
        empresa_id: int | None
    ) -> bool:
        """
        Verifica se o motorista pode registrar uma operação
        vinculada a determinada empresa.
        """

        if not self.pode_registrar(usuario):
            return False

        if empresa_id is None:
            return True

        return self._pode_acessar_empresa(
            usuario,
            empresa_id
        )

    def _pode_acessar_empresa(
        self,
        usuario,
        empresa_id: int | None
    ) -> bool:

        if empresa_id is None:
            return False

        return any(
            vinculo.empresa_id == empresa_id and vinculo.ativo
            for vinculo in usuario.empresas_vinculos
        )