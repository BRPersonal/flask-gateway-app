import json
import os

import requests
from dotenv import load_dotenv

from api_response import ApiResponse
from utils import get_current_timestamp
from datetime import datetime
import pandas as pd
from pandas.core.frame import DataFrame
import analytics_repository as repository

load_dotenv()

TYK_AUTHORIZATION = os.getenv("X-TYK-AUTHORIZATION")
TYK_BASE_URL = os.getenv("TYK_BASE_URL")
ORG_ID = os.getenv("ORG_ID")
INTERNAL_SERVER_ERROR = "500"

print(f"authorization={TYK_AUTHORIZATION}")
print(f"baseUrl={TYK_BASE_URL}")
print(f"OrgId={ORG_ID}")



def create_key(plan: str) -> dict:
    api_response: ApiResponse = None
    post_data = {
        "allowance": 0,
        "apply_policies": [plan],
        "enable_detailed_recording": True,
        "date_created": get_current_timestamp(),
        "org_id": ORG_ID,
        "tags": [
            "security",
            "edge",
            "edge-eu"
        ],
        "throttle_interval": 10,
        "throttle_retry_limit": 10
    }

    try:
        tyk_response = requests.post(
            f"{TYK_BASE_URL}/tyk/keys",
            headers={
                "Content-Type": "application/json",
                "x-tyk-authorization": TYK_AUTHORIZATION
            },
            data=json.dumps(post_data)
        )

        if tyk_response.status_code == 200 or tyk_response.status_code == 201:
            api_response = ApiResponse(message="Key creation successful",
                                       statuscode=tyk_response.status_code,
                                       response=tyk_response.json())
        else:
            api_response = ApiResponse(error="Key creation Failed",
                                       statuscode=tyk_response.status_code,
                                       response=tyk_response.text)

    except Exception as e:
        api_response = ApiResponse(error="Request failed",
                                   statuscode=INTERNAL_SERVER_ERROR,
                                   response=str(e)
                                   )
    return api_response.to_dictionary()

def list_keys() -> dict:
    api_response : ApiResponse = None

    try:
        tyk_response = requests.get(
            f"{TYK_BASE_URL}/tyk/keys",
            headers={
                "Content-Type": "application/json",
                "x-tyk-authorization": TYK_AUTHORIZATION
            }
        )

        if tyk_response.status_code == 200 or tyk_response.status_code == 201:
            api_response = ApiResponse(message="Keys retrieved successfully",
                                       statuscode=tyk_response.status_code,
                                       response=tyk_response.json())
        else:
            api_response = ApiResponse(error="Keys retrieval Failed",
                                       statuscode=tyk_response.status_code,
                                       response=tyk_response.text)

    except Exception as e:
        api_response = ApiResponse(error="Request failed",
                                   statuscode=INTERNAL_SERVER_ERROR,
                                   response=str(e)
                                   )

    return api_response.to_dictionary()

def get_key_details(key: str) -> dict:
    api_response : ApiResponse = None

    try:
        tyk_response = requests.get(
            f"{TYK_BASE_URL}/tyk/keys/{key}",
            headers={
                "Content-Type": "application/json",
                "x-tyk-authorization": TYK_AUTHORIZATION
            }
        )

        if tyk_response.status_code == 200 or tyk_response.status_code == 201:
            api_response = ApiResponse(message=f"Key {key} retrieved successfully",
                                       statuscode=tyk_response.status_code,
                                       response=tyk_response.json())
        else:
            api_response = ApiResponse(error=f"Key {key} retrieval Failed",
                                       statuscode=tyk_response.status_code,
                                       response=tyk_response.text)

    except Exception as e:
        api_response = ApiResponse(error=f"Request failed for Key {key}",
                                   statuscode=INTERNAL_SERVER_ERROR,
                                   response=str(e)
                                   )

    return api_response.to_dictionary()

def update_key_plan(request_body:dict) -> dict:
    api_response: ApiResponse = None

    plan = request_body["plan"]
    key = request_body["key"]
    post_data = {
        "apply_policies": [plan]
    }

    try:
        tyk_response = requests.post(
            f"{TYK_BASE_URL}/tyk/keys/{key}",
            headers={
                "Content-Type": "application/json",
                "x-tyk-authorization": TYK_AUTHORIZATION
            },
            data=json.dumps(post_data)
        )

        if tyk_response.status_code == 200 or tyk_response.status_code == 201:
            api_response = ApiResponse(message=f"Plan updation for key {key} successful",
                                       statuscode=tyk_response.status_code,
                                       response=tyk_response.json())
        else:
            api_response = ApiResponse(error=f"Plan updation for key {key} Failed",
                                       statuscode=tyk_response.status_code,
                                       response=tyk_response.text)

    except Exception as e:
        api_response = ApiResponse(error="Request failed",
                                   statuscode=INTERNAL_SERVER_ERROR,
                                   response=str(e)
                                   )
    return api_response.to_dictionary()

def delete_key(key:str) -> dict:
    api_response : ApiResponse = None

    try:
        tyk_response = requests.delete(
            f"{TYK_BASE_URL}/tyk/keys/{key}",
            headers={
                "Content-Type": "application/json",
                "x-tyk-authorization": TYK_AUTHORIZATION
            }
        )

        if tyk_response.status_code == 200 or tyk_response.status_code == 201:
            api_response = ApiResponse(message=f"Key {key} deleted successfully",
                                       statuscode=tyk_response.status_code,
                                       response=tyk_response.json())
        else:
            api_response = ApiResponse(error=f"Key {key} deletion failed",
                                       statuscode=tyk_response.status_code,
                                       response=tyk_response.text)

    except Exception as e:
        api_response = ApiResponse(error="Request failed",
                                   statuscode=INTERNAL_SERVER_ERROR,
                                   response=str(e)
                                   )

    return api_response.to_dictionary()

def get_analytics(group_by_column:str, start_date_str:str, end_date_str:str,user_id: int = None) -> dict:

    try:
        analytics_data_frame = repository.get_analytics(group_by_column, start_date_str, end_date_str, user_id)

        if analytics_data_frame.empty:
            print("No records found")
            api_response = ApiResponse(message="No Data Found",
                                       response=None,
                                       statuscode="200")
        else:
            print("df from source=\n", analytics_data_frame)

            days_count = _count_dates_between(start_date_str, end_date_str)
            if days_count > 30:
                print("Input range exceeds 30 days. Regrouping by month")

                aggregate_month = True

                # Convert request_date to string in 'YYYY-mm-dd' format and drop the day part from date
                analytics_data_frame['request_date'] = analytics_data_frame['request_date'].astype(str).str.slice(0, 7)

                # form the group again and calculate fresh sum
                analytics_data_frame = analytics_data_frame.groupby(["request_date", group_by_column], as_index=False)['cntr'].sum()
            else:

                aggregate_month = False

                # Convert request_date to string in 'YYYY-mm-dd' format
                analytics_data_frame['request_date'] = analytics_data_frame['request_date'].astype(str)

            print("df after converting to string=\n", analytics_data_frame)

            unique_dates = _get_date_range(start_date_str, end_date_str, aggregate_month)
            corrected_df = _insert_missing_rows(analytics_data_frame, group_by_column,unique_dates)
            print("corrected_df after insert=\n", corrected_df)

            analytics_data = _get_analytics_data(corrected_df, group_by_column, days_count)

            api_response = ApiResponse(message="Success",
                                       response = json.loads(json.dumps(analytics_data, indent=4)),
                                       statuscode="200")
    except Exception as e:
        api_response = ApiResponse(error="Request failed",
                                   statuscode=INTERNAL_SERVER_ERROR,
                                   response=str(e))
    return api_response.to_dictionary()

def get_top_users(group_by_column:str, start_date_str:str, end_date_str:str,
                  limit:int,offset:int, group_by_filter:str = None) -> dict:

    try:
        top_users_data_frame = repository.get_top_users(group_by_column, start_date_str, end_date_str,
                                             limit,offset,group_by_filter)

        if top_users_data_frame.empty:
            api_response = ApiResponse(message="No Data Found",
                                       response=None,
                                       statuscode="200")
        else:
            top_users_data = _get_top_users(top_users_data_frame,group_by_column)
            api_response = ApiResponse(message="Success",
                                       response = json.loads(json.dumps(top_users_data, indent=4)),
                                       statuscode="200")

    except Exception as e:
        api_response = ApiResponse(error="Request failed",
                                   statuscode=INTERNAL_SERVER_ERROR,
                                   response=str(e))

    return api_response.to_dictionary()

def _get_analytics_data(data_frame:DataFrame,group_by_column:str,total_days:int ) -> dict:

    # Calculate total_requests and average_daily_requests
    total_requests = int(data_frame['cntr'].sum())
    average_daily_requests = int(total_requests // total_days)

    # Create the analytics_data dictionary
    analytics_data = {
        "range": data_frame['request_date'].unique().tolist(),
        "cumulative": data_frame.groupby('request_date')['cntr'].sum().tolist(),
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

def _insert_missing_rows(data_frame:DataFrame, group_by_column:str,unique_dates:list[str]) -> DataFrame:

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
        return pd.concat([data_frame, new_df], ignore_index=True).sort_values(by=['request_date', group_by_column]).reset_index(drop=True)

    return data_frame  #return original if no new changes

def _count_dates_between(start_date_str, end_date_str) -> int:
    # Convert the date strings to datetime objects
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

    # Calculate the difference in days
    delta = (end_date - start_date).days

    return delta

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
            "email": row['email'],
            "usage": int(row['cntr'])
        }
        result_dict["data"]["users"].append(user_info)

    return result_dict

def _get_date_range(start_date_str:str, end_date_str:str,aggregate_month:bool = False) -> list[str] :
    if aggregate_month:
        date_range = pd.date_range(start=start_date_str, end=end_date_str).strftime('%Y-%m').unique().tolist()
    else:
        date_range = pd.date_range(start=start_date_str, end=end_date_str).strftime('%Y-%m-%d').tolist()
    return date_range

if __name__ == "__main__":

    group_by_column_name = "tier";
    #group_by_column_name = "ref_app";

    result = get_analytics(group_by_column_name, "2024-12-01", "2024-12-04")
    print("analytics_data=\n", json.dumps(result, indent=4))

    filter_by = None  #"chrome_extension"
    result = get_top_users(group_by_column_name, "2024-12-01", "2024-12-04",limit=10,offset=0,group_by_filter=filter_by)
    print("top users=\n", json.dumps(result, indent=4))
