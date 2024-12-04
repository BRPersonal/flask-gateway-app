import json
import os

import pandas as pd
from dotenv import load_dotenv
from pandas.core.frame import DataFrame
from sqlalchemy import create_engine

# Load environment variables from .env file
load_dotenv()

# Database connection parameters
db_config = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_DATABASE')
}

def get_db_url() -> str :
    suffix = f"{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
    if db_config["port"] == "3306":
        print("Generating connect url for MySql")
        return "mysql+pymysql://" + suffix
    elif db_config["port"] == "5432":
        print("Generating connect url for PostGre")
        return "postgresql://" + suffix

def execute_sql_query(query : str) -> DataFrame:
    db_url = get_db_url()
    engine = create_engine(db_url)
    return pd.read_sql_query(query, engine)

def get_analytics_data(data_frame:DataFrame ) -> dict:

    # Calculate total_requests and average_daily_requests
    total_requests = int(data_frame['cntr'].sum())
    unique_dates_count = data_frame['request_date'].nunique()
    average_daily_requests = int(total_requests // unique_dates_count)

    # Create the analytics_data dictionary
    analytics_data = {
        "range": data_frame['request_date'].unique().tolist(),
        "cummulative": data_frame.groupby('request_date')['cntr'].sum().tolist(),
        "trend": []
    }

    # Group by ref_app and create trend data
    for app in data_frame['ref_app'].unique():
        trend_data = {
            "group": app,
            "data": data_frame[data_frame['ref_app'] == app]['cntr'].tolist()
        }
        analytics_data["trend"].append(trend_data)

    # Create the final output structure
    final_result = {
        "data": {
            "summary": {
                "total_requests": total_requests,
                "average_daily_requests": average_daily_requests
            },
            "analytics_data": analytics_data
        }
    }

    return final_result

def get_request_counts(group_by_column_names: list[str],
                       start_date_str: str, end_date_str: str,
                       user_id: int | None) -> dict:

    # Step 1: Execute the SQL query with dynamic date parameters
    if user_id:
        user_id_filter = f"and b.user_id={user_id}"
    else:
        user_id_filter = ""

    query = f"""
    SELECT
        a.request_date,
        b.ref_app,
        b.user_id,
        COUNT(*) AS cntr
    FROM tyk_analytics_data a, key_tbl b
    WHERE a.request_date BETWEEN '{start_date_str}' AND '{end_date_str}'
    {user_id_filter}
    and b.value = a.api_key
    GROUP BY a.request_date, b.ref_app, b.user_id;
    """

    # Fetch data from database into a DataFrame
    df = execute_sql_query(query)

    if df.empty:
        print("No records found")
        return None

    # Step 2: Group by one or more columns and sum 'cntr'.
    grouped_df = df.groupby(group_by_column_names, as_index=False)['cntr'].sum()

    #Convert request_date to string in 'YYYY-mm-dd' format
    grouped_df['request_date'] = grouped_df['request_date'].astype(str)
    print("grouped_df=\n", grouped_df)

    analytics_data = get_analytics_data(grouped_df)

    return analytics_data

if __name__ == "__main__":

    group_by_column_names = ["request_date", "ref_app"]
    analytics_data = get_request_counts(group_by_column_names,"2024-12-01","2024-12-03",None)
    print("analytics_data=\n", json.dumps(analytics_data, indent=4))





