# Runbook — GGT API

This runbook walks through running the GGT API locally and in Docker, plus how to run tests. It also includes common troubleshooting for issues observed in this repository.

## Quick facts

- Main entrypoint: [app/main.py](file:///workspace/app/main.py)
- Local dev command: [app/run.sh](file:///workspace/app/run.sh)
- Primary app package: [app/ggt](file:///workspace/app/ggt)
- Config loader: [app/ggt/configs/config_loader.py](file:///workspace/app/ggt/configs/config_loader.py)
- DB adapter: [app/ggt/lib/adapters/mysql_adapter.py](file:///workspace/app/ggt/lib/adapters/mysql_adapter.py)
- DB schema dump: [docs/db_init.sql](file:///workspace/docs/db_init.sql)

## Prerequisites

### Local machine tools

- Python 3.7+ (repo declares 3.7 in [Pipfile](file:///workspace/Pipfile#L58-L59))
- pip and virtualenv tooling (recommended: `pipenv`, used by [test.sh](file:///workspace/test.sh))
- Docker (optional, for containerized runs)

### External dependencies (required for real end-to-end runs)

This backend is not fully self-contained. Depending on which endpoints you hit, it may require:

- MySQL database (schema at [docs/db_init.sql](file:///workspace/docs/db_init.sql))
- AWS Secrets Manager (the default configuration model) via [secret_adaptor.py](file:///workspace/app/ggt/lib/adapters/secret_adaptor.py#L5-L17)
- Auth0 (JWT verification) via [auth.py](file:///workspace/app/ggt/lib/auth.py)
- Optional integrations: S3/SQS/SNS/Pinpoint/DynamoDB, Twilio, SendGrid, Stripe, Google Cloud Storage

## Configuration model (critical)

The app reads configuration from a global dict `cfg` loaded at import-time in [config_loader.py](file:///workspace/app/ggt/configs/config_loader.py#L23-L36).

`app/ggt/configs/config.yml` is expected to exist and contains:

- `env`
- `secret_name`

Behavior:

- If `env == 'LOCAL'`: `cfg` is set to the YAML content of `config.yml` (meaning `config.yml` must contain the full runtime config).
- Else: `cfg` is loaded from AWS Secrets Manager using `secret_name` (meaning AWS credentials + region + secret must exist).

The repo includes `config-*.yml` files, but they are only pointers (env + secret_name), not full configs (example: [config-dev.yml](file:///workspace/app/ggt/configs/config-dev.yml#L1-L2)).

## Run modes

### Mode A — Local run using AWS Secrets Manager (closest to production behavior)

Use this if you have AWS credentials and the configured secrets already exist.

1. Install dependencies

   From repo root:

   ```bash
   pip install pipenv
   pipenv install --dev
   ```

2. Select environment pointer

   Copy the desired pointer file into `config.yml`:

   - dev: [config-dev.yml](file:///workspace/app/ggt/configs/config-dev.yml)
   - dev2: [config-dev2.yml](file:///workspace/app/ggt/configs/config-dev2.yml)
   - qa: [config-qa.yml](file:///workspace/app/ggt/configs/config-qa.yml)
   - prod: [config-prod.yml](file:///workspace/app/ggt/configs/config-prod.yml)

   Example:

   ```bash
   cp app/ggt/configs/config-dev.yml app/ggt/configs/config.yml
   ```

3. Provide AWS environment variables

   You need credentials with permission to read the configured secret:

   ```bash
   export AWS_ACCESS_KEY_ID=...
   export AWS_SECRET_ACCESS_KEY=...
   export AWS_REGION=us-east-2
   ```

4. Run the API

   ```bash
   cd app
   pipenv run ./run.sh
   ```

5. Verify it started

   - The API docs paths are config-driven: `docs_url` and `redoc_url` are read from config in [main.py](file:///workspace/app/main.py#L33-L40).
   - If docs are enabled in your config, open the docs URL in the console output.

### Mode B — Local run without AWS (full local config file)

Use this if you do not have AWS Secrets access. This requires creating a full config document locally.

1. Install dependencies

   ```bash
   pip install pipenv
   pipenv install --dev
   ```

2. Create a full local `config.yml`

   Replace `app/ggt/configs/config.yml` content with:

   - `env: LOCAL`
   - plus all keys referenced by the app (examples from code):
     - `server.host`, `server.port` ([main.py](file:///workspace/app/main.py#L187-L191))
     - `origins`, `docs.swagger_url`, `docs.redoc_url` ([main.py](file:///workspace/app/main.py#L38-L49))
     - `databases.mysql.*` ([mysql_adapter.py](file:///workspace/app/ggt/lib/adapters/mysql_adapter.py#L13-L35))
     - `vendors.auth0.*` ([auth.py](file:///workspace/app/ggt/lib/auth.py#L31-L33), [auth.py](file:///workspace/app/ggt/lib/auth.py#L152-L156))
     - `security.ggv_secret` ([utils.get_ggv_tokens](file:///workspace/app/ggt/lib/utils.py#L287-L300))

   Minimal starter keys that are typically necessary just to boot the service:

   - server host/port
   - docs urls (or set them to null/empty)
   - origins (or a permissive list for dev)
   - mysql connection info
   - auth0 domain/algorithms/audience (or adjust for anonymous-only endpoints)

3. Run the API

   ```bash
   cd app
   pipenv run ./run.sh
   ```

4. Verify with an anonymous endpoint

   Many patient endpoints are declared anonymous in [rt_patient.py](file:///workspace/app/ggt/routers/rt_patient.py#L59-L71) via `Security(authorize_user, scopes=[PermissionsEnum.ANONYMOUS])`.

   If you still hit auth failures, your config may be missing required keys used by [auth.py](file:///workspace/app/ggt/lib/auth.py) even for anonymous flows (see troubleshooting).

### Mode C — Docker run (service container)

Use this if you want to run without installing Python locally.

1. Build the image

   ```bash
   docker build -t ggt-api .
   ```

2. Provide configuration at runtime

   The container still needs `app/ggt/configs/config.yml` and access to secrets (Mode A) or a full local config (Mode B).

   For Mode A (AWS secrets), pass AWS env vars:

   ```bash
   docker run --rm -p 8000:80 \
     -e AWS_ACCESS_KEY_ID=... \
     -e AWS_SECRET_ACCESS_KEY=... \
     -e AWS_REGION=us-east-2 \
     ggt-api
   ```

3. Verify it started

   The base image in [Dockerfile](file:///workspace/Dockerfile#L1-L13) runs Gunicorn/Uvicorn on port `80`, so `-p 8000:80` exposes it at `http://localhost:8000`.

### Mode D — AWS Lambda container (for deployment parity)

This repo includes a Lambda container setup:

- [lambda/Dockerfile](file:///workspace/lambda/Dockerfile#L1-L16)
- handler: `app/main.handler` ([main.py](file:///workspace/app/main.py#L195-L196))

Build:

```bash
docker build -t ggt-api-lambda -f lambda/Dockerfile .
```

Running a Lambda container locally typically requires AWS’s Lambda Runtime Interface Emulator; this repo does not include that wiring by default, so treat this mode primarily as a deployment artifact unless you add local RIE support.

## Database setup (MySQL)

1. Provision a MySQL instance (local container or cloud-managed).
2. Initialize schema:

   - Use [docs/db_init.sql](file:///workspace/docs/db_init.sql) as the baseline schema dump.

3. Set database config keys (used by [mysql_adapter.py](file:///workspace/app/ggt/lib/adapters/mysql_adapter.py#L13-L35)):

- `databases.mysql.username`
- `databases.mysql.password`
- `databases.mysql.host`
- `databases.mysql.read_replica_host` (can be same as host for local)
- `databases.mysql.db`

## Running tests

### Pytest suite

The helper script [test.sh](file:///workspace/test.sh#L12-L16) does:

- regenerates requirements from pipenv
- copies `config-TEST.yml` pointer into `config.yml`
- runs `pytest`

Run:

```bash
./test.sh
```

Notes:

- `config-TEST.yml` is a pointer only ([config-TEST.yml](file:///workspace/app/ggt/configs/config-TEST.yml#L1-L2)), so tests will still require working secrets access or you must replace it with a full local test config.
- Many tests may require reachable databases and external integrations.

### Unit tests (unittest)

See [app/tests/ggt_tests/README.md](file:///workspace/app/tests/ggt_tests/README.md#L30-L44):

```bash
export PYTHONPATH="${PYTHONPATH}:/path/to/your/repo/app"
python -m unittest discover -v app/tests/ggt_tests
```

## Common troubleshooting

### 1) `ModuleNotFoundError: No module named 'uvicorn'` (or other packages)

Cause:

- Dependencies are not installed in your environment.

Fix:

- Use pipenv:

  ```bash
  pip install pipenv
  pipenv install --dev
  cd app
  pipenv run ./run.sh
  ```

Or install exported requirements:

```bash
pip install -r app/requirements.txt
```

### 2) App crashes on import with missing config keys (`KeyError` in `get_config_val`)

Cause:

- `config.yml` is a pointer file (env + secret_name) but you are running in `LOCAL` mode, or secrets were not loaded successfully.
- `get_config_val()` assumes keys exist and does not guard against missing entries ([utils.py](file:///workspace/app/ggt/lib/utils.py#L27-L41)).

Fix:

- For AWS-backed config: ensure AWS credentials and region are set and the secret exists.
- For offline local: make `config.yml` a full config document (Mode B).

### 3) AWS secrets errors (`NoRegionError`, `UnrecognizedClientException`, `AccessDeniedException`, missing secret)

Cause:

- AWS credentials/region not set, invalid, or lacking permission; secret name not present.

Fix:

- Set region:

  ```bash
  export AWS_REGION=us-east-2
  ```

- Verify credentials and IAM policy can call `secretsmanager:GetSecretValue` for the `secret_name` in [config.yml](file:///workspace/app/ggt/configs/config.yml).

### 4) MySQL connection failures

Symptoms:

- `mysql.connector` errors: connection refused, access denied, unknown database, etc.

Cause:

- DB host/port not reachable, wrong credentials, schema not loaded.

Fix:

- Confirm config keys used by [mysql_adapter.py](file:///workspace/app/ggt/lib/adapters/mysql_adapter.py#L13-L35).
- Import schema from [docs/db_init.sql](file:///workspace/docs/db_init.sql).
- For local dev, set `databases.mysql.read_replica_host` equal to `databases.mysql.host`.

### 5) Auth failures (`401 Not Authorized`) even for endpoints you expect to be public

Cause:

- While many endpoints use `PermissionsEnum.ANONYMOUS` ([rt_patient.py](file:///workspace/app/ggt/routers/rt_patient.py#L59-L71)), the auth module still imports and may evaluate config keys for Auth0 during module import or when handling non-anonymous endpoints.

Fix:

- Ensure Auth0 config keys exist:
  - `vendors.auth0.auth0_domain`
  - `vendors.auth0.algorithms`
  - `vendors.auth0.api_audience`

### 6) Docs endpoints not visible

Cause:

- `docs_url` / `redoc_url` are config-driven ([main.py](file:///workspace/app/main.py#L38-L40)). They may be disabled via config.

Fix:

- In your config, set `docs.swagger_url` and `docs.redoc_url` to desired paths (e.g., `/docs`, `/redoc`).

### 7) Syntax warnings about invalid escape sequences

Symptoms:

- Warnings around `\&`, `\s`, `\/` in HL7 and regex strings.

Impact:

- Typically not fatal today, but can break in future Python versions.

Fix:

- Convert to raw strings or escape backslashes in affected files (examples in [app/ggt/models/data_models/hl7.py](file:///workspace/app/ggt/models/data_models/hl7.py) and [bp_patient_experience.py](file:///workspace/app/ggt/models/process_models/bp_patient_experience.py)).

## Recommended “first successful boot” checklist

- Install dependencies with pipenv
- Choose Mode A (AWS secrets) if you have access, otherwise create a full local config (Mode B)
- Point DB config to a reachable MySQL instance initialized with [docs/db_init.sql](file:///workspace/docs/db_init.sql)
- Start server with [run.sh](file:///workspace/app/run.sh)
- Validate a simple anonymous endpoint from [rt_patient.py](file:///workspace/app/ggt/routers/rt_patient.py)

