import datetime
import logging
import os
import random
import re
import threading
import time

from dotenv import load_dotenv
from slack_bolt import App
from slack_sdk.errors import SlackApiError

app = App(token="SLACK_TOKEN_HERE",
          signing_secret=os.getenv("OTHER_TOKEN_HERE"))

leaderboard = {}  # Moved leaderboard to global scope

# Load environment variables from .env file
load_dotenv()

daily_topics = [
"song submission",
"photo of what you're doing",
"describe your current project",          
"share your favorite playlist"
]

channel_name = "#YourChannelName"


def generate_random_time():
    """Generate a random time between 9:00 and 15:45"""
    hour = random.randint(9, 15)
    minute = random.randint(0, 59)
    return f"{hour:02d}:{minute:02d}"


def send_daily_task():
    """Send the daily task to the channel"""
    random_topic = random.choice(daily_topics)
    current_topic = random_topic
    task_message = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Hi everyone! Today's topic is: {random_topic}"
                            f". Please share your thoughts"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Share",
                        "emoji": True
                    },
                    "action_id": "share_button"
                }
            }
        ]
    }
    app.client.chat_postMessage(channel=channel_name, text=task_message['blocks'][0]['text']['text'],
                                blocks=task_message['blocks'])
    return current_topic


def assign_points(user_id):
    """Assign points to a user"""
    leaderboard[user_id] = leaderboard.get(user_id, 0) + 1


def handle_message_submission(messages, topic):
    if topic is None:
        return
    elif topic == daily_topics[0]:
        print("song submission")
        links = check_link(messages["messages"][0]["text"])
        if links:
            print("link found")
            print(links)
            if check_song_link(links[0]):
                response_if_valid_submission(messages["messages"][0]["user"])
    elif topic == daily_topics[1]:
        print("photo of what you're doing")
        if "files" in messages["messages"][0]:
            print("file found")
            files = messages["messages"][0]["files"][0]["filetype"]
            check_photo(files)

    elif topic == daily_topics[2]:
        print("describe your current project")
        if "text" in messages["messages"][0]:
            print("text found")
            print(messages["messages"][0]["text"])

    elif topic == daily_topics[3]:
        print("share your favorite playlist")
        links = check_link(messages["messages"][0]["text"])
        if links:
            print("link found")
            # Check Playlist Link


def check_link(message) -> list:
    link_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    return re.findall(link_pattern, message)


def check_spotify_track(url):
    pattern = r"https?://open\.spotify\.com/[a-zA-Z\-]*/track/[\w]+(\?si=[\w]+)?"
    return re.findall(pattern, url)


def check_song_link(link) -> bool:
    """Check if a link is a valid song link"""
    if check_spotify_track(link):
        print("valid song link")
        return True
    else:
        print("invalid song link")
        return False


def check_photo(files) -> bool:
    """Check if a link is a valid photo link"""
    if "png" in files or "jpg" in files:
        print("valid photo link")
        return True
    else:
        print("invalid photo link")
        return False


def check_text(text) -> bool:
    """Check text is valid"""
    if len(text) < 30:
        print("valid text")
        return True
    else:
        print("invalid text")
        return False


def response_if_valid_submission(user_id) -> None:
    app.client.chat_postMessage(
        channel=channel_name,
        text=f"Thanks for your submission, <@{user_id}>!")
    #  Your current score is {leaderboard[user_id]}


def run_bot():
    time_now = datetime.datetime.now() + datetime.timedelta(seconds=2)
    # convert time to string with format %H:%M (e.g. 08:45)
    time_now = time_now.strftime("%H:%M:%S")
    prompt_time = time_now  # Generate a random time for the request
    topic = None
    while True:
        current_time = time.strftime("%H:%M:%S")  # Get the current time
        if current_time == prompt_time:
            topic = send_daily_task()
            prompt_time = generate_random_time()  # Generate a new random time for the next request
        time.sleep(1)  # Wait before checking the time again
        if time.strftime("%A") == "Saturday" or time.strftime("%A") == "Sunday":
            break  # Stop the bot on Saturdays and Sundays
        messages = app.client.conversations_history(channel="C058SPUS0DD")
        handle_message_submission(messages, topic)

    # Print the leaderboard
    for i, (user_id, score) in enumerate(leaderboard.items()):
        print(f"{i + 1}. User {user_id}: {score} posts")


if __name__ == "__main__":
    # Configure the logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())

    # Start the Bolt app in a separate thread
    threading.Thread(target=app.start, kwargs={'port': int(os.getenv("PORT", 3001))}).start()

    # Start the bot functionality
    run_bot()
