## Apllication English version
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
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


# Page setup
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# Font setup
font_path = 'NotoSansCJKjp-Regular.otf'
fm.fontManager.addfont(font_path)
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['text.usetex'] = False

# CSV URLs
csv_url = "https://raw.githubusercontent.com/kento-koyama/food_micro_data_risk/main/database/contamination_rate.csv"
csv_url_gui = "https://github.com/kento-koyama/food_micro_data_risk/blob/main/database/contamination_rate.csv"

st.write('### Contamionation rate of Foodborne Bacteria')
st.write("Visualization of [contamination_rate.csv](%s)" % csv_url_gui)
st.write('You can download a csv file for each table')
st.write('-----------')

# Read CSV
df = pd.read_csv(csv_url, encoding='utf-8-sig')
df = df[df['Number of Samples'].notna() & df['Number of Positives'].notna()]
df['Organism_Detail'] = df['Organism']
df['Organism'] = df['Organism'].apply(lambda x: 'Campylobacter spp.' if 'Campylobacter' in str(x) else x)
df['Organism_LaTeX'] = df['Organism'].apply(format_bacteria_name_latex)

st.sidebar.write("### Filters")

food_groups = ["", "All"] + list(df['Food Category'].unique())
food_names = ["", "All"] + list(df['Food Name'].unique())
bacteria_names = ["", "All"] + list(df['Organism'].unique())
institutions = ["", "All"] + list(df['Agency'].unique())

selected_group = st.sidebar.selectbox('Select or input a Food Category:', food_groups, format_func=lambda x: "" if x == "" else x, key="group_selected")
df_filtered = df if selected_group in ["", "All"] else df[df['Food Category'] == selected_group]

food_names_filtered = ["", "All"] + list(df_filtered['Food Name'].unique())
selected_food = st.sidebar.selectbox('Select or input a Food Name:', food_names_filtered, format_func=lambda x: "" if x == "" else x, key="food_selected")
df_filtered = df_filtered if selected_food in ["", "All"] else df_filtered[df_filtered['Food Name'] == selected_food]

bacteria_names_filtered = ["", "All"] + list(df_filtered['Organism'].unique())
selected_bacteria = st.sidebar.selectbox('Select or input a Bacteria:', bacteria_names_filtered, format_func=lambda x: "" if x == "" else x, key="bacteria_selected")
df_filtered = df_filtered if selected_bacteria in ["", "All"] else df_filtered[df_filtered['Organism'] == selected_bacteria]

institutions_filtered = ["", "All"] + list(df_filtered['Agency'].unique())
selected_institution = st.sidebar.selectbox('Select or input an Agency:', institutions_filtered, format_func=lambda x: "" if x == "" else x, key="institution_selected")
df_filtered = df_filtered if selected_institution in ["", "All"] else df_filtered[df_filtered['Agency'] == selected_institution]

if selected_group == "" and (selected_food != "" or selected_bacteria != "" or selected_institution != ""):
    selected_group = "All"
if selected_food == "" and (selected_group != "" or selected_bacteria != "" or selected_institution != ""):
    selected_food = "All"
if selected_bacteria == "" and (selected_group != "" or selected_food != "" or selected_institution != ""):
    selected_bacteria = "All"
if selected_institution == "" and (selected_group != "" or selected_food != "" or selected_bacteria != ""):
    selected_institution = "All"

group_title = f"({selected_group} - {selected_food} - {selected_bacteria} - {selected_institution})" \
              if any(v != 'All' for v in [selected_group, selected_food, selected_bacteria, selected_institution]) else "(All)"

if selected_group == "" and selected_food == "" and selected_bacteria == "" and selected_institution == "":
    st.info("Please input or select from the sidebar.")
elif df_filtered.empty:
    st.warning("No matching data found. Try adjusting the filters.")
else:
    if selected_bacteria == "All":
        bacteria_counts = df_filtered.groupby(['Organism', 'Organism_LaTeX']).agg({
            'Number of Samples': 'sum', 'Number of Positives': 'sum'
        }).reset_index()
        bacteria_counts['Positive Rate (%)'] = bacteria_counts['Number of Positives'] / bacteria_counts['Number of Samples'] * 100
        bacteria_counts['Positive Rate (%)'] = bacteria_counts['Positive Rate (%)'].apply(lambda x: func_round(x, 2))
        bacteria_counts.rename(columns={'Organism_LaTeX': 'Display Name (LaTeX)'}, inplace=True)

        col1, col2 = st.columns(2)
        with col1:
            st.write(f'Number of Samples by Bacteria {group_title}')
            st.dataframe(bacteria_counts[['Organism', 'Number of Samples']], hide_index=True)
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
            st.dataframe(bacteria_counts[['Organism', 'Positive Rate (%)']], hide_index=True)
        with col4:
            fig2, ax2 = plt.subplots(figsize=(6, 6))
            ax2.barh(bacteria_counts['Display Name (LaTeX)'], bacteria_counts['Positive Rate (%)'], color='skyblue')
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
            st.dataframe(category_summary, hide_index=True)
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
    st.dataframe(df_filtered, hide_index=True)
    st.write("-----------")

    positive_df = df_filtered[df_filtered['Number of Positives'] >= 1]
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
        <a href="/" target="_self" class="{ 'inactive' if current_page == 'jp' else 'active' }">🇯🇵 Japanese</a> |
        <a href="/main_eng" target="_self" class="{ 'inactive' if current_page == 'en' else 'active' }">🇬🇧 English</a>
    </div>
"""
st.markdown(language_switch_html, unsafe_allow_html=True)

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
