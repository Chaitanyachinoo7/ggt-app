#python 3
import hmac
import hashlib
import base64
import json

nonce = 1

secret_key = 'CVPfGDjat9mseb5TKcb5FeMuZeG3Y3Dr'
encoded=secret_key.encode('utf-8')
array=bytearray(encoded)
base64_secret_key = base64.b64encode(array)
print(base64_secret_key)

app_id = 'J873t7ZwJ6UvXGwz'



payload = {
    "Id":"01",
    "Ref_Date": "10/07/2020",
    "Msg": "Test",
    "Data":[
       {
          "Id": "01",
          "FirstName":"John",
          "LastName":"Doe",
          "SSN":"xxx-xx-6789 or 6789",
          "Birthdate":"08/25/1958",
          "Phone":"+1 (954) 702-7934",
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

payload_string = json.dumps(payload)
print(payload_string)


signature = hmac.new(bytes(base64_secret_key ), msg = bytes(payload_string , 'utf-8'), digestmod = hashlib.sha256).hexdigest()
print(signature)
encoded_signature=signature.encode('utf-8')
signature_array=bytearray(encoded_signature)
base64_signature = base64.b64encode(signature_array)
print(base64_signature)