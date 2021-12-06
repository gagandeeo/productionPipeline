import json
import pandas as pd
from sklearn.model_selection import train_test_split
import requests

df = pd.read_csv("https://raw.githubusercontent.com/pplonski/datasets-for-start/master/adult/data.csv", skipinitialspace=True)
x_cols = [c for c in df.columns if c != "income"]
X = df[x_cols]
y = df["income"]
endpoint_name = "income_classifier"
# print(df.head())

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1234)

for i in range(50):

    input_data = json.dumps({"data": X_test.iloc[i].to_dict()})
    target = y_test.iloc[i]
    r = requests.post(
        f"http://127.0.0.1:8000/api/v1/{endpoint_name}/predict/ab_testing",
        input_data
    )
    response = r.json()

    print(f"iter:{i} {response}")
    requests.put(
        f"http://127.0.0.1:8000/api/v1/mlrequests/{response['request_id']}",
        json.dumps({"feedback": target})
    )
