import os

def rename_genome_files(folder_path):
    # Loop through all files in the specified folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        # Skip non-files
        if not os.path.isfile(file_path):
            continue

        # Read the first line of the file
        with open(file_path, 'r') as file:
            first_line = file.readline().strip()

            # Check if the line starts with ">"
            if first_line.startswith(">"):
                # Extract the species name after the first space
                parts = first_line.split()
                if len(parts) > 1:
                    species_name = f"{parts[1]}_{parts[2]}"
                    # Replace spaces with underscores in species name
                    species_name = species_name.replace(" ", "_")
                    # Create new filename
                    new_filename = f"{species_name}_genomic.fna"
                    new_file_path = os.path.join(folder_path, new_filename)

                    # Rename the file
                    os.rename(file_path, new_file_path)
                    print(f"Renamed: {filename} -> {new_filename}")
                else:
                    print(f"Could not extract species name from: {filename}")
            else:
                print(f"First line of {filename} does not start with '>'")

# Example usage
folder_path = "Hym/Hym_genomes"  # Replace with your folder path
rename_genome_files(folder_path)
