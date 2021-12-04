import uvicorn
from fastapi import FastAPI, Depends, status
from fastapi.responses import JSONResponse
from numpy.random import rand
import crud
import schemas
from backend.server.wsgi import register_algo
from database import SessionLocal, engine
from sqlalchemy.orm import Session
import models
import datetime

models.Base.metadata.create_all(bind=engine)
app = FastAPI()
registry = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def startup_event():
    global registry
    with SessionLocal() as db:
        registry = register_algo(db)


@app.post("/api/v1/{endpoint_name}/predict/{algorithm_status}", response_model=schemas.PredictResponse)
def predict(endpoint_name: str, algorithm_status: models.StatusName, request: schemas.PredictCreate,
            db: Session = Depends(get_db)):
    try:

        query_params = {
            "endpoint_name": endpoint_name,
            "algorithm_status": algorithm_status.value,
            "status": True,
        }

        algs = crud.get_algos(db, query_params)
        algs = algs.all()

        if len(algs) == 0:
            content = {"status": "Error", "message": "ML Algorithm is not available"}
            return JSONResponse(
                content=content,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        if len(algs) != 1 and algorithm_status.value != "ab_testing":
            content = {"status": "Error",
                       "message": "ML Algorithm selection is ambiguous. Please specify algorithm version"}
            return JSONResponse(
                content=content,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        alg_index = 0
        if algorithm_status.value == "ab_testing":
            alg_index = 0 if rand() < 0.5 else 1

        algorithm_object = registry.endpoints[algs[alg_index].id]
        prediction = algorithm_object.compute_prediction(request.data)

        label = prediction["label"] if "label" in prediction else "error"

        values = {
            "input_data": str(request.data),
            "full_response": str(prediction),
            "response": label,
            "feedback": "",
            "parent_mlalgorithm": algs[alg_index].id
        }

        ml_request = crud.add_mlrequest(db, values)

        prediction["request_id"] = ml_request.id
        if label == "error":
            content = {"request_id": ml_request.id, "status": "Error in prediction", "message": "Check Inputs"}
            return JSONResponse(
                content=content,
                status_code=status.HTTP_200_OK
            )
        return JSONResponse(content=prediction, status_code=status.HTTP_200_OK)
    except Exception as e:
        content = {"status": "Error", "message": str(e)}
        return JSONResponse(
            content=content,
            status_code=status.HTTP_400_BAD_REQUEST
        )


@app.post("/api/v1/abtests/", response_model=schemas.ABTestResponse)
def add_abtests(request: schemas.ABTestCreate, db: Session = Depends(get_db)):
    try:
        abtest = crud.add_abtest(db, request)
        values = {"status": "ab_testing", "created_by": request.created_by, "active": True}

        query_params = {"created_by": None, "item_id": request.parent_mlalgorithm1}
        status_1 = crud.get_update_mlalgorithmstatus(db, query_params, values)

        query_params["item_id"] = request.parent_mlalgorithm2
        status_2 = crud.get_update_mlalgorithmstatus(db, query_params, values)

        content = {"id": abtest.id}

        return JSONResponse(
            content=content,
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        content = {"status": "Error", "message": str(e)}
        return JSONResponse(
            content=content,
            status_code=status.HTTP_400_BAD_REQUEST
        )


@app.post("/api/v1/stop_abtests/{item_id}", response_model=schemas.StopABTestResponse)
def stop_abtests(item_id: int, db: Session = Depends(get_db)):
    try:
        query_params = {"item_id": item_id}
        ab_test = crud.get_abtest(db, query_params)
        if ab_test.ended_at is not None:
            content = {"status": "Success", "message": "AB Test already finished."}
            return JSONResponse(
                content=content,
                status_code=status.HTTP_200_OK
            )

        date_now = datetime.datetime.now()
        query_params = {
            "parent_mlalgorithm": ab_test.parent_mlalgorithm1,
            "created_at": ab_test.created_at,
            "date_now": date_now
        }
        all_response1 = crud.get_mlrequest(db, query_params)
        correct_response1 = 0
        for record in all_response1:
            if record.response == record.feedback:
                correct_response1 += 1
        accuracy1 = 0
        all_response1 = all_response1.count()
        if all_response1:
            accuracy1 = correct_response1 / all_response1

        query_params['parent_mlalgorithm'] = ab_test.parent_mlalgorithm2
        all_response2 = crud.get_mlrequest(db, query_params)
        correct_response2 = 0
        for record in all_response2:
            if record.response == record.feedback:
                correct_response2 += 1
        accuracy2 = 0
        all_response2 = all_response2.count()
        if all_response2:
            accuracy2 = correct_response2 / all_response2

        alg_id1, alg_id2 = ab_test.parent_mlalgorithm1, ab_test.parent_mlalgorithm2
        if accuracy1 < accuracy2:
            alg_id1, alg_id2 = alg_id2, alg_id1

        values = {
            "status": "production",
            "active": True
        }
        query_params = {
            "item_id": alg_id1,
            "created_by": ab_test.created_by
        }
        status_1 = crud.get_update_mlalgorithmstatus(db, query_params, values)

        values['status'] = "testing"
        query_params["item_id"] = alg_id2
        status_2 = crud.get_update_mlalgorithmstatus(db, query_params, values)

        summary = f"Algorithm A {ab_test.parent_mlalgorithm1} accuracy: {accuracy1}, Algorithm B {ab_test.parent_mlalgorithm2}  accuracy: {accuracy2}"
        values = {
            "ended_at": date_now,
            "summary": summary
        }
        query_params = {
            "item_id": item_id
        }
        ab_test = crud.get_update_abtest(db, query_params, values)

    except Exception as e:
        content = {"status": "Error", "message": str(e)}
        return JSONResponse(
            content=content, status_code=status.HTTP_400_BAD_REQUEST
        )

    content = {"message": "AB Test finished", "summary": summary}
    return JSONResponse(
        content=content, status_code=status.HTTP_200_OK
    )


@app.put("/api/v1/mlrequests/{item_id}", response_model=schemas.MLRequestResponse)
def put_mlrequest(item_id: int, request: schemas.MLRequestCreate, db: Session = Depends(get_db)):
    try:
        query_params = {"item_id": item_id}
        values = dict(request)
        mlrequest = crud.get_update_mlrequest(db, query_params, values)
        content = {"status": "Success", "message": "updated"}
        return JSONResponse(
            content=content,
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        content = {"status": "Error", "message": str(e)}
        return JSONResponse(
            content=content,
            status_code=status.HTTP_400_BAD_REQUEST
        )


@app.get("/")
def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
