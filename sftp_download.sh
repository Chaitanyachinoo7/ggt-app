cd ~/ggt-tasks/downloads/Reports
sftp wellpay@healthtrackrx.com

i=1
while [ "$i" -ne 0 ]
do
  get -r *
  sleep 10
done