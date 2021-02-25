def run():
    import csv
    with open('temp/bcg_location_list.txt', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter='\t')
        for row in spamreader:
            print(', '.join(row))
            name = row[0]
            addr1= row[1]
            addr2= row[2]
            city= row[3]
            st= row[4] 
            zip= row[5]
            operator= row[7]
            phone_number= row[8]
            website= row[8]
            open_hours = row[11]
            add_to_locations(name, addr1, addr2, city, st, zip, operator, phone_number, website, open_hours)



def add_to_locations(name, addr1, addr2, city, st, zip, operator, phone_number, website, open_hours):
    import requests

    url = 'http://localhost:8888/api/portal/site-admin/create_location'
    payload = {
        "site_code": "GGT",
        "group_code": "_DEFAULT_",
        "name": name,
        "addr1": addr1,
        "addr2": addr2,
        "addr3": "",
        "city": city,
        "st": st,
        "zip": zip,
        "lat": 0,
        "lng": 0,
        "time_zone": "CST",
        "time_zone_offset": "-06:00",
        "test_type_offered": "oral",
        "status": "enabled",
        "type": "drive_thru",
        "billing_type": "client_bill",
        "collect_insurance_info": 0,
        "allow_insurance_skip": 1,
        "collect_upfront_payment": 0,
        "image_thumbnail": "",
        "accepts_bookings": True,
        "accepts_walkins": True,
        "operator": operator,
        "phone_number": phone_number,
        "website": website,
        "open_hours": open_hours,
        "is_external": True,
        "group_ids": [1],
        "service_ids": [1]
    }

    x = requests.post(url, data = payload)

    print(x.text)




run()
