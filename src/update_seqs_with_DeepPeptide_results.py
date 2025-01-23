import json
import csv
import logging

# Configure logging
logging.basicConfig(
    filename="Hym/reworked_with_SignalP6_out_reworked_with_DeepPeptide_out_logfile.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Input file paths
dataset_path = "Hym/reworked_with_SignalP6_out.csv"  # Replace with your dataset file path
deeppeptide_output_path = "Hym/Hymenoptera_toxins/propeptide_prediction_DeepPeptide_23_01.json"  # Replace with your DeepPeptide output file path
output_path = "Hym/reworked_with_SignalP6_out_reworked_with_DeepPeptide_out.csv"

# Load DeepPeptide output
with open(deeppeptide_output_path, "r") as f:
    deeppeptide_data = json.load(f)

# Function to modify mature sequence based on DeepPeptide predictions
def process_mature_sequence(mature_seq, predictions):
    original_seq = mature_seq
    for peptide in predictions:
        start = peptide["start"] - 1  # Convert to 0-based index
        end = peptide["end"]  # End is exclusive
        type = str(peptide["type"])
        if type == "Propeptide":
            mature_seq = mature_seq[:start] + mature_seq[end:]

    return mature_seq, original_seq != mature_seq

# Process the dataset
with open(dataset_path, "r") as csvfile, open(output_path, "w", newline="") as outfile:
    reader = csv.DictReader(csvfile, delimiter=';')
    fieldnames = reader.fieldnames
    writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter=';')

    writer.writeheader()
    for row in reader:
        unique_id = row["Unique_ID"]
        mature_seq = row["mature_seq"]
        full_seq = row.get("full_seq", "")

        # Get predictions for this unique ID
        predictions = deeppeptide_data["PREDICTIONS"].get(f">{unique_id}", {}).get("peptides", [])

        if predictions:
            # Modify mature sequence
            new_mature_seq, changed = process_mature_sequence(mature_seq, predictions)
            if changed:
                logging.info(f"Entry {unique_id}: Mature sequence changed from {mature_seq} to {new_mature_seq}")
                row["mature_seq"] = new_mature_seq

                if not full_seq:
                    # Set old mature sequence as new full sequence only if changed
                    row["full_seq"] = mature_seq
                    logging.info(f"Entry {unique_id}: Full sequence was missing. Set to original mature sequence {mature_seq}")

        writer.writerow(row)

print(f"Processed dataset saved to {output_path}")
