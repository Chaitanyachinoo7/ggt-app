# Details

Date : 2020-07-20 00:57:21

Directory /Users/suresh/Library/Mobile Documents/com~apple~CloudDocs/IO Technology/wellhealth/ggt-pfe-api/app

Total : 55 files,  2486 codes, 459 comments, 773 blanks, all 3718 lines

[summary](results.md)

## Files
| filename | language | code | comment | blank | total |
| :--- | :--- | ---: | ---: | ---: | ---: |
| [app/__init__.py](/app/__init__.py) | Python | 1 | 0 | 1 | 2 |
| [app/ggt/__init__.py](/app/ggt/__init__.py) | Python | 1 | 0 | 1 | 2 |
| [app/ggt/configs/__init__.py](/app/ggt/configs/__init__.py) | Python | 1 | 0 | 1 | 2 |
| [app/ggt/configs/config-dev.yml](/app/ggt/configs/config-dev.yml) | YAML | 33 | 0 | 9 | 42 |
| [app/ggt/configs/config-prod.yml](/app/ggt/configs/config-prod.yml) | YAML | 34 | 0 | 9 | 43 |
| [app/ggt/configs/config-qa.yml](/app/ggt/configs/config-qa.yml) | YAML | 33 | 0 | 9 | 42 |
| [app/ggt/configs/config.yml](/app/ggt/configs/config.yml) | YAML | 36 | 0 | 9 | 45 |
| [app/ggt/configs/config_loader.py](/app/ggt/configs/config_loader.py) | Python | 17 | 2 | 8 | 27 |
| [app/ggt/configs/copy-content-config.yml](/app/ggt/configs/copy-content-config.yml) | YAML | 0 | 0 | 1 | 1 |
| [app/ggt/configs/log-config.yml](/app/ggt/configs/log-config.yml) | YAML | 28 | 0 | 4 | 32 |
| [app/ggt/lib/__init__.py](/app/ggt/lib/__init__.py) | Python | 1 | 0 | 1 | 2 |
| [app/ggt/lib/adapters/mysql_adapter.py](/app/ggt/lib/adapters/mysql_adapter.py) | Python | 108 | 3 | 37 | 148 |
| [app/ggt/lib/adapters/pinpoint_adapter.py](/app/ggt/lib/adapters/pinpoint_adapter.py) | Python | 44 | 21 | 13 | 78 |
| [app/ggt/lib/adapters/sendgrid_adapter.py](/app/ggt/lib/adapters/sendgrid_adapter.py) | Python | 42 | 0 | 11 | 53 |
| [app/ggt/lib/adapters/sns_adapter.py](/app/ggt/lib/adapters/sns_adapter.py) | Python | 28 | 0 | 10 | 38 |
| [app/ggt/lib/adapters/sqs_adapter.py](/app/ggt/lib/adapters/sqs_adapter.py) | Python | 33 | 0 | 10 | 43 |
| [app/ggt/lib/adapters/twilio_adapter.py](/app/ggt/lib/adapters/twilio_adapter.py) | Python | 24 | 0 | 11 | 35 |
| [app/ggt/lib/sms.py](/app/ggt/lib/sms.py) | Python | 3 | 0 | 3 | 6 |
| [app/ggt/lib/sys_log.py](/app/ggt/lib/sys_log.py) | Python | 12 | 6 | 9 | 27 |
| [app/ggt/lib/utils.py](/app/ggt/lib/utils.py) | Python | 94 | 6 | 29 | 129 |
| [app/ggt/models/__init__.py](/app/ggt/models/__init__.py) | Python | 1 | 0 | 1 | 2 |
| [app/ggt/models/data_models/appointments.py](/app/ggt/models/data_models/appointments.py) | Python | 65 | 58 | 18 | 141 |
| [app/ggt/models/data_models/data_types.py](/app/ggt/models/data_models/data_types.py) | Python | 96 | 0 | 42 | 138 |
| [app/ggt/models/data_models/locations.py](/app/ggt/models/data_models/locations.py) | Python | 18 | 6 | 7 | 31 |
| [app/ggt/models/data_models/patients.py](/app/ggt/models/data_models/patients.py) | Python | 51 | 6 | 16 | 73 |
| [app/ggt/models/data_models/providers.py](/app/ggt/models/data_models/providers.py) | Python | 10 | 6 | 6 | 22 |
| [app/ggt/models/data_models/questionnaires.py](/app/ggt/models/data_models/questionnaires.py) | Python | 38 | 15 | 13 | 66 |
| [app/ggt/models/data_models/schedules.py](/app/ggt/models/data_models/schedules.py) | Python | 92 | 57 | 40 | 189 |
| [app/ggt/models/data_models/signups.py](/app/ggt/models/data_models/signups.py) | Python | 51 | 6 | 25 | 82 |
| [app/ggt/models/data_models/test_results.py](/app/ggt/models/data_models/test_results.py) | Python | 82 | 80 | 19 | 181 |
| [app/ggt/models/process_models/bp_appointments.py](/app/ggt/models/process_models/bp_appointments.py) | Python | 164 | 19 | 36 | 219 |
| [app/ggt/models/process_models/bp_contact_center_experience.py](/app/ggt/models/process_models/bp_contact_center_experience.py) | Python | 15 | 3 | 6 | 24 |
| [app/ggt/models/process_models/bp_patient_experience.py](/app/ggt/models/process_models/bp_patient_experience.py) | Python | 337 | 23 | 88 | 448 |
| [app/ggt/models/process_models/bp_schedules.py](/app/ggt/models/process_models/bp_schedules.py) | Python | 102 | 7 | 30 | 139 |
| [app/ggt/models/workflow_models/admin_flows.py](/app/ggt/models/workflow_models/admin_flows.py) | Python | 0 | 0 | 1 | 1 |
| [app/ggt/models/workflow_models/clinical_provider_flow.py](/app/ggt/models/workflow_models/clinical_provider_flow.py) | Python | 0 | 0 | 1 | 1 |
| [app/ggt/models/workflow_models/contact_center_flows.py](/app/ggt/models/workflow_models/contact_center_flows.py) | Python | 33 | 8 | 10 | 51 |
| [app/ggt/models/workflow_models/patient_test_scheduling_flow.py](/app/ggt/models/workflow_models/patient_test_scheduling_flow.py) | Python | 168 | 5 | 36 | 209 |
| [app/ggt/models/workflow_models/provider_field_testing_flow.py](/app/ggt/models/workflow_models/provider_field_testing_flow.py) | Python | 47 | 9 | 16 | 72 |
| [app/ggt/models/workflow_models/test_site_admin_flow.py](/app/ggt/models/workflow_models/test_site_admin_flow.py) | Python | 0 | 0 | 1 | 1 |
| [app/ggt/routers/__init__.py](/app/ggt/routers/__init__.py) | Python | 1 | 0 | 1 | 2 |
| [app/ggt/routers/rt_contact_center.py](/app/ggt/routers/rt_contact_center.py) | Python | 28 | 0 | 10 | 38 |
| [app/ggt/routers/rt_patient.py](/app/ggt/routers/rt_patient.py) | Python | 51 | 4 | 26 | 81 |
| [app/ggt/routers/rt_provider.py](/app/ggt/routers/rt_provider.py) | Python | 42 | 0 | 12 | 54 |
| [app/ggt/routers/rt_redirect.py](/app/ggt/routers/rt_redirect.py) | Python | 6 | 0 | 4 | 10 |
| [app/ggt/routers/rt_task.py](/app/ggt/routers/rt_task.py) | Python | 36 | 1 | 14 | 51 |
| [app/ggt/tasks/call_queue_processor.py](/app/ggt/tasks/call_queue_processor.py) | Python | 2 | 0 | 0 | 2 |
| [app/ggt/tasks/email_queue_processor.py](/app/ggt/tasks/email_queue_processor.py) | Python | 2 | 0 | 0 | 2 |
| [app/ggt/tasks/inbound_lab_reports.py](/app/ggt/tasks/inbound_lab_reports.py) | Python | 156 | 23 | 53 | 232 |
| [app/ggt/tasks/outbound_lab_orders.py](/app/ggt/tasks/outbound_lab_orders.py) | Python | 2 | 0 | 0 | 2 |
| [app/ggt/tasks/report_notifications.py](/app/ggt/tasks/report_notifications.py) | Python | 74 | 72 | 26 | 172 |
| [app/ggt/tasks/sms_queue_processor.py](/app/ggt/tasks/sms_queue_processor.py) | Python | 24 | 8 | 6 | 38 |
| [app/main.py](/app/main.py) | Python | 61 | 5 | 21 | 87 |
| [app/requirements.txt](/app/requirements.txt) | pip requirements | 57 | 0 | 1 | 58 |
| [app/run.sh](/app/run.sh) | Shell Script | 1 | 0 | 1 | 2 |

[summary](results.md)