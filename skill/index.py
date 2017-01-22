from __future__ import print_function
import httplib2
import os
import json
import boto3
import datetime
import re

from apiclient import discovery
from oauth2client import client
from oauth2client import tools


# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar'
credentials1 = '{"_module": "oauth2client.client", "scopes": ["https://www.googleapis.com/auth/calendar"], "token_expiry": "2017-01-21T06:36:10Z", "id_token": null, "access_token": "ya29.GlvaAwp7TL1rO0v214lDUvDhzrHTl2UOSMnjGJWfEEZ6KixXilKJDq0BD8plJrFlZcMvXXieQLrl3FCAHTuKyFOa8Xg0dVMQizUBwG4JHuI0okQ2knnLGbJg3Cb5", "token_uri": "https://accounts.google.com/o/oauth2/token", "invalid": false, "token_response": {"access_token": "ya29.GlvaAwp7TL1rO0v214lDUvDhzrHTl2UOSMnjGJWfEEZ6KixXilKJDq0BD8plJrFlZcMvXXieQLrl3FCAHTuKyFOa8Xg0dVMQizUBwG4JHuI0okQ2knnLGbJg3Cb5", "token_type": "Bearer", "expires_in": 3600, "refresh_token": "1/QQdroBj9RtxlVHZ2-5j02Zm5jRDv_jXJns4b_7fT9mR8F5cfJII3vyZEgunWA7XQ"}, "client_id": "281882156338-oa05uk2hgngaln938m3u69hahnca6nng.apps.googleusercontent.com", "token_info_uri": "https://www.googleapis.com/oauth2/v3/tokeninfo", "client_secret": "GbB7LG0qZQQG_NfAM9uyqVwz", "revoke_uri": "https://accounts.google.com/o/oauth2/revoke", "_class": "OAuth2Credentials", "refresh_token": "1/QQdroBj9RtxlVHZ2-5j02Zm5jRDv_jXJns4b_7fT9mR8F5cfJII3vyZEgunWA7XQ", "user_agent": "Google Calendar API Python Quickstart"}'

error_msg = "Sorry. I could not get that"

print('Loading function')

USER = "Amit Jain"
multiplier = 1

def send_response_interactive(message, sessionAttr):
    if sessionAttr == "{}":
        endSession = "true"
    else:
        endSession = "false"
    attr = eval(sessionAttr)
    print("Session attr %s and endSession %s" % (sessionAttr, endSession) )
    return {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": message
            },
            "shouldEndSession": endSession,
            "card": {
                "type": "Simple",
                "title": "SessionSpeechlet - Welcome",
                "content": message
            }
        },
        "sessionAttributes": attr
    }

def send_response(message):
    return {
        "version": "1.0",
        "sessionAttributes": {},
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": message
            },
            "card": {
                "type": "Simple",
                "title": "SessionSpeechlet - Welcome",
                "content": message
            }
        }
    }

def scheduleCoffeeMakerDur(val, duration):
    # TODO Get current status first if busy or idle
    client = boto3.client('iot-data', region_name='us-east-1')
    dur_in_secs = duration["value"]
    matchObj = re.match(r'PT([0-9]+)([a-zA-Z]+)', dur_in_secs, re.M|re.I)
    print("%s %s" % (matchObj.group(1), matchObj.group(2)))
    timeUnit = matchObj.group(2)
    timeNo = matchObj.group(1)
    if (timeUnit == 'S'):
        multiplier = 1
        if (int(timeNo) > 1):
            timeUnit = "seconds"
        else:
            timeUnit = "second"
    elif (timeUnit == 'M'):
        multiplier = 60
        if (int(timeNo) > 1):
            timeUnit = "Minutes"
        else:
            timeUnit = "Minute"
    elif (timeUnit == 'H'):
        multiplier = 3600
        if (int(timeNo) > 1):
            timeUnit = "Hours"
        else:
            timeUnit = "Hour"
    dur_in_secs = int(timeNo) * int(multiplier)
    data = '{"state": {"desired": {"state": "%s","duration": %d,"status": "busy","fromTime": 0,"toTime": 0,"tillTime": 0}}}' %(val, int(dur_in_secs))
    client.update_thing_shadow(thingName = 'coffee_maker', payload = data)
    message = 'keeping coffee maker %s for %s %s' % (val, timeNo, timeUnit)
    return message
    
def scheduleCoffeeMakerSpan(val, fromTime, toTime):
    print("fromTime %s and toTime %s" % (fromTime, toTime))
    message = 'Will keep coffee maker %s for specified time period' % val
    return message
    
def scheduleCoffeeMakerPeriod(val, tillTime):
    message = 'Will keep coffee maker %s till specified time' % val
    print("tillTime %s" % tillTime)
    return message


def bookConf(mname, date, stime, etime):
    print("bookConf meeting")

    meeting = {
	    'summary': 'Marvell Hackathon',
	    'location': 'Pune, India',
	    'description': 'A chance to show your innovation',
	    'start': {
		    'dateTime': '2017-01-23T03:00:00-07:00',
	    },
	    'end': {
		    'dateTime': '2017-01-23T04:00:00-07:00',
	    },
    }
    meeting['summary'] = mname
    meeting['start']['dateTime'] = date + 'T' + stime + ':00+05:30'
    meeting['end']['dateTime'] = date + 'T' + etime + ':00+05:30'

    credentials = client.OAuth2Credentials.from_json(credentials1)
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    #now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    mstart = meeting['start']['dateTime']
    mend = meeting['end']['dateTime']
    print('Getting the upcoming event')
    eventsResult = service.events().list(
        calendarId='primary', timeMin=mstart, timeMax=mend, maxResults=1, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    if not events:
        meeting = service.events().insert(calendarId='primary', body=meeting).execute()
        #start = event['start'].get('dateTime', event['start'].get('date'))
        message = 'Scheduled ' + mname + ' As per your request'
    else:
	message = 'There is already a meeting scheduled for given time'

    return message

def handleLight(value, method):
    client = boto3.client('iot-data', region_name='us-east-1')
    if method == 0:
        response = client.get_thing_shadow(thingName = 'panel_light')
        body = json.loads(response["payload"].read())
        print("Response is: %s" % body)
        message = "The light is %s" % body["state"]["reported"]["state"]
    else:
        if value == "on" or value == "off":
            message = "Turning %s light" % value
            data = "{\"state\" : { \"desired\" : { \"state\" : \"%s\" }}}" % value
            client.update_thing_shadow(thingName = 'panel_light', payload = data)
        else:
            message = error_msg
    return message

def handleConnect(person):
    dict = {'Mahavir': 'mahavir.coep@gmail.com', 'Amit': 'amitsheth90@gmail.com', 'Rishi': 'dhayagudehrishikesh@gmail.com'}
    if person == "Mahavir" or person == "Amit" or person == "Rishi":
        sns = boto3.client('sns')
        sns.publish(
            TopicArn = 'arn:aws:sns:us-east-1:815345597136:contactDetails',
            Message='Thank you',
            Subject="Please contact %s (%s)" % (person, dict[person]),
            MessageStructure='string',
            MessageAttributes={
                'string': {
                    'DataType': 'String',
                    'StringValue': 'string',
                }
            }
        )
        message = "Okay. Notified the concerned person"
    else:
        message = "Sorry. Unknown user '%s'" % person
    return message
    print("HandleConnect")
    
def handleInventory(item):
    print("Item is: ", item)
    if item == "water" or item == "milk" or item == "snacks" or item == "biscuits":
        sns = boto3.client('sns')
        sns.publish(
            TopicArn = 'arn:aws:sns:us-east-1:815345597136:contactDetails',
            Message='Looks like the stock for %s is about to get over. Please check and refill or reorder.' % item,
            Subject="[INVENTORY] Please check %s " % item,
            MessageStructure='string',
            MessageAttributes={
                'string': {
                    'DataType': 'String',
                    'StringValue': 'string',
                }
            }
        )
        message = "Okay. Notified the inventory unit"
    else:
        message = "Sorry. The item %s is not in the inventory" % item
    return message

def handleShipments():
    shipment = 2
    if shipment != 0:
        message = "You have %s new shipments" % shipment
    else:
        message = "You have no new shipments"
    return message

def lambda_handler(event, context):
    leaveDateFound = 0
    leavePeriodFound = 0
    sessionAttr = "{}"
    leaveDate = "{}"
    leavePeriod = "{}"
    print("Function is: ", event["request"]["intent"]["name"])
    intent = event["request"]["intent"]["name"]
    print("Keys: %s" % event.keys())

    if intent == "leaveApply":
    	if 'attributes' in event['session']:
        	if 'leaveDate' in event['session']['attributes']:
            		leaveDate = event['session']['attributes']['leaveDate']
            		leaveDateFound = 1
        	if 'leavePeriod' in event['session']['attributes']:
            		leavePeriod = event['session']['attributes']['leavePeriod']
            		leavePeriodFound = 1

	if leaveDate == "{}":
        	if 'value' in event['request']['intent']['slots']['leaveDate']:
            		leaveDate = event['request']['intent']['slots']['leaveDate']['value']
            		leaveDateFound = 1
    	if leavePeriod == "{}":
        	if 'value' in event['request']['intent']['slots']['leavePeriod']:
            		leavePeriod = event['request']['intent']['slots']['leavePeriod']['value']
            		leavePeriodFound = 1
    	if leaveDateFound == 0:
        	message = "What date"
        	sessionAttr = '{"intentSequence": "leaveApply"}'
    	else:
        	if leavePeriodFound == 0:
            		message = "For how many days"
            		sessionAttr = '{"intentSequence": "leaveApply", "leaveDate": "%s"}' % leaveDate
            		my_type = type(sessionAttr)
            		print("Type is: %s" % my_type)
            		print("Session attr is: %s" % sessionAttr)
        	else:
            		print("Date: %s Period %s" % (leaveDate, leavePeriod))
            		sns = boto3.client('sns')
            		sns.publish(
                		TopicArn='arn:aws:sns:us-east-1:815345597136:contactDetails',
		                Message='Leave application has been submitted for approval. Details are given below:\n\tEmployee Name: %s\n\tFrom: %s\n\tNo of Days:%s' % (USER, str(leaveDate), str(leavePeriod)),
                		Subject='Leave Application from %s' % USER,
		                MessageStructure='string',
                		MessageAttributes={
                    			'string': {
		                        'DataType': 'String',
        		                'StringValue': 'string',
                			}
                		}
            		)
    			message = "Okay. Leave application has been sent for approval."
    	return send_response_interactive(message, sessionAttr)

    elif intent == "getState":
        message = handleLight("null", 0)

    elif intent == "setState":
        try:
            val = event["request"]["intent"]["slots"]["state"]["value"]
            message = handleLight(val, 1)
        except KeyError:
            message = error_msg

    elif intent == "connect":
        try:
            val = event["request"]["intent"]["slots"]["person"]["value"]
            message = handleConnect(val)
        except KeyError:
            message = error_msg
            
    elif intent == "manageInventory":
        try:
            val = event["request"]["intent"]["slots"]["item"]["value"]
            message = handleInventory(val)
        except KeyError:
            message = error_msg
            
    elif intent == "getShipments":
        message = handleShipments()

    elif intent == "BookConf":
	try:
	    meeting = event["request"]["intent"]["slots"]["meeting"]["value"]
	    date = event["request"]["intent"]["slots"]["date"]["value"]
	    stime = event["request"]["intent"]["slots"]["stime"]["value"]
	    etime = event["request"]["intent"]["slots"]["etime"]["value"]
            message = bookConf(meeting, date, stime, etime)
        except KeyError:
            message = error_msg

    elif intent == "schedule":
        try:
            val = event["request"]["intent"]["slots"]["state"]["value"]
            if "value" in event["request"]["intent"]["slots"]["duration"]:
                message = scheduleCoffeeMakerDur(val, event["request"]["intent"]["slots"]["duration"])
                
            elif "value" in event["request"]["intent"]["slots"]["fromTime"]:
                message = scheduleCoffeeMakerSpan(val, event["request"]["intent"]["slots"]["fromTime"]["value"],
                                        event["request"]["intent"]["slots"]["toTime"]["value"])
                                        
            elif "value" in event["request"]["intent"]["slots"]["tillTime"]:
                message = scheduleCoffeeMakerPeriod(val, event["request"]["intent"]["slots"]["tillTime"]["value"])
            
        except KeyError:
            message = error_msg

    elif intent == "CancelIntent":
        message = "In Cancel Intent"
    else:
        message = error_msg
    return send_response(message)
