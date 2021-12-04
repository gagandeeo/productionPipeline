from enum import Enum
from database import Base
from sqlalchemy import DateTime, sql, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class EndPoint(Base):
    """
    The Endpoint object represents ML API endpoint.

    Attributes:
        name: The name of the endpoint, it will be used in API URL,
        owner: The string with owner name,
        created_at: The date when endpoint was created.
    """
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
    """
    The MLAlgorithm represent the ML algorithm object.

    Attributes:
        name: The name of the algorithm.
        description: The short description of how the algorithm works.
        code: The code of the algorithm.
        version: The version of the algorithm similar to software versioning.
        owner: The name of the owner.
        created_at: The date when MLAlgorithm was added.
        parent_endpoint: The reference to the Endpoint.
    """
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
    """
    The MLAlgorithmStatus represent status of the MLAlgorithm which can change during the time.

    Attributes:
        status: The status of algorithm in the endpoint. Can be: testing, staging, production, ab_testing.
        active: The boolean flag which point to currently active status.
        created_by: The name of creator.
        created_at: The date of status creation.
        parent_mlalgorithm: The reference to corresponding MLAlgorithm.

    """
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
    """
    The MLRequest will keep information about all requests to ML algorithms.

    Attributes:
        input_data: The input data to ML algorithm in JSON format.
        full_response: The response of the ML algorithm.
        response: The response of the ML algorithm in JSON format.
        feedback: The feedback about the response in JSON format.
        created_at: The date when request was created.
        parent_mlalgorithm: The reference to MLAlgorithm used to compute response.
    """
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
