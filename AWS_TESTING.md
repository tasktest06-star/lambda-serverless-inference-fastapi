# Test Execution on AWS

After `cdk deploy` succeeds, use this guide to verify the live endpoint (API Gateway → Lambda → FastAPI → model).

## 1. Get the endpoint URL

### From CDK / CloudFormation

1. Open **AWS Console** → **CloudFormation** → your stack (e.g. `FastapiModelServingStack` or `FastapiModelServingStacktsStack`).
2. Open the **Outputs** tab.
3. Copy the API Gateway URL (looks like):

```text
https://<api-id>.execute-api.<region>.amazonaws.com/prod/
```

### From CLI

```bash
aws cloudformation describe-stacks \
  --stack-name FastapiModelServingStack \
  --query "Stacks[0].Outputs" \
  --output table
```

Use your real stack name if it differs (e.g. `FastapiModelServingStacktsStack`).

Set a helper variable:

```bash
export API_URL="https://<api-id>.execute-api.<region>.amazonaws.com/prod"
```

## 2. Smoke test — health / root

```bash
curl -s "$API_URL/"
```

Expected:

```json
{"message":"Hello World"}
```

**Note:** First request after deploy (or after idle time) may be slow because of Lambda cold start. Retry once or twice if you get a timeout or 502.

## 3. Test inference — `/predict`

The model expects a numeric query param `input_val`.

```bash
curl -s "$API_URL/predict?input_val=5.0"
```

Expected shape:

```json
{"input":5.0,"prediction":14.978...}
```

Try a few values:

```bash
curl -s "$API_URL/predict?input_val=0"
curl -s "$API_URL/predict?input_val=2.5"
curl -s "$API_URL/predict?input_val=10"
```

### Browser

Open:

```text
https://<api-id>.execute-api.<region>.amazonaws.com/prod/predict?input_val=5.0
```

### Swagger UI (interactive)

Open:

```text
https://<api-id>.execute-api.<region>.amazonaws.com/prod/docs
```

1. Expand **GET /predict**.
2. Click **Try it out**.
3. Enter `input_val` (e.g. `5.0`).
4. Click **Execute**.
5. Confirm status `200` and a JSON body with `input` and `prediction`.

Also try **GET /** to confirm the hello-world route.

## 4. Test from Python

```python
import requests

API_URL = "https://<api-id>.execute-api.<region>.amazonaws.com/prod"

# Root
print(requests.get(f"{API_URL}/").json())

# Predict
r = requests.get(f"{API_URL}/predict", params={"input_val": 5.0})
print(r.status_code, r.json())
```

## 5. Test from AWS Console (optional)

### API Gateway

1. **API Gateway** → your REST API → **Stages** → `prod`.
2. Copy the **Invoke URL**.
3. Use curl/browser as above, or **Resources** → method → **Test** (if available for the proxy resource).

### Lambda

1. **Lambda** → function `fastapi_model_serving_endpoint_docker` (or your function name).
2. **Test** tab → create an event that mimics API Gateway HTTP API / REST proxy for `GET /predict?input_val=5.0`.

Simpler path for day-to-day checks: call the API Gateway URL with curl (section 3). Console Lambda test events are more verbose to craft for FastAPI + Mangum.

## 6. Check logs if something fails

```bash
aws logs tail /aws/lambda/fastapi_model_serving_endpoint_docker --follow
```

Or in the console: **CloudWatch** → **Log groups** → `/aws/lambda/fastapi_model_serving_endpoint_docker`.

Look for:

- Import errors (`ModuleNotFoundError`, missing `model.pkl`)
- FastAPI / Mangum exceptions
- Timeouts (increase memory/timeout in the CDK stack if needed)

## 7. Pass / fail checklist

| Check | How | Pass criteria |
|-------|-----|----------------|
| Stack deployed | CloudFormation status | `CREATE_COMPLETE` or `UPDATE_COMPLETE` |
| Root route | `GET /` | `{"message":"Hello World"}` |
| Predict route | `GET /predict?input_val=5.0` | HTTP 200, JSON with `prediction` number |
| Docs | Open `/docs` | Swagger UI loads |
| Bad input | `GET /predict?input_val=abc` | HTTP 422 validation error from FastAPI |

## 8. Common issues

| Symptom | Likely cause | What to do |
|---------|--------------|------------|
| 403 / missing auth | Wrong URL or stage | Use Outputs URL ending in `/prod` |
| 502 / timeout on first call | Cold start | Retry; check Lambda timeout (60s in stack) |
| 404 on `/predict` | Stale image or wrong path | Confirm URL includes `/prod/predict`; redeploy after `make package_model` |
| 500 on `/predict` | Missing `model.pkl` or import error | Check CloudWatch logs; rebuild image so train step ran |
| Empty / wrong response | Old deployment | `cdk deploy` again after packaging |

## 9. Clean up when done

```bash
cdk destroy
# or
make destroy
```
