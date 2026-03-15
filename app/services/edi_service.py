from app.engine.build_hierarchy import build_hierarchy
from app.engine.parser import parse_edi
from app.engine.validator import validate
from app.engine.rules_loader import load_rules


def process_edi_file(edi_string):

    parsed = parse_edi(edi_string)

    transaction_type = parsed["metadata"]["transaction_type"]

    rules = load_rules(transaction_type)

    errors = validate(parsed, rules)

    # print(build_hierarchy(parsed["segments"], rules))

    return {
        "metadata": parsed["metadata"],
        "segments": parsed["segments"],
        "component_descriptions": {},
        "errors": errors
    }