import json
from pathlib import Path

BASE = Path("rules")

def load_json(path):
    with open(path) as f:
        return json.load(f)

def load_rules(transaction):

    rules = {}

    rules["types"] = load_json(BASE / "types.json")
    rules["values"] = load_json(BASE / "values.json")
    rules["errors"] = load_json(BASE / "errors.json")

    tx_dir = BASE / transaction

    rules["segments"] = load_json(tx_dir / "segments.json")["segments"]
    rules["loops"] = load_json(tx_dir / "loops.json")["loops"]
    rules["structure"] = load_json(tx_dir / "structure.json")["structure"]

    return rules