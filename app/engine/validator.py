import re


def add_error(errors, code, row=None, column=None, rules=None, expanded_desc=""):

    desc = rules["errors"].get(code, {}).get("description", "Unknown error") + f": {expanded_desc}"

    errors.append({
        "code": code,
        "description": desc,
        "row": row,
        "column": column
    })


def validate(parsed, rules):

    errors = []

    segments = parsed["segments"]

    segment_ids = [s["segment_id"] for s in segments]

    # ----------------------
    # Required Segment Check
    # ----------------------

    for seg, rule in rules["segments"].items():

        if rule.get("required") and seg not in segment_ids:
            add_error(errors, "SEG_MISSING", rules=rules, expanded_desc=f"{seg} segment must be present.!")

    # ----------------------
    # Segment Validation
    # ----------------------

    for seg in segments:

        seg_id = seg["segment_id"]
        row = seg["row"]

        if seg_id not in rules["segments"]:
            continue

        seg_rule = rules["segments"][seg_id]

        elements = seg["elements"]

        if "min_elements" in seg_rule and len(elements) < seg_rule["min_elements"]:
            add_error(errors, "SEG_MIN_ELEMENTS", row=row, rules=rules, expanded_desc=f"{seg_id} segment must have at least {seg_rule['min_elements']} elements.")

        if "max_elements" in seg_rule and len(elements) > seg_rule["max_elements"]:
            add_error(errors, "SEG_MAX_ELEMENTS", row=row, rules=rules, expanded_desc=f"{seg_id} segment must have at most {seg_rule['max_elements']} elements.")

        # ----------------------
        # Element Validation
        # ----------------------

        for el in elements:

            column = el["column"]
            value = el["value"]

            element_key = f"{seg_id}{column:02}"

            element_rule = seg_rule.get("elements", {}).get(element_key)

            if not element_rule:
                continue

            # Type validation
            if "type" in element_rule:

                type_rule = rules["types"][element_rule["type"]]

                if not re.match(type_rule["regex"], value):
                    add_error(errors, "INVALID_FORMAT", row, column, rules, expanded_desc=f"Unexpected format for {element_key} element. Required format: {type_rule['description']}.")

            # Value set validation
            if "value_set" in element_rule:

                allowed = rules["values"]["possible_values"].get(
                    element_rule["value_set"], {}
                )

                if value not in allowed:
                    add_error(errors, "INVALID_VALUE", row, column, rules, expanded_desc=f"Invalid value for {element_key} element. Allowed values: {', '.join(allowed)}.")

            # Required value validation
            if "required_value" in element_rule:

                if value != element_rule["required_value"]:
                    add_error(errors, "INVALID_VALUE", row, column, rules, expanded_desc=f"{element_key} element must have value '{element_rule['required_value']}'.")

    return errors