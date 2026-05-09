# GGT API — Code Wiki

This repository contains a Python FastAPI backend (the “GGT API”) that supports multiple experiences (patient, portal/admin, clinical provider, contact center, billing, printers, vendor integration) plus background processors (email/sms queues, lab integration, reporting tasks). It can run as a normal ASGI service (Uvicorn/Gunicorn) or as an AWS Lambda function via Mangum.

## Contents

- [Architecture](#architecture)
- [Repository layout](#repository-layout)
- [Major modules](#major-modules)
- [Key classes & functions](#key-classes--functions)
- [Dependency relationships](#dependency-relationships)
- [Running the project](#running-the-project)

## Architecture

### High-level flow

1. An HTTP request enters the FastAPI app assembled in [main.py](file:///workspace/app/main.py#L33-L196).
2. FastAPI routes dispatch to “routers” in [ggt/routers](file:///workspace/app/ggt/routers).
3. Router handlers call workflow functions in [ggt/models/workflow_models](file:///workspace/app/ggt/models/workflow_models).
4. Workflow functions call “process models” (business processes) in [ggt/models/process_models](file:///workspace/app/ggt/models/process_models).
5. Process models read/write application data through “data models” in [ggt/models/data_models](file:///workspace/app/ggt/models/data_models), which execute SQL through a thin DB layer.
6. Process models also integrate with external services through adapters in [ggt/lib/adapters](file:///workspace/app/ggt/lib/adapters) (AWS, Auth0, Stripe, Twilio, SendGrid, etc.).

### Layering model (how code is organized)

- **Routers**: define API endpoints and bind authorization requirements; generally thin wrappers around workflow functions (example: [rt_patient.py](file:///workspace/app/ggt/routers/rt_patient.py#L56-L190)).
- **Workflow models**: “API-facing” orchestration that typically:
  - calls a single process function
  - normalizes the response with `x_response` / `y_response`
  - optionally applies caching (example: [verify_existing_patient](file:///workspace/app/ggt/models/workflow_models/patient_portal_flow.py#L20-L24))
- **Process models (`bp_*`)**: larger business processes; compose multiple data models/adapters and implement flows like scheduling, OTP verification, results retrieval, wallet pass creation, payments, etc. (example: [bp_initiate_verification_flow](file:///workspace/app/ggt/models/process_models/bp_patient_experience.py#L208-L220))
- **Data models**: direct access to persistent data (primarily MySQL) + object mapping; usually one file per domain aggregate (patients, appointments, schedules, reporting, etc.). (example: [patients.create_patient_record](file:///workspace/app/ggt/models/data_models/patients.py#L38-L101))
- **Adapters**: integration boundaries for external systems (Auth0, AWS, Stripe, Twilio, SendGrid, address validation, maps, etc.).

### Runtime variants

- **ASGI server**: runs the FastAPI app with Uvicorn in dev ([run.sh](file:///workspace/app/run.sh#L1)) or Gunicorn/Uvicorn in Docker ([Dockerfile](file:///workspace/Dockerfile#L1-L13)).
- **AWS Lambda**: exports `handler = Mangum(app=app)` ([main.py](file:///workspace/app/main.py#L195-L196)); Lambda container entrypoint is [lambda/Dockerfile](file:///workspace/lambda/Dockerfile#L1-L16).
- **Multi-port launchers**: convenience entrypoints that run the same app on different ports (likely for distinct processor deployments):
  - inbound processor: [launch1.py](file:///workspace/app/launch1.py#L1-L15)
  - SMS queue processor: [launch2.py](file:///workspace/app/launch2.py#L1-L15)
  - email queue processor: [launch3.py](file:///workspace/app/launch3.py#L1-L15)
  - outbound processor: [launch4.py](file:///workspace/app/launch4.py#L1-L15)

## Repository layout

- [app/](file:///workspace/app)
  - [main.py](file:///workspace/app/main.py): FastAPI application assembly and router registration
  - [run.sh](file:///workspace/app/run.sh): local dev run command
  - [ggt/](file:///workspace/app/ggt): core application package
    - [routers/](file:///workspace/app/ggt/routers): API surface (FastAPI `APIRouter`s)
    - [models/](file:///workspace/app/ggt/models): domain and business logic
      - [data_models/](file:///workspace/app/ggt/models/data_models): DB access layer + domain query helpers
      - [process_models/](file:///workspace/app/ggt/models/process_models): “bp_*” business processes
      - [workflow_models/](file:///workspace/app/ggt/models/workflow_models): workflow wrappers used by routers
    - [lib/](file:///workspace/app/ggt/lib): shared utilities (auth, db wrappers, response helpers, constants)
      - [adapters/](file:///workspace/app/ggt/lib/adapters): external system wrappers
    - [tasks/](file:///workspace/app/ggt/tasks): batch jobs / queue processors / HL7 integration tasks
    - [templates/](file:///workspace/app/ggt/templates): email templates and PDF templates
    - [configs/](file:///workspace/app/ggt/configs): environment pointers, log config, i18n, build configs
  - [tests/](file:///workspace/app/tests): pytest tests
- Root-level deployment/build tooling:
  - Main service container: [Dockerfile](file:///workspace/Dockerfile)
  - Lambda container: [lambda/Dockerfile](file:///workspace/lambda/Dockerfile)
  - CI/CD pipeline: [bitbucket-pipelines.yml](file:///workspace/bitbucket-pipelines.yml)
  - Test helper: [test.sh](file:///workspace/test.sh)
  - Dependency definition: [Pipfile](file:///workspace/Pipfile), frozen deps: [app/requirements.txt](file:///workspace/app/requirements.txt)

## Major modules

### app/main.py (application assembly)

- Creates FastAPI app with config-controlled docs paths ([main.py](file:///workspace/app/main.py#L33-L40)).
- Adds CORS + GZip middleware ([main.py](file:///workspace/app/main.py#L42-L54)).
- Registers the router set for each functional domain (patient, portal, billing, etc.) ([main.py](file:///workspace/app/main.py#L56-L181)).
- Exposes Lambda handler using Mangum ([main.py](file:///workspace/app/main.py#L195-L196)).

### ggt/configs (configuration and logging)

- `config_loader.py` loads an environment pointer file `config.yml` and then either:
  - returns the YAML directly when `env == 'LOCAL'`, or
  - loads a full config document from AWS Secrets Manager via `secret_name` ([config_loader.py](file:///workspace/app/ggt/configs/config_loader.py#L23-L34)).
- `log-config.yml` is a standard Python `logging.config.dictConfig` document used to configure console/file handlers ([log-config.yml](file:///workspace/app/ggt/configs/log-config.yml#L1-L27)).
- `lang_loader.py` loads `lang.yml` into a dictionary for localized messages ([lang_loader.py](file:///workspace/app/ggt/configs/lang_loader.py#L1-L16)).

Operationally, CI/CD copies a stage-specific pointer into `app/ggt/configs/config.yml` (example: [bitbucket-pipelines.yml](file:///workspace/bitbucket-pipelines.yml#L66-L68)).

### ggt/lib (shared utilities)

- **Configuration access**: `get_config_val(key)` reads nested config keys from the loaded config dict (example usage: `cfg('server.host')`) ([utils.py](file:///workspace/app/ggt/lib/utils.py#L27-L41)).
- **Response normalization**:
  - `x_response(...)`: wraps a single result into `{status: success|failed, ...}` ([utils.py](file:///workspace/app/ggt/lib/utils.py#L176-L195))
  - `y_response(...)`: wraps arrays/lists into `{status: success, results: [...]}` ([utils.py](file:///workspace/app/ggt/lib/utils.py#L197-L210))
- **Auth**: Auth0 JWT validation + permission enforcement in [auth.py](file:///workspace/app/ggt/lib/auth.py). Routers typically use FastAPI `Security(authorize_user, scopes=[...])` (example in [rt_patient.py](file:///workspace/app/ggt/routers/rt_patient.py#L59-L71)).
- **DB façade**: [db.py](file:///workspace/app/ggt/lib/db.py#L19-L52) re-exports a limited set of MySQL operations from the MySQL adapter:
  - inserts: `exec_insert`
  - updates/deletes: `exec_update`, `exec_delete`
  - reads: `read_row`, `read_rows`, plus `replica_read_row`, `replica_read_rows`

### ggt/lib/adapters (external integrations)

The adapters directory is the main boundary for external services:

- Auth0: [auth0_adapter.py](file:///workspace/app/ggt/lib/adapters/auth0_adapter.py), [auth0_config.py](file:///workspace/app/ggt/lib/adapters/auth0_config.py)
- MySQL: [mysql_adapter.py](file:///workspace/app/ggt/lib/adapters/mysql_adapter.py)
- AWS Secrets Manager: [secret_adaptor.py](file:///workspace/app/ggt/lib/adapters/secret_adaptor.py#L5-L17)
- AWS S3: [s3_adapter.py](file:///workspace/app/ggt/lib/adapters/s3_adapter.py)
- AWS SNS/SQS/Pinpoint: [sns_adapter.py](file:///workspace/app/ggt/lib/adapters/sns_adapter.py), [sqs_adapter.py](file:///workspace/app/ggt/lib/adapters/sqs_adapter.py), [pinpoint_adapter.py](file:///workspace/app/ggt/lib/adapters/pinpoint_adapter.py)
- AWS DynamoDB: [dynamo_adapter.py](file:///workspace/app/ggt/lib/adapters/dynamo_adapter.py)
- Stripe: [stripe_adapter.py](file:///workspace/app/ggt/lib/adapters/stripe_adapter.py)
- Twilio: [twilio_adapter.py](file:///workspace/app/ggt/lib/adapters/twilio_adapter.py)
- SendGrid: [sendgrid_adapter.py](file:///workspace/app/ggt/lib/adapters/sendgrid_adapter.py)
- Address validation: [smartystreets.py](file:///workspace/app/ggt/lib/adapters/smartystreets.py)
- Google integrations: [google_adapter.py](file:///workspace/app/ggt/lib/adapters/google_adapter.py), [google_maps.py](file:///workspace/app/ggt/lib/adapters/google_maps.py)

### ggt/models/data_models (persistence & domain queries)

Data models are mostly “SQL-first”: functions compose SQL strings and call DB primitives from [db.py](file:///workspace/app/ggt/lib/db.py#L19-L52). Example domains:

- Patients: [patients.py](file:///workspace/app/ggt/models/data_models/patients.py)
- Appointments: [appointments.py](file:///workspace/app/ggt/models/data_models/appointments.py)
- Scheduling: [schedules.py](file:///workspace/app/ggt/models/data_models/schedules.py)
- Reporting: [reporting.py](file:///workspace/app/ggt/models/data_models/reporting.py)
- Users/auth: [users.py](file:///workspace/app/ggt/models/data_models/users.py)
- HL7 utilities: [hl7.py](file:///workspace/app/ggt/models/data_models/hl7.py)

### ggt/models/process_models (business processes, “bp_*”)

These modules implement larger cross-domain flows and use both data models and adapters. A key example is [bp_patient_experience.py](file:///workspace/app/ggt/models/process_models/bp_patient_experience.py):

- screen flow sequencing (group-specific UX): [bp_get_screen_flow_seq](file:///workspace/app/ggt/models/process_models/bp_patient_experience.py#L158-L205)
- OTP/verification flows: [bp_initiate_verification_flow](file:///workspace/app/ggt/models/process_models/bp_patient_experience.py#L208-L220)
- “has appointments” check used for existing-patient verification: [bp_has_appointments](file:///workspace/app/ggt/models/process_models/bp_patient_experience.py#L758-L778)

### ggt/models/workflow_models (router-facing workflows)

Workflow models are frequently thin wrappers that return standardized responses. Example:

- [patient_portal_flow.verify_existing_patient](file:///workspace/app/ggt/models/workflow_models/patient_portal_flow.py#L20-L24) returns `x_response(bp_has_appointments(...))`.

### ggt/routers (HTTP API endpoints)

Routers define endpoint paths and authorization scopes. The router set included by [main.py](file:///workspace/app/main.py#L56-L181) maps to “apps”/roles:

- Patient API: [rt_patient.py](file:///workspace/app/ggt/routers/rt_patient.py)
- Portal/admin: [rt_portal.py](file:///workspace/app/ggt/routers/rt_portal.py)
- Clinical provider: [rt_clinical_provider.py](file:///workspace/app/ggt/routers/rt_clinical_provider.py)
- Care provider: [rt_care_provider.py](file:///workspace/app/ggt/routers/rt_care_provider.py)
- Contact center: [rt_contact_center.py](file:///workspace/app/ggt/routers/rt_contact_center.py)
- Billing: [rt_billing.py](file:///workspace/app/ggt/routers/rt_billing.py)
- Reporting: [rt_reporting.py](file:///workspace/app/ggt/routers/rt_reporting.py)
- Management: [rt_management.py](file:///workspace/app/ggt/routers/rt_management.py)
- Printer hub: [rt_printer_hub.py](file:///workspace/app/ggt/routers/rt_printer_hub.py)
- Vendor integration: [rt_vendor.py](file:///workspace/app/ggt/routers/rt_vendor.py)
- Payment integration: [rt_payment.py](file:///workspace/app/ggt/routers/rt_payment.py)
- Background task triggers: [rt_task.py](file:///workspace/app/ggt/routers/rt_task.py)
- Redirect helper: [rt_redirect.py](file:///workspace/app/ggt/routers/rt_redirect.py)

### ggt/tasks (batch jobs and integration tasks)

The [tasks/](file:///workspace/app/ggt/tasks) package contains standalone scripts that are typically run as cron jobs, queue processors, or administrative utilities (examples: SMS/email queue processors, HL7 inbound/outbound order processing, reporting notifications). These scripts often import process/data models and invoke them in a loop.

## Key classes & functions

### Application wiring

- FastAPI app instantiation and router registration: [main.py](file:///workspace/app/main.py#L33-L181)
- AWS Lambda handler: [main.py](file:///workspace/app/main.py#L195-L196)

### Configuration & logging

- Secrets-backed config load: [config_loader.cfg](file:///workspace/app/ggt/configs/config_loader.py#L23-L34)
- Config access helper: [get_config_val](file:///workspace/app/ggt/lib/utils.py#L27-L41)
- Language loading: [load_languages](file:///workspace/app/ggt/configs/lang_loader.py#L15-L16)

### Auth & permissions

- Auth0 JWT decoding and permission enforcement: [authorize_user](file:///workspace/app/ggt/lib/auth.py#L122-L141) and [authorize](file:///workspace/app/ggt/lib/auth.py#L143-L174)
- Vendor API key enforcement via header `x-api-key`: [get_vendor_api_key](file:///workspace/app/ggt/lib/auth.py#L176-L192)
- Permission enum used by routers: [PermissionsEnum](file:///workspace/app/ggt/models/data_models/data_types.py#L881-L940)

### Response shape helpers

- Single-object success/failure wrapper: [x_response](file:///workspace/app/ggt/lib/utils.py#L176-L195)
- Array success wrapper: [y_response](file:///workspace/app/ggt/lib/utils.py#L197-L210)
- Standard keys/constants: [constants.py](file:///workspace/app/ggt/lib/constants.py#L1-L11)

### Database access

- DB “public API” re-export layer: [db.py](file:///workspace/app/ggt/lib/db.py#L19-L52)
- MySQL adapter primitives (writer + read-replica): [mysql_adapter.py](file:///workspace/app/ggt/lib/adapters/mysql_adapter.py#L13-L35), [exec_insert](file:///workspace/app/ggt/lib/adapters/mysql_adapter.py#L80-L105), [replica_read_row](file:///workspace/app/ggt/lib/adapters/mysql_adapter.py#L251-L280)

### Patient verification example (end-to-end)

- HTTP endpoint: `/api/verify_existing_patient` in [rt_patient.py](file:///workspace/app/ggt/routers/rt_patient.py#L225-L230)
- Workflow: [verify_existing_patient](file:///workspace/app/ggt/models/workflow_models/patient_portal_flow.py#L20-L24)
- Process: [bp_has_appointments](file:///workspace/app/ggt/models/process_models/bp_patient_experience.py#L758-L778)
- Data model: appointment count query in [appointments.py](file:///workspace/app/ggt/models/data_models/appointments.py) (called by `get_appointment_count_by_phone_dob(...)` from the process layer)

## Dependency relationships

### Internal (package-level)

- `app/main.py`
  - imports constants: [constants.py](file:///workspace/app/ggt/lib/constants.py)
  - imports config access: [utils.get_config_val](file:///workspace/app/ggt/lib/utils.py#L27-L41)
  - imports routers: [ggt/routers](file:///workspace/app/ggt/routers)
- `ggt/routers/*`
  - depend on `ggt/lib/auth.py` for authorization hooks (example: [rt_patient.py](file:///workspace/app/ggt/routers/rt_patient.py#L1-L6))
  - depend on `ggt/models/workflow_models/*` for business logic dispatch (example: [rt_patient.py](file:///workspace/app/ggt/routers/rt_patient.py#L22-L48))
  - depend on Pydantic request/response models from [data_types.py](file:///workspace/app/ggt/models/data_models/data_types.py)
- `ggt/models/workflow_models/*`
  - depend on `ggt/models/process_models/*` for the real “work”
  - commonly use `ggt/lib/utils.py` response normalization
- `ggt/models/process_models/*`
  - depend on `ggt/models/data_models/*` for persistence
  - depend on `ggt/lib/adapters/*` for external services
- `ggt/models/data_models/*`
  - depend on DB façade [db.py](file:///workspace/app/ggt/lib/db.py#L19-L52) and utilities/logging
- `ggt/lib/db.py` → `ggt/lib/adapters/mysql_adapter.py` → `mysql.connector`

### External services (high-level)

From dependencies and adapters, the system integrates with:

- **Auth0** for JWT validation and permission enforcement (see [auth.py](file:///workspace/app/ggt/lib/auth.py#L143-L174)).
- **AWS Secrets Manager** for environment configuration (see [secret_adaptor.py](file:///workspace/app/ggt/lib/adapters/secret_adaptor.py#L5-L17)).
- **MySQL** for primary storage (see [mysql_adapter.py](file:///workspace/app/ggt/lib/adapters/mysql_adapter.py#L80-L333)).
- **AWS S3/SQS/SNS/Pinpoint/DynamoDB** via corresponding adapters.
- **Twilio** for OTP/phone interactions (imported by patient process flows, example: [bp_patient_experience.py](file:///workspace/app/ggt/models/process_models/bp_patient_experience.py#L22-L23)).
- **SendGrid** for email delivery; template rendering uses Jinja2 ([templates/email](file:///workspace/app/ggt/templates/email)).
- **Stripe** for payments.
- **Google Cloud Storage** and Google auth libraries (used for storage and token verification).

## Running the project

### Prerequisites

- Python 3.7+ (repo declares 3.7 in [Pipfile](file:///workspace/Pipfile#L58-L59); Docker base is Python 3.8 in [Dockerfile](file:///workspace/Dockerfile#L1)).
- `pipenv` (used by [test.sh](file:///workspace/test.sh#L12-L16) and the Dockerfile).
- Access to configuration secrets in AWS Secrets Manager, or a locally supplied config document compatible with `get_config_val(...)`.

### Configuration model (important)

- The application expects a configuration dict available as `ggt.configs.config_loader.cfg`.
- `app/ggt/configs/config.yml` is an environment pointer with two keys: `env` and `secret_name` (example: [config.yml](file:///workspace/app/ggt/configs/config.yml#L1-L2)).
- When `env != 'LOCAL'`, the config loader retrieves the full config JSON from AWS Secrets Manager using `secret_name` ([config_loader.py](file:///workspace/app/ggt/configs/config_loader.py#L23-L34)).

If you are running locally without AWS access, you will need to provide a full config document (matching the keys accessed by `get_config_val`) and ensure `config_loader.cfg` is populated accordingly.

### Local dev (Uvicorn)

1. Install dependencies:
   - `pipenv install --dev`
2. Ensure `app/ggt/configs/config.yml` points to a usable config (either AWS Secrets Manager-backed, or a local full config).
3. Run:
   - `cd app`
   - `./run.sh`
4. Open API docs:
   - The docs endpoints (`docs_url`, `redoc_url`) are read from config in [main.py](file:///workspace/app/main.py#L33-L40).

### Docker (service container)

Build:

- `docker build -t ggt-api .`

Run (example):

- `docker run --rm -p 8000:80 ggt-api`

The base image [Dockerfile](file:///workspace/Dockerfile#L1-L13) is the tiangolo Uvicorn+Gunicorn image, which listens on port `80` by default.

### AWS Lambda container

Build:

- `docker build -t ggt-api-lambda -f lambda/Dockerfile .`

This image runs the Lambda handler `app/main.handler` as defined in [lambda/Dockerfile](file:///workspace/lambda/Dockerfile#L16).

### Tests

The repo includes pytest tests under [app/tests](file:///workspace/app/tests). The helper script [test.sh](file:///workspace/test.sh#L12-L16) regenerates requirements, copies a test config pointer, and runs pytest.

Note: tests still require a working configuration and likely access to backing services (MySQL and other integrations), depending on the test suite’s scope.

