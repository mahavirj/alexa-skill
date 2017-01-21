from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools

import datetime

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar'
credentials1 = '{"_module": "oauth2client.client", "scopes": ["https://www.googleapis.com/auth/calendar"], "token_expiry": "2017-01-21T06:36:10Z", "id_token": null, "access_token": "ya29.GlvaAwp7TL1rO0v214lDUvDhzrHTl2UOSMnjGJWfEEZ6KixXilKJDq0BD8plJrFlZcMvXXieQLrl3FCAHTuKyFOa8Xg0dVMQizUBwG4JHuI0okQ2knnLGbJg3Cb5", "token_uri": "https://accounts.google.com/o/oauth2/token", "invalid": false, "token_response": {"access_token": "ya29.GlvaAwp7TL1rO0v214lDUvDhzrHTl2UOSMnjGJWfEEZ6KixXilKJDq0BD8plJrFlZcMvXXieQLrl3FCAHTuKyFOa8Xg0dVMQizUBwG4JHuI0okQ2knnLGbJg3Cb5", "token_type": "Bearer", "expires_in": 3600, "refresh_token": "1/QQdroBj9RtxlVHZ2-5j02Zm5jRDv_jXJns4b_7fT9mR8F5cfJII3vyZEgunWA7XQ"}, "client_id": "281882156338-oa05uk2hgngaln938m3u69hahnca6nng.apps.googleusercontent.com", "token_info_uri": "https://www.googleapis.com/oauth2/v3/tokeninfo", "client_secret": "GbB7LG0qZQQG_NfAM9uyqVwz", "revoke_uri": "https://accounts.google.com/o/oauth2/revoke", "_class": "OAuth2Credentials", "refresh_token": "1/QQdroBj9RtxlVHZ2-5j02Zm5jRDv_jXJns4b_7fT9mR8F5cfJII3vyZEgunWA7XQ", "user_agent": "Google Calendar API Python Quickstart"}'


def lambda_handler(event, context):
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    event = {
	    'summary': 'Marvell Hackathon',
	    'location': 'Pune, India',
	    'description': 'A chance to show your innovation',
	    'start': {
		    'dateTime': '2017-01-23T09:00:00-07:00',
		    'timeZone': 'Asia/Kolkata',
	    },
	    'end': {
		    'dateTime': '2017-01-23T10:00:00-07:00',
		    'timeZone': 'Asia/Kolkata',
	    },
	    'recurrence': [
		    'RRULE:FREQ=DAILY;COUNT=1'
	    ],
	    'attendees': [
	    {'email': 'lpage@example.com'},
	    {'email': 'sbrin@example.com'},
	    ],
	    'reminders': {
		    'useDefault': False,
		    'overrides': [
		    {'method': 'email', 'minutes': 24 * 60},
		    {'method': 'popup', 'minutes': 10},
		    ],
	    },
    }
    credentials = client.OAuth2Credentials.from_json(credentials1)
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    event = service.events().insert(calendarId='primary', body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))

    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    eventsResult = service.events().list(
        calendarId='primary', timeMin=now, maxResults=10, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])
    return 'OKAY'
