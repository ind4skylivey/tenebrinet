# tenebrinet/core/models.py
from sqlalchemy import Column, String, DateTime, JSON, Integer, ForeignKey, Boolean, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from tenebrinet.core.database import Base # Import Base from our database setup

class Attack(Base):
    """Main attack event record."""
    __tablename__ = "attacks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ip = Column(String(45), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    service = Column(String(50), nullable=False)
    payload = Column(JSON)
    threat_type = Column(String(50))  # ML classification result
    confidence = Column(Float)  # ML confidence score
    country = Column(String(2))  # ISO country code
    asn = Column(Integer)  # Autonomous System Number

    sessions = relationship("Session", back_populates="attack")
    credentials = relationship("Credential", back_populates="attack")

    def __repr__(self):
        return (
            f"<Attack(id='{self.id}', ip='{self.ip}', service='{self.service}', "
            f"threat_type='{self.threat_type}')>"
        )
    
class Session(Base):
    """Attack session lifecycle."""
    __tablename__ = "sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attack_id = Column(UUID(as_uuid=True), ForeignKey("attacks.id"))
    start_time = Column(DateTime(timezone=True), default=datetime.utcnow)
    end_time = Column(DateTime(timezone=True))
    commands = Column(JSON)  # Commands executed during session

    attack = relationship("Attack", back_populates="sessions")

    def __repr__(self):
        return (
            f"<Session(id='{self.id}', attack_id='{self.attack_id}', "
            f"start_time='{self.start_time}')>"
        )

class Credential(Base):
    """Captured credentials."""
    __tablename__ = "credentials"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attack_id = Column(UUID(as_uuid=True), ForeignKey("attacks.id"))
    username = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    success = Column(Boolean, default=False)

    attack = relationship("Attack", back_populates="credentials")

    def __repr__(self):
        return (
            f"<Credential(id='{self.id}', attack_id='{self.attack_id}', "
            f"username='{self.username}', success='{self.success}')>"
        )
