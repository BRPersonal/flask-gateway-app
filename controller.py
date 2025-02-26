from flask import Flask,request,jsonify,Response
import service as service

from api_response import ApiResponse

app = Flask(__name__)


@app.route('/create-key', methods=['POST'])
def create_key() -> (Response,str):
    api_response: ApiResponse
    result : dict

    post_data = request.get_json()
    if not post_data or "plan" not in post_data:
        api_response = ApiResponse(error="Missing 'plan' in request body",
                                   statuscode=400)
        result = api_response.to_dictionary()
    else:
        result = service.create_key(post_data["plan"])

    return jsonify(result), result['status_code']

@app.route('/list-keys', methods=['GET'])
def list_keys() -> (Response,str):
    result = service.list_keys()
    return jsonify(result), result['status_code']

@app.route('/get-key/<key>', methods=['GET'])
def get_key_details(key:str) -> (Response,str):
    result = service.get_key_details(key)
    return jsonify(result), result['status_code']

@app.route('/update-plan', methods=['PUT'])
def update_key_plan() -> (Response,str):
    api_response: ApiResponse = None
    result : dict = None

    post_data = request.get_json()
    if not post_data or "plan" not in post_data or "key" not in post_data:
        api_response = ApiResponse(error="Missing 'plan' or 'key' in request body",
                                   statuscode=400)
        result = api_response.to_dictionary()
    else:
        result = service.update_key_plan(post_data)

    return jsonify(result), result['status_code']

@app.route('/delete-key/<key>', methods=['DELETE'])
def delete_key(key: str) -> (Response,str):
    result = service.delete_key(key)
    return jsonify(result), result['status_code']

@app.route('/analytics', methods=['GET'])
def get_analytics() -> (Response,str):

    group_by = request.args.get('group_by', default="tier")  # tier if not provided

    start_date_str = request.args.get('start_date')  # Required parameter
    end_date_str = request.args.get('end_date')  # Required parameter
    user_id = request.args.get('user_id', default=None)

    if not start_date_str:
        api_response = ApiResponse(error="Missing 'start_date' in request parameter",
                                   statuscode=400)
        result = api_response.to_dictionary()
    elif not end_date_str:
        api_response = ApiResponse(error="Missing 'end_date' in request parameter",
                                   statuscode=400)
        result = api_response.to_dictionary()
    else:
        result = service.get_analytics(group_by,start_date_str,end_date_str,user_id)

    return jsonify(result), result['status_code']

@app.route('/top-users', methods=['GET'])
def get_top_users() -> (Response,str):

    group_by = request.args.get('group_by', default="tier")  # tier if not provided

    start_date_str = request.args.get('start_date')  # Required parameter
    end_date_str = request.args.get('end_date')  # Required parameter
    limit = int(request.args.get('limit', default=10))
    offset = int(request.args.get('offset', default=0))
    filter_by = request.args.get('filter_by', default=None)


    if not start_date_str:
        api_response = ApiResponse(error="Missing 'start_date' in request parameter",
                                   statuscode=400)
        result = api_response.to_dictionary()
    elif not end_date_str:
        api_response = ApiResponse(error="Missing 'end_date' in request parameter",
                                   statuscode=400)
        result = api_response.to_dictionary()
    else:
        result = service.get_top_users(group_by,start_date_str,end_date_str,limit,offset,filter_by)

    return jsonify(result), result['status_code']

if __name__ == "__main__":
    app.run(debug=True, port=5002)
