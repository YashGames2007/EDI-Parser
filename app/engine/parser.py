def parse_edi(edi_string):

    segments = []
    row = 1

    for raw in edi_string.strip().split("~"):

        raw = raw.strip()
        if not raw:
            continue

        parts = raw.split("*")

        seg_id = parts[0]

        elements = []

        for i, val in enumerate(parts[1:], start=1):

            elements.append({
                "column": i,
                "value": val
            })

        segments.append({
            "segment_id": seg_id,
            "row": row,
            "elements": elements
        })

        row += 1

    metadata = {}

    for seg in segments:
        if seg["segment_id"] == "ST":
            metadata["transaction_type"] = seg["elements"][0]["value"]

    return {
        "metadata": metadata,
        "segments": segments
    }