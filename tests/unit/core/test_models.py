# tests/unit/core/test_models.py
import pytest
import uuid
from datetime import datetime
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship, RelationshipProperty # Added RelationshipProperty
from sqlalchemy.sql.schema import Column, ForeignKey, Table, CallableColumnDefault
from sqlalchemy.sql.sqltypes import String, DateTime, JSON, Integer, Boolean, Float
from unittest.mock import patch


# Mock the Base import to avoid actual database connection during model definition tests
# For testing relationships, we'll need a way to mock the related classes too or define them.
# Given that Base is imported from tenebrinet.core.database, we'll patch that import.
from tenebrinet.core.database import Base
from tenebrinet.core.models import Attack, Session, Credential


def test_attack_model_definition():
    """Test the Attack model's column definitions and types."""
    assert isinstance(Attack.__table__.columns.id.type, postgresql.UUID)
    assert Attack.__table__.columns.id.primary_key
    # Check that the default is a callable and specifically uuid.uuid4
    assert isinstance(Attack.__table__.columns.id.default, CallableColumnDefault)
    assert Attack.__table__.columns.id.default.arg.__module__ == uuid.uuid4.__module__
    assert Attack.__table__.columns.id.default.arg.__name__ == uuid.uuid4.__name__

    assert isinstance(Attack.__table__.columns.ip.type, String)
    assert Attack.__table__.columns.ip.nullable is False
    assert Attack.__table__.columns.ip.index

    assert isinstance(Attack.__table__.columns.timestamp.type, DateTime)
    # Check that the default is a callable and specifically datetime.utcnow
    assert isinstance(Attack.__table__.columns.timestamp.default, CallableColumnDefault)
    assert Attack.__table__.columns.timestamp.default.arg.__module__ == datetime.utcnow.__module__
    assert Attack.__table__.columns.timestamp.default.arg.__name__ == datetime.utcnow.__name__
    assert Attack.__table__.columns.timestamp.index

    assert isinstance(Attack.__table__.columns.service.type, String)
    assert Attack.__table__.columns.service.nullable is False

    assert isinstance(Attack.__table__.columns.payload.type, JSON)
    assert isinstance(Attack.__table__.columns.threat_type.type, String)
    assert isinstance(Attack.__table__.columns.confidence.type, Float)
    assert isinstance(Attack.__table__.columns.country.type, String)
    assert isinstance(Attack.__table__.columns.asn.type, Integer)

    # Check relationships
    assert isinstance(Attack.sessions.property, RelationshipProperty) # Changed from relationship to RelationshipProperty
    assert Attack.sessions.property.back_populates == "attack"
    assert isinstance(Attack.credentials.property, RelationshipProperty) # Changed from relationship to RelationshipProperty
    assert Attack.credentials.property.back_populates == "attack"


def test_session_model_definition():
    """Test the Session model's column definitions and types."""
    assert isinstance(Session.__table__.columns.id.type, postgresql.UUID)
    assert Session.__table__.columns.id.primary_key
    # Check that the default is a callable and specifically uuid.uuid4
    assert isinstance(Session.__table__.columns.id.default, CallableColumnDefault)
    assert Session.__table__.columns.id.default.arg.__module__ == uuid.uuid4.__module__
    assert Session.__table__.columns.id.default.arg.__name__ == uuid.uuid4.__name__

    assert isinstance(Session.__table__.columns.attack_id.type, postgresql.UUID)
    # Correctly check foreign key type. Note: foreign_keys is a set.
    fk_col = next(iter(Session.__table__.columns.attack_id.foreign_keys)).column
    assert isinstance(fk_col.type, postgresql.UUID)

    assert isinstance(Session.__table__.columns.start_time.type, DateTime)
    # Check that the default is a callable and specifically datetime.utcnow
    assert isinstance(Session.__table__.columns.start_time.default, CallableColumnDefault)
    assert Session.__table__.columns.start_time.default.arg.__module__ == datetime.utcnow.__module__
    assert Session.__table__.columns.start_time.default.arg.__name__ == datetime.utcnow.__name__
    assert isinstance(Session.__table__.columns.end_time.type, DateTime)
    assert isinstance(Session.__table__.columns.commands.type, JSON)

    # Check relationships
    assert isinstance(Session.attack.property, RelationshipProperty) # Changed from relationship to RelationshipProperty
    assert Session.attack.property.back_populates == "sessions"

def test_credential_model_definition():
    """Test the Credential model's column definitions and types."""
    assert isinstance(Credential.__table__.columns.id.type, postgresql.UUID)
    assert Credential.__table__.columns.id.primary_key
    # Check that the default is a callable and specifically uuid.uuid4
    assert isinstance(Credential.__table__.columns.id.default, CallableColumnDefault)
    assert Credential.__table__.columns.id.default.arg.__module__ == uuid.uuid4.__module__
    assert Credential.__table__.columns.id.default.arg.__name__ == uuid.uuid4.__name__

    assert isinstance(Credential.__table__.columns.attack_id.type, postgresql.UUID)
    # Correctly check foreign key type
    fk_col = next(iter(Credential.__table__.columns.attack_id.foreign_keys)).column
    assert isinstance(fk_col.type, postgresql.UUID)

    assert isinstance(Credential.__table__.columns.username.type, String)
    assert Credential.__table__.columns.username.nullable is False
    assert isinstance(Credential.__table__.columns.password.type, String)
    assert Credential.__table__.columns.password.nullable is False
    assert isinstance(Credential.__table__.columns.success.type, Boolean)
    assert Credential.__table__.columns.success.default.arg is False # Use .arg for ScalarElementColumnDefault

    # Check relationships
    assert isinstance(Credential.attack.property, RelationshipProperty) # Changed from relationship to RelationshipProperty
    assert Credential.attack.property.back_populates == "credentials"


def test_model_repr_methods():
    """Test the __repr__ methods for all models."""
    attack_id = uuid.uuid4()
    mock_attack = Attack(id=attack_id, ip="127.0.0.1", service="ssh", threat_type="brute_force")
    assert f"<Attack(id='{attack_id}', ip='127.0.0.1', service='ssh', threat_type='brute_force')>" in repr(mock_attack)

    session_id = uuid.uuid4()
    # Mocking datetime.utcnow() for consistent repr testing
    with patch('tenebrinet.core.models.datetime') as mock_dt:
        mock_dt.utcnow.return_value = datetime(2023, 1, 1, 12, 0, 0)
        mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw) # Allow normal datetime behavior for others
        mock_session = Session(id=session_id, attack_id=attack_id, start_time=mock_dt.utcnow())
        assert f"<Session(id='{session_id}', attack_id='{attack_id}', start_time='{mock_dt.utcnow()}')>" in repr(mock_session)

    credential_id = uuid.uuid4()
    mock_credential = Credential(id=credential_id, attack_id=attack_id, username="user", password="pass", success=True)
    assert f"<Credential(id='{credential_id}', attack_id='{attack_id}', username='user', success='True')>" in repr(mock_credential)
