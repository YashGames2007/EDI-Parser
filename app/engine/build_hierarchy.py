def build_hierarchy(segments, transaction_type):

    loop_rules = LOOP_START.get(transaction_type, {})

    root = {
        "loop_id": "ROOT",
        "children": []
    }

    stack = [root]

    for seg in segments:

        seg_id = seg["segment_id"]

        loop_name = None
        for loop, start_seg in loop_rules.items():
            if start_seg == seg_id:
                loop_name = loop
                break

        if loop_name:

            new_loop = {
                "loop_id": loop_name,
                "segments": [],
                "children": []
            }

            stack[-1]["children"].append(new_loop)
            stack.append(new_loop)

        current_loop = stack[-1]

        if "segments" not in current_loop:
            current_loop["segments"] = []

        current_loop["segments"].append(seg)

    return root
