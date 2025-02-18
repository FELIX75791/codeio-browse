"""
Usage:
    python browse_jsonl.py path/to/data.jsonl

Description:
    1. Reads the JSONL file once to build an index of byte offsets for each line.
    2. Lets you:
       - Type in an integer line index to see that line
       - Type 'random' to see a random line
       - Type 'quit' to exit

Install requirements:
    - No extra libraries needed beyond the standard library.
    - For convenience, you might also install "jsonlines" (pip install jsonlines),
      but this script uses only built-in libraries for indexing and reading lines.
"""

import sys
import random
import json

def create_offset_index(jsonl_path):
    """
    Create a list of file offsets so we can seek directly to any line in O(1).
    Returns a list of byte offsets; each element corresponds to the start of a line.
    """
    offsets = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        while True:
            current_pos = f.tell()
            line = f.readline()
            if not line:
                # End of file
                break
            offsets.append(current_pos)
    return offsets

def read_line_at_offset(jsonl_path, offset):
    """
    Given a file path and byte offset, open the file, seek to offset,
    and return that entire line of text.
    """
    with open(jsonl_path, "r", encoding="utf-8") as f:
        f.seek(offset)
        return f.readline().rstrip("\n")
    

def indent_json_2levels(obj, current_level=0, max_level=2):
    """
    Pretty-print the JSON object `obj` so that only the outermost and
    second outermost levels are indented. Anything deeper is collapsed
    into a single-line JSON string.
    
    :param obj:          The Python object to serialize (dict, list, etc.).
    :param current_level:Current depth in the recursive traversal.
    :param max_level:    The cutoff level for multi-line indentation.
                         By default, 2 means we indent up to the second level.
    :return:             A string with the custom JSON formatting.
    """
    
    # If we're at or beyond the max indentation level, dump compactly
    # with no extra spaces or line breaks.
    if current_level >= max_level or not isinstance(obj, (dict, list)):
        return json.dumps(obj, separators=(",", ":"))
    
    # Handle dictionary with partial indentation
    if isinstance(obj, dict):
        lines = ["{"]
        items = list(obj.items())
        for i, (k, v) in enumerate(items):
            v_str = indent_json_2levels(v, current_level + 1, max_level)
            indent_str = "  " * (current_level + 1)
            # Build a line like: '    "key": {...}' with appropriate commas
            line = f'{indent_str}"{k}": {v_str}'
            if i < len(items) - 1:
                line += ","
            lines.append(line)
        
        closing_indent = "  " * current_level
        lines.append(f"{closing_indent}}}")
        return "\n".join(lines)
    
    # Handle list with partial indentation
    elif isinstance(obj, list):
        lines = ["["]
        for i, item in enumerate(obj):
            item_str = indent_json_2levels(item, current_level + 1, max_level)
            indent_str = "  " * (current_level + 1)
            line = f"{indent_str}{item_str}"
            if i < len(obj) - 1:
                line += ","
            lines.append(line)
        
        closing_indent = "  " * current_level
        lines.append(f"{closing_indent}]")
        return "\n".join(lines)



def browse_jsonl(jsonl_path):
    """
    Indexes the JSONL file, then provides an interactive prompt:
      - Type a line index (0-based) to display that line
      - Type 'random' to display a random line
      - Type 'quit' to exit
    """
    print(f"Indexing lines in {jsonl_path} (this may take a while for very large files)...")
    offsets = create_offset_index(jsonl_path)
    total_lines = len(offsets)
    print(f"Done. Found {total_lines} lines in {jsonl_path}.\n")

    while True:
        user_input = input(
            "Enter line index (0..{}), 'random', or 'quit': "
            .format(total_lines - 1)
        ).strip().lower()

        if user_input == "quit":
            print("Exiting.")
            break
        elif user_input == "random":
            if total_lines == 0:
                print("The file is empty—no lines to sample.")
                continue
            line_idx = random.randint(0, total_lines - 1)
            line = read_line_at_offset(jsonl_path, offsets[line_idx])
            print(f"\n--- Line {line_idx} ---")
            parsed = json.loads(line)
            print(indent_json_2levels(parsed))
            print()
        else:
            # Try to parse as an integer line index
            if user_input.isdigit():
                idx = int(user_input)
                if 0 <= idx < total_lines:
                    line = read_line_at_offset(jsonl_path, offsets[idx])
                    print(f"\n--- Line {idx} ---")
                    parsed = json.loads(line)
                    print(indent_json_2levels(parsed))
                    print()
                else:
                    print(f"Invalid index. Must be in [0..{total_lines - 1}].\n")
            else:
                print("Invalid command. Type an integer, 'random', or 'quit'.\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} path/to/data.jsonl")
        sys.exit(1)

    browse_jsonl(sys.argv[1])
