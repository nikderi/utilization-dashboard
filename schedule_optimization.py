import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import datetime as dt
import calendar
import math


def utilization_heatmap(df, option):
    wd_df = pd.read_excel('working_days.xlsx')
    attended_working_days = wd_df.iloc[wd_df.index[wd_df['Month'] == option].tolist()[0]]['Working Days']
    datetime_object = dt.datetime.strptime(option, '%B')
    unattended_working_days = calendar.monthrange(datetime_object.year, datetime_object.month)[1]
    # Get the number of days in the month
    df = df[['StartTime','EndTime', 'HostMachineName']]
    df['StartTime'] = pd.to_datetime(df['StartTime'])
    df['EndTime'] = pd.to_datetime(df['EndTime'])
    hourly_df = df.copy()
    hourly_df['Duration'] = hourly_df['EndTime'] - hourly_df['StartTime']
    hourly_df['Duration'] = hourly_df['Duration'].dt.seconds
    hours = [str(i) for i in range(24)]
    hourly_df[hours] = 0
    machine_labels = np.unique(np.array(hourly_df['HostMachineName']).tolist())

    for index, row in hourly_df.iterrows():
        start_hour = row['StartTime'].hour
        start_second = row['StartTime'].minute*60 + row['StartTime'].second
        end_second = row['EndTime'].minute*60 + row['EndTime'].second
        end_hour = row['EndTime'].hour
        total_duration = row['Duration']
        if row['EndTime'].day - row['StartTime'].day == 0 :
            for hour in range(start_hour, end_hour + 1):
                if start_hour == end_hour :
                    hourly_df.loc[index, str(hour)] = total_duration 
                else:
                    if hour == start_hour :
                            current_duration = abs(3600 - start_second)
                    elif hour == end_hour :
                            current_duration = end_second
                    else : 
                        if total_duration/3600 >= 1 :
                            current_duration = 3600          
                    total_duration = total_duration - current_duration
                    hourly_df.loc[index, str(hour)] = current_duration
        else :
            for hour in range(0, end_hour + 1):
                if hour == end_hour :
                    current_duration = end_second
                else : 
                    if total_duration/3600 >= 1 :
                        current_duration = 3600          
                total_duration = total_duration - current_duration
                hourly_df.loc[index, str(hour)] = current_duration

            for hour in range(start_hour, 24):
                if hour == start_hour :
                    current_duration = 3600 - start_second
                else : 
                    if total_duration/3600 >= 1 :
                        current_duration = 3600          
                total_duration = total_duration - current_duration
                hourly_df.loc[index, str(hour)] = current_duration

    
    hourly_df = hourly_df.drop(['StartTime', 'EndTime', 'Duration'], axis=1)
    grouped_hourly_df = hourly_df.set_index('HostMachineName')
    grouped_hourly_df = hourly_df.groupby('HostMachineName').sum()
    hours = np.array(range(0, 24))
    # st.write(grouped_hourly_df)
    
    title1 = 'Total Utilization Minutes by Hour'

    fig1 = go.Figure(data=go.Heatmap(
            z=grouped_hourly_df,
            x=hours,
            y=machine_labels,
            colorscale='BuPu'))

    fig1.update_layout(
        title= title1,
        xaxis_nticks=36)

    attended_percentage_df = grouped_hourly_df[grouped_hourly_df.index != 'CTX 195']
    attended_percentage_df = round(attended_percentage_df/(attended_working_days*60*60)*100, 2)
    unattended_percentage_df = grouped_hourly_df[grouped_hourly_df.index == 'CTX 195']
    unattended_percentage_df = round(unattended_percentage_df/(unattended_working_days*60*60)*100, 2)
    percentage_df = pd.concat([attended_percentage_df, unattended_percentage_df], ignore_index=False)
    # min_val = grouped_hourly_df.min(axis=1)
    # max_val = grouped_hourly_df.max(axis=1)
    # scaled_df = (grouped_hourly_df.T - min_val) / (max_val - min_val)

    # normalized_hourly_df = scaled_df.T  # Transpose back to the original orientation
    # st.table(scaled_df)
    # normalized_hourly_df = (grouped_hourly_df-grouped_hourly_df.min().min())/(grouped_hourly_df.max().max()-grouped_hourly_df.min().min())
    # testdf = grouped_hourly_df.copy()
    # testdf = testdf.iloc[0,:]
    # normalized_hourly_df = (testdf.min().min())/(testdf.max().max()-testdf.min().min())
    # st.table(normalized_hourly_df)
    # normalized_hourly_df = (grouped_hourly_df-grouped_hourly_df.min(axis=0))/(grouped_hourly_df.max(axis=0)-grouped_hourly_df.min(axis=0))
    # st.table(grouped_hourly_df)
    # st.table(normalized_hourly_df)
    title2 = 'Percentage of Utilization by Hour'

    fig2 = go.Figure(data=go.Heatmap(
            z=percentage_df,
            x=hours,
            y=machine_labels,
            colorscale='BuPu'))

    fig2.update_layout(
        title= title2,
        xaxis_nticks=36)
          
    # Extract the date from StartTime and EndTime
    # st.table(hourly_df)
    df['Day'] = df['StartTime'].dt.date
    # st.table(df)
    # df['EndDate'] = df['EndTime'].dt.date
    grouped_df = df.groupby(['HostMachineName', 'Day']).size().reset_index(name='Frequency')
    grouped_df['Day'] = pd.to_datetime(grouped_df['Day']).dt.day
    # st.table(grouped_df)
    # st.table(grouped_df)
    pivot_df = grouped_df.pivot(index='HostMachineName', columns='Day', values='Frequency').fillna(0)
    # st.write(pivot_df)
    # all_days = pd.date_range(start=df['StartTime'].min().date(), end=df['StartTime'].max().date(), freq='D')
    all_days = range(1, 31)
    pivot_df = pivot_df.reindex(columns=all_days, fill_value=0)
    machine_labels = np.unique(np.array(df['HostMachineName']).tolist())
    newdf = pd.DataFrame(0, index=machine_labels, columns=all_days)
    # st.write(grouped_df)
    # st.write(newdf)
    for i in range(0, len(newdf.index)):
            for j in range(0, len(newdf.columns)):
                # if len(grouped_df[(grouped_df[grouped_df.HostMachineName == "MBBCTXRPAPRD175"]) & (grouped_df[grouped_df.Day == newdf.columns[j]])]) > 0 :
                if len(grouped_df[(grouped_df.HostMachineName == newdf.index[i]) & (grouped_df.Day == newdf.columns[j])]) > 0 :
                    newdf.iloc[i,j] = grouped_df[(grouped_df.HostMachineName == newdf.index[i]) & (grouped_df.Day == newdf.columns[j])]['Frequency']
    base = dt.datetime.today()
    # Calculate the first day of the current month
    first_day_current_month = dt.datetime(base.year, base.month, 1)
    last_day_prev_month = first_day_current_month - dt.timedelta(days=1)
    num_days_prev_month = last_day_prev_month.day

    dates = last_day_prev_month - np.arange(num_days_prev_month) * dt.timedelta(days=1)
    machine_labels = np.unique(np.array(grouped_df['HostMachineName']).tolist())

    title3 = 'Utilization by Day'

    fig3 = go.Figure(data=go.Heatmap(
            z=newdf,
            x=dates,
            y=machine_labels,
            colorscale='BuPu'))

    fig3.update_layout(
        title=title3,
        xaxis_nticks=36)

    # fig.show()

    tab1, tab2, tab3 = st.tabs([title1, title2, title3])

    with tab1:
        st.plotly_chart(fig1)
    with tab2:
        st.plotly_chart(fig2)
    with tab3:
        st.plotly_chart(fig3)



    unutilized_percentage_df = 100 - percentage_df
    title4 = 'Percentage of Utilization by Hour'

    fig4 = go.Figure(data=go.Heatmap(
            z=unutilized_percentage_df,
            x=hours,
            y=machine_labels,
            colorscale='Mint'))

    fig4.update_layout(
        title= title2,
        xaxis_nticks=36)

    # st.plotly_chart(fig4)
    expected_duration = st.number_input('Insert expected process duration:', min_value= 1, max_value= 24)
    expected_duration = math.ceil(expected_duration)
    unutilized_threshold = st.slider(label=
    "Select how free the machines are:", 
    min_value=1.0, max_value=100.0, value=50.0, step=1.0, format="%g %%", help='The higher the number, the less the timeslot suggestions given.')
    df_validate = unutilized_percentage_df >= unutilized_threshold
    
    final_df = df_validate.copy()
    for index, row in df_validate.iterrows():
        row_index = df_validate.index.get_loc(index)
        counter = 0
        start = None
        for col in df_validate.columns:
            col_index = int(col)
            if df_validate.iloc[row_index, col_index]:
                if start is None:
                    start = col_index
                counter = counter + 1
            else:
                counter = 0
                start = None
            
            if counter>= expected_duration:
                final_df.iloc[row_index, start : start + counter] = 1
            else:
                final_df.iloc[row_index, col_index] = 0

    title5 = 'Timeslot Available Of ' + str(expected_duration) + ' Hour(s) Utilization'

    fig5 = go.Figure(data=go.Heatmap(
            z=final_df,
            x=hours,
            y=machine_labels,
            zmin=0,
            zmax=1,
            colorscale=[(0, '#f7fcfd'), (1,'#873d9b')]))
            # colorscale=[[1.0,'green'], [0.0, 'white']]))

    fig5.update_layout(
        title= title5,
        xaxis_nticks=36)

    st.plotly_chart(fig5)

    
    # best_hours = find_best_hours(unutilized_percentage_df, 2, 99.0)
#     for i, machine_ranges in enumerate(best_hours):
#         machine_name = machine_labels[i]
#         range_str = ", ".join([f"{start}-{end}" for start, end in machine_ranges])
#         # print(f"Best hours for {machine_name}: {range_str}")
#         st.write(f"Best hours for {machine_name}: {range_str}")

    
# def find_best_hours(df, expected_duration, threshold):
#     best_hours = []
#     # st.table(df)
#     updated_df = df.copy()

#     for col in df.columns:
#         col_name = 24+ int(col)
#         # print(col(idx))
#         updated_df[str(col_name)] = df[str(col_name%24)]
   
#     for index, row in updated_df.iterrows():
#         machine = updated_df.loc[index]
#         best_hours_machine = np.where(machine >= threshold)[0]
#         best_ranges = []
#         # start = None
#         # end = None
#         # counter = 0
#         # # st.table(best_hours_machine)
#         # for hour in best_hours_machine:
#         #     if start is None:
#         #         start = hour
#         #         counter = 1
#         #     elif hour == start + counter:
#         #         if hour - start == expected_duration:
#         #             if hour > 23:
#         #                 end = hour%24
#         #             else:
#         #                 end = hour
#         #             # end = start + expected_duration
#         #             if start < 23:
#         #                 best_ranges.append((start, end))
#         #             start = hour
#         #             end = None
#         #             counter = 1
#         #         else:
#         #             counter = counter + 1
#         #     else:
#         #         start = hour
#         #         counter = 1
        
#         start = None
#         end = None
#         counter = 0
#         # st.table(best_hours_machine)
#         for hour in best_hours_machine:
#             if start is None:
#                 start = hour+1
#                 counter = 1
#             elif hour == start + counter:
#                 if hour - start == expected_duration:
#                     if hour > 23:
#                         end = hour%24
#                     else:
#                         end = hour
#                     # end = start + expected_duration
#                     if start < 23:
#                         best_ranges.append((start, end))
#                     start = hour
#                     end = None
#                     counter = 1
#                 else:
#                     counter = counter + 1
#             else:
#                 start = hour
#                 counter = 1
#         # start = None
#         # end = None
#         # counter = 0
#         # for hour in best_hours_machine:
#         #     if start is None:
#         #         start = hour + 1
#         #     elif hour == start + counter:
#         #         if hour - start == expected_duration:
#         #             end = hour
#         #             # end = start + expected_duration
#         #             best_ranges.append((start, end))
#         #             start = hour+1
#         #             end = None
#         #             counter = 1
#         #         else:
#         #             counter = counter + 1
#         #     else:
#         #         start = hour
#         #         counter = 1
          
    
#         # for hour in best_hours_machine:
#         #     if start is None:
#         #         start = hour
#         #         counter = 1
#         #     elif hour == start + counter:
#         #         if hour - start == expected_duration:
#         #             end = hour
#         #             # end = start + expected_duration
#         #             best_ranges.append((start, end))
#         #             print(hour, start, end)
#         #             start = hour
#         #             end = None
#         #             counter = 1
#         #         else:
#         #             counter = counter + 1
#         #     else:
#         #         start = hour
#         #         # counter = 1
          
#         #     print(hour, start)

#         # start = None
#         # end = None
#         # counter = 0
#         # for hour in best_hours_machine:
#         #     if start is None:
#         #         start = hour + 1
#         #     elif hour == start + counter:
#         #         if hour - start == expected_duration:
#         #             end = hour
#         #             # end = start + expected_duration
#         #             best_ranges.append((start, end))
#         #             start = hour+1
#         #             end = None
#         #             counter = 1
#         #         else:
#         #             counter = counter + 1
#         #     else:
#         #         start = hour
#         #         counter = 1
          

                

#         #    for hour in best_hours_machine:
#         #     if start is None:
#         #         start = hour
#         #     elif hour == start + 1:
#         #         if hour - start == expected_duration:
#         #             end = start + expected_duration
#         #         else:
#         #             end = hour
#         #         best_ranges.append((start, end))
#         #         start = hour
#         #     else:
#         #         start = hour
#         # if start is not None:
#         #     end = (start + expected_duration) % 24
#         #     best_ranges.append((start, end))
#         best_ranges.sort()
#         best_hours.append(best_ranges)
#     return best_hours