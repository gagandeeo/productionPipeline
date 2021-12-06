import models
import schemas
from sqlalchemy.orm import Session
from sqlalchemy import and_


def add_abtest(db: Session, values: schemas.ABTestCreate):
    abtest = models.ABTest()
    abtest.__dict__.update(dict(values))
    db.add(abtest)
    db.commit()
    db.refresh(abtest)

    return abtest


def get_update_abtest(db: Session, query_params: schemas.QueryParams, values: schemas.Values):
    ab_test = db.query(models.ABTest).filter(
        models.ABTest.id == query_params["item_id"]
    ).update(values)
    db.commit()

    return ab_test


def get_abtest(db: Session, query_params: schemas.QueryParams):
    abtest = db.query(models.ABTest).filter(
        models.ABTest.id == query_params["item_id"]
    ).first()

    return abtest


def add_mlrequest(db: Session, values: schemas.Values):

    ml_request = models.MLRequest()
    ml_request.__dict__.update(values)
    db.add(ml_request)
    db.commit()
    db.refresh(ml_request)

    return ml_request


def get_mlrequest(db: Session, query_param: schemas.QueryParams):
    mlrequests = db.query(models.MLRequest).filter(
        and_(
            models.MLRequest.parent_mlalgorithm == query_param["parent_mlalgorithm"],
            models.MLRequest.created_at >= query_param["created_at"],
            models.MLRequest.created_at <= query_param["date_now"]
        )
    )

    return mlrequests


def get_update_mlrequest(db: Session, query_params: schemas.QueryParams, values: schemas.Values):
    mlrequest = db.query(models.MLRequest).filter(
        models.MLRequest.id == query_params["item_id"]
    ).update(values)
    db.commit()

    return mlrequest


def get_update_mlalgorithmstatus(db: Session, query_params: schemas.QueryParams, values: schemas.Values):
    if query_params["created_by"]:
        algo_status = db.query(models.MLAlgorithmStatus).filter(
            and_(
                models.MLAlgorithmStatus.parent_mlalgorithm == query_params["item_id"],
                models.MLAlgorithmStatus.created_by == query_params["created_by"]
            )
        )
    else:
        algo_status = db.query(models.MLAlgorithmStatus).filter(
                models.MLAlgorithmStatus.parent_mlalgorithm == query_params["item_id"],
        )
    algo_status.update(values)
    db.commit()

    return algo_status


def get_algos(db: Session, query_params: schemas.QueryParams):
    endpoints = db.query(models.EndPoint.id).filter(
        and_(
            models.EndPoint.name == query_params["endpoint_name"],
        )
    ).subquery()

    algos = db.query(models.MLAlgorithm).filter(
            models.MLAlgorithm.parent_endpoint.in_(endpoints)
    )
    algos = algos.join(models.MLAlgorithmStatus).filter(
        and_(
            models.MLAlgorithmStatus.status == query_params["algorithm_status"],
            models.MLAlgorithmStatus.active == query_params["status"]
        )
    )

    return algos
