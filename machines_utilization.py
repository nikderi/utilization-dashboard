import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import math
#from massage_report import machines_report
import massage_report as report
from streamlit_option_menu import option_menu
import matplotlib.pyplot as plt
from matplotlib.patches import ConnectionPatch
import altair as alt
from streamlit_vega_lite import vega_lite_component, altair_component
import plotly.figure_factory as ff
import plotly.graph_objects as go
import datetime as dt

month_map = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

def machines_util_metrics(machines_df, option):
    current_machines_df = machines_df[machines_df.Month == option]
    if machines_df is not None:
        # Filter overutilization
        overutil_df = current_machines_df[current_machines_df['Utilization'].astype(float) >= 80]
        # Filter normal utilized
        normal_util_df = current_machines_df[(current_machines_df['Utilization'].astype(float) >= 20) & (current_machines_df['Utilization'].astype(float) < 80)]
        # Filter underutilized
        underutil_df = current_machines_df[current_machines_df['Utilization'].astype(float) < 20]

        given_date = dt.datetime.strptime(option, '%B')
        last_month = given_date - dt.timedelta(days=given_date.day)
        last_month = last_month.strftime('%B')

        previous_machines_df = machines_df[machines_df.Month == last_month]

        def get_util_metric (util_df) :
            if len(util_df.index) > 0 :
                ncol = len(util_df.index)
                cols = st.columns(ncol)
                col_no = 3
                row_no = math.ceil(ncol/col_no)
                    
                def make_grid(rows,cols):
                    grid = [0]*rows
                    for i in range(rows):
                        with st.container():
                            grid[i] = st.columns(cols)
                    return grid

                grid= make_grid(row_no, col_no)
                counter = 0
                st.markdown("""
                    <style>
                        div[data-testid="metric-container"] {
                        background-color: #EEEEEE;;
                        border: 1px solid rgba(28, 131, 225, 0.1);
                        padding: 5% 5% 5% 10%;
                        border-radius: 10px;
                        color: rgb(30, 103, 119);
                        overflow-wrap: break-word;
                        }
                        /* breakline for metric text         */
                        div[data-testid="metric-container"] > label[data-testid="stMetricLabel"] > div {
                        overflow-wrap: break-word;
                        white-space: break-spaces;
                        color: #1F1B24;
                        }
                    </style>
                        """
                        , unsafe_allow_html=True)
                for i in range(0, row_no):
                    for j in range(0, col_no):
                        try:
                            utilization_delta = str(round(float(util_df.iloc[counter]['Utilization'])-
                                                        float(previous_machines_df.iloc[counter]['Utilization']),2))+ " % from {}".format(last_month)
                            grid[i][j].metric(util_df.iloc[counter]['HostMachineName'], util_df.iloc[counter]['Utilization']+ '%', utilization_delta)
                        except:
                            print('')
                        counter = counter + 1
        st.write('Overutilized')
        get_util_metric(overutil_df)
        st.write('Normal')
        get_util_metric(normal_util_df)
        st.write('Underutilized')
        get_util_metric(underutil_df)

def machines_util_pie_chart(machines_df, option):

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 5))
    fig.subplots_adjust(wspace=0)

    pie_df['HoursUtilized'] = pie_df["HoursUtilized"].astype(float)
    pie_df = pie_df.sort_values(by='HoursUtilized', ascending=True)
    total_utilized_ratio = pie_df['HoursUtilized'].astype(float).sum()/(8*8*len(pie_df.index))
    overall_ratios = [total_utilized_ratio, 1-total_utilized_ratio]
    labels = ['Utilized', 'Unutilized']
    explode = [0.1, 0]
    # rotate so that first wedge is split by the x-axis
    angle = -180 * overall_ratios[0]
    wedges, *_ = ax1.pie(overall_ratios, autopct='%1.1f%%', startangle=angle,
                        labels=labels, explode=explode)

    # bar chart parameters
    pie_df['Utilization Ratio'] = pie_df['HoursUtilized'].astype(float).apply(lambda x: round(x/pie_df['HoursUtilized'].astype(float).sum(),4))
    machine_ratios = np.array(pie_df['Utilization Ratio']).tolist()
    machine_labels = np.array(pie_df['HostMachineName']).tolist()
    bottom = 1
    width = .2

    # Adding from the top matches the legend.
    for j, (height, label) in enumerate(reversed([*zip(machine_ratios, machine_labels)])):
        bottom -= height
        bc = ax2.bar(0, height, width, bottom=bottom, align='center', color='C0', label=label,
                    alpha=0.1 + 0.08 * j)
        ax2.bar_label(bc, labels=[f"{height:.0%}"], label_type='center')

    ax2.set_title('Utilization of machines')
    ax2.legend()
    ax2.axis('off')
    ax2.set_xlim(- 2.5 * width, 2.5 * width)

    # use ConnectionPatch to draw lines between the two plots
    theta1, theta2 = wedges[0].theta1, wedges[0].theta2
    center, r = wedges[0].center, wedges[0].r
    bar_height = sum(machine_ratios)

    # draw top connecting line
    x = r * np.cos(np.pi / 180 * theta2) + center[0]
    y = r * np.sin(np.pi / 180 * theta2) + center[1]
    con = ConnectionPatch(xyA=(-width / 2, bar_height), coordsA=ax2.transData,
                        xyB=(x, y), coordsB=ax1.transData)
    con.set_color([0, 0, 0])
    con.set_linewidth(2)
    ax2.add_artist(con)

    # draw bottom connecting line
    x = r * np.cos(np.pi / 180 * theta1) + center[0]
    y = r * np.sin(np.pi / 180 * theta1) + center[1]
    con = ConnectionPatch(xyA=(-width / 2, 0), coordsA=ax2.transData,
                        xyB=(x, y), coordsB=ax1.transData)
    con.set_color([0, 0, 0])
    ax2.add_artist(con)
    con.set_linewidth(2)
    st.pyplot(plt)


def machines_util_line_graph(machines_df, option) :
    aggregated_df = machines_df[machines_df.HostMachineName == option]
    aggregated_df['Month'] = pd.Categorical(aggregated_df['Month'], categories=month_map, ordered=True)
    aggregated_df = aggregated_df.sort_values('Month', ascending=True)
    tab1, tab2 = st.tabs(["Hours Utilized", "Utilization (%)"])
    fig1 = px.line(aggregated_df, x='Month', y='HoursUtilized', color='HostMachineName', markers=False, title='Hours Utilized')
    fig2 = px.line(aggregated_df, x='Month', y='Utilization', color='HostMachineName', markers=False, title='Utilization (%)')
    # current_machines_df = machines_df.copy()
    # # given_date = dt.datetime.strptime(option, '%B')
    # # last_month = given_date - dt.timedelta(days=given_date.day)
    # # last_month = last_month.strftime('%B')
    # # previous_machines_df = machines_df[machines_df.Month == last_month]
    # month_map = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
    # total_hours = current_machines_df['HoursUtilized'].astype(float).sum()
    # total_max_hours = current_machines_df['HoursUtilized'].astype(float).sum()
    # new_row = pd.DataFrame({'HostMachineName': ['Overall'], 'HoursUtilized': [total_hours], 'Utilization': [0], 'Max HoursUtilized': [total_max_hours]})
    # current_machines_df = pd.concat([current_machines_df, new_row], ignore_index=True)
    # current_machines_df["Month"] = option
    # current_machines_df["Max HoursUtilized"] = current_machines_df.loc[0]['Max HoursUtilized']
    # current_machines_df.at[len(current_machines_df)-1, 'Utilization'] = round(current_machines_df.loc[len(current_machines_df)-1, 'HoursUtilized']/((len(current_machines_df)-1)*current_machines_df.loc[len(current_machines_df)-1, 'Max HoursUtilized'])*100, 2)
    # total_hours = previous_machines_df['HoursUtilized'].astype(float).sum()
    # total_max_hours = previous_machines_df['HoursUtilized'].astype(float).sum()
    # new_row = pd.DataFrame({'HostMachineName': ['Overall'], 'HoursUtilized': [total_hours], 'Utilization': [0], 'Max HoursUtilized': [total_max_hours]})
    # previous_machines_df = pd.concat([previous_machines_df, new_row], ignore_index=True)
    # previous_machines_df.at[0, 'Utilization'] = str(round(previous_machines_df.loc[previous_machines_df.index,'HoursUtilized'].astype(float)/previous_machines_df.loc[previous_machines_df.index,'Max HoursUtilized'].astype(float),2))
    # previous_machines_df["Month"] = "Mar"
    # previous_machines_df["Max HoursUtilized"] = previous_machines_df.loc[0]['Max HoursUtilized']
    # previous_machines_df.at[len(previous_machines_df)-1, 'Utilization'] = round(previous_machines_df.loc[len(previous_machines_df)-1, 'HoursUtilized']/((len(previous_machines_df)-1)*previous_machines_df.loc[len(previous_machines_df)-1, 'Max HoursUtilized'])*100, 2)
    # df_final = pd.concat([current_machines_df, previous_machines_df], ignore_index=True)
    # df_final = df_final.sort_values('Month', key = lambda x : x.apply (lambda x : month_map[x]
    with tab1:
        st.plotly_chart(fig1, theme="streamlit")
    with tab2:
        st.plotly_chart(fig2, theme="streamlit")


def machines_util_table(jobs_df, option) :
    process_df = report.processes(jobs_df)
    filtered_df = process_df[process_df.HostMachineName == option]
    filtered_df.reset_index(drop=True, inplace=True)
    total_hours = round(filtered_df['HoursUtilized'].astype(float).sum(), 4)
    total_utilization = round(filtered_df['Utilization'].astype(float).sum(), 4)
    new_row = pd.DataFrame({'ReleaseName': ['Total'], 'HostMachineName': [filtered_df.loc[0, 'HostMachineName']], 'HoursUtilized': [total_hours], 'Utilization': [total_utilization]})
    filtered_df = pd.concat([filtered_df, new_row], ignore_index=True)
    filtered_df = filtered_df.drop(['Year', 'Month'], axis=1)
    st.markdown("""
        <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
        </style>
        """, unsafe_allow_html=True)
    filtered_df['HoursUtilized'] = filtered_df['HoursUtilized'].astype(str)
    filtered_df['Utilization'] = filtered_df['Utilization'].astype(str)
    filtered_df = filtered_df[filtered_df.HostMachineName == option]
    filtered_df = filtered_df.drop(['HostMachineName'], axis=1)
    st.table(filtered_df)