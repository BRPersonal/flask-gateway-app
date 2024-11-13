# flask_gateway_app
Flask application to interact with Tyk Gateway API

Tyk Integration notes
------------------
1)Put your apis as json files under apps folder in tyk installation folder
2)Put your policies as json files under policies folder in tyk installation folder
3)In all policy files make sure "access_rights" section includes all the apis.
4)In policy json "access_rights" section , the top-element
should not be api "name". It should be "api_id" only
5)In every api and policy json , make sure it has "org_id" and that it matches ORG_ID 
specified in .env file in this application folder
6)Make sure TYK_GW_SECRET environment set in docker-compose.yml matches X-TYK-AUTHORIZATION
specified in .env file in this application folder

What you define specific  for an api?
-----------------
api_id,org_id,name,listen_path,target_url
Other details just use the defaults

What you define specific for a policy?
---------------------------
access_rights,org_id,id,name,per,quota_max,quota_renewal_rate,rate
Other details just use the defaults

Setting up Tyk Open source APi Gateway in local machine
--------------------------------------------------------
$ git clone https://github.com/TykTechnologies/tyk-gateway-docker
$ cd tyk-gateway-docker

put your api definition json files in apps folder
put your policy definition json files in policies folder

$ docker-compose up -d

test the installation
$ curl localhost:8080/hello

Use start/stop commands to start or stop the tyk-gateway services using these commands
$ docker-compose start
$ docker-compose stop

Note: If you run the command
$ docker-compose down 
the api keys created will be lost. Dont use it. Use stop / start command instead


