# Hymenopteran Venom Dataset Curation

This repository documents the curation process applied to a dataset of venom proteins from Hymenopteran species. The goal was to ensure data quality and prepare the dataset for downstream analyses, such as evolutionary studies and functional annotation.

## Curation Overview

The dataset curation process involved the following steps:

### **Closed Curation Tasks**
1. **Check for Duplicates:**
   - Identified and removed redundant sequences to ensure protein uniqueness.

2. **Add Missing Mature Sequences:**
   - Filled in gaps by predicting and adding missing mature sequences where needed.

3. **Proteins Containing Gaps:**
   - Addressed proteins with alignment gaps to improve sequence quality.

4. **Check Mature Sequences for Signal Peptides:**
   - Used SignalP 6.0 to identify and verify signal peptides.
   - Updated mature sequences based on SignalP predictions.

5. **Check Mature Sequences for Propeptides**
   - Used DeepPeptide to identify and verify propeptides.
   - Updated mature sequences based on DeepPeptide predictions.

## Tools and Software
- **SignalP 6.0**: Used for signal peptide prediction.
   https://github.com/fteufel/signalp-6.0
- **DeepPeptide**: Used for Propeptide prediction
   https://github.com/fteufel/DeepPeptide
- Others (see scripts).

## Repository Structure
```
├── data/
│   ├── # Dataset in different versions
├── logs/
│   ├── # Logs generated from scripts
├── src/
│   ├── # Scripts
├── curated_Dataset.xlsx    # The curated dataset file
├── README.md               # Project documentation (this file)
```
