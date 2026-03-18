import traceback
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from app.services.edi_service import process_edi_file, fix_edi_error

router = APIRouter()


@router.post("/parse-edi")
async def parse_edi(file: UploadFile = File(...)):

    try:

        contents = await file.read()
        edi_string = contents.decode("utf-8")

        result = process_edi_file(edi_string)
        # print(result)
        return result

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.post("/fix-error")
async def fix_error(
    file: UploadFile = File(...),
    code: str = Form(...),
    row: int = Form(...),
    column: Optional[int] = Form(None),
    segment_id: Optional[str] = Form(None),
):
    try:
        contents = await file.read()
        edi_string = contents.decode("utf-8")

        result = fix_edi_error(
            edi_string=edi_string,
            code=code,
            row=row,
            column=column,
            segment_id=segment_id,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
