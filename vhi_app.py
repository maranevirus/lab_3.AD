import os
import pandas as pd
import glob
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

regionS = {
    1: "Вінницька", 2: "Волинська", 3: "Дніпропетровська", 4: "Донецька",
    5: "Житомирська", 6: "Закарпатська", 7: "Запорізька", 8: "Івано-Франківська",
    9: "Київська", 10: "Кіровоградська", 11: "Луганська", 12: "Львівська",
    13: "Миколаївська", 14: "Одеська", 15: "Полтавська", 16: "Рівненська",
    17: "Сумська", 18: "Тернопільська", 19: "Харківська", 20: "Херсонська",
    21: "Хмельницька", 22: "Черкаська", 23: "Чернівецька", 24: "Чернігівська",
    25: "Республіка Крим"
}

newua = {
    1: 13, 2: 14, 3: 15, 4: 16, 5: 17, 6: 18, 7: 19, 8: 20,
    9: 21, 10: 22, 11: 23, 12: 24, 13: 1, 14: 2, 15: 3, 16: 4,
    17: 5, 18: 6, 19: 7, 20: 8, 21: 9, 22: 10, 23: 11, 24: 12,
    25: 25
}

def read_data_to_dataframe(directory):
    csv_files = glob.glob(os.path.join(directory, "VHI_*.csv"))
    
    frames = []
    for filename in csv_files:
        try:
            with open(filename, 'r') as file:
                lines = file.readlines()
            
            region_id = int(lines[0].split('Province=')[1].split(':')[0].strip())
            
            data_rows = []
            for line in lines[2:]:
                clean_line = (line.replace('<tt><pre>', '')
                              .replace('</tt></pre>', '')
                              .strip())
                
                if clean_line and not clean_line.startswith('<'): 
                    values = [v.strip() for v in clean_line.split(',') if v.strip()]
                    if len(values) >= 7: 
                        try:
                            row = {
                                'Year': int(values[0]),
                                'Week': int(values[1]),
                                'SMN': float(values[2]),
                                'SMT': float(values[3]),
                                'VCI': float(values[4]),
                                'TCI': float(values[5]),
                                'VHI': float(values[6]),
                                'Region': region_id
                            }
                            data_rows.append(row)
                        except (ValueError, IndexError) as e:
                            continue
            
            if data_rows:
                df = pd.DataFrame(data_rows)
                df.columns = (
                    df.columns
                    .str.replace("[^a-zA-Z0-9]", "_", regex=True)  
                    .str.lower() 
                )
                frames.append(df)
            
        except Exception as e:
            continue

    if frames:
        combined_df = pd.concat(frames, ignore_index=True)
        last_df = combined_df.drop(combined_df.loc[combined_df['vhi'] == -1].index)
        last_df['region_name'] = last_df['region'].map(regionS)
        return last_df
    return pd.DataFrame()

def reset_filters():
    """Функція для скидання фільтрів"""
    st.session_state.analysis_type_widget = "VHI"
    st.session_state.region_widget = list(st.session_state.region_options.keys())[0]
    st.session_state.week_range_widget = (1, 52)
    st.session_state.year_range_widget = (1981, 2024)

def main():
    st.set_page_config(layout="wide", page_title="Data Analysis App")
    st.title("lab 3")
    
    df = read_data_to_dataframe(DATA_DIR)
    
    # Ініціалізація станів перед створенням віджетів
    if 'analysis_type_widget' not in st.session_state:
        st.session_state.analysis_type_widget = "VHI"
    if 'region_options' not in st.session_state:
        st.session_state.region_options = {k: v for k, v in regionS.items() if k in df['region'].unique()}
    if 'region_widget' not in st.session_state:
        st.session_state.region_widget = list(st.session_state.region_options.keys())[0]
    if 'week_range_widget' not in st.session_state:
        st.session_state.week_range_widget = (1, 52)
    if 'year_range_widget' not in st.session_state:
        st.session_state.year_range_widget = (1981, 2024)
    
    filter, graf = st.columns([1, 6])
    
    with filter:
        st.header("Filters")
        
        # Використовуємо унікальні ключі для віджетів
        analysis_type = st.selectbox(
            "Select analysis type",
            ["VHI", "VCI", "TCI"],
            index=0,
            key="analysis_type_widget"
        )
    
        selected_region = st.selectbox(
            "Select region",
            options=list(st.session_state.region_options.keys()),
            format_func=lambda x: st.session_state.region_options[x],
            index=0,
            key="region_widget"
        )
        
        min_week, max_week = st.slider(
            "Select week range",
            min_value=int(df['week'].min()),
            max_value=int(df['week'].max()),
            value=st.session_state.week_range_widget,
            key="week_range_widget"
        )
        
        min_year, max_year = st.slider(
            "Select year range",
            min_value=int(df['year'].min()),
            max_value=int(df['year'].max()),
            value=st.session_state.year_range_widget,
            key="year_range_widget"
        )
        
        if st.button("Reset Filters", on_click=reset_filters):
            st.rerun()
        
        st.write("Sorting options:")
        sort_asc = st.checkbox("Sort ascending", key="sort_asc")
        sort_desc = st.checkbox("Sort descending", key="sort_desc")
        
        if sort_asc and sort_desc:
            st.warning("Both sort options selected. Defaulting to ascending.")
            sort_desc = False
    
    filtered_df = df[
        (df['region'] == selected_region) &
        (df['week'] >= min_week) &
        (df['week'] <= max_week) &
        (df['year'] >= min_year) &
        (df['year'] <= max_year)
    ].copy()
    
    if sort_asc:
        filtered_df = filtered_df.sort_values(by=analysis_type.lower(), ascending=True)
    elif sort_desc:
        filtered_df = filtered_df.sort_values(by=analysis_type.lower(), ascending=False)
    
    with graf:
        tab1, tab2, tab3 = st.tabs(["Data Table", "Time Series", "Region Comparison"])
        
        with tab1:
            st.dataframe(filtered_df, use_container_width=True)
        
        with tab2:
            st.subheader(f"{analysis_type} Time Series for {st.session_state.region_options[selected_region]}")
            
            plot_df = filtered_df.copy()
            plot_df['date'] = pd.to_datetime(plot_df['year'].astype(str) + ' ' + plot_df['week'].astype(str) + ' 0', format='%Y %W %w')
            
            fig, ax = plt.subplots(figsize=(12, 6))
            sns.lineplot(
                data=plot_df,
                x='date',
                y=analysis_type.lower(),
                ax=ax
            )
            ax.set_title(f"{analysis_type} over Time")
            ax.set_xlabel("Date")
            ax.set_ylabel(analysis_type)
            ax.grid(True)
            st.pyplot(fig)
        
        with tab3:
            st.subheader(f"{analysis_type} Comparison Across Regions")
            
            compare_df = df[
                (df['week'] >= min_week) &
                (df['week'] <= max_week) &
                (df['year'] >= min_year) &
                (df['year'] <= max_year)
            ].copy()
            
            compare_stats = compare_df.groupby(['region', 'region_name'])[analysis_type.lower()].mean().reset_index()
            compare_stats['is_selected'] = compare_stats['region'] == selected_region
            compare_stats = compare_stats.sort_values(['is_selected', analysis_type.lower()], ascending=[False, False])
            
            fig, ax = plt.subplots(figsize=(12, 6))
            sns.barplot(
                data=compare_stats,
                x='region_name',
                y=analysis_type.lower(),
                palette=['red' if x == st.session_state.region_options[selected_region] else 'blue' for x in compare_stats['region_name']],
                ax=ax
            )
            ax.set_title(f"Average {analysis_type} by Region")
            ax.set_xlabel("Region")
            ax.set_ylabel(f"Average {analysis_type}")
            ax.tick_params(axis='x', rotation=90)
            st.pyplot(fig)

if __name__ == "__main__":
    main()