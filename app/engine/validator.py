import re

def validate(parsed_data, rules):

    errors = []

    segments = parsed_data["segments"]

    segment_ids = [s["segment_id"] for s in segments]

    # -------------------------
    # Required Segment Check
    # -------------------------

    for seg in rules.get("required_segments", []):

        if seg not in segment_ids:

            errors.append({
                "code": "SEG_MISSING",
                "description": f"Missing required segment {seg}"
            })

    # -------------------------
    # Segment Structure Rules
    # -------------------------

    for seg in segments:

        seg_id = seg["segment_id"]
        row = seg["row"]

        if seg_id not in rules["segments"]:
            continue

        seg_rule = rules["segments"][seg_id]

        element_count = len(seg["elements"])

        if "min_elements" in seg_rule and element_count < seg_rule["min_elements"]:

            errors.append({
                "code": "SEG_MIN_ELEMENTS",
                "description": f"{seg_id} has too few elements",
                "row": row
            })

        if "max_elements" in seg_rule and element_count > seg_rule["max_elements"]:

            errors.append({
                "code": "SEG_MAX_ELEMENTS",
                "description": f"{seg_id} has too many elements",
                "row": row
            })

    # -------------------------
    # Element Validation
    # -------------------------

    for seg in segments:

        seg_id = seg["segment_id"]
        row = seg["row"]

        for el in seg["elements"]:

            col = el["column"]
            value = el["value"]

            key = f"{seg_id}{col:02}"

            rule = rules.get("element_rules", {}).get(key)

            if not rule:
                continue

            if rule["type"] == "date":

                if not re.match(r"^\d{8}$", value):

                    errors.append({
                        "code": "INVALID_DATE",
                        "description": f"{key} must be CCYYMMDD",
                        "row": row
                    })

            if rule["type"] == "npi":

                if not re.match(r"^\d{10}$", value):

                    errors.append({
                        "code": "INVALID_NPI",
                        "description": f"{key} must be 10 digit NPI",
                        "row": row
                    })

    return errors