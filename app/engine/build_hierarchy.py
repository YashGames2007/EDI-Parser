# import json
# from pathlib import Path

# BASE_DIR = Path(__file__).resolve().parent
# PROJECT_ROOT = BASE_DIR.parent.parent
# RULES_DIR = PROJECT_ROOT / "rules"

# LOOP_RULES_PATH = RULES_DIR / "loop_rules.json"

# with open(LOOP_RULES_PATH) as f:
#     LOOP_START = json.load(f)
    
# def build_hierarchy(segments, transaction_type):

#     loop_rules = LOOP_START.get(transaction_type, {})

#     root = {
#         "loop_id": "ROOT",
#         "children": []
#     }

#     current_loop = root

#     for seg in segments:

#         seg_id = seg["segment_id"]

#         loop_name = None

#         for loop, start_seg in loop_rules.items():
#             if start_seg == seg_id:
#                 loop_name = loop
#                 break

#         if loop_name:

#             new_loop = {
#                 "loop_id": loop_name,
#                 "segments": [],
#                 "children": []
#             }

#             root["children"].append(new_loop)
#             current_loop = new_loop

#         if "segments" not in current_loop:
#             current_loop["segments"] = []

#         current_loop["segments"].append(seg)

#     return root