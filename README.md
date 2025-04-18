# flask_gateway_app
Flask application to interact with Tyk Gateway API

Tyk Integration notes
------------------
1)Put your apis as json files under apps folder in tyk installation folder
2)Put your policies as json files under policies folder in tyk installation folder
3)In all policy files make sure "access_rights" section includes all the apis.
4)In policy json "access_rights" section , the top-element
should match "api_id" only and not "api_name"
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
quota_max is cumulative for a day (It is actually for the window period defined by quota_renewal_rate)
quota_renewal_rate is in seconds. if it says 86400, the quota is for entire day
per is in seconds. Together with rate , this defines a shorter window period
quota is a larger window; rate is a shorter window
For eg., 
  "per": 60,
  "quota_max": 1000,
  "quota_renewal_rate": 86400,
  "rate": 5,
says you can hit a max. of 5 requests in a minute and a max. of 1000 requests in a day


Setting up Tyk Open source APi Gateway in local machine
--------------------------------------------------------
$ cd ~/poc
$ git clone https://github.com/TykTechnologies/tyk-gateway-docker
$ cd tyk-gateway-docker
$ pwd
/Users/adiyen/poc/tyk-gateway-docker


put your api definition json files in apps folder (refer samples/apis folder)
put your policy definition json files in policies folder (refer samples/policies)

Run this command only the first time after you have cloned the repo.For subsequent times
use only start and stop commands
$ docker-compose up -d

test the installation
$ curl localhost:8080/hello

Use start/stop commands to start or stop the tyk-gateway services using these commands
$ docker-compose start
$ docker-compose stop

Note: If you run the command
$ docker-compose down 
the api keys created will be lost. Dont use it. Use stop / start command instead


Api Demo
---------
Create environment in Postman give a name "Flask-Tyk-App-Local"
Set base_url to http://localhost:5002
In the post man collection "Flask-Tyk-App-Local" in the top right you
will see "No Environment" dropdown. choose , "Flask-Tyk-App-Local"

POST {{base_url}}/create-key
Body raw
{
    "plan":"FreeDesign"
}

POST {{base_url}}/create-key
Body raw
{
    "plan":"FreeDeveloper"
}

GET {{base_url}}/list-keys
GET {{base_url}}/get-key/FleetStudio68031d2590614c30a940d5c43af07d5f
DELETE {{base_url}}/delete-key/FleetStudio38656e51f71648498f4cccc956c6826c


PUT {{base_url}}/update-plan
Body raw
{
    "plan":"FreeDeveloper",
    "key":"FleetStudio6d1c21956aee463da152259e3f707cc8"
}

Apis that can be accessed through Tyk Gateway. You can test RateLimiting and Quota limit as well
http://localhost:8080/posts/
http://localhost:8080/comments/
When you exceed rate limit you will get http status 429 (Too many requests)
When you exceed quota limit you will get http status 403(Forbidden)

You need to set "Authorization" header as api key that you created.
In postman, you can also goto Authorization tab, choose "API Key" for AuthType
and set value as api key

04-Dec-24
--------
key_tbl will be dropped from Postgre database . So query in 
analytics_repository will work only in local mysql. It will no longer 
work for postgre. The table was added by me for making testing easier.
It has to be dropped in production. product should only use Key table

Key is a reserved word and has to be handled differently in mysql
and postgre. That's the reason I went for this new table



