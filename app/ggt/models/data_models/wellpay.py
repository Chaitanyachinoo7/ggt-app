from pydantic import BaseModel
from typing import Dict, List, Optional
import datetime    

class WellpayCreateBillRequest(BaseModel):
    first_name: str = None
    last_name: str = None
    phone: str = None
    email: str = None
    date_of_birth: str = None
    street_address: str = None
    adddress_complement: str = None
    city: str = None
    state: str = None
    zip_code: str = None
    external_account_id: str = None
    autopay: bool
    billed_amount: int = 0
    external_bill_id: str = None
    service_date: str = None
    type: str = None


class WellpayCreateBillResponse(BaseModel):
    customer_id: int = None
    url: str = None
    receipt_token: str = None


class WellpayApiCredentials(BaseModel):
    api_key: str = None
    refresh_token: str = None

