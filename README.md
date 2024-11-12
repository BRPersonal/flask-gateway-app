# flask_gateway_app
Flask application to interact with Tyk Gateway API

Tyk Integration notes
------------------
1)Put your apis as json files under apps folder in tyk installation folder
2)Put your policies as json files under policies folder in tyk installation folder
3)In all policy files make sure "access_rights" section includes all the apis 
4)In every api and policy json , make sure it has "org_id" and that it matches ORG_ID 
specified in .env file in this application folder
5)Make sure TYK_GW_SECRET environment set in docker-compose.yml matches X-TYK-AUTHORIZATION
specified in .env file in this application folder

 

