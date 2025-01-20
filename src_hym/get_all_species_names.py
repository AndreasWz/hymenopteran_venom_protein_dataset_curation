import csv

def extract_unique_species(file_path):
    species_set = set()

    with open(file_path, 'r') as csv_file:
        reader = csv.DictReader(csv_file, delimiter=';')
        for row in reader:
            species = row['Species']
            if species:
                species_set.add(species)
    
    return sorted(species_set)

# Replace 'your_file.csv' with the actual path to your CSV file
file_path = 'Hym/Hymenoptera_toxins/Dataset_filtered_remove_uncertain_min_mature.csv'
unique_species = extract_unique_species(file_path)

# Output the unique species
for species in unique_species:
    print(species)
