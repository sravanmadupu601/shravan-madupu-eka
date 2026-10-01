# EKA ML Service (Block 7)

Block 7 owns traditional local machine-learning lifecycles: dataset cataloging, preprocessing, feature selection, training, evaluation, model artifact persistence/versioning, loading, and prediction. It is not the embedding, RAG, agent, or MCP service.

## Architecture

```text
Dataset (built-in Iris or local CSV)
	-> validate target/features
	-> deterministic train/test split
	-> numeric imputation/scaling + categorical imputation/encoding
	-> Logistic Regression or Random Forest
	-> accuracy, weighted precision/recall/F1
	-> local joblib artifact + JSON metadata (v1, v2, ...)
	-> exact-version prediction
```

FastAPI routes call application use cases. Dataset/model repositories, sklearn preprocessing/training/evaluation, and local storage are infrastructure adapters. Domain metadata and repository/trainer ports do not import FastAPI or scikit-learn.

## Datasets

`iris` is available from scikit-learn's bundled dataset loader and requires no network access. Local CSV uploads are assigned generated `csv-<uuid>` IDs and stored under `DATASET_STORAGE_PATH`; callers cannot supply a filesystem path. Training requires an explicit target column. CSV columns are candidate features until training selects the target. Dataset metadata reports ID, name, version, format, row/feature counts, columns, optional target, and creation time.

Uploaded CSV datasets use version `1` and are immutable through the API; uploading the same content creates a new generated dataset ID rather than overwriting an existing file.

## Preprocessing and feature engineering

Feature selection is explicit and reproducible. The sklearn adapter identifies numeric and categorical columns from training data. Numeric features use median imputation and standard scaling; categorical features use most-frequent imputation and one-hot encoding with unknown categories ignored. These transformations are part of the persisted sklearn pipeline and are recorded in metadata.

## Training and evaluation

`POST /ml/train` synchronously trains one small local classification model. Allowed algorithms are `logistic_regression` and `random_forest`; arbitrary imports/classes are rejected. A deterministic `random_state` is recorded and stratified splitting is used. Evaluation metrics are calculated from the held-out split: accuracy and weighted precision, recall, and F1.

Training is intentionally synchronous and intended for small learning datasets; no job queue or distributed training is present.

## Model registry and versioning

Trusted local artifacts are stored beneath `MODEL_STORAGE_PATH/<model_id>/vN/` as `model.joblib`, with a sibling `metadata.json`. Versions increment without overwriting existing versions. API users provide only model ID and explicit version, never a filesystem path. Joblib artifacts are executable Python serialization and must only be loaded from this trusted service-owned local registry; do not copy untrusted artifacts into it.

## Framework status

- scikit-learn: implemented end-to-end for the two allowlisted classifiers.
- PyTorch: architecture extension point only; no trainer, model, or dependency in this service.
- TensorFlow: architecture extension point only; no trainer, model, or dependency.
- MLflow: not included.

The scikit-learn workflow does not duplicate Block 3 Sentence Transformer embeddings. Block 7 is for traditional ML/deep learning lifecycle work.

## Configuration

Copy `.env.example` to `.env` for overrides. Defaults are local:

```dotenv
ML_SERVICE_PORT=8006
DATASET_STORAGE_PATH=../../data/datasets
MODEL_STORAGE_PATH=./models
DEFAULT_TEST_SIZE=0.2
DEFAULT_RANDOM_STATE=42
```

## API

- `GET /health`, `GET /ready`, `GET /info`
- `GET /ml/datasets`, `GET /ml/datasets/{dataset_id}`
- `POST /ml/datasets` (CSV multipart upload)
- `POST /ml/train`
- `GET /ml/models`, `GET /ml/models/{model_id}`, `GET /ml/models/{model_id}/{version}`
- `POST /ml/predict`

Example training request:

```json
{
	"dataset_id": "iris",
	"target_column": "target",
	"algorithm": "logistic_regression",
	"test_size": 0.2,
	"random_state": 42
}
```

Example prediction request:

```json
{
	"model_id": "iris-classifier",
	"version": "v1",
	"features": [
		{"sepal length (cm)": 5.1, "sepal width (cm)": 3.5, "petal length (cm)": 1.4, "petal width (cm)": 0.2}
	]
}
```

## Run locally on Windows

```powershell
cd services/ml-service
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8006
```

Run tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

The root launcher also starts this service on port `8006`. Block 7 uses local files only and requires no database, model download, cloud credential, or external service.
