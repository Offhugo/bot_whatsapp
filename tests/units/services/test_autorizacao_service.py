from app.models import Usuario, UsuarioEmpresa, Viagem, Registro
from app.services.autorizacao_service import AutorizacaoService


def test_motorista_pode_acessar_sua_propria_viagem():
    service = AutorizacaoService()

    usuario = Usuario(
        id=1,
        telefone="5511999999999",
        perfil="motorista"
    )

    viagem = Viagem(
        id=10,
        usuario_id=1,
        empresa_id=5
    )

    assert service.pode_acessar_viagem(usuario, viagem) is True


def test_motorista_nao_pode_acessar_viagem_de_outro_usuario():
    service = AutorizacaoService()

    usuario = Usuario(
        id=1,
        telefone="5511999999999",
        perfil="motorista"
    )

    viagem = Viagem(
        id=10,
        usuario_id=2,
        empresa_id=5
    )

    assert service.pode_acessar_viagem(usuario, viagem) is False


def test_gerente_pode_acessar_viagem_de_empresa_com_vinculo_ativo():
    service = AutorizacaoService()

    usuario = Usuario(
        id=1,
        telefone="5511999999999",
        perfil="gerente"
    )

    vinculo = UsuarioEmpresa(
        usuario_id=1,
        empresa_id=5,
        ativo=True
    )

    usuario.empresas_vinculos = [vinculo]

    viagem = Viagem(
        id=10,
        usuario_id=2,
        empresa_id=5
    )

    assert service.pode_acessar_viagem(usuario, viagem) is True


def test_gerente_nao_pode_acessar_empresa_sem_vinculo_ativo():
    service = AutorizacaoService()

    usuario = Usuario(
        id=1,
        telefone="5511999999999",
        perfil="gerente"
    )

    vinculo = UsuarioEmpresa(
        usuario_id=1,
        empresa_id=5,
        ativo=False
    )

    usuario.empresas_vinculos = [vinculo]

    viagem = Viagem(
        id=10,
        usuario_id=2,
        empresa_id=5
    )

    assert service.pode_acessar_viagem(usuario, viagem) is False


def test_gerente_nao_pode_acessar_empresa_diferente_do_vinculo():
    service = AutorizacaoService()

    usuario = Usuario(
        id=1,
        telefone="5511999999999",
        perfil="gerente"
    )

    vinculo = UsuarioEmpresa(
        usuario_id=1,
        empresa_id=5,
        ativo=True
    )

    usuario.empresas_vinculos = [vinculo]

    viagem = Viagem(
        id=10,
        usuario_id=2,
        empresa_id=8
    )

    assert service.pode_acessar_viagem(usuario, viagem) is False


def test_gerente_nao_pode_acessar_viagem_sem_empresa():
    service = AutorizacaoService()

    usuario = Usuario(
        id=1,
        telefone="5511999999999",
        perfil="gerente"
    )

    viagem = Viagem(
        id=10,
        usuario_id=2,
        empresa_id=None
    )

    assert service.pode_acessar_viagem(usuario, viagem) is False


def test_motorista_pode_acessar_seu_proprio_registro():
    service = AutorizacaoService()

    usuario = Usuario(
        id=1,
        telefone="5511999999999",
        perfil="motorista"
    )

    registro = Registro(
        id=20,
        usuario_id=1,
        empresa_id=5,
        viagem_id=10
    )

    assert service.pode_acessar_registro(usuario, registro) is True


def test_motorista_nao_pode_acessar_registro_de_outro_usuario():
    service = AutorizacaoService()

    usuario = Usuario(
        id=1,
        telefone="5511999999999",
        perfil="motorista"
    )

    registro = Registro(
        id=20,
        usuario_id=2,
        empresa_id=5,
        viagem_id=10
    )

    assert service.pode_acessar_registro(usuario, registro) is False


def test_gerente_pode_acessar_registro_de_empresa_com_vinculo_ativo():
    service = AutorizacaoService()

    usuario = Usuario(
        id=1,
        telefone="5511999999999",
        perfil="gerente"
    )

    vinculo = UsuarioEmpresa(
        usuario_id=1,
        empresa_id=5,
        ativo=True
    )

    usuario.empresas_vinculos = [vinculo]

    registro = Registro(
        id=20,
        usuario_id=2,
        empresa_id=5,
        viagem_id=10
    )

    assert service.pode_acessar_registro(usuario, registro) is True


def test_perfil_desconhecido_nao_tem_acesso():
    service = AutorizacaoService()

    usuario = Usuario(
        id=1,
        telefone="5511999999999",
        perfil="perfil_desconhecido"
    )

    viagem = Viagem(
        id=10,
        usuario_id=1,
        empresa_id=5
    )

    assert service.pode_acessar_viagem(usuario, viagem) is False