import json
import random
import matplotlib.pyplot as plt
from collections import defaultdict

def analyze_pythonedu_reasoning(jsonl_path, io_requirements_out="sample_io_requirements.txt"):
    """
    Reads a JSONL file containing data in the format specified:
      {
        "problem_description": ...,
        "io_requirements": ...,
        "refcode": ...,
        "funcname": ...,
        "ios": [
          {"input": ..., "output": ...}, ...
        ],
        "source": ...,
        "category": ...,
        "meta": ...
      }

    The script performs:
      1. Bins # of test cases (len(ios)) into 0..19, and ">=20".
         Makes a bar chart: x-axis = number of test cases, y-axis = number of questions.
      2. Counts how many questions have a non-empty funcname.
      3. Randomly selects 10 io_requirements from questions WITH funcname and 10 from
         those WITHOUT funcname; saves them to a text file with group labels/separator.
      4. Plots the distribution of questions by category.
    """

    # Counters for I/O distribution
    max_explicit_bin = 19  # up to 19 individually
    ios_counts = [0] * (max_explicit_bin + 1)  # indices 0..19
    above_20_count = 0

    # Track how many have a non-empty funcname
    funcname_count = 0

    # Prepare to pick random io_requirements
    # - separate lists for with-func and without-func
    io_req_with_func = []
    io_req_without_func = []

    # Category counts
    category_counts = defaultdict(int)

    # 1) Read the JSONL file line by line
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            data = json.loads(line)

            # Extract the fields we care about
            ios = data.get("ios", [])
            funcname = data.get("funcname", "")
            io_req = data.get("io_requirements", "")
            category = data.get("category", "")

            # 1) Bin the length of ios into 0..19 or >=20
            num_ios = len(ios)
            if num_ios <= max_explicit_bin:
                ios_counts[num_ios] += 1
            else:
                above_20_count += 1

            # 2) Check if funcname is non-empty (or not None)
            if funcname:
                funcname_count += 1

            # Separate io_requirements based on whether funcname is empty or not
            if io_req:
                if funcname:
                    io_req_with_func.append(io_req)
                else:
                    io_req_without_func.append(io_req)

            # 4) Count category
            if category:
                category_counts[category] += 1

    # -------------------------------
    # (1) Plot the distribution of # of I/O test cases
    # -------------------------------
    labels = [str(i) for i in range(max_explicit_bin + 1)] + [">=20"]
    values = ios_counts + [above_20_count]
    x_positions = range(len(labels))

    plt.figure(figsize=(10, 10))
    bars = plt.bar(x_positions, values, color='steelblue', alpha=0.7)
    plt.title("Distribution of # of Test Cases (ios)")
    plt.xlabel("Number of Test Cases")
    plt.ylabel("Number of Questions")
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Put numeric labels on top of each bar
    for rect in bars:
        height = rect.get_height()
        if height > 0:
            x_center = rect.get_x() + rect.get_width() / 2
            plt.text(
                x_center,
                height,
                f"{int(height)}",
                ha="center",
                va="bottom",
                fontsize=8,
                rotation=90
            )

    plt.xticks(x_positions, labels)
    plt.tight_layout()
    plt.savefig("ios_distribution.png", dpi=300)
    print("Saved histogram of # of test cases as: ios_distribution.png")
    plt.close()

    # -------------------------------
    # (2) Print how many questions have funcname
    # -------------------------------
    print(f"Number of questions with a non-empty funcname: {funcname_count}")

    # -------------------------------
    # (3) Randomly select 10 io_requirements from WITH funcname and 10 from WITHOUT funcname
    # -------------------------------
    # Shuffle or directly sample
    n_with_func = min(10, len(io_req_with_func))
    n_without_func = min(10, len(io_req_without_func))
    sample_with_func = random.sample(io_req_with_func, n_with_func)
    sample_without_func = random.sample(io_req_without_func, n_without_func)

    with open(io_requirements_out, "w", encoding="utf-8") as txt_f:
        # Label group 1
        txt_f.write("=== IO REQUIREMENTS FOR RECORDS WITH FUNCNAME ===\n")
        for i, req in enumerate(sample_with_func, start=1):
            txt_f.write(f"--- Sample {i} (With funcname) ---\n{req}\n\n")

        txt_f.write("---------------------------------------------------------\n")

        # Label group 2
        txt_f.write("=== IO REQUIREMENTS FOR RECORDS WITHOUT FUNCNAME ===\n")
        for i, req in enumerate(sample_without_func, start=1):
            txt_f.write(f"--- Sample {i} (No funcname) ---\n{req}\n\n")

    print(f"Saved {n_with_func} + {n_without_func} random io_requirements to: {io_requirements_out}")

    # -------------------------------
    # (4) Plot # of questions by category
    # -------------------------------
    if category_counts:
        cat_pairs_sorted = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        cat_labels = [p[0] for p in cat_pairs_sorted]
        cat_values = [p[1] for p in cat_pairs_sorted]

        x_cat = range(len(cat_labels))

        plt.figure(figsize=(10, 10))
        cat_bars = plt.bar(x_cat, cat_values, color='darkorange', alpha=0.8)
        plt.title("Number of Questions by Category")
        plt.xlabel("Category")
        plt.ylabel("Number of Questions")
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.xticks(x_cat, cat_labels, rotation=45, ha='right')

        # Put numeric labels on top of each bar
        for rect in cat_bars:
            height = rect.get_height()
            if height > 0:
                x_center = rect.get_x() + rect.get_width() / 2
                plt.text(
                    x_center,
                    height,
                    f"{int(height)}",
                    ha="center",
                    va="bottom",
                    fontsize=8,
                    rotation=90
                )

        plt.tight_layout()
        plt.savefig("category_distribution.png", dpi=300)
        print("Saved category distribution plot as: category_distribution.png")
        plt.close()
    else:
        print("No 'category' field found in any record to plot.")

if __name__ == "__main__":
    # Example usage:
    analyze_pythonedu_reasoning("/ephnvme/ziyue/codeio_dataset/0_368500_filtered_v2_ds25.sced.jsonl")
