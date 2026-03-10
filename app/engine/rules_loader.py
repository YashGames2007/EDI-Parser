import json

def load_rules(transaction_type):

    with open("rules/base.json") as f:
        base_rules = json.load(f)

    try:
        with open(f"rules/{transaction_type}.json") as f:
            tx_rules = json.load(f)
    except:
        tx_rules = {}

    return {**base_rules, **tx_rules}