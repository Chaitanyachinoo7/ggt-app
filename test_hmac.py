# python 3
import hmac
import hashlib
import base64
import ujson

nonce = 1

secret_key = 'Q1ZQZkdEamF0OW1zZWI1VEtjYjVGZU11WmVHM1kzRHI='
app_id = 'J873t7ZwJ6UvXGwz'

payload = {
    "Id": "01",
    "Ref_Date": "10/07/2020",
    "Msg": "Test",
    "Data": [
        {
           "Id": "01",
          "FirstName": "John",
          "LastName": "Doe",
          "SSN": "xxx-xx-6789 or 6789",
          "Birthdate": "08/25/1958",
          "Phone": "+1 (954) 702-7934",
          "Gender": "Female",
          "CollectedIn": "10/01/2020 14:30",
          "CollectorName": "Collector A",
          "PaymentMethod": "Insurance",
          "InsuranceName": "Insurance Company ABC",
          "InsurancePhoneNo": "+x (xxx) xxx-xxxx",
          "InsuranceAddress": "123 Blvd, City, State, ZipCode",
          "InsurancePolicyNo": "1234567890",
          "InsuranceGroup": "ABC123"
        }
    ]
}

payload_string = ujson.dumps(payload).encode('utf-8')

encoded_secret_key = secret_key.encode('utf-8')
b_secret_key = bytearray(encoded_secret_key)

digest = hmac.new(
    b_secret_key, 
    msg=payload_string,
    digestmod=hashlib.sha256
).digest()

signature = base64.b64encode(digest).decode()
print(signature)
