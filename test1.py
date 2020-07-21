'''
from faker import Faker

faker = Faker()

for x in range(765):
  print("{}\t{}\t{}".format(faker.first_name(), faker.last_name(), faker.date()))

'''

'''
import pysftp
host = "sftp.healthtrackrx.com"

username = "wellpay"
password = "9cTE3fh@8H"
cnopts = pysftp.CnOpts()
cnopts.hostkeys = None

with pysftp.Connection(host, username=username, password=password, cnopts=cnopts) as sftp:
  print ("Connection succesfully stablished ... ")


'''

