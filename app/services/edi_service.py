from app.engine.parser import parse_edi
from app.engine.validator import validate
from app.engine.rules_loader import load_rules
# from util.desc import COMPONENT_DESCRIPTIONS


def process_edi_file(edi_string):

    parsed = parse_edi(edi_string)

    transaction_type = parsed["metadata"]["transaction_type"]

    rules = load_rules(transaction_type)

    errors = validate(parsed, rules)

    return {
        "metadata": parsed["metadata"],
        "parsed_data": parsed["segments"],
        "component_descriptions": "COMPONENT_DESCRIPTIONS TO BE ADDED HERE",
        "errors": errors
    }