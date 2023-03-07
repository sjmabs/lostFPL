# for runnin on server
#import json

# with open('/etc/config.json') as config_file:
# 	config = json.load(config_file)

# class Config:
#     SECRET_KEY = config.get("SECRET_KEY")

# this is so it works out for people running from git but if you want to put it on a server you need to hide this key
# and generate a new one
class Config:
    SECRET_KEY = 'putakeyhere'



