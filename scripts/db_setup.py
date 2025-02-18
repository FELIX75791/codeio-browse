import sqlite3
import json

# Connect to a local SQLite database (creates mydb.sqlite if it doesn't exist).
conn = sqlite3.connect("mydb.sqlite")
cur = conn.cursor()

# I store ios and meta as text (containing JSON) to preserve their structure.
cur.execute("""
CREATE TABLE IF NOT EXISTS mytable (
    problem_description TEXT,
    io_requirements TEXT,
    refcode TEXT,
    funcname TEXT,
    ios TEXT,
    source TEXT,
    category TEXT,
    meta TEXT
)
""")

jsonl_file = "/ephnvme/ziyue/codeio-browse/data/0_368500_filtered_v2_ds25.sced.jsonl"

with open(jsonl_file, "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)

        # Extract fields. If the field doesn't exist, default to empty string or empty structure
        problem_description = data.get("problem_description", "")
        io_requirements = data.get("io_requirements", "")
        refcode = data.get("refcode", "")
        funcname = data.get("funcname", "")
        ios = data.get("ios", [])
        source = data.get("source", "")
        category = data.get("category", "")
        meta = data.get("meta", {})

        # Convert ios and meta to JSON strings since they're not just strings
        ios_json = json.dumps(ios, separators=(",", ":"))
        meta_json = json.dumps(meta, separators=(",", ":"))

        # Insert into the SQLite table
        cur.execute("""
            INSERT INTO mytable (
                problem_description,
                io_requirements,
                refcode,
                funcname,
                ios,
                source,
                category,
                meta
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            problem_description,
            io_requirements,
            refcode,
            funcname,
            ios_json,
            source,
            category,
            meta_json
        ))

conn.commit()

# Example query: how many rows are in the table?
count_rows = cur.execute("SELECT COUNT(*) FROM mytable").fetchone()[0]
print("Total rows in mytable:", count_rows)

conn.close()
