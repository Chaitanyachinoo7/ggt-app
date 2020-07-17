# Project setup notes

Initialize PIPENV dependency manager (Onetime time task per project):
`pipenv install`

Activate Virtual enviornment:
`pipenv shell`

Adding a new Package
`pipenv install pytest --dev`

Launch Server with
`uvicorn main:app --reload`


`docker run --name myadmin -d -e PMA_HOST=wh-mobile-test-1.clwbkkblucao.us-east-1.rds.amazonaws.com -p 8080:80 phpmyadmin/phpmyadmin`

State Machine for test_samples

inform_status
ENUM('pending_notification', 'attempted_notification', 'acknowledged_notification', 'use_group_settings')

consultation_status
ENUM('not_required', 'required', 'completed')

status
ENUM('test_in_progress', 'test_completed', 'ready_to_tx', 'pending_tx', 'with_lab', 'lab_result_received', 'attempted_notification', 'notification_acknowledged', 'attempted_consultation', 'consultation_in_progress', 'consultation_completed', 'record_locked')

State Machine for Appointments

status
ENUM('scheduled', 'checked_in', 'test_in_progress', 'test_completed', 'record_locked')

Host: sftp.healthtrackrx.com
Username: WellPay
Password: 9cTE3fh@8H