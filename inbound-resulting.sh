#!/bin/bash
while true
do
	echo "Press [CTRL+C] to stop.."
    curl -X POST "http://localhost:8000/api/task/process_inbound_lab_reports" -H  "accept: application/json" -d ""
    sleep 60
    curl -X POST "http://localhost:8000/api/task/schedule_result_notifications_and_followups" -H  "accept: application/json" -d ""
    curl -X POST "http://localhost:8000/api/task/process_sms_queue" -H  "accept: application/json" -d ""
    curl -X POST "http://localhost:8000/api/task/process_email_queue" -H  "accept: application/json" -d ""
	sleep 300
done




