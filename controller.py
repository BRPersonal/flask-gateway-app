from flask import Flask,request,jsonify,Response
from service import *
from api_response import ApiResponse

app = Flask(__name__)


@app.route('/create-key', methods=['POST'])
def key_create() -> (Response,str):
    api_response: ApiResponse = None
    result : dict = None

    post_data = request.get_json()
    if not post_data or "plan" not in post_data:
        api_response = ApiResponse(error="Missing 'plan' in request body",
                                   statuscode=400)
        result = api_response.to_json()
    else:
        result = create_key(post_data["plan"])

    return jsonify(result), result['status_code']

@app.route('/list-keys', methods=['GET'])
def listKeys() -> (Response,str):
    result = list_keys()
    return jsonify(result), result['status_code']

@app.route('/get-key/<key>', methods=['GET'])
def get_key(key:str) -> (Response,str):
    result = get_key_details(key)
    return jsonify(result), result['status_code']

@app.route('/update-plan', methods=['PUT'])
def updateKeyPlan() -> (Response,str):
    api_response: ApiResponse = None
    result : dict = None

    post_data = request.get_json()
    if not post_data or "plan" not in post_data or "key" not in post_data:
        api_response = ApiResponse(error="Missing 'plan' or 'key' in request body",
                                   statuscode=400)
        result = api_response.to_json()
    else:
        result = update_key_plan(post_data)

    return jsonify(result), result['status_code']

@app.route('/delete-key/<key>', methods=['DELETE'])
def keyDeletion(key: str) -> (Response,str):
    result = delete_key(key)
    return jsonify(result), result['status_code']

if __name__ == "__main__":
    app.run(debug=True, port=5001)
