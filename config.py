import logging

# Youtube channel ID
yt_channel_id = ""

# Youtube channel URL
yt_channel_url = ''

# YouTube API credentials file path, used to check if the livestream is still running
client_secrets_file = "client_secret.json"

# Token JSON file
token_json = "/home/pi/birdbox/token.json"

# Lock file name. The lock file is used to prevent the script from running in parallel
lock_file = '/home/pi/birdbox/birdbox.lock'

# Time in seconds the lock file is valid until deleted
max_lockfile_age = 600

# How often to check if the livestream is running
livestream_check_frequency = 1200

# How often the Youtube API will be used to check the livestream.
# Use the same frequency as above to use only the API. All other checks will using scraping, which is less reliable.
livestream_check_api_frequency = 1200

# Log level: logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL
log_level = logging.DEBUG
log_file = "birdbox.log"

json_save_file = "data.json"
