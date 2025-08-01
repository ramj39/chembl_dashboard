import streamlit as st
from chembl_webresource_client.new_client import new_client
from rdkit import Chem
from rdkit.Chem import Draw, AllChem, DataStructs
import pandas as pd
import io

# ChEMBL clients
molecule_client = new_client.molecule
activity_client = new_client.activity

st.title("🔬 ChEMBL Cheminformatics Dashboard")

# Tabs for modular tools
tab1, tab2, tab3 = st.tabs(["🧪 Compound Explorer", "🎯 Bioactivity Explorer", "🔍 Similar Compounds"])

# -------------------------------
# 🧪 Tab 1: Compound Explorer
# -------------------------------
with tab1:
    compound_list = st.text_area("Enter compound names (one per line)").splitlines()
    if compound_list:
        all_data = []
        smiles_dict = {}

        for compound_name in compound_list:
            st.subheader(f"🔍 {compound_name}")
            results = molecule_client.filter(pref_name__iexact=compound_name).only(
                ['molecule_chembl_id', 'molecule_structures', 'molecule_properties']
            )

            if results:
                mol_data = results[0]
                chembl_id = mol_data['molecule_chembl_id']
                props = mol_data.get('molecule_properties', {})
                smiles = mol_data.get('molecule_structures', {}).get('canonical_smiles', None)

                st.markdown(f"**ChEMBL ID:** `{chembl_id}`")
                if smiles:
                    mol = Chem.MolFromSmiles(smiles)
                    st.image(Draw.MolToImage(mol, size=(250, 250)), caption=compound_name)
                    smiles_dict[compound_name] = smiles

                display_props = {
                    'Compound Name': compound_name,
                    'ChEMBL ID': chembl_id,
                    'SMILES': smiles,
                    'Molecular Weight': props.get('full_mwt', 'N/A'),
                    'AlogP': props.get('alogp', 'N/A'),
                    'HBA': props.get('hba', 'N/A'),
                    'HBD': props.get('hbd', 'N/A'),
                    'RO5 Violations': props.get('num_ro5_violations', 'N/A')
                }

                st.dataframe(pd.DataFrame([display_props]))
                all_data.append(display_props)
            else:
                st.warning(f"No compound found for '{compound_name}'.")

        if all_data:
            df_export = pd.DataFrame(all_data)
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_export.to_excel(writer, index=False, sheet_name='Compound Properties')
            buffer.seek(0)

            st.download_button(
                label="📥 Download All Properties as Excel",
                data=buffer,
                file_name="chembl_compound_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# -------------------------------
# 🎯 Tab 2: Bioactivity Explorer
# -------------------------------
with tab2:
    chembl_id_input = st.text_input("Enter ChEMBL ID (e.g., CHEMBL25 for aspirin)")
    if chembl_id_input:
        st.subheader(f"🔬 Bioactivity Data for {chembl_id_input}")
        activities = activity_client.filter(molecule_chembl_id=chembl_id_input).only(
            ['target_chembl_id', 'target_organism', 'standard_type', 'standard_value', 'standard_units']
        )
        if activities:
            df_bio = pd.DataFrame(activities)
            st.dataframe(df_bio)
            bio_buffer = io.BytesIO()
            with pd.ExcelWriter(bio_buffer, engine='xlsxwriter') as writer:
                df_bio.to_excel(writer, index=False, sheet_name='Bioactivity')
            bio_buffer.seek(0)

            st.download_button(
                label="📥 Download Bioactivity Data",
                data=bio_buffer,
                file_name=f"{chembl_id_input}_bioactivity.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("No bioactivity data found.")

# -------------------------------
# 🔍 Tab 3: Similar Compounds
# -------------------------------
with tab3:
    query_smiles = st.text_input("Enter SMILES to find similar compounds")
    if query_smiles:
        try:
            query_mol = Chem.MolFromSmiles(query_smiles)
            query_fp = AllChem.GetMorganFingerprintAsBitVect(query_mol, 2, nBits=2048)

            st.info("🔍 Comparing against known ChEMBL molecules...")

            # Sample set of ChEMBL molecules (for demo purposes)
            sample_names = ["aspirin", "ibuprofen", "acetaminophen", "caffeine", "acetone"]
            sim_data = []

            for name in sample_names:
                res = molecule_client.filter(pref_name__iexact=name).only(['molecule_chembl_id', 'molecule_structures'])
                if res:
                    smiles = res[0].get('molecule_structures', {}).get('canonical_smiles', None)
                    if smiles:
                        mol = Chem.MolFromSmiles(smiles)
                        fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)
                        sim = DataStructs.TanimotoSimilarity(query_fp, fp)
                        sim_data.append({
                            "Name": name,
                            "SMILES": smiles,
                            "Similarity": round(sim, 3)
                        })

            df_sim = pd.DataFrame(sim_data).sort_values(by="Similarity", ascending=False)
            st.dataframe(df_sim)

        except Exception as e:
            st.error(f"Invalid SMILES. Please check your input. Error: {str(e)}")
