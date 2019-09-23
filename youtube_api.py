import os
import json
import os.path
import google.oauth2.credentials
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
channel_id = 'UCom6YhUY62jM52nIMjf5_dw'


def get_authenticated_service():

    if os.path.isfile("credentials.json"):
        with open("credentials.json", 'r') as f:
            creds_data = json.load(f)
        creds = Credentials(creds_data['token'])

    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, SCOPES)
        creds = flow.run_console()
        creds_data = {
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': creds.scopes
        }
        print(creds_data)
        with open("credentials.json", 'w') as outfile:
            json.dump(creds_data, outfile)
    return build(API_SERVICE_NAME, API_VERSION, credentials=creds)


def get_channel_videos(service, channel_id):
    res = service.channels().list(id=channel_id,
                                  part='contentDetails').execute()
    playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    videos = []
    next_page_token = None

    while 1:
        res = service.playlistItems().list(playlistId=playlist_id,
                                           part='contentDetails',
                                           maxResults=50,
                                           pageToken=next_page_token).execute()
        videos += res['items']
        next_page_token = res.get('nextPageToken')

        if next_page_token is None:
            break

    output = []

    for video in videos:
        res = service.videos().list(id=video['contentDetails']['videoId'],
                                    part='statistics').execute()
        output.append(res)

    print(output)


if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    service = get_authenticated_service()
    get_channel_videos(service, channel_id)
