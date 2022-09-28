import datetime
import os.path
from sys import argv
from time import time
from dateutil import parser

import sqlite3

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json. (Calendar)
SCOPES = ['https://www.googleapis.com/auth/calendar']  # remove readonly


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    if argv[1] == 'add':
        duration = argv[2]
        description = argv[3]
        addEvent(creds, duration, description)
        # py .\bot_time_admin.py add 3 "Testing"

    if argv[1] == 'commit':
        commitHours(creds)

    if argv[1] == 'get':
        duration = argv[2]
        getavghours(creds, duration)


def commitHours(creds):
    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        # 'Z' indicates UTC time
        # now = datetime.datetime.utcnow().isoformat() + 'Z'
        today = datetime.date.today()
        timeStart = str(today) + "T10:00:00Z"
        timeEnd = str(today) + "T23:59:59Z"

        print("Getting today's hours")
        #print('Getting the upcoming 10 events')
        """ events_result = service.events().list(calendarId='primary', timeMin=now,  #primary = default calendar, u can replace with ur prefered calendar id
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute() """

        events_result = service.events().list(calendarId='primary', timeMin=timeStart, timeMax=timeEnd,
                                              singleEvents=True,
                                              orderBy='startTime', timeZone='America/Lima').execute()

        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return

        total_duration = datetime.timedelta(
            seconds=0,
            minutes=0,
            hours=0,
        )

        print("Today's Hours Log:")
        # formated time
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))

            # chaging the start time to datetime formatted
            start_formatted = parser.isoparse(start)
            # changing the end time to datetime format
            end_formatted = parser.isoparse(end)
            duration = end_formatted - start_formatted

            total_duration += duration

            print(f"\t{event['summary']}, duration:{duration}")
        print(f"Total time: {total_duration}")

        # For Print the start and name of the next 10 events
        """ for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary']) """

        conn = sqlite3.connect('hours.db')
        cur = conn.cursor()
        print('Opened database successfully')
        date = datetime.date.today()

        formatted_total_duration = total_duration.seconds/60/60  # get in hours

        today_hours = (date, 'Daily', formatted_total_duration)
        try: 
            cur.execute("INSERT INTO hours VALUES(?,?,?);", today_hours)
            conn.commit()
            print('Daily hours added to db successfully')
        except:
            print('Record is already in the database')

    except HttpError as error:
        print('An error occurred: %s' % error)


def getavghours(creds, duration):
    try:
        service = build('calendar', 'v3', credentials=creds)

        #today = datetime.date.today()

        timeStart = datetime.datetime.utcnow()
        timeEnd = datetime.datetime.utcnow() + datetime.timedelta(days=int(duration)
                                                                  )  # timedelta != currenttime
        start_formatted = timeStart.isoformat() + 'Z'
        end_formatted = timeEnd.isoformat() + 'Z'

        # timeStart = str(today) + "T10:00:00Z"
        # timeEnd = str(today) + "T23:59:59Z"

        print("Getting total hours of " + duration + " days and the average")
        #print('Getting the upcoming 10 events')
        """ events_result = service.events().list(calendarId='primary', timeMin=now,  #primary = default calendar, u can replace with ur prefered calendar id
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute() """

        events_result = service.events().list(calendarId='primary', timeMin=start_formatted, timeMax=end_formatted,
                                              singleEvents=True,
                                              orderBy='startTime', timeZone='America/Lima').execute()

        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return

        total_duration = datetime.timedelta(
            seconds=0,
            minutes=0,
            hours=0,
        )

        print("TOTAL HOURS:")
        # formated time
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))

            # chaging the start time to datetime formatted
            start_formatted = parser.isoparse(start)
            # changing the end time to datetime format
            end_formatted = parser.isoparse(end)
            duration = end_formatted - start_formatted

            total_duration += duration

            print(f"{event['summary']}, duration:{duration}")

        print(f"Total time: {total_duration}")
        print(f"Average time : {total_duration/duration}")

        # For Print the start and name of the next 10 events
        """ for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary']) """

        """ conn = sqlite3.connect('hours.db')
        cur = conn.cursor()
        print('Opened database successfully')
        date = datetime.date.today()

        formatted_total_duration = total_duration.seconds/60/60  # get in hours
        coding_hours = (date, 'CODING', formatted_total_duration)
        cur.execute("INSERT INTO hours VALUES(?,?,?);", coding_hours)
        conn.commit()
        print('Coding hours addded to db successfully') """

    except HttpError as error:
        print('An error occurred: %s' % error)


def addEvent(creds, duration, description):
    start = datetime.datetime.utcnow()
    end = datetime.datetime.utcnow() + datetime.timedelta(hours=int(duration)
                                                          )  # timedelta != currenttime
    start_formatted = start.isoformat() + 'Z'
    end_formatted = end.isoformat() + 'Z'

    event = {
        'summary': description,
        'start': {
            'dateTime': start_formatted,
            'timeZone': 'America/Lima',
        },
        'end': {
            'dateTime': end_formatted,
            'timeZone': 'America/Lima',
        },
    }

    service = build('calendar', 'v3', credentials=creds)
    event = service.events().insert(calendarId='primary', body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))


if __name__ == '__main__':
    main()
