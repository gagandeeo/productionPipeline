from enum import Enum
from database import Base
from sqlalchemy import DateTime, sql, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class EndPoint(Base):
    __tablename__ = "endpoints"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    owner = Column(String)
    created_at = Column(
        DateTime(timezone=True),
        server_default=sql.func.now(), autoincrement=True,
    )
    mlalgorithm = relationship("MLAlgorithm", back_populates="endpoint")


class MLAlgorithm(Base):
    __tablename__ = "mlalgorithms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String, nullable=True)
    code = Column(String, nullable=True)
    version = Column(String)
    owner = Column(String)
    created_at = Column(
        DateTime(timezone=True),
        server_default=sql.func.now(), autoincrement=True
    )
    parent_endpoint = Column(Integer, ForeignKey("endpoints.id"))
    endpoint = relationship("EndPoint", back_populates="mlalgorithm")
    mlalgorithm_status = relationship("MLAlgorithmStatus", back_populates="mlalgorithm")
    mlrequest = relationship("MLRequest", back_populates="mlalgorithm")


class MLAlgorithmStatus(Base):
    __tablename__ = "mlalgorithmstatus"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String)
    active = Column(Boolean)
    created_by = Column(String)
    created_at = Column(
        DateTime(timezone=True),
        server_default=sql.func.now(), autoincrement=True
    )
    parent_mlalgorithm = Column(Integer, ForeignKey("mlalgorithms.id"))
    mlalgorithm = relationship("MLAlgorithm", back_populates="mlalgorithm_status")


class MLRequest(Base):
    __tablename__ = "mlrequests"

    id = Column(Integer, primary_key=True, index=True)
    input_data = Column(String)
    full_response = Column(String)
    response = Column(String)
    feedback = Column(String)
    created_at = Column(
        DateTime(timezone=True),
        server_default=sql.func.now(), autoincrement=True
    )
    parent_mlalgorithm = Column(Integer, ForeignKey("mlalgorithms.id"))
    mlalgorithm = relationship("MLAlgorithm", back_populates="mlrequest")


class ABTest(Base):
    __tablename__ = "abtests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    created_by = Column(String)
    created_at = Column(
        DateTime(timezone=True),
        server_default=sql.func.now(), autoincrement=True
    )
    ended_at = Column(DateTime(timezone=True), nullable=True)
    summary = Column(String)

    parent_mlalgorithm1 = Column(Integer, ForeignKey("mlalgorithms.id"))
    parent_mlalgorithm2 = Column(Integer, ForeignKey("mlalgorithms.id"))


class StatusName(str, Enum):
    production = "production"
    ab_testing = "ab_testing"
