import csv
import sys
from pathlib import Path
import json

def parse_signalp_output(signalp_file):
    """Parse SignalP6.0 JSON output file to extract predicted signal peptides."""
    predicted_signals = {}

    with open(signalp_file, 'r') as sp_file:
        data = json.load(sp_file)
        for unique_id, details in data.get('SEQUENCES', {}).items():
            if details.get('Prediction') == "Signal Peptide (Sec/SPI)":
                cs_pos = details.get('CS_pos', '')
                if cs_pos:
                    # Extract cleavage site end position from CS_pos
                    try:
                        signal_peptide_end = int(cs_pos.split('between pos. ')[1].split(' and')[0].split('.')[0])
                        predicted_signals[unique_id] = signal_peptide_end
                    except (IndexError, ValueError):
                        continue

    return predicted_signals

def process_csv(input_csv, signalp_predictions):
    """Process the CSV file based on SignalP predictions."""
    updated_rows = []
    log_entries = []
    
    with open(input_csv, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')

        if reader.fieldnames[0].startswith('\ufeff'):
            reader.fieldnames[0] = reader.fieldnames[0][1:]  # Strip the BOM
        
        fieldnames = reader.fieldnames

        for row in reader:
            unique_id = row['Unique_ID']
            mature_seq = row['mature_seq']
            full_seq = row.get('full_seq', '')

            if unique_id in signalp_predictions:
                signal_peptide_end = signalp_predictions[unique_id]
                
                if full_seq:
                    updated_mature_seq = mature_seq[signal_peptide_end:]
                    log_entries.append(f"{unique_id}: ----------------------------------------------------------------------------------------------------------------------------------------------------------")
                    log_entries.append(f"{unique_id}: Signal peptide removed from mature_seq using full_seq. Updated mature_seq.")
                    log_entries.append(f"{unique_id}: old mature: {mature_seq}")
                    log_entries.append(f"{unique_id}: updated mature: {updated_mature_seq}")
                    log_entries.append(f"{unique_id}: ----------------------------------------------------------------------------------------------------------------------------------------------------------")
                else:
                    row['full_seq'] = mature_seq  # Promote mature_seq to full_seq
                    updated_mature_seq = mature_seq[signal_peptide_end:]
                    log_entries.append(f"{unique_id}: No full_seq. Promoted mature_seq to full_seq and updated mature_seq.")

                row['mature_seq'] = updated_mature_seq
            else:
                log_entries.append(f"{unique_id}: No signal peptide predicted. No changes made.")

            updated_rows.append(row)

    return fieldnames, updated_rows, log_entries

def save_updated_csv(output_csv, fieldnames, rows):
    """Save the updated rows to a new CSV file."""
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(rows)

def save_log_file(log_file, log_entries):
    """Save log entries to a log file."""
    with open(log_file, 'w', encoding='utf-8') as logfile:
        logfile.write("\n".join(log_entries))

def main():
    if len(sys.argv) != 4:
        print("Usage: python script.py <input_csv> <signalp_output_json> <output_dir>")
        sys.exit(1)

    input_csv = sys.argv[1]
    signalp_output = sys.argv[2]
    output_dir = Path(sys.argv[3])

    output_dir.mkdir(parents=True, exist_ok=True)

    output_csv = output_dir / "reworked_with_SignalP6_out.csv"
    log_file = output_dir / "reworked_with_SignalP6_out_logfile.log"

    signalp_predictions = parse_signalp_output(signalp_output)
    fieldnames, updated_rows, log_entries = process_csv(input_csv, signalp_predictions)

    save_updated_csv(output_csv, fieldnames, updated_rows)
    save_log_file(log_file, log_entries)

    print(f"Updated CSV saved to {output_csv}")
    print(f"Log file saved to {log_file}")

if __name__ == "__main__":
    main()
