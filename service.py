import requests
import json
import os
from dotenv import load_dotenv
from api_response import ApiResponse
from utils import get_current_timestamp

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
    return api_response.to_json()

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

    return api_response.to_json()

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

    return api_response.to_json()

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
    return api_response.to_json()

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

    return api_response.to_json()