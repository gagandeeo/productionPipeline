from models import EndPoint, MLAlgorithm, MLAlgorithmStatus


class MLRegistry:
    def __init__(self, db):
        self.endpoints = {}
        self.db = db
        # self.db = Session

    def get_or_create(self, model, **kwargs):
        instance = self.db.query(model).filter_by(**kwargs).first()
        if instance:
            return instance, False
        else:
            instance = model(**kwargs)
            self.db.add(instance)
            self.db.commit()
            self.db.refresh(instance)
            return instance, True

    def add_algorithm(self, endpoint_name, algorithm_object, algorithm_name,
                      algorithm_status, algorithm_version, owner,
                      algorithm_description, algorithm_code):

        # get endpoint
        params = {"name": endpoint_name, "owner": owner}
        endpoint, _ = self.get_or_create(EndPoint, **params)

        params = {"name": algorithm_name,
                  "description": algorithm_description,
                  "code": algorithm_code,
                  "version": algorithm_version,
                  "owner": owner,
                  "parent_endpoint": endpoint.id}
        database_object, algorithm_created = self.get_or_create(MLAlgorithm, **params)
        print("--------------", database_object, "--------------")
        if algorithm_created:
            status = MLAlgorithmStatus(
                status=algorithm_status,
                created_by=owner,
                parent_mlalgorithm=database_object.id,
                active=True
            )
            self.db.add(status)
            self.db.commit()
            self.db.refresh(status)

        self.endpoints[database_object.id] = algorithm_object

