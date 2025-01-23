#!/usr/bin/env python3
"""
Duplicate Sequence Finder - This script was initially generated with AI assistance and subsequently refined.

This script identifies duplicate sequences in a dataset containing mature and full sequences.
It processes CSV-formatted data and generates a detailed log file reporting all duplications.

Features:
- Robust error handling for file operations and data processing
- Input validation for file formats and data structure
- Detailed logging with sequence statistics
- Progress tracking for large files
- Memory-efficient processing using generators
- Detection of cases where both mature and full sequences are duplicated
"""

import sys
import csv
from pathlib import Path
from collections import defaultdict
from typing import Iterator, Tuple, Dict, List, Set
from datetime import datetime

class DuplicateFinderError(Exception):
    """Custom exception for handling script-specific errors."""
    pass

def read_csv_file(file_path: Path) -> Iterator[Tuple[int, List[str]]]:
    """
    Generator function to read and validate CSV file contents.
    
    Args:
        file_path: Path to the input CSV file
    
    Yields:
        Tuple containing line number and list of fields
    
    Raises:
        DuplicateFinderError: If file format is invalid or required columns are missing
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=';')
            for line_num, row in enumerate(reader, start=1):
                if len(row) < 11:
                    print(f"Warning: Skipping line {line_num} - insufficient columns")
                    continue
                yield line_num, row
    except FileNotFoundError:
        raise DuplicateFinderError(f"Input file not found: {file_path}")
    except csv.Error as e:
        raise DuplicateFinderError(f"CSV parsing error at line {line_num}: {str(e)}")

def process_sequences(data_iterator: Iterator[Tuple[int, List[str]]]) -> Tuple[Dict, Dict, int]:
    """
    Process sequence data and identify duplicates.
    
    Args:
        data_iterator: Iterator yielding line numbers and data rows
    
    Returns:
        Tuple containing mature sequence dict, full sequence dict, and total lines processed
    """
    mature_seq_dict = defaultdict(list)
    full_seq_dict = defaultdict(list)
    total_lines = 0

    for line_num, row in data_iterator:
        total_lines += 1
        if total_lines % 1000 == 0:  # Progress indicator
            print(f"Processing line {total_lines}...")

        # Unpack row into named variables for clarity
        (unique_id, study_name, family_subtype, family_type, 
         hymenoptera_group, species, species_id, uniprot_id, 
         db, mature_seq, full_seq) = row

        # Store non-empty sequences
        if mature_seq.strip():
            mature_seq_dict[mature_seq].append((line_num, row))
        if full_seq.strip():
            full_seq_dict[full_seq].append((line_num, row))

    return mature_seq_dict, full_seq_dict, total_lines

def find_both_duplicates(mature_dict: Dict, full_dict: Dict) -> Dict[Tuple[str, str], List]:
    """
    Find entries where both mature and full sequences are duplicated.
    
    Args:
        mature_dict: Dictionary of mature sequences
        full_dict: Dictionary of full sequences
    
    Returns:
        Dictionary of duplicate pairs with their corresponding entries
    """
    both_dupes = defaultdict(list)
    
    # Get sets of duplicate sequences
    mature_dupes = {seq for seq, entries in mature_dict.items() if len(entries) > 1}
    full_dupes = {seq for seq, entries in full_dict.items() if len(entries) > 1}
    
    # Check each mature duplicate entry
    for mature_seq in mature_dupes:
        for line_num, row in mature_dict[mature_seq]:
            full_seq = row[10]  # Full sequence is at index 10
            if full_seq in full_dupes:
                both_dupes[(mature_seq, full_seq)].append((line_num, row))
    
    return both_dupes

def write_duplicate_report(
    output_path: Path,
    mature_dict: Dict,
    full_dict: Dict,
    total_lines: int
) -> None:
    """
    Write detailed duplicate analysis to output file.
    
    Args:
        output_path: Path to output file
        mature_dict: Dictionary of mature sequences
        full_dict: Dictionary of full sequences
        total_lines: Total number of lines processed
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as logfile:
            # Write header with metadata
            logfile.write("Duplicate Sequences Report\n")
            logfile.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            logfile.write("=" * 50 + "\n\n")

            # Find entries where both sequences are duplicated
            both_dupes = find_both_duplicates(mature_dict, full_dict)

            # Write statistics
            logfile.write("Summary Statistics:\n")
            logfile.write(f"Total sequences processed: {total_lines}\n")
            mature_dupes = sum(1 for entries in mature_dict.values() if len(entries) > 1)
            full_dupes = sum(1 for entries in full_dict.values() if len(entries) > 1)
            both_dupes_count = len(both_dupes)
            logfile.write(f"Duplicate mature sequences found: {mature_dupes}\n")
            logfile.write(f"Duplicate full sequences found: {full_dupes}\n")
            logfile.write(f"Entries with both sequences duplicated: {both_dupes_count}\n\n")

            # Write entries where both sequences are duplicated
            logfile.write("Entries with Both Sequences Duplicated:\n" + "=" * 40 + "\n\n")
            for (mature_seq, full_seq), entries in both_dupes.items():
                logfile.write(f"Mature Sequence ({len(mature_seq)} bp): {mature_seq}\n")
                logfile.write(f"Full Sequence ({len(full_seq)} bp): {full_seq}\n")
                logfile.write(f"Found in {len(entries)} entries:\n")
                for line_num, row in entries:
                    logfile.write(f"Line {line_num}: {';'.join(row)}\n")
                logfile.write("\n")

            # Get sets of sequences that appear in both_dupes
            both_mature_seqs = {mature_seq for (mature_seq, _) in both_dupes.keys()}
            both_full_seqs = {full_seq for (_, full_seq) in both_dupes.keys()}

            # Write mature sequence duplicates (excluding those in both_dupes)
            logfile.write("\nDuplicates in Mature Sequences Only:\n" + "=" * 35 + "\n\n")
            for seq, entries in mature_dict.items():
                if len(entries) > 1 and seq not in both_mature_seqs:
                    logfile.write(f"Sequence ({len(seq)} bp): {seq}\n")
                    logfile.write(f"Found in {len(entries)} entries:\n")
                    for line_num, row in entries:
                        logfile.write(f"Line {line_num}: {';'.join(row)}\n")
                    logfile.write("\n")

            # Write full sequence duplicates (excluding those in both_dupes)
            logfile.write("\nDuplicates in Full Sequences Only:\n" + "=" * 35 + "\n\n")
            for seq, entries in full_dict.items():
                if len(entries) > 1 and seq not in both_full_seqs:
                    logfile.write(f"Sequence ({len(seq)} bp): {seq}\n")
                    logfile.write(f"Found in {len(entries)} entries:\n")
                    for line_num, row in entries:
                        logfile.write(f"Line {line_num}: {';'.join(row)}\n")
                    logfile.write("\n")

    except IOError as e:
        raise DuplicateFinderError(f"Error writing to output file: {str(e)}")

def main():
    """Main execution function."""
    try:
        # Configure input/output paths
        input_path = Path("Hym/Hymenoptera_toxins/Dataset.csv")
        output_path = Path("Hym/Hymenoptera_toxins/duplicate_log_file.txt")

        # Create output directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Process the data
        print(f"Processing input file: {input_path}")
        data_iterator = read_csv_file(input_path)
        mature_dict, full_dict, total_lines = process_sequences(data_iterator)

        # Generate the report
        print("Writing duplicate report...")
        write_duplicate_report(output_path, mature_dict, full_dict, total_lines)

        print(f"\nDuplicate analysis complete. Results written to: {output_path}")
        print(f"Total sequences processed: {total_lines}")

    except DuplicateFinderError as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()