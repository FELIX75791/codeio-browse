# codeio-browse

2 way to browse the dataset conveniently.

First download the JSONL data from https://huggingface.co/datasets/hkust-nlp/CodeIO-PyEdu-Reasoning-Raw.

## Through SQLite and Datasette for a Browser-based GUI (Recomended)

1. Change the file path in line 19 of db_setup.py
2. python3 db_setup.py (This will generate mydb.sqlite)
3. pip install datasette
4. datasette mydb.sqlite

## Therough naive python scripts

1. python3 view_jsonl.py path/to/data.jsonl
2. In interactive prompt, you can either enter line number, or random.


