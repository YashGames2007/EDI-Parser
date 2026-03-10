def parse_edi(edi_string: str):

    edi_string = edi_string.strip()

    if not edi_string.startswith("ISA"):
        raise ValueError("Invalid EDI file: Missing ISA segment")

    element_sep = edi_string[3]
    segment_term = "~"

    segments_raw = edi_string.split(segment_term)

    segments = []

    for row_index, seg in enumerate(segments_raw, start=1):

        seg = seg.strip()

        if not seg:
            continue

        elements = seg.split(element_sep)

        segment_data = {
            "row": row_index,
            "segment_id": elements[0],
            "elements": [
                {
                    "column": i + 1,
                    "value": el
                }
                for i, el in enumerate(elements[1:])
            ]
        }

        segments.append(segment_data)

    metadata = {
        "sender_id": None,
        "receiver_id": None,
        "transaction_type": None
    }

    for seg in segments:

        if seg["segment_id"] == "ISA":

            elements = [e["value"] for e in seg["elements"]]

            if len(elements) > 5:
                metadata["sender_id"] = elements[5]

            if len(elements) > 7:
                metadata["receiver_id"] = elements[7]

        if seg["segment_id"] == "ST":

            st_code = seg["elements"][0]["value"]

            if st_code == "837":
                metadata["transaction_type"] = "837"
            elif st_code == "835":
                metadata["transaction_type"] = "835"
            elif st_code == "834":
                metadata["transaction_type"] = "834"
            else:
                metadata["transaction_type"] = f"Unknown ({st_code})"

    return {
        "metadata": metadata,
        "segments": segments
    }