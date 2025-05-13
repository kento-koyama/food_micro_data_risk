import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.font_manager as fm
import re

# === Formatting Functions ===
def format_bacteria_name_latex(name):
    if pd.isna(name):
        return name
    spp_match = re.match(r'^([A-Z][a-z]+)\s+(spp?\.)$', name)
    if spp_match:
        genus, spp = spp_match.groups()
        return rf"$\it{{{genus}}}$ {spp}"
    match = re.match(r'^([A-Z][a-z]+)\s+([a-z]+)(.*)$', name)
    if match:
        genus, species, rest = match.groups()
        return rf"$\it{{{genus}\ {species}}}${rest}"
    return rf"$\it{{{name}}}$"

def func_round(number, ndigits=0):
    if pd.isna(number):
        return np.nan
    p = 10 ** ndigits
    return float(int(number * p + 0.5) / p)

def convert_to_mpn_per_g(row):
    if isinstance(row['Unit'], str) and 'MPN/' in row['Unit']:
        match = re.search(r'MPN/(\d+)g', row['Unit'])
        weight = int(match.group(1)) if match else 1
        return row['Concentration'] / weight
    return np.nan

def format_number(number, ndigits=0):
    formatted = f"{number:.{ndigits}f}".rstrip('0').rstrip('.')
    return formatted

def calc_df_height(df, max_rows=5, row_height=35):
    return row_height * (min(len(df), max_rows) + 1)

# === Streamlit Setup ===
st.set_page_config(layout="wide", initial_sidebar_state="expanded")
font_path = 'NotoSansCJKjp-Regular.otf'
fm.fontManager.addfont(font_path)
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['text.usetex'] = False

# === Load Data ===
csv_url = "https://raw.githubusercontent.com/kento-koyama/food_micro_data_risk/main/database/concentration_of_contamination.csv"
csv_url_gui = "https://github.com/kento-koyama/food_micro_data_risk/blob/main/database/concentration_of_contamination.csv"
df = pd.read_csv(csv_url, encoding='utf-8-sig')

# === Data Cleaning ===
df = df[~((df['Concentration'] == 'Not Detected') |
          (df['Concentration'] == '-') |
          (df['Concentration'].isna()) |
          (df['Concentration'].astype(str).str.contains('<')))]
df = df[~(df['Food Category'].isna() & df['Food Name'].isna())]
df = df[(df['Unit'].isin(['log CFU/g', 'CFU/g'])) | (df['Method'] == 'MPN')]
df['Concentration'] = pd.to_numeric(df['Concentration'], errors='coerce')
df = df[~df['Concentration'].isna()]

# === Concentration Transformation ===
df['MPN per g'] = df.apply(lambda row: convert_to_mpn_per_g(row) if 'MPN' in str(row['Unit']) else np.nan, axis=1)
df['log CFU/g'] = np.where(df['Unit'].str.contains('MPN', na=False),
                            np.log10(df['MPN per g']),
                            np.where(df['Unit'] == 'CFU/g',
                                     np.log10(df['Concentration']),
                                     df['Concentration']))
df['log CFU/g'] = df['log CFU/g'].apply(lambda x: func_round(x, ndigits=2))
df['Organism_Detail'] = df['Organism']
df['Organism'] = df['Organism'].apply(lambda x: 'Campylobacter spp.' if 'Campylobacter' in str(x) else x)
df['Organism_LaTeX'] = df['Organism'].apply(format_bacteria_name_latex)

# === UI ===
st.title("Contamination Concentration of Foodborne Bacteria")
st.write("Visualization of [concentration_of_contamination.csv]"% csv_url_gui)
st.write("Each table can be downloaded as a CSV.")
st.write("-----------")
st.sidebar.title("Filter Options")

# === Filters ===
cat_opts = ["", "All"] + list(df['Food Category'].dropna().unique())
name_opts = ["", "All"] + list(df['Food Name'].dropna().unique())
bact_opts = ["", "All"] + list(df['Organism'].dropna().unique())
inst_opts = ["", "All"] + list(df['Agency'].dropna().unique())

sel_cat = st.sidebar.selectbox("Select Food Category:", cat_opts)
df_filtered = df if sel_cat in ["", "All"] else df[df['Food Category'] == sel_cat]

sel_name = st.sidebar.selectbox("Select Food Name:", ["", "All"] + list(df_filtered['Food Name'].unique()))
df_filtered = df_filtered if sel_name in ["", "All"] else df_filtered[df_filtered['Food Name'] == sel_name]

sel_bact = st.sidebar.selectbox("Select Bacteria:", ["", "All"] + list(df_filtered['Organism'].unique()))
df_filtered = df_filtered if sel_bact in ["", "All"] else df_filtered[df_filtered['Organism'] == sel_bact]

sel_inst = st.sidebar.selectbox("Select Agency:", ["", "All"] + list(df_filtered['Agency'].unique()))
df_filtered = df_filtered if sel_inst in ["", "All"] else df_filtered[df_filtered['Agency'] == sel_inst]

# Default condition handling
group_title = f"({sel_cat} - {sel_name} - {sel_bact} - {sel_inst})" if any(v != 'All' for v in [sel_cat, sel_name, sel_bact, sel_inst]) else "(All)"

if sel_cat == "" and sel_name == "" and sel_bact == "" and sel_inst == "":
    st.info("Please enter or select from the sidebar.")
elif df_filtered.empty:
    st.warning("No matching data. Please adjust filters.")
else:
    st.subheader(f"Number of Samples by Bacteria {group_title}")
    bacteria_samples = df_filtered['Organism'].value_counts().reset_index()
    bacteria_samples.columns = ['Organism', 'Sample Count']
    latex_map = df_filtered[['Organism', 'Organism_LaTeX']].drop_duplicates()
    bacteria_samples = bacteria_samples.merge(latex_map, on='Organism', how='left')

    col1, col2 = st.columns(2)
    with col1:
        st.dataframe(bacteria_samples[['Organism', 'Sample Count']], hide_index=True)
    with col2:
        fig1, ax1 = plt.subplots(figsize=(8, 6))
        ax1.barh(bacteria_samples['Organism_LaTeX'], bacteria_samples['Sample Count'], color='skyblue')
        ax1.set_xlabel('Sample Count', fontsize=14)
        ax1.set_ylabel('Bacteria', fontsize=14)
        ax1.set_title(f'Sample Count by Bacteria {group_title}', fontsize=18)
        ax1.tick_params(axis='both', labelsize=12)
        st.pyplot(fig1)

    st.write('-----------')
    st.subheader(f"Concentration Distribution (log CFU/g) {group_title}")
    df_conc = df_filtered[['Year', 'Organism', 'log CFU/g', 'Food Name', 'Food details']].copy()
    df_conc.columns = ['Year', 'Bacteria', 'log CFU/g', 'Food Name', 'Food Details']
    col3, col4 = st.columns(2)
    with col3:
        st.dataframe(df_conc, height=calc_df_height(df_conc), hide_index=True)
        n = len(df_conc['log CFU/g'])
        mean_val = func_round(df_conc['log CFU/g'].mean(), 2)
        std_val = func_round(df_conc['log CFU/g'].std(ddof=1), 2)
        stats_df = pd.DataFrame({'Mean [log CFU/g]': [format_number(mean_val, 2)], 'Std Dev': [format_number(std_val, 2)], 'n': n})
        st.dataframe(stats_df, hide_index=True)
    with col4:
        fig2, ax2 = plt.subplots(figsize=(8, 6))
        values = df_conc['log CFU/g'].dropna().astype(float)
        ax2.hist(values, bins=range(int(values.min()), int(values.max()) + 2, 1), color='lightsalmon', edgecolor='black')
        ax2.set_xlim([0, 10])
        ax2.set_xlabel('log CFU/g', fontsize=14)
        ax2.set_ylabel('Frequency', fontsize=14)
        ax2.set_title(f'Histogram of log CFU/g {group_title}', fontsize=18)
        ax2.tick_params(axis='both', labelsize=12)
        st.pyplot(fig2)

    # === Per-Bacteria Specific Section ===
    df_Campy = df_filtered[df_filtered['Organism'].str.contains('Campylobacter', na=False)]
    df_Listeria = df_filtered[df_filtered['Organism'].str.contains('Listeria monocytogenes', na=False)]
    df_EHEC = df_filtered[df_filtered['Organism'].str.contains('Escherichia coli', na=False)]
    df_Salmonella = df_filtered[df_filtered['Organism'].str.contains('Salmonella', na=False)]
    bacteria_data = [('Campylobacter spp.', df_Campy), ('Listeria monocytogenes', df_Listeria), ('Escherichia coli (EHEC)', df_EHEC), ('Salmonella spp.', df_Salmonella)]
    bacteria_data.sort(key=lambda x: len(x[1]), reverse=True)

    for bact_label, df_bact in bacteria_data:
        if not df_bact.empty:
            st.write("-----------")
            st.subheader(f"Contamination Concentration of {bact_label} {group_title}")
            col5, col6 = st.columns(2)
            with col5:
                df_bact_conc = df_bact[['Year', 'Organism', 'log CFU/g', 'Food Name', 'Food details']].copy()
                df_bact_conc.columns = ['Year', 'Bacteria', 'log CFU/g', 'Food Name', 'Food Details']
                st.dataframe(df_bact_conc, height=calc_df_height(df_bact_conc), hide_index=True)
                n_bacteria = len(df_bact_conc['log CFU/g'])
                mean_conc = func_round(df_bact_conc['log CFU/g'].mean(), 2)
                std_conc = func_round(df_bact_conc['log CFU/g'].std(ddof=1), 2)
                stats_df = pd.DataFrame({'Mean [log CFU/g]': [format_number(mean_conc, 2)], 'Std Dev': [format_number(std_conc, 2)], 'n': n_bacteria})
                st.dataframe(stats_df, hide_index=True)
            with col6:
                fig3, ax3 = plt.subplots(figsize=(8, 6))
                values = df_bact_conc['log CFU/g'].dropna().astype(float)
                ax3.hist(values, bins=range(int(values.min()), int(values.max()) + 2, 1), color='lightsalmon', edgecolor='black')
                ax3.set_xlim([0, 10])
                ax3.set_xlabel('log CFU/g', fontsize=14)
                ax3.set_ylabel('Frequency', fontsize=14)
                ax3.set_title(f"Distribution of log CFU/g for {bact_label} {group_title}", fontsize=18)
                ax3.tick_params(axis='both', labelsize=12)
                st.pyplot(fig3)

    st.write("-----------")
    st.subheader(f"Filtered Data for Selected Food Category and Name {group_title}")
    st.dataframe(df_filtered.reset_index(drop=True))
    st.write("*Note: This graph includes processed literature values such as max/min/mean from reports. Ongoing updates will improve this with raw data.*")

# === Footer ===
st.markdown("""
<style>
.footer {
    position: fixed;
    bottom: 10px;
    right: 10px;
    font-size: 16px;
}
.footer a {
    text-decoration: none;
    color: #0366d6;
}
</style>
<div class="footer">
    For inquiries, click <a href="https://docs.google.com/forms/d/e/1FAIpQLSf2FwkiAWmr3g_50BpPAx5_87w3pwLMPRYeKwCFSfqgSJ1iTA/viewform?usp=header" target="_blank">here</a>.
</div>
""", unsafe_allow_html=True)
