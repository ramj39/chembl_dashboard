# chembl_dashboard
# 🧬 ChEMBL Cheminformatics Dashboard

A powerful, interactive Streamlit app for exploring molecular properties, bioactivity data, and compound similarity using the ChEMBL database and RDKit.

---

## 🚀 Features

- 🔍 **Compound Explorer**  
  Enter multiple compound names to:
  - Resolve ChEMBL IDs
  - Display molecular structures
  - View key properties (MW, logP, HBA/HBD, RO5 violations)
  - Export results to Excel

- 🎯 **Bioactivity Explorer**  
  Input a ChEMBL ID to:
  - Retrieve assay data (IC50, Ki, etc.)
  - View target organisms and types
  - Export bioactivity data to Excel

- 🔎 **Similar Compound Finder**  
  Input a SMILES string to:
  - Compute Tanimoto similarity using RDKit
  - Compare against known ChEMBL compounds
  - View and rank similar molecules
## 🗂 Legacy Scripts

Older versions of the app are stored in the `legacy/` folder for reference. These may contain experimental features or earlier designs.

---

## 📦 Installation

1. Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/chembl-dashboard.git
cd chembl-dashboard
