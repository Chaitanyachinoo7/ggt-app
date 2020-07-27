'''
from faker import Faker

faker = Faker()

for x in range(765):
  print("{}\t{}\t{}".format(faker.first_name(), faker.last_name(), faker.date()))

'''
