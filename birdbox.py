#!/usr/bin/env python3
import subprocess
import sys
import time
import config
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError
import psutil
import os
import os.path
import json
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import traceback
import logging

# Define the scopes required for YouTube API access
SCOPES = ['https://www.googleapis.com/auth/youtube']


class LivestreamNotActiveError(Exception):
    pass


class BroadcastNotTestingError(Exception):
    pass


# Function to save variables to a JSON file
def save_to_json(data, filename):
    with open(filename, 'w') as json_file:
        json.dump(data, json_file)


# Function to load variables from a JSON file
def load_from_json(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as json_file:
            data = json.load(json_file)
        return data
    else:
        return None


def check_internet_connection():
    try:
        test = subprocess.check_call(["ping", "-c", "1", "-W", "1", "google.com"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError:
        return False


def run_streaming_command(ingestion_address, stream_name):
    logging.info("Attempt to start streaming")
    url = ingestion_address + "/" + stream_name
    logging.debug("Streaming URL: %s", url)

    command = "raspivid -o - -t 0 -w 1920 -h 1080 -fps 25 -b 4000000 -g 50 | ffmpeg -re -ar 44100 -ac 2 -acodec pcm_s16le -f s16le -ac 2 -i /dev/zero -f h264 -i - -vcodec copy -acodec aac -ab 128k -g 50 -strict experimental -f flv " + url
    process = subprocess.Popen(command, shell=True)


def check_ffmpeg_process():
    try:
        output = subprocess.check_output(["ps", "aux"])
        return b"ffmpeg" in output
    except subprocess.CalledProcessError:
        return False


def kill_process_by_name(process_name):
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] == process_name:
            try:
                process.kill()
                logging.info(f"Process '{process_name}' killed.")
            except psutil.AccessDenied as e:
                logging.error(e, exc_info=True)
            return True
    logging.info(f"No process with name '{process_name}' found.")
    return False


def is_channel_live_api(youtube, channel_id):
    # Request live broadcasts from the channel
    request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        eventType="live",
        type="video"
    )
    response = request.execute()

    # Check if there are live broadcasts
    if response['items']:
        return True
    else:
        return False


def is_channel_live_scraping(channel_url):
    response = requests.get(channel_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        live_indicator = soup.find('span', {'class': 'style-scope ytd-badge-supported-renderer'})
        if live_indicator and 'LIVE' in live_indicator.text:
            return True
    return False


def create_youtube_live_broadcast(youtube, title):
    # Create a liveBroadcast resource and set its title
    logging.info("Setting up a new live broadcast and stream.")

    start_time = datetime.utcnow().isoformat() + 'Z'
    logging.debug("Sending Youtube Live API request to insert a broadcast. Title: %s, Start Time: %s", title,
                  start_time)
    broadcast = youtube.liveBroadcasts().insert(
        part="snippet,status,contentDetails",
        body=dict(
            snippet=dict(
                title=title,
                scheduledStartTime=start_time
            ),
            status=dict(
                privacyStatus="public"
            ),
            contentDetails=dict(
                enableAutoStop=True
            )
        )
    ).execute()

    # Extract the broadcast id from the response
    broadcast_id = broadcast['id']
    logging.debug("Broadcast ID is %s", broadcast_id)

    # Create a liveStream resource and set its title, stream type, and ingest settings
    logging.debug("Sending Youtube Live API request to insert a live stream. Title: %s", title)
    stream = youtube.liveStreams().insert(
        part="snippet,cdn",
        body=dict(
            snippet=dict(
                title=title
            ),
            cdn=dict(
                frameRate="variable",
                ingestionType="rtmp",
                resolution="variable"
            )
        )
    ).execute()

    # Extract the stream id and ingestion address from the response
    stream_id = stream['id']
    ingestion_address = stream['cdn']['ingestionInfo']['ingestionAddress']
    stream_name = stream['cdn']['ingestionInfo']['streamName']

    logging.debug("Stream ID: %s, Ingestion address: %s, Stream name: %s", stream_id, ingestion_address, stream_name)

    # Bind the stream to the broadcast
    logging.debug("Binding stream to broadcast.")
    bind_broadcast_response = youtube.liveBroadcasts().bind(
        part="id,contentDetails",
        id=broadcast_id,
        streamId=stream_id
    ).execute()

    return ingestion_address, stream_name, broadcast_id, stream_id


def transition_youtube_broadcast_to_testing(youtube, broadcast_id, stream_id, max_retries=10, retry_interval=10):
    """
    Wait for the livestream status to be active and then transition the broadcast to status "testing".

    Args:
        youtube: An authenticated instance of the YouTube Data API service.
        broadcast_id (str): The ID of the broadcast.
        stream_id (str): The ID of the stream.
        max_retries (int): Maximum number of retries to check the livestream status.
        retry_interval (int): Time interval (in seconds) between retries.
    """
    for _ in range(max_retries):
        logging.debug("Attempt %s at testing if the livestream status is active. Broadcast ID: %s", _ + 1, broadcast_id)
        livestream_status = youtube.liveStreams().list(part="status", id=stream_id).execute()
        logging.debug("Livestream status: %s", livestream_status)
        if 'items' in livestream_status and livestream_status['items']:
            if livestream_status['items'][0]['status']['streamStatus'] == 'active':
                logging.debug("Livestream is active, transition broadcast to \"testing\"")
                youtube.liveBroadcasts().transition(
                    part="status",
                    broadcastStatus="testing",
                    id=broadcast_id
                ).execute()
                return True
        time.sleep(retry_interval)
    raise LivestreamNotActiveError("Livestream did not become active within the specified retries.")


def transition_youtube_broadcast_to_live(youtube, broadcast_id, max_retries=10, retry_interval=10):
    """
    Wait for broadcast lifeCycleStatus to become testing and then transition the broadcast status to live.

    Args:
        youtube: An authenticated instance of the YouTube Data API service.
        broadcast_id (str): The ID of the broadcast.
        max_retries (int): Maximum number of retries to check the broadcast status.
        retry_interval (int): Time interval (in seconds) between retries.
    """
    for _ in range(max_retries):
        logging.debug("Attempt %s at testing if broadcast lifeCycleStatus is testing. Broadcast ID: %s", _ + 1, broadcast_id)
        broadcast_status = youtube.liveBroadcasts().list(
            part="status",
            id=broadcast_id
        ).execute()
        logging.debug("Broadcast status: %s", broadcast_status)
        if broadcast_status['items'][0]['status']['lifeCycleStatus'] == 'testing':
            logging.debug("Broadcast is in testing, transition to \"live\"")
            youtube.liveBroadcasts().transition(
                part="id,status",
                broadcastStatus="live",
                id=broadcast_id
            ).execute()
            return True
        time.sleep(retry_interval)
    raise BroadcastNotTestingError("Broadcast did not enter 'testing' status within the specified retries.")


def authenticate_youtube_api():
    # Authenticate and authorize access to the YouTube API
    creds = None

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists(config.token_json):
        creds = Credentials.from_authorized_user_file(config.token_json)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError as e:
                logging.error(e, exc_info=True)
                # It's possible we need to delete the token file at this point and regenerate it next run. Further testing needed.
                sys.exit(1)

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(config.token_json, 'w') as token:
            token.write(creds.to_json())

    # Build the YouTube API service object
    return build('youtube', 'v3', credentials=creds)


def main():
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',filename=config.log_file, encoding='utf-8', level=config.log_level)

    last_events = {
        'last_livestream_check': 0,
        'last_livestream_check_api': 0,
        'last_livestream_restart': 0,
    }

    file_contents = load_from_json(config.json_save_file)

    if file_contents:
        last_events = file_contents
        logging.debug("Loaded variables from data file")
    else:
        logging.debug("Could not load data file or file empty")

    logging.info("last_events: " + str(last_events))

    youtube = authenticate_youtube_api()

    if check_internet_connection():
        logging.debug("Internet connection OK")

        now = time.time()
        last_livestream_check = now - last_events['last_livestream_check']
        last_livestream_check_api = now - last_events['last_livestream_check_api']

        logging.debug("Last livestream check was done %s seconds ago", last_livestream_check)
        logging.debug("The Youtube API was last used %s seconds ago", last_livestream_check_api)

        if last_livestream_check > config.livestream_check_frequency:
            logging.info("Starting livestream check")
            last_events['last_livestream_check'] = now

            if last_livestream_check_api > config.livestream_check_api_frequency:
                # API has a limit and could only be used every 20 minutes daily
                logging.info("Use the Youtube API to check if the channel is live")
                last_events['last_livestream_check_api'] = now
                channel_is_live = is_channel_live_api(youtube, config.yt_channel_id)

            else:
                # Scraping works every time, but is less reliable
                logging.info("Use scraping to check if the channel is live")
                channel_is_live = is_channel_live_scraping(config.yt_channel_url)

            if not channel_is_live:
                logging.info("There is no live stream currently, attempting to start a stream")

                logging.debug("Check for running ffmpeg processes")
                if check_ffmpeg_process():
                    logging.debug("Found process, attempt to kill ffmpeg process")
                    kill_process_by_name("ffmpeg")
                else:
                    logging.debug("No ffmpeg process running")

                # Create a new livestream
                title = "Bird Box Basel " + datetime.now().strftime("%Y-%m-%d")
                ingestion_address, stream_name, broadcast_id, stream_id = create_youtube_live_broadcast(youtube, title)
                logging.info("Livestream created. Ingestion Address: %s, Stream Name: %s, Broadcast ID: %s", ingestion_address, stream_name, broadcast_id)

                run_streaming_command(ingestion_address, stream_name)

                try:
                    transition_youtube_broadcast_to_testing(youtube, broadcast_id, stream_id)
                except LivestreamNotActiveError as e:
                    logging.error(e, exc_info=True)
                    sys.exit(1)

                try:
                    transition_youtube_broadcast_to_live(youtube, broadcast_id)
                except BroadcastNotTestingError as e:
                    logging.error(e, exc_info=True)
                    sys.exit(1)

                last_events['last_livestream_restart'] = now
            else:
                logging.info("A live stream is currently active on the channel. Nothing to do.")
        else:
            logging.info("checked livestream last %s seconds ago. Skipping.", last_livestream_check)
    else:
        logging.warning("No internet connection.")

    logging.debug("Saving data to data json file: " + str(last_events))
    save_to_json(last_events, config.json_save_file)


if __name__ == "__main__":
    main()
