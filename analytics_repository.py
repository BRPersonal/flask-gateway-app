"""
functions that start with an underscore are meant be private to this module
"""

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

def get_analytics(group_by_column: str,
                  start_date_str: str, end_date_str: str,
                  user_id: int = None) -> DataFrame:
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
    GROUP BY a.request_date, b.{group_by_column}
    ORDER BY a.request_date, b.{group_by_column};
    """

    query_params = {
        "start_date" : start_date_str,
        "end_date" : end_date_str
    }

    # Fetch data from database into a DataFrame
    df = _execute_sql_query(query,query_params)

    return df

def get_top_users(
                group_by_column: str,
                start_date_str: str, end_date_str: str,
                limit:int = 10, offset:int = 0,
                group_by_filter: str = None) -> DataFrame:

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
        ORDER BY pd.cntr DESC,ud.user_id
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
    return df
