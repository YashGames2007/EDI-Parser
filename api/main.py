from fastapi import FastAPI, UploadFile, File, HTTPException
import json

app = FastAPI()


def parse_edi_string(edi_string: str):

    edi_string = edi_string.strip()

    if not edi_string.startswith("ISA"):
        raise ValueError("Invalid EDI file: Missing ISA segment")

    # Detect delimiters from ISA
    element_sep = edi_string[3]
    segment_term = "~"
    component_sep = ":"

    isa_segment = edi_string.split(segment_term)[0]
    isa_elements = isa_segment.split(element_sep)

    if len(isa_elements) >= 16:
        component_sep = isa_elements[16][-1]

    segments_raw = edi_string.split(segment_term)

    segments = []

    for seg in segments_raw:
        seg = seg.strip()
        if not seg:
            continue

        elements = seg.split(element_sep)

        segment_data = {
            "segment_id": elements[0],
            "elements": elements[1:]
        }

        segments.append(segment_data)

    metadata = {
        "sender_id": None,
        "receiver_id": None,
        "transaction_type": None
    }

    for seg in segments:

        if seg["segment_id"] == "ISA":
            metadata["sender_id"] = seg["elements"][5] if len(seg["elements"]) > 5 else None
            metadata["receiver_id"] = seg["elements"][7] if len(seg["elements"]) > 7 else None

        if seg["segment_id"] == "ST":
            st_code = seg["elements"][0]

            if st_code == "837":
                metadata["transaction_type"] = "837 Healthcare Claim"
            elif st_code == "835":
                metadata["transaction_type"] = "835 Payment"
            elif st_code == "834":
                metadata["transaction_type"] = "834 Enrollment"
            else:
                metadata["transaction_type"] = f"Unknown ({st_code})"

    parsed = {
        "metadata": metadata,
        "segment_count": len(segments),
        "segments": segments
    }

    return parsed


@app.post("/parse-edi")
async def parse_edi(file: UploadFile = File(...)):

    try:
        contents = await file.read()
        edi_string = contents.decode("utf-8")

        parsed = parse_edi_string(edi_string)

        return parsed

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)