import sqlite3
import json

conn = sqlite3.connect("mydb.sqlite")
cur = conn.cursor()

# Example: create a table with some columns. Adjust to your actual fields.
cur.execute("""
CREATE TABLE IF NOT EXISTS mytable (
    problem_description TEXT,
    io_requirements TEXT,
    funcname TEXT,
    category TEXT
    -- Add more columns as needed
)
""")

# Now parse each line in your JSONL and insert row(s)
jsonl_file = "0_368500_filtered_v2_ds25.sced.jsonl"
with open(jsonl_file, "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        # Extract fields
        problem_description = data.get("problem_description", "")
        io_requirements = data.get("io_requirements", "")
        funcname = data.get("funcname", "")
        category = data.get("category", "")

        cur.execute("""
        INSERT INTO mytable (problem_description, io_requirements, funcname, category)
        VALUES (?, ?, ?, ?)
        """, (problem_description, io_requirements, funcname, category))

conn.commit()

# Then you can query:
res = cur.execute("SELECT COUNT(*) FROM mytable WHERE category = 'arithmetic'").fetchone()
print("Arithmetic samples:", res[0])

conn.close()
