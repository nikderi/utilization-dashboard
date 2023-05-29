import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import datetime as dt


month_map = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

def processes_util_overview(processes_df, option):
    given_date = dt.datetime.strptime(option, '%B')
    last_month = given_date - dt.timedelta(days=given_date.day)
    last_month = last_month.strftime('%B')
    current_processes_df = processes_df[processes_df.Month == option]
    previous_processes_df = processes_df[processes_df.Month == last_month]
    aggregated_df = get_aggregated_table(current_processes_df)
    last_month_df = get_aggregated_table(previous_processes_df)
    merged_df = pd.merge(aggregated_df, last_month_df, on='ReleaseName', how='outer', suffixes=('_current','_last'))
    merged_df = merged_df.fillna(0)
    merged_df['Utilization (%)'] = merged_df['Utilization_current'].astype(float) - merged_df['Utilization_last'].astype(float)
    merged_df = merged_df[['ReleaseName', 'Utilization (%)']]
    merged_df = merged_df.sort_values('Utilization (%)', ascending=False)
    tab1, tab2, tab3, tab4 = st.tabs(["Top Utilized Processes", "Top Gainers", "Least Utilized Processes", "Top Losers"])
    with tab1:
        table = aggregated_df.head(3)
        st.markdown("""
            <style>
                thead tr th:first-child {display:none}
                tbody th {display:none}
            </style>
            """, unsafe_allow_html=True)
        st.table(table)
    with tab2:
        st.table(merged_df.head(3))
    with tab3:
        table = aggregated_df.tail(3)
        st.markdown("""
            <style>
                thead tr th:first-child {display:none}
                tbody th {display:none}
            </style>
            """, unsafe_allow_html=True)
        st.table(table)
    with tab4:
        losers_df = merged_df.sort_values('Utilization (%)', ascending=True)
        st.table(losers_df.head(3))

def processes_util_line_chart(processes_df, option):
  
    process_list = np.unique(np.array(processes_df['ReleaseName'])).tolist()
    option = st.selectbox(
        'Which process you want to view?', process_list)
    aggregated_df = processes_df[processes_df.ReleaseName == option]
    aggregated_df['Month'] = pd.Categorical(aggregated_df['Month'], categories=month_map, ordered=True)
    aggregated_df = aggregated_df.sort_values('Month', ascending=True)
    tab1_name = 'HoursUtilized'
    tab2_name = 'Utilization'
    tab1, tab2 = st.tabs([tab1_name, tab2_name])
    fig1 = px.line(aggregated_df, x='Month', y=tab1_name, color='ReleaseName', markers=False, title=tab1_name)
    fig2 = px.line(aggregated_df, x='Month', y=tab2_name, color='ReleaseName', markers=False, title=tab2_name)
    
    with tab1:
        st.plotly_chart(fig1)
    with tab2:
        st.plotly_chart(fig2)
    st.markdown("""
        <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
        </style>
    """, unsafe_allow_html=True)
    st.table(aggregated_df)
    fig = px.bar(aggregated_df, x="Month", y="HoursUtilized", color="HostMachineName", text="HostMachineName")
    st.plotly_chart(fig, theme="streamlit")


def get_aggregated_table(df):
    aggregated_process_df = df.copy()
    aggregated_process_df['HoursUtilized'] = aggregated_process_df['HoursUtilized'].astype(float)
    aggregated_process_df['Utilization'] = aggregated_process_df['Utilization'].astype(float)
    aggregated_process_df = aggregated_process_df.groupby(['ReleaseName'], as_index=False).sum()
    aggregated_process_df = aggregated_process_df[['ReleaseName', 'HoursUtilized', 'Utilization']]
    aggregated_process_df.sort_values(by='HoursUtilized',ascending=False, inplace=True)
    aggregated_process_df['HoursUtilized'] = aggregated_process_df['HoursUtilized'].apply(lambda x: round(x,2)).astype(str)
    aggregated_process_df.reset_index(drop=True, inplace=True)
    return aggregated_process_df