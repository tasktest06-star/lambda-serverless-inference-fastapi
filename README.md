# Serverless ML Inference with FastAPI, AWS Lambda, and CDK

Deploy a scikit-learn linear regression model behind a FastAPI endpoint on AWS Lambda (container image) with API Gateway, using AWS CDK.

During the Docker image build, `train_predict.py` trains a simple model on synthetic data and saves `model.pkl`. At runtime, `GET /predict` loads that artifact and returns a prediction.

## Architecture

```
Client → API Gateway → Lambda (Docker) → FastAPI (Mangum) → inference.predict() → model.pkl
```

Key pieces:

| Path | Role |
|------|------|
| `model_endpoint/docker/Dockerfile` | Lambda container image |
| `model_endpoint/docker/train_predict.py` | Train + save `model.pkl` at image build time |
| `model_endpoint/runtime/serving_api/serving_api.py` | FastAPI routes + Lambda handler |
| `model_endpoint/runtime/serving_api/custom_lambda_utils/scripts/inference.py` | Load model and run `predict` |
| `fastapi_model_serving/fastapi_model_serving_stack.py` | CDK stack (Lambda + API Gateway) |

## Prerequisites

- Python 3.10 (aligned with the Dockerfile base image)
- AWS CLI configured (`aws configure`) with permissions for CDK, Lambda, API Gateway, and ECR
- AWS CDK v2 (`npm install -g aws-cdk` or equivalent)
- Docker installed and running (`docker ps`)
- `make` (Git Bash / WSL on Windows)

Check versions:

```shell
python3 --version
cdk --version
docker --version
aws sts get-caller-identity
```

Default deploy region is `eu-west-1` (`DEPLOYMENT_REGION` in `cdk.json`). Change that value if you want another region. The stack and Dockerfile use **x86_64**.

## Quick start

From the repo root:

### 1. Prepare the environment

Creates `.venv` and installs root `requirements.txt` (CDK + tooling):

```shell
make prep
```

### 2. Package the Lambda API code

Builds `model_endpoint/docker/serving_api.tar.gz` from the serving runtime (FastAPI app, inference code, requirements):

```shell
make package_model
```

Re-run this whenever you change `serving_api.py`, `inference.py`, or `model_endpoint/runtime/serving_api/requirements.txt`.

### 3. Bootstrap CDK (first time only)

```shell
make cdk_bootstrap
```

### 4. Ensure Docker is running

```shell
docker ps
```

### 5. Deploy

```shell
make deploy
```

This builds the Docker image (installs deps, runs training to create `model.pkl`, sets the Lambda handler), pushes it, and deploys the CloudFormation stack. Expect roughly **5–10 minutes**.

When deploy finishes, copy the API Gateway URL from the stack **Outputs**.

## Call the API

### Browser / Swagger UI

1. Open the output URL — you should see `{"message":"Hello World"}` (cold starts may need a refresh).
2. Open `{endpoint_url}/docs` for the interactive Swagger UI.
3. Try `GET /predict` with a numeric `input_val` (for example `5.0`).

### curl

```shell
curl "https://<API_ID>.execute-api.<REGION>.amazonaws.com/prod/predict?input_val=5.0"
```

Example response:

```json
{"input":5.0,"prediction":14.978...}
```

### Python

```python
import requests

url = "https://<API_ID>.execute-api.<REGION>.amazonaws.com/prod/predict"
response = requests.get(url, params={"input_val": 5.0})
print(response.json())
```

## How the image is built

The Dockerfile roughly does:

1. Unpack `serving_api.tar.gz` into `${LAMBDA_TASK_ROOT}`
2. Copy `train_predict.py` into `${LAMBDA_TASK_ROOT}`
3. `pip install` from `requirements.txt` into `${LAMBDA_TASK_ROOT}`
4. Train and write `model.pkl` under `${LAMBDA_TASK_ROOT}`
5. Set `CMD` to `serving_api.lambda_handler`

Inference loads the same path:

```text
${LAMBDA_TASK_ROOT}/model.pkl
```

## Project layout

```text
.
├── app.py
├── cdk.json
├── Makefile
├── requirements.txt                 # local CDK / tooling deps
├── fastapi_model_serving/
│   └── fastapi_model_serving_stack.py
├── model_endpoint/
│   ├── docker/
│   │   ├── Dockerfile
│   │   ├── train_predict.py         # train at image build time
│   │   └── serving_api.tar.gz       # created by make package_model
│   └── runtime/
│       └── serving_api/
│           ├── serving_api.py       # FastAPI + Mangum
│           ├── requirements.txt     # runtime deps (fastapi, mangum, sklearn, ...)
│           └── custom_lambda_utils/
│               └── scripts/
│                   └── inference.py
└── scripts/
    └── setup.sh
```

## Useful Make targets

| Command | Description |
|---------|-------------|
| `make prep` | Create venv and install deps |
| `make package_model` | Build `serving_api.tar.gz` |
| `make cdk_bootstrap` | First-time CDK bootstrap |
| `make synth` | Synthesize CloudFormation |
| `make deploy` | Build image and deploy stack |
| `make destroy` | Tear down the stack |
| `make clean` | Remove `.venv` and `cdk.out` |

Full flow after a code change:

```shell
make package_model
make deploy
```

## Clean up

```shell
make destroy
```

## Troubleshooting

- **Docker / ECR login issues on Mac** — if `docker login` to ECR fails with credential store errors, set `credsStore` to `osxkeychain` in `~/.docker/config.json`.
- **Cold start** — first request after deploy or idle time can be slow; retry once or twice.
- **Stale API code in the image** — you changed Python under `runtime/serving_api` but forgot `make package_model` before `make deploy`.
- **Train step fails in Docker with `ModuleNotFoundError`** — the Dockerfile uses `PYTHONPATH=${LAMBDA_TASK_ROOT}` when running `train_predict.py` so packages installed with `--target` are visible.
- **Windows** — run Make targets from Git Bash or WSL so `scripts/setup.sh` and `.venv/bin/activate` work.
