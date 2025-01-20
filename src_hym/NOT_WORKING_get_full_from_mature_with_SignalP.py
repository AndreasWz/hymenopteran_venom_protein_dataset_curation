import pandas as pd
import subprocess
import tempfile
import os
import sys
sys.path.append('ant_repo/src')
import get_seqs_with_fna_and_gff

"""
This script was initially generated with AI assistance and subsequently refined.
"""

def create_fasta_from_seq(sequence, identifier, filename):
    """Create a FASTA file from a sequence."""
    with open(filename, 'w') as f:
        f.write(f">{identifier}\n{sequence}\n")

def run_mmseqs_search(query_fasta, target_db):
    """
    Run MMseqs2 easysearch against target database.
    Returns the path to the results file.
    """
    output_file = query_fasta + ".m8"
    
    # Run mmseqs easysearch with sensitivity 7.0
    subprocess.run([
        "mmseqs", "easy-search", 
        query_fasta,
        target_db,
        output_file,
        "tmp",
        "-s", "7.0"
    ], check=True)
    
    return output_file

def sanitize_attribute(value):
        """
        Replace problematic characters in attributes (like embedded `=`) to conform to GFF standards.
        """
        return value.replace("=", "_").replace(";", "_")

def parse_mmseqs_results(result_file):
    """
    Parse MMseqs2 m8 format results file to find the best hit.
    Returns tuple of (target_id, start_pos, end_pos) for the best match
    """
    best_hit = None
    max_bitscore = 0
    
    with open(result_file, 'r') as f:
        for line in f:
            print(line)
            # Parse m8 format:
            # query, target, pident, alnlen, mismatch, gapopen, qstart, qend, tstart, tend, evalue, bits
            columns = line.strip().split('\t')
            query_id = sanitize_attribute(columns[0])
            subject_id = columns[1]
            percent_identity = columns[2]
            alignment_length = columns[3]
            subject_start = int(columns[8])
            subject_end = int(columns[9])
            e_value = columns[10]
            bit_score = columns[11]
            print(percent_identity)
            if int(percent_identity*1000) == 1000:
                print("#################hello#####################")
                if alignment_length > max_bitscore:
                    max_bitscore = bit_score
                    best_hit = (subject_id, subject_start, subject_end)

    return best_hit

def run_signalp(sequence, identifier, output_dir):
    """
    Run SignalP 6.0 on a sequence.
    Returns the predicted signal peptide information.
    """
    fasta_file = os.path.join(output_dir, f"{identifier}.fasta")
    create_fasta_from_seq(sequence, identifier, fasta_file)
    
    # Run SignalP6
    subprocess.run([
        "signalp6", 
        "--fastafile", fasta_file,
        "--output_dir", output_dir,
        "--format", "none"
    ], check=True)
    
    # Parse SignalP output
    prediction_file = os.path.join(output_dir, "prediction_results.txt")
    return parse_signalp_output(prediction_file)

def parse_signalp_output(prediction_file):
    """
    Parse SignalP6 output file to extract prediction results.
    Returns dictionary with prediction information.
    """
    results = {}
    with open(prediction_file, 'r') as f:
        # Skip header line
        next(f)
        # Read prediction line
        line = next(f)
        fields = line.strip().split('\t')
        results = {
            'id': fields[0],
            'prediction': fields[1],
            'sp_probability': float(fields[2]),
            'cleavage_site': int(fields[3]) if len(fields) > 3 else None
        }
    return results

def process_sequences(csv_file):
    """
    Main function to process the CSV file and identify sequences needing completion.
    Returns a list of tuples containing (unique_id, mature_seq, species_id) for processing.
    """
    # Read the CSV
    df = pd.read_csv(csv_file, sep=';')
    
    # Find entries with mature_seq but no full_seq
    sequences_to_process = []
    for _, row in df.iterrows():
        if pd.notna(row['mature_seq']) and pd.isna(row['full_seq']):
            sequences_to_process.append({
                'unique_id': row['Unique_ID'],
                'mature_seq': row['mature_seq'],
                'Species': row['Species']
            })
    
    return sequences_to_process

def main():
    """
    Main workflow function.
    Note: File paths and sequence extraction will be handled externally.
    """
    csv_file = "Hym/Hymenoptera_toxins/Dataset_filtered_remove_uncertain_min_mature.csv"
    
    # Get sequences that need processing
    sequences_to_process = process_sequences(csv_file)
    
    # Process each sequence
    for seq_info in sequences_to_process:
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create query FASTA
            query_fasta = os.path.join(temp_dir, f"{seq_info['unique_id']}.fasta")
            create_fasta_from_seq(seq_info['mature_seq'], seq_info['unique_id'], query_fasta)
            
            # Run MMseqs2 search
            # Note: target_db path would be provided externally
            print(seq_info['Species'])
            target_db = f"Hym/Hym_genomes/{seq_info['Species'].replace(' ', '_')}_genomic.fna"
            
            result_file = None

            if os.path.isfile(target_db):
                result_file = run_mmseqs_search(query_fasta, target_db)
            
        
                # Parse results
                if result_file:
                    print("mmseqs run done")
                    best_hit = parse_mmseqs_results(result_file)
                else:
                    best_hit = None
                    raise KeyError("Error in mmseqs")
                
                if best_hit:
                    target_id, start_pos, end_pos = best_hit
                    print(f"Found match for {seq_info['unique_id']}:")
                    print(f"Target: {target_id}")
                    print(f"Position: {start_pos}-{end_pos}")
                    


                    # At this point, you would extract the sequence from the genome file
                    full_sequence = get_seqs_with_fna_and_gff.extract_sequences_from_genomes(target_id, start_pos, end_pos, "ant_data/genomes_no_folder_structure")
                    
                    # Once you have the full sequence, run SignalP
                    signalp_results = run_signalp(full_sequence, seq_info['unique_id'], temp_dir)
                    
                    # Print SignalP results
                    print(f"SignalP results for {seq_info['unique_id']}:")
                    print(f"Prediction: {signalp_results['prediction']}")
                    print(f"Signal peptide probability: {signalp_results['sp_probability']}")
                    if signalp_results['cleavage_site']:
                        print(f"Cleavage site: {signalp_results['cleavage_site']}")
                else:
                    raise KeyError("Error parsing mmseqs output")
            else:
                print(f"{target_db} is missing")

if __name__ == "__main__":
    main()