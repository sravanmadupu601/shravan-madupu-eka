import pytest

def test_health_readiness_info_and_dataset_catalog(client):
    assert client.get("/health").json() == {"status": "healthy"}
    assert client.get("/ready").status_code in {200, 503}
    info = client.get("/info").json()
    assert info["port"] == 8006
    assert info["frameworks"]["scikit_learn"] == "implemented"
    dataset_response = client.get("/ml/datasets")
    assert dataset_response.status_code == 200
    assert dataset_response.json()["datasets"][0]["dataset_id"] == "iris"
    assert dataset_response.json()["datasets"][0]["number_of_features"] == 4


def test_train_list_version_metadata_and_predict(client):
    trained = client.post(
        "/ml/train",
        json={"dataset_id": "iris", "target_column": "target", "algorithm": "logistic_regression", "random_state": 42},
    )
    if trained.status_code == 503:
        assert trained.json()["detail"]["code"] == "ML_FRAMEWORK_UNAVAILABLE"
        pytest.skip("Local scikit-learn runtime is unavailable in this environment.")
    assert trained.status_code == 201
    model = trained.json()["model"]
    assert model["version"] == "v1"
    assert set(model["metrics"]) == {"accuracy", "precision", "recall", "f1"}

    listed = client.get("/ml/models")
    details = client.get(f"/ml/models/{model['model_id']}/v1")
    prediction = client.post(
        "/ml/predict",
        json={
            "model_id": model["model_id"],
            "version": "v1",
            "features": [{"sepal length (cm)": 5.1, "sepal width (cm)": 3.5, "petal length (cm)": 1.4, "petal width (cm)": 0.2}],
        },
    )

    assert listed.status_code == 200
    assert details.status_code == 200
    assert prediction.status_code == 200
    assert prediction.json()["predictions"] == ["setosa"]


def test_training_and_prediction_errors_are_validated(client):
    bad_algorithm = client.post("/ml/train", json={"dataset_id": "iris", "target_column": "target", "algorithm": "arbitrary_import"})
    missing_dataset = client.post("/ml/train", json={"dataset_id": "missing", "target_column": "target"})
    missing_model = client.post("/ml/predict", json={"model_id": "unknown", "version": "v1", "features": [{"x": 1}]})

    assert bad_algorithm.status_code == 422
    assert missing_dataset.status_code == 404
    assert missing_model.status_code == 404


def test_csv_dataset_upload_and_detail(client):
    uploaded = client.post(
        "/ml/datasets",
        files={"file": ("tiny.csv", b"height,label\n1.2,a\n2.4,b\n", "text/csv")},
    )
    assert uploaded.status_code == 201
    dataset = uploaded.json()
    assert dataset["format"] == "csv"
    assert dataset["number_of_rows"] == 2
    assert dataset["number_of_features"] == 2
    detail = client.get(f"/ml/datasets/{dataset['dataset_id']}")
    assert detail.status_code == 200
    assert detail.json()["preview"][0]["height"] == 1.2


def test_training_and_prediction_parameter_validation(client):
    invalid_split = client.post(
        "/ml/train",
        json={"dataset_id": "iris", "target_column": "target", "test_size": 0.01},
    )
    invalid_version = client.post(
        "/ml/predict",
        json={"model_id": "iris-classifier", "version": "latest", "features": [{"x": 1}]},
    )
    assert invalid_split.status_code == 422
    assert invalid_version.status_code == 422
