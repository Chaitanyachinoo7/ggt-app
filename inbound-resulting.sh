#!/bin/bash
while true
do
	echo "Press [CTRL+C] to stop.."
    echo "process_inbound_lab_reports"
    curl -X POST "http://localhost:5000/api/task/process_inbound_lab_reports" -H  "accept: application/json" -d ""
    sleep 180
    echo "schedule_result_notifications_and_followups"
    curl -X POST "http://localhost:5000/api/task/schedule_result_notifications_and_followups" -H  "accept: application/json" -d ""
    echo "process_sms_queue"
    curl -X POST "http://localhost:5000/api/task/process_sms_queue" -H  "accept: application/json" -d ""
    echo "process_email_queue"
    curl -X POST "http://localhost:5000/api/task/process_email_queue" -H  "accept: application/json" -d ""
	echo "—————————————————————————————————————————"
done




