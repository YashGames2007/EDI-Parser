from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.edi_service import process_edi_file

router = APIRouter()

@router.post("/parse-edi")
async def parse_edi(file: UploadFile = File(...)):

    try:

        contents = await file.read()
        edi_string = contents.decode("utf-8")

        result = process_edi_file(edi_string)

        return result

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )