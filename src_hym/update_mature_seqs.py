import csv
import subprocess, os, re
from typing import List, Dict

"""

This script was initially generated with AI assistance and subsequently refined.

"""


def create_fasta_from_seq(sequence, identifier, filename):
    """Create a FASTA file from a sequence."""
    with open(filename, 'w') as f:
        f.write(f">{identifier}\n{sequence}\n")

def run_signalp(sequence: str, temp_path: str) -> Dict[str, str]:
    """
    Runs SignalP 6.0 on a given sequence.

    Args:
        sequence (str): The protein sequence to analyze.

    Returns:
        Dict[str, str]: A dictionary containing SignalP results, including 'mature_seq'.
    """

    #fasta_file = os.path.join(temp_path, f"temp_will_be_overwritten_pls_delete.fasta")
    fasta_file = "signalp6_slow_sequential/out/tmp_fasta.fna"
    create_fasta_from_seq(sequence, "seq", fasta_file)

    subprocess.run(
    [
        "signalp6",
        "--fastafile", "out/tmp_fasta.fna",
        "--organism", "eukarya",
        "--output_dir", "out",
        "--format", "txt",
        "--mode", "slow"
    ],
    cwd="signalp6_slow_sequential",  # Change the working directory for the subprocess
    check=True
    )
    
    prediction_file = "signalp6_slow_sequential/out/prediction_results.txt"
    signalp_out = parse_signalp_output(prediction_file)

    result = {
        "signal_peptide": signalp_out["prediction"] == "SP",
        "mature_seq": sequence[int(re.search(r"CS pos: (\d+)-\d+",signalp_out["cleavage_site"]).group(1)):] if signalp_out["cleavage_site"] else None,
    }
    return result

def parse_signalp_output(prediction_file):
    """
    Parse SignalP6 output file to extract prediction results.
    Returns dictionary with prediction information.
    """
    results = {}
    with open(prediction_file, 'r') as f:
        for line in f:
            if line.strip().startswith("seq"):
                fields = line.strip().split('\t')
                results = {
                    'id': fields[0],
                    'prediction': fields[1],
                    'no_sp_probability': float(fields[2]),
                    'sp_probability': float(fields[3]),
                    'cleavage_site': fields[4] if len(fields) > 4 else None
                    #'cleavage_conf': fields[5] if len(fields) > 4 else None
                }
    return results

import csv

def update_mature_sequences(input_csv: str, output_csv: str, log_file: str):
    """
    Processes mature sequences to check and potentially update using SignalP 6.0.

    Args:
        input_csv (str): Path to the input CSV file containing mature and full sequences.
        output_csv (str): Path to the output CSV file with updated mature sequences.
        log_file (str): Path to the log file recording changes made.
    """
    with open(input_csv, mode='r', encoding='utf-8-sig') as infile, \
         open(output_csv, mode='w', newline='', encoding='utf-8') as outfile, \
         open(log_file, mode='w', encoding='utf-8') as log:

        # Change the delimiter to semicolon
        reader = csv.DictReader(infile, delimiter=';')
        fieldnames = reader.fieldnames
        
        # Use the same delimiter for writing
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter=';')

        writer.writeheader()
        log.write("Changes Log\n")
        log.write("=" * 50 + "\n")

        for row in reader:
            mature_seq = row['mature_seq']
            full_seq = row['full_seq']

            # Run SignalP on the mature sequence
            mature_signalp_result = run_signalp(mature_seq, output_csv)
            print(mature_signalp_result)

            if mature_signalp_result["signal_peptide"]:
                full_there = False
                # Run SignalP on the full sequence
                if full_seq:
                    full_there = True
                    full_signalp_result = run_signalp(full_seq, output_csv)  # Added missing temp_path parameter
                    new_mature_seq = full_signalp_result["mature_seq"]

                # Compare and decide to update
                if full_there:
                    if new_mature_seq == mature_signalp_result["mature_seq"]:
                        row['mature_seq'] = new_mature_seq
                        log.write(f"Updated mature sequence for entry {row['Unique_ID']}:\n")  # Changed from 'id' to 'Unique_ID'
                        log.write(f"  Old: {mature_seq}\n")
                        log.write(f"  New: {new_mature_seq}\n")
                    else:
                        row['mature_seq'] = mature_seq
                else:
                    row['mature_seq'] = mature_signalp_result["mature_seq"]
                    row['full_seq'] = mature_seq
                    log.write(f"Updated mature sequence for entry {row['Unique_ID']}:\n")  # Changed from 'id' to 'Unique_ID'
                    log.write(f"  Old: {mature_seq}\n")
                    log.write(f'  New: {mature_signalp_result["mature_seq"]}\n')
                    log.write(f"Added full sequence for entry {row['Unique_ID']}:\n")  # Changed from 'id' to 'Unique_ID'
                    log.write(f"  New: {mature_seq}\n")
                    log.write("-" * 50 + "\n")
            else:
                log.write(f"{row['Unique_ID']}: no changes")
                row['mature_seq'] = mature_seq

            writer.writerow(row)

if __name__ == "__main__":
    input_csv_path = "Hym/Hymenoptera_toxins/Dataset_filtered_remove_uncertain_min_mature.csv"  # Replace with your input file path
    output_csv_path = "Hym/Hymenoptera_toxins/Dataset_filtered_remove_uncertain_min_mature_updated_mature.csv"  # Replace with your desired output file path
    log_file_path = "Hym/Hymenoptera_toxins/update_mature_signalp.log"  # Replace with your desired log file path

    update_mature_sequences(input_csv_path, output_csv_path, log_file_path)
