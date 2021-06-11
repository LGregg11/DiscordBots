import tweepy
import json
import sys


class StreamListener(tweepy.StreamListener):
    def __init__(self, discord_bot):
        super().__init__()
        self.discord_bot = discord_bot

    def on_data(self, raw_data):
        data = json.loads(raw_data)
        if 'text' not in data.keys():
            return

        check = any(keyword.lower() for keyword in self.discord_bot.get_config()["twitter_keywords"]
                    if keyword.lower() in data["text"].lower())
        if not check:
            return
        self.discord_bot.send_tweet_to_discord_bot(data)
        self.discord_bot.twitter_stream.disconnect()
        print(f"Twitter Stream Listener has Disconnected!")

    def on_status(self, status):
        print(status.id_str)

    def on_error(self, status_code):
        print(f"Encountered streaming error ({status_code}")
        sys.exit()
