from pydantic import BaseModel
from typing import Dict, List, Optional
import datetime    

class WellpayBillRequest(BaseModel):
    first_name: str = ''
    last_name: str = ''
    phone: str = ''
    email: str = ''
    date_of_birth: str = ''
    street_address: str = ''
    adddress_complement: str = ''
    city: str = ''
    state: str = ''
    zip_code: str = ''
    external_account_id: str = ''
    autopay: bool
    billed_amount: int = 0
    external_bill_id: str = ''
    service_date: str = ''
    type: str = ''
