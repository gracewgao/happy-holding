import os
from twilio.rest import Client

# account_sid = os.environ["TWILIO_ACCOUNT_SID"]
# auth_token = os.environ["TWILIO_AUTH_TOKEN"]

# test credentials
# account_sid = "AC13d754ddf12b2dd5825d69550754cc15"
# auth_token = "d6fdd689351d81f8f96e648cda9fd3c6"

account_sid = "AC4f3c1ec5c49f7f9ec0e1969f24941852"
auth_token = "c50755ff5bf33daf9eb0d7002ed83533"

client = Client(account_sid, auth_token)

call = client.calls.create(
    # to=os.environ["MY_PHONE_NUMBER"],
    to="+16139810982",
    from_="+13204417411",
    url="http://demo.twilio.com/docs/voice.xml"
)

print(call.sid)
