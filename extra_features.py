"""
extra_features.py - ChemSportx Plug-and-Play Analytics Module
"""

import streamlit as st
import pandas as pd
from rdkit import Chem
from rdkit.Chem import DataStructs
from molecules import flat_library

def render_extra_features(mol, properties, smiles):
    """Renders 4 unique advanced sports-cheminformatics tools."""
    
    st.markdown("## 🏟️ ChemSportx Arena Analytics")
    st.caption("Advanced analytical tools and performance filters for the current molecule.")

    tab1, tab2, tab3, tab4 = st.tabs([
        "🏃‍♂️ Doping & BBB Screen", 
        "🔍 Functional Group Matcher", 
        "🌈 Chromophore & UV-Vis", 
        "🧬 Library Leaderboard"
    ])
    
    # -------------------------------------------------------------
    # 1. Doping & Central Nervous System (CNS) Screening
    # -------------------------------------------------------------
    with tab1:
        st.subheader("Anti-Doping & Bioavailability Filters")
        st.write("Evaluates molecular parameters against standard medicinal chemistry and pharmacokinetic rules.")
        
        mw = properties.get("Molecular Weight", 0)
        logp = properties.get("LogP", 0)
        tpsa = properties.get("TPSA", 0)
        hbd = properties.get("Hydrogen Bond Donors", 0)
        hba = properties.get("Hydrogen Bond Acceptors", 0)
        rot_bonds = properties.get("Rotatable Bonds", 0)
        
        # Lipinski Rule of 5
        lipinski_pass = (mw <= 500) and (logp <= 5) and (hbd <= 5) and (hba <= 10)
        
        # Veber Bioavailability Rule
        veber_pass = (rot_bonds <= 10) and (tpsa <= 140)
        
        # Blood-Brain Barrier (CNS) Penetration Heuristic
        cns_likely = (tpsa < 90) and (1.0 <= logp <= 4.0) and (mw < 400)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Lipinski's Rule of 5", "Passed 🟢" if lipinski_pass else "Failed 🔴", "Oral bioavailability filter")
        col2.metric("Veber Filter", "Passed 🟢" if veber_pass else "Failed 🔴", "Rotatable bonds & TPSA")
        col3.metric("Blood-Brain Barrier (BBB)", "Likely Penetrant 🧠" if cns_likely else "Poor Penetrant 🛡️", "CNS activity profile")

    # -------------------------------------------------------------
    # 2. Functional Group Substructure Matcher
    # -------------------------------------------------------------
    with tab2:
        st.subheader("Automated Reactive Group Finder")
        st.write("Scans the molecular structure for key chemical functional groups using SMARTS patterns.")
        
        patterns = {
            "Hydroxyl (-OH, Alcohol/Phenol)": "[OX2H]",
            "Carboxylic Acid (-COOH)": "C(=O)[OX2H1]",
            "Primary Amine (-NH2)": "[NX3H2]",
            "Carbonyl (C=O)": "[CX3](=O)[#6,#1]",
            "Aromatic Ring System": "a1aaaaa1",
            "Ether (C-O-C)": "[OD2]([#6])[#6]",
            "Halogen (-Cl, -Br, -I, -F)": "[F,Cl,Br,I]"
        }
        
        found_groups = []
        for name, smarts in patterns.items():
            patt = Chem.MolFromSmarts(smarts)
            if patt and mol.HasSubstructMatch(patt):
                matches = mol.GetSubstructMatches(patt)
                found_groups.append({"Functional Group": name, "Matches Found": len(matches)})
                
        if found_groups:
            st.dataframe(pd.DataFrame(found_groups), use_container_width=True, hide_index=True)
        else:
            st.info("No standard matched functional groups found in this molecule.")

    # -------------------------------------------------------------
    # 3. Chromophore & UV-Vis Estimator
    # -------------------------------------------------------------
    with tab3:
        st.subheader("Conjugation & Light Absorption Estimator")
        st.write("Estimates UV-Vis absorption wavelength peak based on conjugated double bonds and aromatic rings.")
        
        pi_bonds = properties.get("Pi (π) Bonds", 0)
        aromatic_rings = properties.get("Aromatic Rings", 0)
        
        # Empirical estimation formula for absorption peak
        estimated_lambda = 200 + (pi_bonds * 15) + (aromatic_rings * 35)
        
        col1, col2 = st.columns(2)
        col1.metric("Estimated λ_max", f"~{estimated_lambda} nm", "Predicted peak absorption wavelength")
        
        if estimated_lambda > 380:
            col2.success("Visible Light Spectrum 🌈 (Likely a colored compound/pigment)")
        else:
            col2.info("UV Spectrum Active 紫外 (Typically colorless under normal light)")

    # -------------------------------------------------------------
    # 4. Tanimoto Library Similarity Leaderboard
    # -------------------------------------------------------------
    with tab4:
        st.subheader("Chemical Similarity Leaderboard")
        st.write("Calculates Tanimoto similarity against all 100+ molecules in `molecules.py` using Morgan Fingerprints.")
        
        if st.button("🚀 Calculate Top Similar Molecules"):
            with st.spinner("Screening molecule library..."):
                from rdkit.Chem import AllChem
                
                ref_fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=1024)
                all_mols = flat_library()
                scores = []
                
                for name, ref_smiles in all_mols.items():
                    m = Chem.MolFromSmiles(ref_smiles)
                    if m:
                        fp = AllChem.GetMorganFingerprintAsBitVect(m, 2, nBits=1024)
                        sim = DataStructs.TanimotoSimilarity(ref_fp, fp)
                        scores.append({"Molecule": name, "SMILES": ref_smiles, "Similarity Score": round(sim, 3)})
                        
                df_sim = pd.DataFrame(scores).sort_values(by="Similarity Score", ascending=False).head(5)
                st.dataframe(df_sim, use_container_width=True, hide_index=True)
