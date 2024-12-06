"""
functions that start with an underscore are meant be private to this module
"""

import json
import os

import pandas as pd
from dotenv import load_dotenv
from pandas.core.frame import DataFrame
from sqlalchemy import create_engine, text


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

def _get_db_url() -> str :
    suffix = f"{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"

    if db_config["port"] == "3306":
        print("Generating connect url for MySql")
        return "mysql+pymysql://" + suffix
    elif db_config["port"] == "5432":
        print("Generating connect url for PostGre")
        return "postgresql://" + suffix
    else:
        raise ValueError(f"Invalid port: {db_config['port']}. Expected 3306 for MySQL or 5432 for PostgreSQL.")

def _execute_sql_query(query : str, params : dict = None) -> DataFrame:
    db_url = _get_db_url()
    engine = create_engine(db_url)

    with engine.connect() as connection:
        # Use text() to create a prepared statement
        result = connection.execute(text(query), params or {})
        df = pd.DataFrame(result.fetchall(), columns=result.keys())

    return df

def _insert_missing_rows(data_frame:DataFrame, group_by_column:str) -> DataFrame:

    #Get unique request dates
    unique_dates = data_frame['request_date'].unique()

    #Get unique values for group_by_column
    unique_groups = data_frame[group_by_column].unique()

    #create a list to hold new rows
    new_rows = []
    # Loop through each unique request date and check for each unique group
    for dt in unique_dates:
        for grp in unique_groups:
            # Check if the combination exists
            if not ((data_frame['request_date'] == dt) & (data_frame[group_by_column] == grp)).any():
                # Insert a new row with cntr as 0
                new_rows.append({'request_date': dt, group_by_column: grp, 'cntr': 0})

    if new_rows:
        new_df = pd.DataFrame(new_rows)
        return pd.concat([data_frame, new_df], ignore_index=True)

    return data_frame  #return original if no new changes


def _get_analytics_data(data_frame:DataFrame,group_by_column:str ) -> dict:

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

    # Group by given column and create trend data
    for app in data_frame[group_by_column].unique():
        trend_data = {
            "group": app,
            "data": data_frame[data_frame[group_by_column] == app]['cntr'].tolist()
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

def get_analytics_data(group_by_column: str,
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
        b.{group_by_column},
        COUNT(*) AS cntr
    FROM tyk_analytics_data a, key_tbl b
    WHERE a.request_date BETWEEN :start_date AND :end_date
    {user_id_filter}
    and b.value = a.api_key
    GROUP BY a.request_date, b.{group_by_column};
    """

    query_params = {
        "start_date" : start_date_str,
        "end_date" : end_date_str
    }

    # Fetch data from database into a DataFrame
    df = _execute_sql_query(query,query_params)

    if df.empty:
        print("No records found")
        return None

    print("df from db=\n", df)

    #Convert request_date to string in 'YYYY-mm-dd' format
    df['request_date'] = df['request_date'].astype(str)
    print("df after converting to string=\n", df)

    corrected_df = _insert_missing_rows(df, group_by_column)
    print("corrected_df after insert=\n", corrected_df)

    analytics_data = _get_analytics_data(corrected_df, group_by_column)

    return analytics_data

def _get_top_users(data_frame: DataFrame, group_by_column: str) -> dict:
    result_dict = {
        "data": {
            "total_users": int(data_frame['total_records'].iloc[0]),  # Get total_records from the first row
            "users": []
        }
    }

    # Populate the users list
    for _, row in data_frame.iterrows():
        user_info = {
            "group": row[group_by_column],
            "user_id": int(row['user_id']),
            "first_name": row['first_name'],
            "last_name": row['last_name'],
            "usage": int(row['cntr'])
        }
        result_dict["data"]["users"].append(user_info)

    return result_dict

def get_top_users(
                group_by_column: str,
                start_date_str: str, end_date_str: str,
                limit:int = 10, offset:int = 0,
                group_by_filter: str = None) -> dict:

    if group_by_filter:
        having_clause = f" having b.{group_by_column} = :filter_value"
    else:
        having_clause = ""

    query = f"""
        with paginated_data as (
          select
          b.{group_by_column},b.user_id,count(*) as cntr
          from tyk_analytics_data a, key_tbl b
          where a.request_date between :start_date AND :end_date
          and b.value = a.api_key
          group by b.{group_by_column},b.user_id
          {having_clause}
        ),
        user_data as (
          select u.user_id,u.first_name,u.last_name,u.email
          from user_tbl u
        )
        SELECT 
            pd.{group_by_column},
            ud.user_id,
            ud.first_name,
            ud.last_name,
            ud.email,
            pd.cntr,
            (SELECT COUNT(*) FROM paginated_data) AS total_records
        FROM paginated_data pd, user_data ud
        WHERE pd.user_id = ud.user_id
        ORDER BY pd.cntr DESC
        LIMIT :rows_per_page OFFSET :starting_row;
    """

    query_params = {
        "start_date" : start_date_str,
        "end_date" : end_date_str,
        "rows_per_page": limit,
        "starting_row": offset
    }

    if group_by_filter:
        query_params["filter_value"] = group_by_filter

    # Fetch data from database into a DataFrame
    df = _execute_sql_query(query,query_params)

    if df.empty:
        print("No records found")
        return None

    print("df=\n", df)
    return _get_top_users(df,group_by_column)

if __name__ == "__main__":

    #group_by_column_name = "tier";
    group_by_column_name = "ref_app";

    result = get_analytics_data(group_by_column_name, "2024-12-03", "2024-12-03", None)
    print("analytics_data=\n", json.dumps(result, indent=4))

    filter_by = "chrome_extension"  #None
    result = get_top_users(group_by_column_name, "2024-12-01", "2024-12-03",group_by_filter=filter_by)
    print("top users=\n", json.dumps(result, indent=4))






