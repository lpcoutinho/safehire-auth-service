"""Testes do UsuarioRepository — persistência e consultas com SQLite in-memory."""

from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base
from app.models.usuario import TipoUsuario
from app.repositories.usuario_repo import UsuarioRepository
from app.schemas.usuario import Usuario


@pytest_asyncio.fixture
async def session() -> AsyncSession:
    """Cria engine SQLite in-memory com tabela usuarios (schema removido) e retorna sessão."""
    # Remove schema constraint so SQLAlchemy creates table without schema prefix
    Usuario.__table__.schema = None

    engine = create_async_engine("sqlite+aiosqlite://", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as sess:
        yield sess
    await engine.dispose()


@pytest_asyncio.fixture
async def repo(session: AsyncSession) -> UsuarioRepository:
    return UsuarioRepository(session)


class TestUsuarioRepositoryCriar:
    @pytest.mark.asyncio
    async def test_cria_usuario_com_id_gerado(self, repo: UsuarioRepository) -> None:
        usuario = Usuario(
            id=uuid4(),
            nome="Fulano",
            email="fulano@example.com",
            senha_hash="hash",
            tipo=TipoUsuario.candidato,
        )
        criado = await repo.criar(usuario)
        assert criado.id is not None
        assert criado.nome == "Fulano"


class TestUsuarioRepositoryBuscarPorEmail:
    @pytest.mark.asyncio
    async def test_retorna_usuario_quando_email_existe(
        self, repo: UsuarioRepository
    ) -> None:
        await repo.criar(
            Usuario(
                id=uuid4(),
                nome="Fulano",
                email="fulano@example.com",
                senha_hash="hash",
                tipo=TipoUsuario.candidato,
            )
        )
        encontrado = await repo.buscar_por_email("fulano@example.com")
        assert encontrado is not None
        assert encontrado.email == "fulano@example.com"

    @pytest.mark.asyncio
    async def test_retorna_none_quando_email_nao_existe(
        self, repo: UsuarioRepository
    ) -> None:
        resultado = await repo.buscar_por_email("inexistente@example.com")
        assert resultado is None


class TestUsuarioRepositoryBuscarPorId:
    @pytest.mark.asyncio
    async def test_retorna_usuario_quando_id_existe(
        self, repo: UsuarioRepository
    ) -> None:
        uid = uuid4()
        await repo.criar(
            Usuario(
                id=uid,
                nome="Fulano",
                email="fulano@example.com",
                senha_hash="hash",
                tipo=TipoUsuario.candidato,
            )
        )
        encontrado = await repo.buscar_por_id(uid)
        assert encontrado is not None
        assert encontrado.id == uid

    @pytest.mark.asyncio
    async def test_retorna_none_quando_id_nao_existe(
        self, repo: UsuarioRepository
    ) -> None:
        resultado = await repo.buscar_por_id(uuid4())
        assert resultado is None


class TestUsuarioRepositoryListarAtivos:
    @pytest.mark.asyncio
    async def test_retorna_apenas_usuarios_ativos(
        self, repo: UsuarioRepository
    ) -> None:
        await repo.criar(
            Usuario(
                id=uuid4(),
                nome="Ativo",
                email="ativo@e.com",
                senha_hash="hash",
                tipo=TipoUsuario.candidato,
            )
        )
        await repo.criar(
            Usuario(
                id=uuid4(),
                nome="Inativo",
                email="inativo@e.com",
                senha_hash="hash",
                tipo=TipoUsuario.candidato,
                ativo=False,
            )
        )
        ativos = await repo.listar_ativos()
        assert len(ativos) == 1
        assert ativos[0].nome == "Ativo"

    @pytest.mark.asyncio
    async def test_retorna_lista_vazia_quando_sem_ativos(
        self, repo: UsuarioRepository
    ) -> None:
        await repo.criar(
            Usuario(
                id=uuid4(),
                nome="Inativo",
                email="inativo@e.com",
                senha_hash="hash",
                tipo=TipoUsuario.candidato,
                ativo=False,
            )
        )
        ativos = await repo.listar_ativos()
        assert ativos == []


class TestUsuarioRepositoryAtualizar:
    @pytest.mark.asyncio
    async def test_atualiza_nome_do_usuario(self, repo: UsuarioRepository) -> None:
        uid = uuid4()
        await repo.criar(
            Usuario(
                id=uid,
                nome="Fulano",
                email="fulano@example.com",
                senha_hash="hash",
                tipo=TipoUsuario.candidato,
            )
        )
        criado = await repo.buscar_por_id(uid)
        assert criado is not None
        criado.nome = "Fulano Atualizado"
        await repo.atualizar(criado)
        encontrado = await repo.buscar_por_id(uid)
        assert encontrado is not None
        assert encontrado.nome == "Fulano Atualizado"
