# Hymenopteran Venom Dataset Curation

This repository documents the curation process applied to a dataset of venom proteins from Hymenopteran species. The goal was to ensure data quality and prepare the dataset for downstream analyses, such as evolutionary studies and functional annotation.

## Curation Overview

The dataset curation process involved the following steps:

### **Closed Curation Tasks**
1. **Check for Duplicates:**
   - Identified and removed redundant sequences to ensure protein uniqueness.

2. **Check Mature Sequences for Signal Peptides:**
   - Used SignalP 6.0 to identify and verify signal peptides.
   - Updated mature sequences based on SignalP predictions.

3. **Add Missing Mature Sequences:**
   - Filled in gaps by predicting and adding missing mature sequences where needed.

### **Open Curation Tasks**
1. **Proteins Identical in Different Organisms:**
   - Investigated proteins that were identical across different species, which are currently removed.

2. **Proteins Containing Gaps:**
   - Addressed proteins with alignment or sequence gaps to improve sequence quality.

3. **Add Full Sequences if Missing:**
   - Found full sequences in the source organism if mature regions were incomplete.
   - Retrieved prefixes and predicted signal peptides for these sequences.

## Tools and Software
- **SignalP 6.0**: Used for signal peptide prediction.
- Others (details provided in associated scripts).

## Repository Structure
```
├── data_and_logs/
│   ├── # Log files generated from scripts, dataset in different stages
├── src_hym/
│   ├── # Scripts
├── curated_Dataset.xlsx    # The curated dataset file
├── README.md               # Project documentation (this file)
```
