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
# Page setup
st.set_page_config(
    page_title="Software visualizing bacterial concentration data", 
    # page_icon="", 
    layout="wide", 
    initial_sidebar_state="expanded"
    )
st.markdown("""
<style>
@import url('https://cdnjs.cloudflare.com/ajax/libs/flag-icon-css/6.6.6/css/flag-icons.min.css');
</style>
""", unsafe_allow_html=True)


# === Load Data ===
csv_url = "https://raw.githubusercontent.com/kento-koyama/food_micro_data_risk/main/database/concentration_of_contamination.csv"
csv_url_gui = "https://github.com/kento-koyama/food_micro_data_risk/blob/main/database/concentration_of_contamination.csv"

# font settings
font_path = 'NotoSansCJKjp-Regular.otf'
fm.fontManager.addfont(font_path)
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['text.usetex'] = False

size_label = 18
size_title = 20

# === UI ===
st.title("Software visualizing concentration of contamination by Food-borne Bacteria")
st.write("This dataset covers food products distributed in Japan that were tested between 2000 and 2025.") 
st.write("[The data](%s) is based on various governmental reports and academic papers published by government agencies, research institutes, and universities." % csv_url_gui)
st.write("Each table can be downloaded as a CSV.")
st.write("-----------")
st.sidebar.title("Filter Settings")

# Data
df = pd.read_csv(csv_url, encoding='utf-8-sig')

# === Data Cleaning ===
# Replace matching values with "Not detected"
not_detected_mask = (
    (df['Concentration'] == 'Not Detected') |
    (df['Concentration'] == '-') |
    (df['Concentration'] == '0') |
    (df['Concentration'].astype(str).str.contains('<', na=False)) |
    (df['Concentration'].astype(str).str.contains('未満', na=False))
)
df.loc[not_detected_mask, 'Concentration'] = 'Not detected'

# Exclude rows where Concentration is NaN or "Not detected"
df = df[~(df['Concentration'].isna() | (df['Concentration'] == 'Not detected'))]
df = df[~(df['Food Category'].isna() & df['Food Name'].isna())]
df = df[df['Unit']!='CFU/と体']
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

df = df.loc[:, ['Year', 'Food Handling Classification', 'Food Category', 'Food Name', 'Food details', 'Organism', 'Organism_Detail', 'Organism_LaTeX', 'Method', 'log CFU/g', 'MPN per g', 'Concentration', 'Unit', 'Agency', 'Survey', 'Source URL', 'Access Date', 'Remarks']]

# =========================
# Interdependent Filters (main.py style)
# - options for each filter are determined by constraints from the OTHER filters
# - if intersection becomes empty, reset downstream selections (upstream priority) and rerun
# - keep legacy behavior: if any input exists, EMPTY ("") is treated as "All" for display only
# =========================
MISSING = "Unknown (Missing)"
ALL = "All"
EMPTY = ""

FILTERS = [
    # (session_key, df_column, label)
    ("handling_selected", "Food Handling Classification", "Food Handling Classification"),
    ("category_selected", "Food Category", "Food Category"),
    ("food_selected", "Food Name", "Food Name"),
    ("bacteria_selected", "Organism", "Bacteria"),
    ("agency_selected", "Agency", "Agency"),
]

# normalize (strip + fillna) so option labels and filtering match
for _, col, _ in FILTERS:
    if col in df.columns:
        df[col] = df[col].astype("string").str.strip().fillna(MISSING)
    else:
        df[col] = MISSING

def is_active(v: str) -> bool:
    return v not in [EMPTY, ALL]

def apply_constraints(df_in: pd.DataFrame, exclude_key: str | None = None) -> pd.DataFrame:
    """Apply all active constraints except exclude_key."""
    out = df_in
    for key, col, _ in FILTERS:
        if key == exclude_key:
            continue
        v = st.session_state.get(key, EMPTY)
        if is_active(v):
            out = out[out[col] == v]
    return out

def make_options(series: pd.Series) -> list[str]:
    vals = sorted(pd.unique(series).tolist())
    return [EMPTY, ALL] + vals

# init session_state
for key, _, _ in FILTERS:
    st.session_state.setdefault(key, EMPTY)

# 1) Build options using only upstream filters
# Each filter's options are narrowed only by filters above it in the list.
# This prevents downstream filter changes from resetting upstream selections.
options_map: dict[str, list[str]] = {}
for i, (key, col, _) in enumerate(FILTERS):
    df_up = df.copy()
    for j in range(i):
        up_key, up_col, _ = FILTERS[j]
        v = st.session_state.get(up_key, EMPTY)
        if is_active(v):
            df_up = df_up[df_up[up_col] == v]
    options_map[key] = make_options(df_up[col])

# 2) Reset only when an upstream change makes the current selection invalid
for key, _, _ in FILTERS:
    if st.session_state[key] not in options_map[key]:
        st.session_state[key] = EMPTY

# 3) render selectboxes (order is UI order; logic itself is order-independent)
for key, _, label in FILTERS:
    st.sidebar.selectbox(
        f"Enter or select {label}:",
        options_map[key],
        format_func=lambda x: "" if x == EMPTY else x,
        key=key,
    )

# 4) final AND filtering
df_filtered = apply_constraints(df, exclude_key=None)

# 5) if contradiction (empty intersection) happens, reset downstream (upstream priority)
any_selected_active = any(is_active(st.session_state[k]) for k, _, _ in FILTERS)
if any_selected_active and df_filtered.empty:
    df_tmp = df.copy()
    for i, (key, col, label) in enumerate(FILTERS):
        v = st.session_state[key]
        if is_active(v):
            next_df = df_tmp[df_tmp[col] == v]
            if next_df.empty:
                # contradiction point -> reset this and downstream
                for j in range(i, len(FILTERS)):
                    st.session_state[FILTERS[j][0]] = EMPTY
                st.warning(f"Inconsistent selections detected. Reset selections from '{label}' onward.")
                st.rerun()
            df_tmp = next_df
    df_filtered = apply_constraints(df, exclude_key=None)

# --- display-only normalization (legacy behavior) ---
any_input = any(st.session_state[k] != EMPTY for k, _, _ in FILTERS)

selected_handling = st.session_state["handling_selected"]
selected_category = st.session_state["category_selected"]
selected_food = st.session_state["food_selected"]
selected_bacteria = st.session_state["bacteria_selected"]
selected_agency = st.session_state["agency_selected"]

if any_input:
    if selected_handling == EMPTY: selected_handling = ALL
    if selected_category == EMPTY: selected_category = ALL
    if selected_food == EMPTY: selected_food = ALL
    if selected_bacteria == EMPTY: selected_bacteria = ALL
    if selected_agency == EMPTY: selected_agency = ALL

# --- Show edible parts only (only when a specific category is selected) ---
show_edible_checkbox = (selected_category not in [EMPTY, ALL])
if show_edible_checkbox:
    edible_only = st.sidebar.checkbox(
        "Show edible parts only",
        value=False,
        help="Exclude inedible parts such as gastrointestinal contents.",
    )
else:
    edible_only = False

if edible_only and "Food Handling Classification" in df_filtered.columns:
    df_filtered = df_filtered[df_filtered["Food Handling Classification"] != "Non-edible Parts"]

# --- group title ---
if all(v == ALL for v in [selected_handling, selected_category, selected_food, selected_bacteria, selected_agency]):
    group_title = "(All)"
else:
    group_title = f"({selected_handling} - {selected_category} - {selected_food} - {selected_bacteria} - {selected_agency})"

# --- gatekeeping (same structure as JP main.py) ---
raw_all_empty = all(st.session_state[k] == EMPTY for k, _, _ in FILTERS)
if raw_all_empty:
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
        ax1.set_xlabel('Sample Count', fontsize=size_label)
        ax1.set_ylabel('Bacteria', fontsize=size_label)
        ax1.set_title(f'Sample Count by Bacteria {group_title}', fontsize=size_title)
        ax1.tick_params(axis='both', labelsize=size_label)
        st.pyplot(fig1)

    st.write('-----------')
    st.subheader(f"Concentration Distribution (log CFU/g) {group_title}")
    df_conc = df_filtered[['Year', 'Organism', 'log CFU/g', 'Food Category', 'Food Name']].copy()
    df_conc.columns = ['Year', 'Bacteria', 'log CFU/g', 'Food Category', 'Food Name']
    col3, col4 = st.columns(2)
    with col3:
        st.dataframe(df_conc, height=calc_df_height(df_conc), hide_index=True)
        n = len(df_conc['log CFU/g'])
        mean_val = func_round(df_conc['log CFU/g'].mean(), 2)
        std_val = func_round(df_conc['log CFU/g'].std(ddof=1), 2)
        stats_df = pd.DataFrame({'Mean [log CFU/g]': [format_number(mean_val, 2)], 'Std Dev': [format_number(std_val, 2)], 'n (the number of samples)': n})
        st.dataframe(stats_df, hide_index=True)
    with col4:
        fig2, ax2 = plt.subplots(figsize=(8, 6))
        values = df_conc['log CFU/g'].dropna().astype(float)
        ax2.hist(values, bins=range(int(values.min()), int(values.max()) + 2, 1), color='lightsalmon', edgecolor='black')
        ax2.set_xlim([0, 10])
        ax2.set_xlabel('Concentration [log CFU/g]', fontsize=size_label)
        ax2.set_ylabel('Frequency', fontsize=size_label)
        ax2.set_title(f'Distribution of Concentration {group_title}', fontsize=size_title)
        ax2.tick_params(axis='both', labelsize=size_label)
        st.pyplot(fig2)

    # === Per-Bacteria Specific Section ===
    df_Campy = df_filtered[df_filtered['Organism'].str.contains('Campylobacter', na=False)]
    df_Listeria = df_filtered[df_filtered['Organism'].str.contains('Listeria monocytogenes', na=False)]
    df_EHEC = df_filtered[df_filtered['Organism'].str.contains('Escherichia coli', na=False)]
    df_Salmonella = df_filtered[df_filtered['Organism'].str.contains('Salmonella', na=False)]
    df_Staphylococcus = df_filtered[df_filtered['Organism'].str.contains('Staphylococcus aureus', na=False)]
    df_Cperfringens = df_filtered[df_filtered['Organism'].str.contains('Clostridium perfringens', na=False)]
    bacteria_data = [('Campylobacter spp.', df_Campy), ('Listeria monocytogenes', df_Listeria), ('Escherichia coli (EHEC)', df_EHEC), ('Salmonella spp.', df_Salmonella), ('Staphylococcus aureus', df_Staphylococcus), ('Clostridium perfringens', df_Cperfringens)]
    bacteria_data.sort(key=lambda x: len(x[1]), reverse=True)

    for bact_label, df_bact in bacteria_data:
        if not df_bact.empty:
            st.write("-----------")
            st.subheader(f"Contamination Concentration of {bact_label} {group_title}")
            col5, col6 = st.columns(2)
            with col5:
                df_bact_conc = df_bact[['Year', 'Organism', 'log CFU/g', 'Food Category', 'Food Name']].copy()
                df_bact_conc.columns = ['Year', 'Bacteria', 'log CFU/g', 'Food Category', 'Food Name']
                st.dataframe(df_bact_conc, height=calc_df_height(df_bact_conc), hide_index=True)
                n_bacteria = len(df_bact_conc['log CFU/g'])
                mean_conc = func_round(df_bact_conc['log CFU/g'].mean(), 2)
                std_conc = func_round(df_bact_conc['log CFU/g'].std(ddof=1), 2)
                stats_df = pd.DataFrame({'Mean [log CFU/g]': [format_number(mean_conc, 2)], 'Std Dev': [format_number(std_conc, 2)], 'n (the number of samples)': n_bacteria})
                st.dataframe(stats_df, hide_index=True)
            with col6:
                fig3, ax3 = plt.subplots(figsize=(8, 6))
                values = df_bact_conc['log CFU/g'].dropna().astype(float)
                ax3.hist(values, bins=range(int(values.min()), int(values.max()) + 2, 1), color='lightsalmon', edgecolor='black')
                ax3.set_xlim([0, 10])
                ax3.set_xlabel('Concentration [log CFU/g]', fontsize=size_label)
                ax3.set_ylabel('Frequency', fontsize=size_label)
                ax3.set_title(f"Distribution of Concentration for {bact_label} {group_title}", fontsize=size_title)
                ax3.tick_params(axis='both', labelsize=size_label)
                st.pyplot(fig3)
                plt.close(fig3)

    st.write("-----------")
    st.subheader(f"Filtered Data for Selected Food Category and Name {group_title}")
    df_filtered_display = df_filtered.copy()
    df_filtered_display = df_filtered_display[['Year', 'Food Handling Classification', 'Food Category', 'Food Name', 'Food details', 'Organism', 'Organism_Detail', 'log CFU/g', 'Concentration', 'Unit', 'Method', 'Agency', 'Survey', 'Source URL', 'Access Date', 'Remarks']]
    df_filtered_display.reset_index(inplace=True, drop=True)
    st.dataframe(df_filtered_display)
    st.write("*Note: This graph includes processed literature values such as max/min/mean from reports. Ongoing updates will improve this with raw data.*")


# setting current page manually
current_page = "en"  

language_switch_html = f"""
    <style>
    .language-switch {{
        position: fixed;
        top: 80px;
        right: 20px;
        z-index: 9999;
        background-color: transparent;  
        border: none;                   
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 14px;
    }}
    .language-switch a {{
        margin: 0 5px;
        text-decoration: none;
        font-weight: bold;
    }}
    .language-switch .inactive {{
        color: #ccc;
        pointer-events: none;
        cursor: default;
    }}
    .language-switch .active {{
        color: #000;
    }}
    .language-switch .active:hover {{
        color: #0366d6;
    }}
    </style>
    <div class="language-switch">
        <a href="/" target="_self" class="{ 'inactive' if current_page == 'jp' else 'active' }">
            <span class="fi fi-jp"></span> Japanese
        </a> |
        <a href="/main_eng" target="_self" class="{ 'inactive' if current_page == 'en' else 'active' }">
            <span class="fi fi-gb"></span> English
        </a>
    </div>
"""
st.markdown(language_switch_html, unsafe_allow_html=True)

# Header
HIDE_MENU_STYLE = """
<style>
#MainMenu {
    visibility: hidden;
    height: 0%;
}
header {
    visibility: hidden;
    height: 0%;
}
</style>
"""
st.markdown(HIDE_MENU_STYLE, unsafe_allow_html=True)


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
