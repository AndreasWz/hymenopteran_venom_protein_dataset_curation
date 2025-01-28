#!/usr/bin/env python3
"""
Dataset Filter - Filters a CSV dataset based on log file annotations.

This script reads a duplicate analysis log file and the original dataset,
then creates filtered versions of the dataset based on the annotations:
+ : Keep the line
- : Remove the line
? : Creates two versions (one treating ? as +, one as -)
"""

import csv
from pathlib import Path
from typing import Set, Tuple


def parse_log_file(file_path: str) -> Tuple[Set[int], Set[int], Set[int]]:
    """
    Parses a duplicate sequences log file and extracts line classifications.

    Args:
        file_path (str): Path to the log file.

    Returns:
        Tuple[Set[int], Set[int], Set[int]]: Sets of line numbers for
                                             keep (+), remove (-), and uncertain (?).
    """
    keep_lines = set()
    remove_lines = set()
    uncertain_lines = set()

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line.startswith("+"):
                parts = line.split("Line", 1)
                if len(parts) > 1:
                    line_number = int(parts[1].split(":")[0].strip())
                    keep_lines.add(line_number)
            elif line.startswith("-"):
                parts = line.split("Line", 1)
                if len(parts) > 1:
                    line_number = int(parts[1].split(":")[0].strip())
                    remove_lines.add(line_number)
            elif line.startswith("?"):
                parts = line.split("Line", 1)
                if len(parts) > 1:
                    line_number = int(parts[1].split(":")[0].strip())
                    uncertain_lines.add(line_number)

    return keep_lines, remove_lines, uncertain_lines


def filter_dataset(
    input_path: Path,
    output_path: Path,
    keep_lines: Set[int],
    remove_lines: Set[int],
    uncertain_lines: Set[int],
    treat_uncertain_as_keep: bool,
) -> None:
    """
    Filters the dataset based on the line classifications.

    Args:
        input_path (Path): Path to the input CSV file.
        output_path (Path): Path to the output CSV file.
        keep_lines (Set[int]): Set of line numbers to keep.
        remove_lines (Set[int]): Set of line numbers to remove.
        uncertain_lines (Set[int]): Set of line numbers marked with ?.
        treat_uncertain_as_keep (bool): Whether to treat ? lines as keep (+) or remove (-).
    """
    with open(input_path, "r", encoding="utf-8") as infile, \
         open(output_path, "w", encoding="utf-8", newline="") as outfile:

        reader = csv.reader(infile, delimiter=";")
        writer = csv.writer(outfile, delimiter=";")

        for i, row in enumerate(reader, start=1):  # Line numbers start at 1
            if i in keep_lines or (treat_uncertain_as_keep and i in uncertain_lines):
                writer.writerow(row)
            elif i in remove_lines or (not treat_uncertain_as_keep and i in uncertain_lines):
                continue
            else:
                # Write lines that aren't mentioned in the log file
                writer.writerow(row)


def main() -> None:
    """
    Main execution function.
    """
    # Configure paths
    base_path = Path("Hym/Hymenoptera_toxins")
    input_path = base_path / "Dataset.csv"
    log_path = "ant_repo/Hym/Hymenoptera_toxins/duplicate_log_file.txt"
    output_keep_uncertain = base_path / "Dataset_filtered_keep_uncertain.csv"
    output_remove_uncertain = base_path / "Dataset_filtered_remove_uncertain.csv"

    # Create output directory if it doesn't exist
    output_keep_uncertain.parent.mkdir(parents=True, exist_ok=True)

    # Parse log file
    print("Parsing log file...")
    keep_lines, remove_lines, uncertain_lines = parse_log_file(log_path)

    # Create filtered datasets
    print("Creating filtered datasets...")

    # Version 1: Treat ? as +
    print("Creating version with uncertain lines kept...")
    filter_dataset(
        input_path,
        output_keep_uncertain,
        keep_lines,
        remove_lines,
        uncertain_lines,
        treat_uncertain_as_keep=True,
    )

    # Version 2: Treat ? as -
    print("Creating version with uncertain lines removed...")
    filter_dataset(
        input_path,
        output_remove_uncertain,
        keep_lines,
        remove_lines,
        uncertain_lines,
        treat_uncertain_as_keep=False,
    )

    # Print summary
    print("\nProcessing complete!")
    print(f"Found {len(keep_lines)} lines marked with +")
    print(f"Found {len(remove_lines)} lines marked with -")
    print(f"Found {len(uncertain_lines)} lines marked with ?")
    print(f"\nCreated two filtered versions of the dataset:")
    print(f"1. Treating ? as + (keep): {output_keep_uncertain}")
    print(f"2. Treating ? as - (remove): {output_remove_uncertain}")


if __name__ == "__main__":
    main()
