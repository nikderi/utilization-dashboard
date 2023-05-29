import pandas as pd
import numpy as np
import datetime as dt
import calendar


wd_df = pd.read_excel('working_days.xlsx')
attended_working_hours = 8
unattended_working_hours = 24


def machines(df, option):
    df = format_columns(df)
    calculated_df = df[['HostMachineName', 'Type', 'HoursUtilized']]
    grouped_df = calculated_df.groupby('HostMachineName').agg({'HoursUtilized': 'sum', 'Type': 'first'}).reset_index()
    current_month = df['StartTime'].dt.strftime('%B')[0]
    current_year = df['StartTime'].dt.strftime('%Y')[0]
    attended_working_days = wd_df.iloc[wd_df.index[wd_df['Month'] == current_month].tolist()[0]]['Working Days']
    # Convert month string to datetime object
    datetime_object = dt.datetime.strptime(option, '%B')
    unattended_working_days = calendar.monthrange(datetime_object.year, datetime_object.month)[1]
    # Get the number of days in the month
    num_days = calendar.monthrange(datetime_object.year, datetime_object.month)[1]
    grouped_df['Utilization'] = grouped_df['HoursUtilized']/(attended_working_days*attended_working_hours)*100
    grouped_df.loc[grouped_df['Type']=='Unattended','Utilization'] = grouped_df.loc[grouped_df['Type']=='Unattended', 'HoursUtilized']/(unattended_working_hours*unattended_working_days)*100
    grouped_df = np.round(grouped_df,2).astype(str)
    grouped_df['MaxHoursUtilization'] = attended_working_days*attended_working_hours
    grouped_df.loc[grouped_df['Type']=='Unattended','MaxHoursUtilization'] = unattended_working_hours*30
    grouped_df['Year'] = current_year
    grouped_df['Month'] = current_month
    grouped_df.sort_values(by=['HostMachineName'], inplace=True,)
    grouped_df.reset_index(drop=True, inplace=True)
    return grouped_df

def processes(df):
    df = format_columns(df)
    calculated_df = df[['ReleaseName','HostMachineName','HoursUtilized']]
    grouped_df = calculated_df.groupby(['ReleaseName', 'HostMachineName'], as_index=False).sum()
    current_month = df['StartTime'].dt.strftime('%B')[0]
    current_year = df['StartTime'].dt.strftime('%Y')[0]
    working_days = wd_df.iloc[wd_df.index[wd_df['Month'] == current_month].tolist()[0]]['Working Days']
    grouped_df['Utilization'] = grouped_df['HoursUtilized']/(working_days*attended_working_hours)*100
    grouped_df = np.round(grouped_df,4).astype(str)
    grouped_df['Year'] = current_year
    grouped_df['Month'] = current_month
    grouped_df.sort_values(by=['HostMachineName'], inplace=True,)
    grouped_df.reset_index(drop=True, inplace=True)
    return grouped_df


def format_columns(df):
    df['StartTime'] = pd.to_datetime(df['StartTime'])
    df['EndTime'] = pd.to_datetime(df['EndTime'])
    df = get_year_and_month(df)
    df['HoursUtilized'] = (df['EndTime'] - df['StartTime']).astype('timedelta64[s]')
    df['HoursUtilized'] = df['HoursUtilized'].apply(lambda x: x.total_seconds()/3600).apply(float)
    df['HostMachineName'] = df['HostMachineName'].replace(['MBBCTXRPAPRD'], 'CTX ', regex=True).replace(['MSSCTXRPAPRD'], 'CTX ', regex=True)
    df['ReleaseName'] =df['ReleaseName'].str.replace('.', ' ')
    df['ReleaseName'] = df['ReleaseName'].str.replace('_', ' ')
    return df

def get_year_and_month(df):
    current_month = df['StartTime'].dt.strftime('%B')[0]
    current_year = df['StartTime'].dt.strftime('%Y')[0]
    df['Year'] = current_year
    df['Month'] = current_month
    return df
