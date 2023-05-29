import pandas as pd
import sqlite3
import streamlit as st
import massage_report

def upload_excel_jobs():
    # Allow user to upload an Excel file
    uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"], accept_multiple_files=True)
    if uploaded_file is not None:
        for file in uploaded_file:     
            # Load the uploaded file into a Pandas DataFrame
            df = pd.read_excel(file, 'Jobs')
            df['HostMachineName'] = df['HostMachineName'].fillna('CTX 179')
            df = df.applymap(str)
            jobs_df = massage_report.format_columns(df)
            machines_df = massage_report.machines(df)
            processes_df = massage_report.processes(df)
            year_month_df = massage_report.get_year_and_month(df)
            year_month_df = year_month_df[['Year', 'Month']]
            year_month_df = year_month_df.head(1)
            # Push the machines table to database
            database_name = 'rpa_jobs.db'
            table_name = 'jobs'
            dataframe_to_sqlite(jobs_df, database_name, table_name)
            table_name = 'machines'
            dataframe_to_sqlite(machines_df, database_name, table_name)
            # Push the processes table to database
            table_name = 'processes'
            dataframe_to_sqlite(processes_df, database_name, table_name)
            table_name = 'year_month'
            dataframe_to_sqlite(year_month_df, database_name, table_name)
            st.info('File uploaded to database.')


def dataframe_to_sqlite(df, db_name, table_name):
    # Create a connection to the SQLite database
    conn = sqlite3.connect(db_name)
        # Check if the table already exists in the database
    try:
        all_df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    except:
        all_df = None

    uploaded_year = df.loc[0, 'Year']
    uploaded_month = df.loc[0, 'Month']
    # Append DataFrame if the table already exists
    if all_df is None:
        df.to_sql(table_name, conn, if_exists='replace', index=False)
    else:
        if not(all_df['Year'].str.contains(uploaded_year, case=False).any() & all_df['Month'].str.contains(uploaded_month, case=False).any()):
            df.to_sql(table_name, conn, if_exists='append', index=False)

    # Close the database connection
    conn.close()




# # Convert the DataFrame to an SQLite database
# dataframe_to_sqlite(df, database_name, table_name)

# conn = sqlite3.connect(database_name)
# cursor = conn.cursor()
# cursor.execute(f"SELECT * FROM {table_name}")
# a = cursor.fetchall()

# for i in a:
#     print(i)
# # print(cursor.fetchall())

# conn.close()


