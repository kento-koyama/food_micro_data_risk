## Apllication English version
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import re

# Rounding function
def func_round(number, ndigits=0):
    if pd.isna(number):
        return np.nan
    p = 10 ** ndigits
    return float(int(number * p + 0.5) / p)

# Format bacterial names in italic for display
def format_bacteria_name_latex(name):
    if pd.isna(name):
        return name
    spp_match = re.match(r'^([A-Z][a-z]+)\s+(spp?\.)$', name)
    if spp_match:
        genus, spp = spp_match.groups()
        return rf"$\it{{{genus}}}$ {spp}"  # ← \\ を \ に直す
    match = re.match(r'^([A-Z][a-z]+)\s+([a-z]+)(.*)$', name)
    if match:
        genus, species, rest = match.groups()
        return rf"$\it{{{genus}\ {species}}}${rest}"
    return rf"$\it{{{name}}}$"

# Dynamic table height adjustment
def calc_df_height(df, max_rows=5, row_height=35):
    """
    Calculate the table height dynamically based on dataframe length.

    Parameters:
        df (pd.DataFrame): Target dataframe
        max_rows (int): Maximum rows to display
        row_height (int): Height per row (pixels)

    Returns:
        int: total display height (pixels)
    """
    rows_to_display = min(len(df), max_rows)+1
    return row_height * rows_to_display

# Page setup
st.set_page_config(
    page_title="Software visualizing prevalence data", 
    # page_icon="", 
    layout="wide", 
    initial_sidebar_state="expanded"
    )
st.markdown("""
<style>
@import url('https://cdnjs.cloudflare.com/ajax/libs/flag-icon-css/6.6.6/css/flag-icons.min.css');
</style>
""", unsafe_allow_html=True)

# Font setup
font_path = 'NotoSansCJKjp-Regular.otf'
fm.fontManager.addfont(font_path)
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['text.usetex'] = False

# CSV URLs
csv_url = "https://raw.githubusercontent.com/kento-koyama/food_micro_data_risk/main/database/contamination_rate.csv"
csv_url_gui = "https://github.com/kento-koyama/food_micro_data_risk/blob/main/database/contamination_rate.csv"

st.title('Software visualizing contamination rate of Food-borne Bacteria')
st.write("This dataset covers food products distributed in Japan that were tested between 2000 and 2025.") 
st.write("[The data](%s) is based on various governmental reports and academic papers published by government agencies, research institutes, and universities." % csv_url_gui)
st.write('Each table can be downloaded as a CSV.')
st.write('-----------')

# Read CSV
df = pd.read_csv(csv_url, encoding='utf-8-sig')
df = df[df['Number of Samples'].notna() & df['Number of Positives'].notna()]
df['Organism_Detail'] = df['Organism']
df['Organism'] = df['Organism'].apply(lambda x: 'Campylobacter spp.' if 'Campylobacter' in str(x) else x)
df['Organism_LaTeX'] = df['Organism'].apply(format_bacteria_name_latex)

# =========================
# Mutually-linked filters (same logic as main.py)
# - Options for each filter are determined by "all other filters"
# - If contradiction happens (intersection is empty), reset downstream filters (upstream priority)
# =========================
MISSING = "Unknown (missing)"
ALL = "All"
EMPTY = ""

FILTERS = [
    # (session_key, df_column, label)
    ("handling_selected", "Food Handling Classification", "Food Handling Classification"),
    ("group_selected", "Food Category", "Food Category"),
    ("food_selected", "Food Name", "Food Name"),
    ("bacteria_selected", "Organism", "Bacteria"),
    ("institution_selected", "Agency", "Agency"),
]

# Normalize missing / whitespace (make options match actual stored values)
for _, col, _ in FILTERS:
    if col in df.columns:
        df[col] = df[col].astype("string").str.strip().fillna(MISSING)

# session_state init
for key, _, _ in FILTERS:
    st.session_state.setdefault(key, EMPTY)
st.session_state.setdefault("edible_only", False)

def is_active(v: str) -> bool:
    return v not in [EMPTY, ALL]

def apply_constraints(df_in: pd.DataFrame, exclude_key: str | None = None) -> pd.DataFrame:
    """Apply all selected constraints except exclude_key."""
    out = df_in

    # Extra constraint: edible only (kept from your EN UI)
    if st.session_state.get("edible_only", False) and "Food Handling Classification" in out.columns:
        out = out[out["Food Handling Classification"] != "Non-edible Parts"]

    for key, col, _ in FILTERS:
        if key == exclude_key:
            continue
        v = st.session_state.get(key, EMPTY)
        if is_active(v) and col in out.columns:
            out = out[out[col] == v]
    return out

def make_options(series: pd.Series) -> list[str]:
    vals = sorted(pd.unique(series).tolist())
    return [EMPTY, ALL] + vals

st.sidebar.header("Filter Settings")

# 1) Build options by applying "other filters"
options_map: dict[str, list[str]] = {}
for key, col, _ in FILTERS:
    if col not in df.columns:
        options_map[key] = [EMPTY, ALL]
        continue
    df_others = apply_constraints(df, exclude_key=key)   # ★ main.pyの肝
    options_map[key] = make_options(df_others[col])

# 2) Self-heal: if current selection is not in candidates, clear it
for key, _, _ in FILTERS:
    if st.session_state[key] not in options_map.get(key, [EMPTY, ALL]):
        st.session_state[key] = EMPTY

# 3) Draw selectboxes (order is UI-only; logic is order-independent)
for key, _, label in FILTERS:
    st.sidebar.selectbox(f"Select {label}:", options_map[key], key=key)

# --- Show Edible Parts Only (only when some Food Category is selected) ---
show_edible_checkbox = is_active(st.session_state["group_selected"])
if show_edible_checkbox:
    st.sidebar.checkbox(
        "Show edible parts only",
        key="edible_only",
        help="Exclude inedible parts such as gastrointestinal contents."
    )
else:
    st.session_state["edible_only"] = False

# 4) Final AND filtering
df_filtered = apply_constraints(df, exclude_key=None)

# 5) If contradiction (intersection empty), reset downstream filters (upstream priority)
any_selected = any(is_active(st.session_state[k]) for k, _, _ in FILTERS) or st.session_state.get("edible_only", False)
if any_selected and df_filtered.empty:
    df_tmp = df.copy()

    if st.session_state.get("edible_only", False) and "Food Handling Classification" in df_tmp.columns:
        df_tmp = df_tmp[df_tmp["Food Handling Classification"] != "Non-edible Parts"]

    for i, (key, col, label) in enumerate(FILTERS):
        v = st.session_state[key]
        if is_active(v) and col in df_tmp.columns:
            next_df = df_tmp[df_tmp[col] == v]
            if next_df.empty:
                for j in range(i, len(FILTERS)):
                    st.session_state[FILTERS[j][0]] = EMPTY
                st.warning(f"Conflicting selections detected. Filters from '{label}' onward were reset.")
                st.rerun()
            df_tmp = next_df

    df_filtered = apply_constraints(df, exclude_key=None)

# For titles / downstream logic (keep your original variable names as much as possible)
def _lab(v: str) -> str:
    return "Unselected" if v == EMPTY else v

selected_handling = st.session_state["handling_selected"]
selected_group = st.session_state["group_selected"]
selected_food = st.session_state["food_selected"]
selected_bacteria = st.session_state["bacteria_selected"]
selected_institution = st.session_state["institution_selected"]

group_title = f"({_lab(selected_handling)} - {_lab(selected_group)} - {_lab(selected_food)} - {_lab(selected_bacteria)} - {_lab(selected_institution)})"

if all(x == "" for x in [selected_handling, selected_group, selected_food, selected_bacteria, selected_institution]):
    st.info("Please input or select from the sidebar.")
elif df_filtered.empty:
    st.warning("No matching data found. Try adjusting the filters.")
else:
    if selected_bacteria in ["", "All"]:
        bacteria_counts = df_filtered.groupby(['Organism', 'Organism_LaTeX']).agg({
            'Number of Samples': 'sum', 'Number of Positives': 'sum'
        }).reset_index()
        bacteria_counts['Positive Rate (%)'] = bacteria_counts['Number of Positives'] / bacteria_counts['Number of Samples'] * 100
        bacteria_counts['Positive Rate (%)'] = bacteria_counts['Positive Rate (%)'].apply(lambda x: func_round(x, 2))
        bacteria_counts.rename(columns={'Organism_LaTeX': 'Display Name (LaTeX)'}, inplace=True)

        col1, col2 = st.columns(2)
        with col1:
            st.write(f'Number of Samples by Bacteria {group_title}')
            st.dataframe(bacteria_counts[['Organism', 'Number of Samples']], height=calc_df_height(bacteria_counts, max_rows=5), hide_index=True)
        with col2:
            fig1, ax1 = plt.subplots(figsize=(6, 6))
            ax1.barh(bacteria_counts['Display Name (LaTeX)'], bacteria_counts['Number of Samples'], color='skyblue')
            ax1.set_xlabel('Number of Samples', fontsize=18)
            ax1.set_ylabel('Bacteria', fontsize=18)
            ax1.set_title(f'Number of Samples by Bacteria {group_title}', fontsize=20)
            ax1.tick_params(axis='both', labelsize=14)
            ax1.invert_yaxis()
            st.pyplot(fig1)

        st.write("-----------")

        col3, col4 = st.columns(2)
        with col3:
            st.write(f'Positive Rate by Bacteria {group_title}')
            st.dataframe(bacteria_counts[['Organism', 'Positive Rate (%)']], height=calc_df_height(bacteria_counts, max_rows=5), hide_index=True)
        with col4:
            fig2, ax2 = plt.subplots(figsize=(6, 6))
            ax2.barh(bacteria_counts['Display Name (LaTeX)'], bacteria_counts['Positive Rate (%)'], color='skyblue')
            ax2.set_xlim([0,100])
            ax2.set_xlabel('Positive Rate (%)', fontsize=18)
            ax2.set_ylabel('Bacteria', fontsize=18)
            ax2.set_title(f'Positive Rate by Bacteria {group_title}', fontsize=20)
            ax2.tick_params(axis='both', labelsize=14)
            ax2.invert_yaxis()
            st.pyplot(fig2)

        st.write("-----------")

    else:
        category_summary = df_filtered.groupby('Food Category').agg({
            'Number of Samples': 'sum', 'Number of Positives': 'sum'
        }).reset_index()
        category_summary['Positive Rate (%)'] = category_summary['Number of Positives'] / category_summary['Number of Samples'] * 100
        category_summary['Positive Rate (%)'] = category_summary['Positive Rate (%)'].apply(lambda x: func_round(x, 2))

        col5, col6 = st.columns(2)
        with col5:
            st.write(f'Positive Rate by Food Category {group_title}')
            st.dataframe(category_summary, height=calc_df_height(category_summary, max_rows=5), hide_index=True)
        with col6:
            fig3, ax3 = plt.subplots(figsize=(8, 6))
            ax3.barh(category_summary['Food Category'], category_summary['Positive Rate (%)'], color='skyblue')
            ax3.set_xlabel('Positive Rate (%)', fontsize=14)
            ax3.set_ylabel('Food Category', fontsize=14)
            ax3.set_title(f'Positive Rate by Food Category {group_title}', fontsize=16)
            ax3.tick_params(axis='both', which='major', labelsize=12)
            ax3.invert_yaxis()
            st.pyplot(fig3)

        st.write("-----------")

    st.write(f'Data for Selected Filters {group_title}')
    df_filtered_display = df_filtered.copy()
    df_filtered_display = df_filtered_display[['Year', 'Food Handling Classification', 'Food Category', 'Food Name', 'Organism', 'Organism_Detail', 'Number of Samples', 'Number of Positives', 'Agency', 'Survey', 'Source URL', 'Access Date', 'Remarks']]
    st.dataframe(df_filtered_display, hide_index=True)
    st.write("-----------")

    positive_df = df_filtered_display[df_filtered_display['Number of Positives'] >= 1]
    st.write(f'Samples with Positive Count >= 1 {group_title}')
    st.dataframe(positive_df, hide_index=True)


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

HIDE_UI_STYLE = """
<style>

header, header[data-testid="stHeader"] {
    visibility: visible !important;
    height: auto !important;
}


[data-testid="stMainMenu"] { 
    display: none !important; 
}
#MainMenu { 
    visibility: hidden; 
}


[data-testid="stDeployButton"] {
    display: none !important;
}
[data-testid="stStatusWidget"] {
    display: none !important;
}


footer {
    visibility: hidden;
}

button[data-testid="collapsedControl"],
button[data-testid="stSidebarCollapseButton"],
button[aria-label="Close sidebar"],
button[aria-label="Open sidebar"] {
    display: inline-flex !important;
    visibility: visible !important;
}

div[data-testid="stToolbar"] {
    visibility: visible !important;
}
</style>
"""
st.markdown(HIDE_UI_STYLE, unsafe_allow_html=True)

# Link
contact_link = """
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
        For inquiries, click 
        <a href="https://docs.google.com/forms/d/e/1FAIpQLSf2FwkiAWmr3g_50BpPAx5_87w3pwLMPRYeKwCFSfqgSJ1iTA/viewform?usp=header" target="_blank">
        here</a>.
    </div>
"""
st.markdown(contact_link, unsafe_allow_html=True)
