import csv
import subprocess
import os
import re
from typing import List, Dict
from multiprocessing import Pool

def create_fasta_from_seq(sequence, identifier, filename):
    """Create a FASTA file from a sequence."""
    with open(filename, 'w') as f:
        f.write(f">{identifier}\n{sequence}\n")

def run_signalp(sequence: str, process_id: int) -> Dict[str, str]:
    """
    Runs SignalP 6.0 on a given sequence.

    Args:
        sequence (str): The protein sequence to analyze.
        process_id (int): Unique process identifier for parallel processing

    Returns:
        Dict[str, str]: A dictionary containing SignalP results, including 'mature_seq'.
    """
    # Create process-specific file names
    fasta_file = f"signalp6_slow_sequential/out/tmp_fasta_{process_id}.fna"
    output_dir = f"signalp6_slow_sequential/out/process_{process_id}"
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    create_fasta_from_seq(sequence, "seq", fasta_file)

    subprocess.run(
        [
            "signalp6",
            "--fastafile", f"out/tmp_fasta_{process_id}.fna",
            "--organism", "eukarya",
            "--output_dir", f"out/process_{process_id}",
            "--format", "txt",
            "--mode", "slow"
        ],
        cwd="signalp6_slow_sequential",
        check=True
    )
    
    prediction_file = f"{output_dir}/prediction_results.txt"
    signalp_out = parse_signalp_output(prediction_file)

    # Clean up process-specific files
    try:
        os.remove(fasta_file)
        os.remove(prediction_file)
        os.rmdir(output_dir)
    except OSError:
        pass

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
                }
    return results

def process_row(args):
    """
    Process a single row of data with SignalP.
    
    Args:
        args (tuple): Tuple containing (row_dict, process_id)
    
    Returns:
        Dict: Updated row data
    """
    row, process_id = args
    mature_seq = row['mature_seq']
    full_seq = row['full_seq']

    # Run SignalP on the mature sequence
    mature_signalp_result = run_signalp(mature_seq, process_id)
    
    if mature_signalp_result["signal_peptide"]:
        full_there = False
        # Run SignalP on the full sequence
        if full_seq:
            full_there = True
            full_signalp_result = run_signalp(full_seq, process_id)
            new_mature_seq = full_signalp_result["mature_seq"]

        # Compare and decide to update
        if full_there:
            if new_mature_seq == mature_signalp_result["mature_seq"]:
                row['mature_seq'] = new_mature_seq
                row['_log'] = f"Updated mature sequence for entry {row['Unique_ID']}:\nOld: {mature_seq}\nNew: {new_mature_seq}\n"
            else:
                row['mature_seq'] = mature_seq
                row['_log'] = f"{row['Unique_ID']}: no changes"
        else:
            row['mature_seq'] = mature_signalp_result["mature_seq"]
            row['full_seq'] = mature_seq
            row['_log'] = (f"Updated mature sequence for entry {row['Unique_ID']}:\n"
                          f"Old: {mature_seq}\n"
                          f"New: {mature_signalp_result['mature_seq']}\n"
                          f"Added full sequence for entry {row['Unique_ID']}:\n"
                          f"New: {mature_seq}\n" + "-" * 50 + "\n")
    else:
        row['_log'] = f"{row['Unique_ID']}: no changes"
        row['mature_seq'] = mature_seq

    return row

def update_mature_sequences(input_csv: str, output_csv: str, log_file: str, num_processes: int = 4):
    """
    Processes mature sequences to check and potentially update using SignalP 6.0.

    Args:
        input_csv (str): Path to the input CSV file containing mature and full sequences.
        output_csv (str): Path to the output CSV file with updated mature sequences.
        log_file (str): Path to the log file recording changes made.
        num_processes (int): Number of parallel processes to use.
    """
    # Read all rows into memory
    with open(input_csv, mode='r', encoding='utf-8-sig') as infile:
        reader = csv.DictReader(infile, delimiter=';')
        rows = list(reader)
        fieldnames = reader.fieldnames

    # Create a pool of workers
    with Pool(num_processes) as pool:
        # Create list of (row, process_id) tuples for processing
        row_args = [(row, i) for i, row in enumerate(rows)]
        # Process rows in parallel
        processed_rows = pool.map(process_row, row_args)

    # Write results and logs
    with open(output_csv, mode='w', newline='', encoding='utf-8') as outfile, \
         open(log_file, mode='w', encoding='utf-8') as log:

        writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()

        log.write("Changes Log\n")
        log.write("=" * 50 + "\n")

        for row in processed_rows:
            # Write log entry
            log.write(row.pop('_log', '') + "\n")
            # Write updated row
            writer.writerow(row)

if __name__ == "__main__":
    input_csv_path = "Hym/Hymenoptera_toxins/Dataset_filtered_remove_uncertain_min_mature.csv"  # Replace with your input file path
    output_csv_path = "Hym/Hymenoptera_toxins/Dataset_filtered_remove_uncertain_min_mature_updated_mature.csv"  # Replace with your desired output file path
    log_file_path = "Hym/Hymenoptera_toxins/update_mature_signalp.log"  # Replace with your desired log file path

    # Use 4 processes by default, but you can adjust this based on your system
    update_mature_sequences(input_csv_path, output_csv_path, log_file_path, num_processes=8)