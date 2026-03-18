# from app.engine.build_hierarchy import build_hierarchy
from app.engine.parser import parse_edi
from app.engine.validator import validate
from app.engine.rules_loader import load_rules


def build_edi_string(segments):
    # Rebuild EDI string using standard separators
    seg_texts = []
    for seg in segments:
        seg_texts.append("*".join([seg["segment_id"]] + [el["value"] for el in seg["elements"]]))
    return "~".join(seg_texts) + "~"


def _generate_type_value(type_name):
    mapping = {
        "ID2": "AA",
        "ID3": "AAA",
        "N1": "1",
        "AN1_80": "A",
        "ANS15": "A",
        "N0_9": "0",
        "DT8": "20250101",
        "DT6": "250101",
        "TM4": "0000",
        "CHAR": "A",
        "SPACE10": "          ",
        "AN10": "A"
    }
    return mapping.get(type_name, "FIXED")


def _build_segment_template(segment_id, rules):
    seg_rule = rules.get("segments", {}).get(segment_id, {})
    elements_rules = seg_rule.get("elements", {})

    template = []
    if not elements_rules:
        return template

    # Order by column number derived from keys like ISA01
    columns = []
    for element_key in elements_rules:
        try:
            col = int(element_key[-2:])
        except ValueError:
            continue
        columns.append((col, element_key))

    columns.sort(key=lambda x: x[0])

    for col, element_key in columns:
        element_rule = elements_rules.get(element_key, {})
        value = ""

        if "required_value" in element_rule:
            value = element_rule["required_value"]
        elif "value_set" in element_rule:
            possible = rules.get("values", {}).get("possible_values", {}).get(element_rule["value_set"], {})
            if possible:
                # pick first key in value_set
                value = next(iter(possible.keys()))
            else:
                value = ""
        elif "type" in element_rule:
            value = _generate_type_value(element_rule["type"])

        template.append({"column": col, "value": value})

    return template


def fix_edi_error(edi_string, code, row=None, column=None, segment_id=None):
    parsed = parse_edi(edi_string)

    segments = parsed["segments"]
    original_segments = [seg.copy() for seg in segments]
    for seg in original_segments:
        seg["elements"] = [el.copy() for el in seg["elements"]]

    # Determine before_line from existing data
    before_line = None
    after_line = None

    if row is not None and 1 <= row <= len(segments):
        before_line = "*".join([segments[row - 1]["segment_id"]] + [el["value"] for el in segments[row - 1]["elements"]])

    # Primary fix behavior
    if code == "SEG_MISSING":
        rules = load_rules(parsed["metadata"].get("transaction_type"))

        # infer missing segment_id from segments.json row mapping if not provided
        if not segment_id and row is not None:
            for sid, sr in rules.get("segments", {}).items():
                if sr.get("row") == row:
                    segment_id = sid
                    break

        if segment_id:
            template_elements = _build_segment_template(segment_id, rules)

            if row is not None and 1 <= row <= len(segments) + 1:
                # capture the line currently at row before shift
                if row <= len(segments):
                    before_line = "*".join([segments[row - 1]["segment_id"]] + [el["value"] for el in segments[row - 1]["elements"]])
                # insert the missing row at row position and shift next rows down
                segments.insert(row - 1, {"segment_id": segment_id, "row": row, "elements": template_elements})
                after_line = "*".join([segment_id] + [el["value"] for el in template_elements])
            else:
                # fallback append
                segments.append({"segment_id": segment_id, "row": len(segments) + 1, "elements": template_elements})
                after_line = "*".join([segment_id] + [el["value"] for el in template_elements])
        else:
            # fallback append empty segment
            segments.append({"segment_id": segment_id or "UNKNOWN", "row": len(segments) + 1, "elements": []})
            after_line = ""

    elif code == "SEG_MIN_ELEMENTS":
        if row is not None and 1 <= row <= len(segments):
            seg = segments[row - 1]
            if segment_id and seg["segment_id"] != segment_id:
                pass
            # best-effort: add missing empty values to reach min from known rules if available in segment_id argument
            # fallback: add one empty element
            if len(seg["elements"] or []) == 0:
                seg["elements"] = [{"column": 1, "value": ""}]
            else:
                seg["elements"].append({"column": len(seg["elements"]) + 1, "value": ""})
            after_line = "*".join([seg["segment_id"]] + [el["value"] for el in seg["elements"]])

    elif code == "SEG_MAX_ELEMENTS":
        if row is not None and 1 <= row <= len(segments):
            seg = segments[row - 1]
            if seg["elements"]:
                seg["elements"] = seg["elements"][:-1]
            after_line = "*".join([seg["segment_id"]] + [el["value"] for el in seg["elements"]])

    elif code in ("INVALID_VALUE", "INVALID_FORMAT"):
        if row is not None and column is not None and 1 <= row <= len(segments):
            seg = segments[row - 1]
            if column - 1 < len(seg["elements"]):
                el = seg["elements"][column - 1]
                if segment_id and seg["segment_id"] != segment_id:
                    # segment mismatch, do nothing
                    pass
                else:
                    # Use either required_value or value_set or type from rules if available
                    rules = load_rules(parsed["metadata"].get("transaction_type"))
                    seg_rule = rules.get("segments", {}).get(seg["segment_id"], {})
                    element_key = f"{seg['segment_id']}{column:02}"
                    element_rule = seg_rule.get("elements", {}).get(element_key, {})

                    if "required_value" in element_rule:
                        el["value"] = element_rule["required_value"]
                    elif "value_set" in element_rule:
                        allowed = list(rules.get("values", {}).get("possible_values", {}).get(element_rule["value_set"], {}).keys())
                        if allowed:
                            el["value"] = allowed[0]
                    elif "type" in element_rule:
                        el["value"] = _generate_type_value(element_rule["type"])
                    else:
                        el["value"] = "FIXED"

                    after_line = "*".join([seg["segment_id"]] + [e["value"] for e in seg["elements"]])

    else:
        # Fallback: no-change for unknown code
        if row is not None and 1 <= row <= len(segments):
            after_line = before_line

    # Update row indexes of segments after modification
    for i, seg in enumerate(segments, start=1):
        seg["row"] = i

    fixed_edi = build_edi_string(segments)

    return {
        "fixed_edi": fixed_edi,
        "before_line": before_line,
        "after_line": after_line,
        # "code": code,
        # "row": row,
        # "column": column,
        # "segment_id": segment_id
    }


def process_edi_file(edi_string):

    parsed = parse_edi(edi_string)

    transaction_type = parsed["metadata"]["transaction_type"]

    rules = load_rules(transaction_type)

    errors = validate(parsed, rules)

    # hierarchy = build_hierarchy(parsed["segments"], transaction_type)

    meta = {
        "senderId": "1234",
        "receiverId": "5678"
    }

    return {
        # "metadata": parsed["metadata"],
        "metadata": meta,
        "segments": parsed["segments"],
        # "hierarchy": hierarchy,
        "component_descriptions": {},
        "errors": errors
    }