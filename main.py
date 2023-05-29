import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import math
#from massage_report import machines_report
from streamlit_option_menu import option_menu
import matplotlib.pyplot as plt
from matplotlib.patches import ConnectionPatch
import altair as alt
from streamlit_vega_lite import vega_lite_component, altair_component
import plotly.figure_factory as ff
import plotly.graph_objects as go
import datetime as dt
import machines_utilization as mu
import processes_utilization as pu
import schedule_optimization as su
import jobs_upload as ju
import sqlite3
#import processes_utilization as pu
# from streamlit_elements import elements, mui, html, nivo


# Define the sidebar menu
with st.sidebar:
    choice = option_menu(menu_title="RPA Dashboard",
                         options=["Machines Utilization","Processes Utilization", "Schedule Optimization", "Jobs Upload"],
                         icons=["pc-display-horizontal","arrow-repeat","calendar4-week","upload"], menu_icon="clipboard-data")

conn = sqlite3.connect('rpa_jobs.db')
# Execute a SELECT query to fetch all rows from the table
try:
    jobs_df = pd.read_sql_query(f"SELECT * FROM {'jobs'}", conn)
except:
    print('No jobs table in the database')

try:
    machines_df = pd.read_sql_query(f"SELECT * FROM {'machines'}", conn)
except:
    print('No machines table in the database')

try:
    processes_df = pd.read_sql_query(f"SELECT * FROM {'processes'}", conn)
except:
    print('No processes table in the database')

try:
    year_month_df = pd.read_sql_query(f"SELECT * FROM {'year_month'}", conn)
    current_year_df = year_month_df[year_month_df.Year == str(dt.date.today().year)]
    current_year_df = current_year_df.sort_values('Month')
    month_map = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    current_year_df['Month'] = pd.Categorical(current_year_df['Month'], categories=month_map, ordered=True)
    current_year_df = current_year_df.sort_values('Month', ascending=False) 
    month_list = np.array(current_year_df['Month']).tolist()
except:
    print('No year_month table in the database')


if choice == "Machines Utilization":
    
    st.title("Machines Utilization")
    #  Select the month for the user to view
    option = st.selectbox(
        'Which month you want to view?', month_list)
    mu.machines_util_metrics(machines_df, option)
    # mu.machines_util_pie_chart(machines_df, option)
    machine_labels = np.unique(np.array(machines_df['HostMachineName']).tolist())
    option = st.selectbox(
        'Which machine you want to view?', machine_labels)
    mu.machines_util_line_graph(machines_df, option)
    mu.machines_util_table(jobs_df, option)

# Define the Processes Utilization menu
if choice == "Processes Utilization":
    st.title("Processes Utilization")
    option = st.selectbox(
        'Which month you want to view?', month_list)

    pu.processes_util_overview(processes_df, option)
    pu.processes_util_line_chart(processes_df, option)
    
if choice == "Schedule Optimization":
    st.title("Schedule Optimization")
    option = st.selectbox(
        'Which month you want to view?', month_list)
    selected_jobs_df = jobs_df[jobs_df.Month == option]
    su.utilization_heatmap(selected_jobs_df, option)


if choice == "Jobs Upload":
    st.title("Jobs Upload")
    ju.upload_excel_jobs()
    # st.write(jobs_df)
    # st.write(machines_df)
    # st.write(processes_df)
    # st.write(month_list)
    # st.write(jobs_df['Month'])
    




