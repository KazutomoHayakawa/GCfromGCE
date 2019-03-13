#!/usr/bin/python
#
# Copyright 2012 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import httplib2
#import sys

from apiclient.discovery import build
from oauth2client import tools
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
import gspread


# For this example, the client id and client secret are command-line arguments.
client_id = '673780291538-0ee0ogep3jtreaik1g449pdvlbfguj2c.apps.googleusercontent.com'  #sys.argv[1]
client_secret = 'PsYDLKNDjHeUY-sfSlE0tPyi' #sys.argv[2]
#apikey = 'AIzaSyDqCWExNwx88hLw2syFq0VKJPdmpEjjuKw'
# AIzaSyDqCWExNwx88hLw2syFq0VKJPdmpEjjuKw

# The scope URL for read/write access to a user's calendar data
scope = ['https://www.googleapis.com/auth/calendar','https://www.googleapis.com/auth/spreadsheets.readonly']

# Create a flow object. This object holds the client_id, client_secret, and
# scope. It assists with OAuth 2.0 steps to get user authorization and
# credentials.
flow = OAuth2WebServerFlow(client_id, client_secret, scope)

def main():

  # Create a Storage object. This object holds the credentials that your
  # application needs to authorize access to the user's data. The name of the
  # credentials file is provided. If the file does not exist, it is
  # created. This object can only hold credentials for a single user, so
  # as-written, this script can only handle a single user.
  storage = Storage('credentials.dat')

  # The get() function returns the credentials for the Storage object. If no
  # credentials were found, None is returned.
  credentials = storage.get()

  # If no credentials are found or the credentials are invalid due to
  # expiration, new credentials need to be obtained from the authorization
  # server. The oauth2client.tools.run_flow() function attempts to open an
  # authorization server page in your default web browser. The server
  # asks the user to grant your application access to the user's data.
  # If the user grants access, the run_flow() function returns new credentials.
  # The new credentials are also stored in the supplied Storage object,
  # which updates the credentials.dat file.
  if credentials is None or credentials.invalid:
    credentials = tools.run_flow(flow, storage, tools.argparser.parse_args())

  gc = gspread.authorize(credentials)

  # Create an httplib2.Http object to handle our HTTP requests, and authorize it
  # using the credentials.authorize() function.
  http = httplib2.Http()
  http = credentials.authorize(http)

  # The apiclient.discovery.build() function returns an instance of an API service
  # object can be used to make API calls. The object is constructed with
  # methods specific to the calendar API. The arguments provided are:
  #   name of the API ('calendar')
  #   version of the API you are using ('v3')
  #   authorized httplib2.Http() object that can be used for API calls
  cal_service = build('calendar', 'v3', http=http)
  #service = build('calendar', 'v3') 

  try:

    # The Calendar API's events().list method returns paginated results, so we
    # have to execute the request in a paging loop. First, build the
    # request object. The arguments provided are:
    #   primary calendar for user
    request = cal_service.events().list(calendarId='hayatetu.dip.jp_b9l5fdldb3mls584p3kvbts88g@group.calendar.google.com',maxResults=10)
    # Loop until all pages have been processed.
    while request != None:
      print('request not NONE')
      # Get the next page.
      response = request.execute()
      print(response)
      # Accessing the response like a dict object with an 'items' key
      # returns a list of item objects (events).
      for event in response.get('items', []):
        # The event object is a dict object with a 'summary' key.
        sss = repr(event.get('summary', 'NO SUMMARY')) + '\n'
        print(sss) 
      # Get the next request object by passing the previous request object to
      # the list_next method.
      request = cal_service.events().list_next(request, response)

  except AccessTokenRefreshError:
    # The AccessTokenRefreshError exception is raised if the credentials
    # have been revoked by the user or they have expired.
    print ('The credentials have been revoked or expired, please re-run'
           'the application to re-authorize')


  try:
    # Call the Sheets API
    print('##########  use build ##############')
    sheet_service = build('sheets', 'v4', http=http)
    sheet = sheet_service.spreadsheets()

    result = sheet.values().get(spreadsheetId='1qqsdubleCo2HxQagmU6jk3whBZGUAVxqbRYkOkrjQx0',range='A2:E').execute()
    print(result)
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        print('Name, Major:')
        for row in values:
            # Print columns A and E, which correspond to indices 0 and 4.
            print('%s, %s' % (row[0], row[1]))

  except AccessTokenRefreshError:
    # The AccessTokenRefreshError exception is raised if the credentials
    # have been revoked by the user or they have expired.
    print ('The credentials have been revoked or expired, please re-run'
           'the application to re-authorize')

  try:
    print('########   use gsheet #############')
    #OAuth2 login
    gc = gspread.authorize(credentials)
    workbook = gc.open_by_key('1qqsdubleCo2HxQagmU6jk3whBZGUAVxqbRYkOkrjQx0')

    #get sheet
    print(workbook.title)
    print(workbook.id)

    #get sheet
    sheet1 = workbook.get_worksheet(0)
    print(sheet1.title)

    #get cells
    cell_list = sheet1.range('A1:C7')

    for cell in cell_list:
      print(cell)

  except AccessTokenRefreshError:
    # The AccessTokenRefreshError exception is raised if the credentials
    # have been revoked by the user or they have expired.
    print ('The credentials have been revoked or expired, please re-run'
           'the application to re-authorize')



if __name__ == '__main__':
  main()