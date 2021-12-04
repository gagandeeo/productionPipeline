from fastapi.testclient import TestClient
from main import app, startup_event
import unittest

client = TestClient(app)
startup_event()


class EndpointTests(unittest.TestCase):

    def test_predict_view(self):
        input_data = {
            "data":
            {
                "age": 37,
                "workclass": "Private",
                "fnlwgt": 34146,
                "education": "HS-grad",
                "education-num": 9,
                "marital-status": "Married-civ-spouse",
                "occupation": "Craft-repair",
                "relationship": "Husband",
                "race": "White",
                "sex": "Male",
                "capital-gain": 0,
                "capital-loss": 0,
                "hours-per-week": 68,
                "native-country": "United-States"
            }
        }
        classifier = "income_classifier"
        classifier_url = f"/api/v1/{classifier}/predict/production"
        response = client.post(
            classifier_url,
            json=input_data
        )

        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(response["label"], "<=50K")
        self.assertTrue("request_id" in response)
        self.assertTrue("status" in response)


if __name__ == '__main__':
    unittest.main()
