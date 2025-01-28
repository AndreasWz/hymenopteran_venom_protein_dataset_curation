import argparse
import csv

def parse_csv_to_fasta(input_file: str, output_file: str) -> None:
    """
    Converts a CSV file to a FASTA file based on the provided rules.

    Args:
        input_file (str): Path to the input CSV file.
        output_file (str): Path to the output FASTA file.
    """
    with open(input_file, mode="r", encoding="utf-8") as csvfile, open(output_file, mode="w", encoding="utf-8") as fastafile:
        reader = csv.DictReader(csvfile, delimiter=",")

        # Remove BOM from the first field name if it exists
        if reader.fieldnames and reader.fieldnames[0].startswith("\ufeff"):
            reader.fieldnames[0] = reader.fieldnames[0][1:]

        for row in reader:
            # Clean keys to avoid issues with whitespace or encoding
            cleaned_row = {key.strip(): value for key, value in row.items()}

            # Extract columns with default values if keys are missing
            unique_id = cleaned_row.get("Unique_ID", "unknown_id")

            # Write mature sequence entry to the FASTA file
            mature_seq = cleaned_row.get("mature_seq")
            if mature_seq:
                fastafile.write(f">{unique_id}\n{mature_seq}\n")


def main() -> None:
    """
    Main function to handle argument parsing and initiate CSV to FASTA conversion.
    """
    parser = argparse.ArgumentParser(description="Convert a CSV file to a FASTA file.")
    parser.add_argument("input_file", type=str, help="Path to the input CSV file.")
    parser.add_argument("output_file", type=str, help="Path to the output FASTA file.")

    args = parser.parse_args()
    parse_csv_to_fasta(args.input_file, args.output_file)


if __name__ == "__main__":
    main()
