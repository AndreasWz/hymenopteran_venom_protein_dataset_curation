import argparse
import csv

def parse_csv_to_fasta(input_file, output_file):
    """
    Converts a CSV file to a FASTA file based on the provided rules.

    Args:
        input_file (str): Path to the input CSV file.
        output_file (str): Path to the output FASTA file.
    """
    with open(input_file, mode='r', encoding='utf-8') as csvfile, open(output_file, mode='w', encoding='utf-8') as fastafile:
        reader = csv.DictReader(csvfile, delimiter=';')
        # Remove BOM if it exists
        if reader.fieldnames[0].startswith('\ufeff'):
            reader.fieldnames[0] = reader.fieldnames[0][1:]  # Strip the BOM


        for row in reader:
            # Clean keys to avoid issues with whitespace or encoding
            row = {key.strip(): value for key, value in row.items()}

            # Extract columns
            unique_id = row.get('Unique_ID', 'unknown_id')
            venom_subtype = row.get('Venom_Family_Subtype', 'unknown_subtype')
            venom_type = row.get('Venom_Family_Type', 'unknown_type')

            # Add mature sequence entry
            if 'mature_seq' in row and row['mature_seq']:
                header = f">{unique_id}"
                sequence = row['mature_seq']
                fastafile.write(f"{header}\n{sequence}\n")

def main():
    parser = argparse.ArgumentParser(description="Convert a CSV file to a FASTA file.")
    parser.add_argument("input_file", type=str, help="Path to the input CSV file.")
    parser.add_argument("output_file", type=str, help="Path to the output FASTA file.")

    args = parser.parse_args()

    parse_csv_to_fasta(args.input_file, args.output_file)

if __name__ == "__main__":
    main()
