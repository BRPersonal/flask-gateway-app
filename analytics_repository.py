import os
from datetime import date, datetime
import pandas as pd
from pandas.core.frame import DataFrame
from dotenv import load_dotenv
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

def get_request_counts(group_by_column_names: list[str],
                       start_date_str: str, end_date_str: str,
                       user_id: int | None) -> list[dict]:

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

    # Step 3: Convert to list of dictionaries. rename cntr as Count
    result = grouped_df.rename(columns={'cntr': 'Count'}).to_dict(orient='records')

    return result

if __name__ == "__main__":

    group_by_column_names = ["request_date", "ref_app"]
    result = get_request_counts(group_by_column_names,"2024-12-01","2024-12-03",None)

    #convert date object to string
    for entry in result:
        entry["request_date"] = entry["request_date"].strftime('%Y-%m-%d')
    print("result=\n", result)

    #group by request_date and find count date_wise
    df = pd.DataFrame(result)
    date_wise_result = df.groupby("request_date", as_index=False)['Count'].sum().to_dict(orient='records')
    print("date_wise_result=\n", date_wise_result)



