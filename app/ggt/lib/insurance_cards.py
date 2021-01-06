# import ggt.lib.textract as textract
#
# from gcloud import storage
# import base64
# import ujson
#
# class InsuranceCard:
#     def __init__(self, img_path=None, b64=None):
#         """
#         Constructor to create an object of InsuranceCard class
#
#         :img_path: (optional) str - path of the Insurance Card image
#         :b64: (optional) str - base64 encoded string of the Insurance Card image
#         """
#
#         if b64:
#             with open("temp.png", "wb") as fh:
#                 fh.write(base64.decodebytes(b64))
#             img_path = "temp.png"
#
#         self.image_path = img_path
#         self._raw_ocr, self._form_ocr = self._perform_ocr()
#
#     def get_details(self):
#         """
#         Gets the required fields from the insurance cards and returns a dict
#         Currently extracts - provider, subsriber_name, subsriber_id, group_id
#         and effective_date
#         """
#         try:
#             member_name, member_id = self.get_subsriber_name_and_id()
#             if member_name.startswith("01"):
#                 member_name = member_name.split("01")[1].strip()
#         except:
#             member_name = member_id = None
#         if not member_id:
#             member_id = self.get_subscriber_id()
#
#         details = {
#             "provider": self.get_insurance_provider(),
#             "subsriber_name": member_name,
#             "subsriber_id": member_id,
#             "group_id": self.get_group_id(),
#             "effective_date": self.get_effective_date()
#         }
#
#         return details
#
#     def get_insurance_provider(self):
#         """
#         Get the insurance provider from the Image
#         """
#
#         # return self._raw_ocr.split("\n")[0].strip().replace(".", "").replace("'", "").replace('"', "")
#
#         providers = ["Anthem", "UnitedHealthcare", "BlueCross", "Blue Cross", "BlueCross BlueShield", "aetna"]
#         for provider in providers:
#             if provider.lower() in self._raw_ocr.lower():
#                 return provider
#
#     def get_subsriber_name_and_id(self):
#         """
#         Gets the subscriber name and ID from the Image
#         """
#
#         labels = ['MEMBER NAME', 'Subscriber Name:', 'Subscriber Name', 'MEMBER NAME:', 'Member Name', 'Subscriber', 'Member:', 'Member']
#         member_id = ''
#         for label in labels:
#             if label in self._form_ocr:
#                 member_name = self._form_ocr.get(label)
#                 if 'MEMBER ID' in member_name:
#                     member_name, member_id = member_name.split('MEMBER ID')
#                 elif 'Identification Number' in member_name:
#                         member_name, member_id = member_name.split('Identification Number')
#                 elif 'Member ID' in member_name:
#                         member_name, member_id = member_name.split('Member ID')
#                 else:
#                     pass
#
#                 return member_name.strip(), member_id.strip()
#         if self.get_insurance_provider() == "Anthem":
#             for line in self._raw_ocr.split("\n"):
#                 if line.isupper():
#                     return line.strip(), None
#         return self._get_member_name_from_raw_text(), None
#
#     def get_subscriber_id(self):
#         """
#         Gets the subscriber ID from the Image
#         """
#         if self.get_insurance_provider() == "aetna":
#             for line in self._raw_ocr.split("\n"):
#                 if line.startswith("ID"):
#                     return line.split("ID")[1].strip()
#
#         labels = ['MEMBER ID', 'Identification Number', 'Identification Number:', 'MEMBER ID:', 'Member ID', 'Member ID:', 'identification Number', 'ID#']
#         for label in labels:
#             if label in self._form_ocr:
#                 return self._form_ocr.get(label)
#
#         return self._get_member_id_from_raw_text()
#
#     def get_group_id(self):
#         """
#         Gets the Group ID from the Image
#         """
#
#         labels = ["Group", "Group Number", "Group:", "Group Number:", "Group No.", "Group No:", "Group #", "GRP", "Group No"]
#         for label in labels:
#             if label in self._form_ocr:
#                 return self._form_ocr.get(label)
#         return self._get_group_from_raw_text()
#
#     def get_effective_date(self):
#         """
#         Gets the Effective Date from the Image
#
#         """
#
#         labels = ["Effective", "Effective Date:", "Coverage Date:", "Effective Date", "Coverage Date", "Member Effective", "Member Effective:", 'Eff Dt']
#         for label in labels:
#             if label in self._form_ocr:
#                 return self._form_ocr.get(label)
#         return self._get_effective_date_from_raw_text()
#
#     def _get_member_name_from_raw_text(self):
#         """
#         Helper function to get supporting details from the Image
#         """
#         labels = ['MEMBER NAME', 'Subscriber Name:', 'Subscriber Name', 'MEMBER NAME:', 'Member Name', 'Subscriber', 'Member:', 'Member', "Name", "Name:", "NAME", "NAME:"]
#         for i, line in enumerate(self._raw_ocr.split("\n")):
#             if line in labels:
#                 name = self._raw_ocr.split("\n")[i + 1]
#                 if name.lower() in ['tdi']:
#                     return self._raw_ocr.split("\n")[i + 2]
#                 return name
#
#         for label in labels:
#             for i, line in enumerate(self._raw_ocr.split("\n")):
#                 if line.startswith(label):
#                     return line.split(label)[1].strip()
#
#     def _get_member_id_from_raw_text(self):
#         """
#         Helper function to get supporting details from the Image
#         """
#
#         labels = ['MEMBER ID', 'Identification Number', 'Identification Number:', 'MEMBER ID:', 'Member ID', 'Member ID:', 'identification Number', 'ID#']
#         for i, line in enumerate(self._raw_ocr.split("\n")):
#             if line in labels:
#                 id_ = self._raw_ocr.split("\n")[i + 1]
#                 if id_.lower() in ['dependent', 'dependents', 'dependent(s)']:
#                     return self._raw_ocr.split("\n")[i + 2]
#                 return id_
#
#     def _get_effective_date_from_raw_text(self):
#         """
#         Helper function to get supporting details from the Image
#         """
#
#         labels = ["Effective", "Effective Date:", "Coverage Date:", "Effective Date", "Coverage Date", "Member Effective", "Member Effective:", 'Eff Dt']
#         for i, line in enumerate(self._raw_ocr.split("\n")):
#             for label in labels:
#                 if label in line:
#                     return line.split(label)[1].strip()
#
#     def _get_group_from_raw_text(self):
#         """
#         Helper function to get supporting details from the Image
#         """
#         labels = ["GRP#", "GRP #", "GRP", "GRP:"]
#         for i, line in enumerate(self._raw_ocr.split("\n")):
#             for label in labels:
#                 if label.lower() in line.lower() and not 'rx' in line.lower():
#                     return line.lower().split(label.lower())[1].strip().replace(":", "").strip()
#
#     def _perform_ocr(self):
#         """
#         Helper function to call the OCR extractor
#         """
#
#         self._ocr_engine = textract.OCR(self.image_path)
#         return self._ocr_engine.get_text_lines(), self._ocr_engine.get_form()
#
#     def save_to_gcloud(self, file_name, bucket_name='ggt-insurance-card-textracts'):
#         """
#         Saves the response of an Insurance Card to the google cloud bucket specified.
#
#         :file_name: str - name of the file to be uploaded to the gs bucket
#         :bucket_name: str (optional) - name of the google cloud bucket
#         """
#
#         client = storage.Client()
#         bucket = client.get_bucket(bucket_name)
#         blob = bucket.blob(file_name)
#         with open('temp.json', 'w') as fp:
#             json.dump(self.get_details(), fp)
#         blob.upload_from_filename('temp.json')
