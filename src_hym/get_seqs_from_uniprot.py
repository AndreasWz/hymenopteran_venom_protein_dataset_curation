#!/usr/bin/env python3
"""
Fetch missing sequences from UniProt using UniProt IDs in the dataset.

This script identifies rows in a CSV dataset where both mature and full sequences 
are missing but a UniProt ID is present. It fetches the corresponding sequences 
from UniProt and generates a new dataset with these entries.

Features:
- Checks for both mature and full sequences
- Only processes entries where both sequences are missing
- Detailed logging of all operations
- Robust error handling
- Progress tracking
"""

import csv
import requests
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple

def setup_logging(log_dir: Path) -> None:
    """
    Set up logging configuration.
    
    Args:
        log_dir: Directory where log file should be created
    """
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"uniprot_fetch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def fetch_uniprot_sequence(uniprot_id: str) -> Optional[str]:
    """
    Fetches the protein sequence for a given UniProt ID using the UniProt API.
    
    Args:
        uniprot_id: The UniProt ID
    
    Returns:
        The protein sequence, or None if not found
    """
    url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.fasta"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        fasta = response.text
        # Extract sequence from FASTA format
        lines = fasta.split("\n")
        sequence = "".join(line.strip() for line in lines if not line.startswith(">"))
        
        if sequence:
            logging.info(f"Successfully fetched sequence for {uniprot_id} ({len(sequence)} bp)")
            return sequence
        else:
            logging.warning(f"Empty sequence returned for {uniprot_id}")
            return None
            
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch sequence for UniProt ID {uniprot_id}: {str(e)}")
        return None

def process_dataset(input_file: Path, output_file: Path) -> Tuple[int, int, int]:
    """
    Process the dataset and fetch missing sequences.
    
    Args:
        input_file: Path to input CSV file
        output_file: Path to output CSV file
    
    Returns:
        Tuple of (total_processed, missing_sequences, successful_fetches)
    """
    total_processed = 0
    missing_sequences = 0
    successful_fetches = 0
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            
            reader = csv.reader(infile, delimiter=';')
            writer = csv.writer(outfile, delimiter=';')
            
            # Write header
            header = next(reader)
            writer.writerow(header)
            
            for row in reader:
                total_processed += 1
                if total_processed % 100 == 0:
                    logging.info(f"Processed {total_processed} rows...")
                
                uniprot_id = row[7].strip()  # Column 8: UniProt ID
                mature_seq = row[9].strip()   # Column 10: Mature Sequence
                full_seq = row[10].strip()    # Column 11: Full Sequence
                
                # Skip rows that have either sequence
                if mature_seq or full_seq:
                    #writer.writerow(row)
                    continue
                
                # Both sequences missing and UniProt ID present
                if uniprot_id:
                    missing_sequences += 1
                    logging.info(f"Found missing sequences for {uniprot_id} at line {total_processed + 1}")
                    
                    fetched_sequence = fetch_uniprot_sequence(uniprot_id)
                    if fetched_sequence:
                        # Only add to full_seq, leaving mature_seq empty
                        row[10] = fetched_sequence
                        successful_fetches += 1
                    else:
                        logging.warning(f"Could not fetch sequence for {uniprot_id}")
                    
                    writer.writerow(row)
                #else:
                    # No sequences and no UniProt ID
                    #writer.writerow(row)
                    
    except Exception as e:
        logging.error(f"Error processing dataset: {str(e)}")
        raise
    
    return total_processed, missing_sequences, successful_fetches

def main():
    """Main execution function."""
    # Configure paths
    base_path = Path("Hym/Hymenoptera_toxins")
    input_file = base_path / "Dataset_filtered_remove_uncertain.csv"
    output_file = base_path / "Dataset_filtered_remove_uncertain_with_fetched_sequences.csv"
    log_dir = base_path / "logs"
    
    # Setup logging
    setup_logging(log_dir)
    logging.info("Starting UniProt sequence fetch process")
    logging.info(f"Input file: {input_file}")
    logging.info(f"Output file: {output_file}")
    
    try:
        # Process dataset
        total, missing, fetched = process_dataset(input_file, output_file)
        
        # Log summary statistics
        logging.info("\nProcess completed successfully!")
        logging.info(f"Total rows processed: {total}")
        logging.info(f"Rows with missing sequences: {missing}")
        logging.info(f"Successful sequence fetches: {fetched}")
        logging.info(f"Updated dataset saved to {output_file}")
        
    except Exception as e:
        logging.error(f"Process failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()