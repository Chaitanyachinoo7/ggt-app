# import boto3
#
# class OCR:
#     def __init__(self, file_path):
#         """
#         Constructor to create an OCR class object
#
#         :file_path: str - path to the image file
#         """
#
#         self.file_path = file_path
#         self.client = boto3.client('textract')
#         self.ocr_data = self.extract_text()
#
#     def extract_text(self):
#         """
#         Uses Amazon Textract to perform OCR on an image and returns the default
#         response
#         """
#
#         with open(self.file_path, 'rb') as document:
#             img = bytearray(document.read())
#
#         response = self.client.analyze_document(
#             Document={'Bytes': img},
#             FeatureTypes=["TABLES", "FORMS"]
#         )
#
#         return response
#
#     def get_form(self):
#         """
#         Gets a direct form (as a dict) if availble in the image
#         """
#
#         self.key_map, self.value_map, self.block_map = self._build_kv_map()
#         return {k.strip(): v.strip() for k, v in self._get_kv_relationship().items()}
#
#     def get_text_lines(self):
#         """
#         Gets the raw lines detected in an image
#         """
#
#         text = ""
#         for item in self.ocr_data["Blocks"]:
#             if item["BlockType"] == "LINE":
#                 text += item["Text"] + "\n"
#         return text
#
#     def _build_kv_map(self):
#         """
#         Helper function to get keys and values from the OCR response
#         """
#
#         blocks = self.ocr_data['Blocks']
#
#         key_map = {}
#         value_map = {}
#         block_map = {}
#
#         for block in blocks:
#             block_id = block['Id']
#             block_map[block_id] = block
#             if block['BlockType'] == "KEY_VALUE_SET":
#                 if 'KEY' in block['EntityTypes']:
#                     key_map[block_id] = block
#                 else:
#                     value_map[block_id] = block
#
#         return key_map, value_map, block_map
#
#     def _find_value_block(self, key_block):
#         """
#         Helper function to get the VALUE relationships from the OCR response
#         """
#
#         for relationship in key_block['Relationships']:
#             if relationship['Type'] == 'VALUE':
#                 for value_id in relationship['Ids']:
#                     value_block = self.value_map[value_id]
#         return value_block
#
#     def _get_text_from_block(self, result):
#         """
#         Helper function to get the text from the OCR response
#         """
#
#         text = ''
#         if 'Relationships' in result:
#             for relationship in result['Relationships']:
#                 if relationship['Type'] == 'CHILD':
#                     for child_id in relationship['Ids']:
#                         word = self.block_map[child_id]
#                         if word['BlockType'] == 'WORD':
#                             text += word['Text'] + ' '
#                         if word['BlockType'] == 'SELECTION_ELEMENT':
#                             if word['SelectionStatus'] == 'SELECTED':
#                                 text += 'X '
#         return text
#
#     def _get_kv_relationship(self):
#         """
#         Helper function to build KEY VALUE relationships from the OCR response
#         """
#
#         kvs = {}
#         for block_id, key_block in self.key_map.items():
#             value_block = self._find_value_block(key_block)
#             key = self._get_text_from_block(key_block)
#             val = self._get_text_from_block(value_block)
#             kvs[key] = val
#         return kvs
