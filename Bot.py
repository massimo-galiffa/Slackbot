import logging
import os
import random
import threading
import time

from dotenv import load_dotenv
from slack_bolt import App

app = App(token="xoxb-5298808072471-5306765357638-BUrqb7zP4EoauV04GBHlehiy",
          signing_secret=os.getenv("6d1e5431208ca834f3f19fb0fbdd4710"))

leaderboard = {}  # Moved leaderboard to global scope

# Load environment variables from .env file
load_dotenv()


def generate_random_time():
    """Generate a random time between 9:00 and 15:45"""
    hour = random.randint(9, 15)
    minute = random.randint(0, 59)
    return f"{hour:02d}:{minute:02d}"


def send_daily_task():
    """Send the daily task to the channel"""
    daily_topics = [
        "song submission",
        "photo of what you're doing",
        "describe your current project",
        "share your favorite playlist"
    ]
    random_topic = random.choice(daily_topics)
    task_message = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Hi everyone! Today's topic is: {random_topic}. Please share your thoughts!"
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
    app.client.chat_postMessage(channel="#slackbots", text=task_message['blocks'][0]['text']['text'],
                                blocks=task_message['blocks'])


@app.event("message")
def handle_message_submission(body, say, logger):
    user_id = body["user"]
    text = body["text"]
    if text.strip() == "":
        say(f"Sorry <@{user_id}>, your submission cannot be empty.")
        return
    leaderboard[user_id] = leaderboard.get(user_id, 0) + 1
    say(f"Thanks for your submission, <@{user_id}>! Your current score is {leaderboard[user_id]}")


def run_bot():
    """Run the bot"""

    prompt_time = "08:58"  # Generate a random time for the request

    while True:
        current_time = time.strftime("%H:%M")
        if current_time == prompt_time:
            send_daily_task()
            prompt_time = generate_random_time()  # Generate a new random time for the next request
        time.sleep(1)  # Wait before checking the time again
        if time.strftime("%A") == "Saturday" or time.strftime("%A") == "Sunday":
            break  # Stop the bot on Saturdays and Sundays

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
