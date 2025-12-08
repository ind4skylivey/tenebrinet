# tests/unit/core/test_database.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.schema import MetaData


# Mocking the database URL to avoid connecting to a real database during tests
@pytest.fixture(autouse=True)
def mock_db_url_env():
    with patch.dict(
        'os.environ',
        {'DATABASE_URL': 'sqlite+aiosqlite:///:memory:'}
    ):
        yield


@pytest.fixture
def mock_base_class():
    """Fixture to provide a mock Base class similar to declarative_base()."""
    # Create a dummy MetaData object for the mock Base
    metadata = MetaData()
    # Dynamically create a mock Base class
    MockBase = declarative_base(metadata=metadata)
    return MockBase


@pytest.fixture
def mock_engine():
    """Fixture to provide a mock AsyncEngine."""
    engine = AsyncMock(spec=AsyncEngine)
    engine.begin.return_value.__aenter__.return_value.run_sync = AsyncMock()
    return engine


@pytest.fixture
def mock_async_session_local():
    """Fixture to provide a mock async_sessionmaker."""
    session_mock = AsyncMock(spec=AsyncSession)
    session_mock.close = AsyncMock()
    # Mock the context manager behavior for async_sessionmaker
    async_session_maker_mock = MagicMock()
    ctx = async_session_maker_mock.return_value.__aenter__
    ctx.return_value = session_mock
    async_session_maker_mock.return_value.__aexit__.return_value = None
    return async_session_maker_mock


@pytest.mark.asyncio
async def test_init_db(mock_engine, mock_base_class):
    """Test that init_db correctly calls create_all on metadata."""
    with patch('tenebrinet.core.database.engine', new=mock_engine), \
         patch('tenebrinet.core.database.Base', new=mock_base_class):
        from tenebrinet.core.database import init_db  # Import after patching

        await init_db()
        mock_engine.begin.assert_called_once()
        ctx = mock_engine.begin.return_value.__aenter__.return_value
        run_sync = ctx.run_sync
        run_sync.assert_called_once_with(mock_base_class.metadata.create_all)


@pytest.mark.asyncio
async def test_get_db_session(
    mock_async_session_local,
    mock_engine,
    mock_base_class
):
    """Test that get_db_session yields a session and closes it."""
    with patch('tenebrinet.core.database.engine', new=mock_engine), \
         patch('tenebrinet.core.database.Base', new=mock_base_class), \
         patch(
             'tenebrinet.core.database.AsyncSessionLocal',
             new=mock_async_session_local
         ):
        # Import after patching
        from tenebrinet.core.database import get_db_session

        async for session in get_db_session():
            # Check if the yielded object is an AsyncSession (mock)
            assert isinstance(session, AsyncSession)
            ctx = mock_async_session_local.return_value.__aenter__
            expected = ctx.return_value
            assert session == expected

        mock_async_session_local.assert_called_once()
        session.close.assert_called_once()
