from backend.ml.income_classifier.random_forest import RandomForestClassifier
from backend.ml.income_classifier.extra_trees import ExtraTreesClassifier
from backend.ml.registry import MLRegistry
import inspect


def register_algo(db):
    try:
        registry = MLRegistry(db=db)  # create ML registry
        # Random Forest classifier
        rf = RandomForestClassifier()
        # add to ML registry
        registry.add_algorithm(endpoint_name="income_classifier",
                               algorithm_object=rf,
                               algorithm_name="random forest",
                               algorithm_status="production",
                               algorithm_version="0.0.1",
                               owner="Piotr",
                               algorithm_description="Random Forest with simple pre- and post-processing",
                               algorithm_code=inspect.getsource(RandomForestClassifier))

        et = ExtraTreesClassifier()
        registry.add_algorithm(endpoint_name="income_classifier",
                               algorithm_object=et,
                               algorithm_name="extra trees",
                               algorithm_status="testing",
                               algorithm_version="0.0.1",
                               owner="Piotr",
                               algorithm_description="Extra Trees with simple pre- and post-processing",
                               algorithm_code=inspect.getsource(ExtraTreesClassifier)
                               )

        return registry

    except Exception as e:
        print("Exception while loading the algorithms to the registry,", str(e))
