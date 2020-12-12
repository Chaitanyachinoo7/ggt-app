from fastapi import APIRouter

from ggt.lib.insurance_cards import InsuranceCard
from ggt.models.data_models.data_types import Base64Image, InsuranceCardResponse

router = APIRouter()


@router.post("/extract_insurance_info/")
async def extract_insurance_info(image: Base64Image):
    """
    Extracts the required fields from a base64 image of an insurance card
    """

    try:
        card = InsuranceCard(b64=str.encode(image.data))
        return InsuranceCardResponse(**card.get_details())
    except Exception as e:
        return {"success": False, "reason": str(e)}
