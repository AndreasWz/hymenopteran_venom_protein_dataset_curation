#!/usr/bin/env python3
import argparse
import sys

def convert_to_fasta(input_file, output_file=None):
    """
    Convert semicolon-delimited data to FASTA format.

    Args:
        input_file (str): Path to input file
        output_file (str, optional): Path to output file. If None, prints to stdout
    """
    try:
        # Read input file
        with open(input_file, 'r') as f:
            lines = f.readlines()

            # Prepare output
            output_lines = []

            # Process each line, skipping the header
            for line in lines[1:]:
                columns = line.strip().split(';')

                # Extract data by column index
                unique_id = columns[0]
                full_seq = columns[10].strip()
                mature_seq = columns[9].strip()

                # Use the first non-empty sequence (prefer full_seq)
                sequence = full_seq or mature_seq

                if not sequence:
                    continue

                # Format the FASTA entry
                header = f">{unique_id}"
                # Wrap sequence at 80 characters
                wrapped_seq = '\n'.join([sequence[i:i+80] for i in range(0, len(sequence), 80)])

                output_lines.extend([header, wrapped_seq])

            # Join all lines
            fasta_content = '\n'.join(output_lines)

            # Write output
            if output_file:
                with open(output_file, 'w') as out:
                    out.write(fasta_content)
            else:
                print(fasta_content)

    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}", file=sys.stderr)
        sys.exit(1)

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Convert semicolon-delimited sequence data to FASTA format'
    )
    parser.add_argument(
        'input_file',
        type=str,
        help='Input file path (semicolon-delimited)'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output file path (optional, defaults to stdout)',
        default=None
    )

    # Parse arguments
    args = parser.parse_args()

    # Convert the file
    convert_to_fasta(args.input_file, args.output)

if __name__ == '__main__':
    main()
