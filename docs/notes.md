# Project setup notes

Initialize PIPENV dependency manager (Onetime time task per project):
`pipenv install`

Activate Virtual enviornment:
`pipenv shell`

Adding a new Package
`pipenv install pytest --dev`

Launch API (local dev)
`cd app && ./run.sh`

Health checks
`curl http://localhost:<port>/healthz`
`curl http://localhost:<port>/readyz`

Deploy Modal compute (optional)
`pip install modal && modal deploy app/ggt/modal_app.py`


`docker run --name myadmin -d -e PMA_HOST=wh-mobile-test-1.clwbkkblucao.us-east-1.rds.amazonaws.com -p 8080:80 phpmyadmin/phpmyadmin`

State Machine for test_samples

inform_status
`ENUM('pending_notification', 'attempted_notification', 'acknowledged_notification', 'use_group_settings')`

consultation_status
`ENUM('not_required', 'required', 'completed')`

status
`ENUM('test_in_progress', 'test_completed', 'ready_to_tx', 'pending_tx', 'with_lab', 'lab_result_received', 'attempted_notification', 'notification_acknowledged', 'attempted_consultation', 'consultation_in_progress', 'consultation_completed', 'record_locked')`

State Machine for Appointments

status
`ENUM('scheduled', 'checked_in', 'test_in_progress', 'test_completed', 'record_locked')`

`docker run --name myadmin-dev -d -e PMA_HOST=35.184.98.83 -p 8090:80 phpmyadmin/phpmyadmin`

`docker run --name myadmin-dev -d -e PMA_HOST=wh-mobile-test-1.clwbkkblucao.us-east-1.rds.amazonaws.com  -p 8090:80 phpmyadmin/phpmyadmin`

`docker run --name myadmin-dev -d -e PMA_HOST=mysqlserver_hostname  -p 8090:80 phpmyadmin/phpmyadmin`


GCP Storage

get a list of files from GS bucket, can be used for checking file errors e.g. 0 Byte files.
`gsutil ls -l gs://ggt-lab-reports-prod/ | sort -k 2 > gcp_reports_data.txt`

delete a file
`gsutil rm gs://ggt-lab-reports-prod/xxx.ext`


countobject in a GS bucket
`gsutil ls -lR gs://ggt-insurance-cards-prod | tail -n 1`


Local Processing
Start API Service:
`cd "/Users/suresh/Library/Mobile Documents/com~apple~CloudDocs/IO Technology/wellhealth/ggt-pfe-api/"`
`source "/Users/suresh/Library/Mobile Documents/com~apple~CloudDocs/IO Technology/wellhealth/ggt-pfe-api/venv/bin/activate"`
`./swith_env.sh prod`
`python3 app/main.py`

Start inbound file processing:
`cd "/Users/suresh/Library/Mobile Documents/com~apple~CloudDocs/IO Technology/wellhealth/ggt-pfe-api/"`
`./inbound-resulting.sh`




Make a copy of Prod DB to Dev
In Prod - From Cloud SQL "export" .sql file to GStorage
In Dev or Prod:
Launch cloudshell
`gsutil cp "gs://ggt-db-exports/Cloud_SQL_Export_2020-11-17 (15:49:58).sql" gs://ggt-dev-db-exports/`
In Dev "import" file to Cloud SQL instance



Aurora MYSQL Events:
Update Parameter Group to enable // Events = On, and restart nodes

Ref# https://medium.com/@buddhi.amigo/scheduled-events-with-aws-aurora-part-1-99f4e18d1658

Create Simple Event:
========================
DELIMITER ;;
CREATE EVENT `basic_scheduled_event` 
ON SCHEDULE EVERY 1 DAY
DO BEGIN
  # Add the business logic here.
END;
;;
DELIMITER ;

Create Threadsafe Event:
========================
DELIMITER ;;
CREATE EVENT `advance_scheduled_event` 
ON SCHEDULE EVERY 2 SECOND 
DO BEGIN
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION
  BEGIN
   DO RELEASE_LOCK('advance_scheduled_event');
  END;
  IF GET_LOCK('advance_scheduled_event', 0) THEN
   # Add the business logic here.
  END IF;
  DO RELEASE_LOCK('advance_scheduled_event');
END;
;;
DELIMITER ;

View Events:
========================
`SHOW EVENTS`

Delete Event:
========================
`DROP EVENT IF EXISTS basic_scheduled_event`
