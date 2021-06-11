from Python.DiscordBotClient import DiscordBotClient
from Python.FootBot.StreamListener import StreamListener
from threading import Thread

import tweepy
import asyncio
import pathlib


CONFIGS = {
    "bot_name": "FootBot",
    "file_path": pathlib.Path(__file__).parent.absolute(),
    "command_prefix": "uppa ",
    "twitter_api_details_file": "TwitterApiDetails.json",
    "account_ids": {
        "Swansea City Official": "472385266",
        "Test Account": "494294876",
    },
    "twitter_keywords": [
        "starting xi",
        "Here's how the #swans line up"
    ]
}


class FootBot(DiscordBotClient):
    """
    A Discord bot used for all things football.

    Current commands:
        - teamsheet
            - Beings a subscription thread to a particular team's twitter and listens out for when the teamsheet appears
            (Currently hardcoded to Swansea City's Official Twitter account)
    """

    def __init__(self, command_prefix=None, debug=False):
        super().__init__(
            CONFIGS["bot_name"],
            CONFIGS["file_path"],
            CONFIGS["command_prefix"] if not command_prefix else command_prefix,
            debug
        )

        self.commands = [
            "teamsheet"
        ]

        self._configs = CONFIGS
        if self.debug:
            self._accounts = {
                key: self._configs["account_ids"][key]
                for key in self._configs["account_ids"]
                if "test" in key.lower()
            }
        else:
            self._accounts = {
                key: self._configs["account_ids"][key]
                for key in self._configs["account_ids"]
                if "test" not in key.lower()
            }
        self._twitter_api_details_file = self._configs["twitter_api_details_file"]
        self._twitter_api_details = self.get_file_details(self._twitter_api_details_file)
        self.auth = self._get_twitter_auth()
        self.twitter_api = tweepy.API(self.auth)
        self.twitter_stream = tweepy.Stream(
            auth=self.twitter_api.auth,
            listener=StreamListener(self)
        )
        self.twitter_thread = self._create_twitter_thread()

    def _get_twitter_auth(self):
        auth = tweepy.OAuthHandler(*self._get_consumer_tokens())
        auth.set_access_token(*self._get_access_tokens())
        return auth

    def _get_consumer_tokens(self):
        return self._twitter_api_details["consumer key"], self._twitter_api_details["consumer key secret"]

    def _get_access_tokens(self):
        return self._twitter_api_details["access token"], self._twitter_api_details["access token secret"]

    def _create_twitter_thread(self):
        return Thread(target=self.start_twitter_stream, daemon=True,  name="Twitter Thread")

    async def on_message(self, ctx):
        # Help command
        if ctx.content.lower().startswith("help"):
            result = f"""
            These are a list of all the commands:
            ```prefix: {self.command_prefix}\n\t""" + "\n\t".join(self.commands) + "\n```"
            await ctx.channel.send(result)
            return

        if ctx.author == self.user or not any(ctx.content.lower().startswith(f"{self.command_prefix}{command}")
                                              for command in self.commands):
            return

        command_with_args = ctx.content[len(self.command_prefix):].lower()
        command = ""
        args = ""
        if " " in command_with_args:
            command = command_with_args.split(" ")[0]
            args = " ".join(command_with_args.split(" ")[1:])
        else:
            command = command_with_args

        # Call the commands
        if command == "teamsheet":
            result = self.get_teamsheet(ctx.channel)
            await ctx.channel.send(result)

    def get_teamsheet(self, channel):
        if self.twitter_thread.is_alive():
            return "The command has already been called and is awaiting the teamsheet already!"

        accounts = ",\n\t - ".join(self._accounts.keys())
        self.channel = channel
        self.twitter_thread = self._create_twitter_thread()
        self.twitter_thread.start()
        return f"Listening in to the following accounts for a teamsheet:\n\t - {accounts}"

    def send_tweet_to_discord_bot(self, data):
        message = data["text"]
        extended_tweet = "extended_tweet"
        entities = "entities"
        media = "media"
        expanded_url = "expanded_url"

        if extended_tweet in data.keys() and entities in data[extended_tweet].keys() \
                and media in data[extended_tweet][entities].keys() \
                and expanded_url in data[extended_tweet][entities][media][0].keys():
            message = str(data[extended_tweet][entities][media][0][expanded_url])
        asyncio.run_coroutine_threadsafe(self.channel.send(message), self.loop)

    def start_twitter_stream(self):
        print("Starting twitter thread..")
        accounts = ',\n\t'.join(self._accounts.keys())
        print(f"Listening to the following twitter accounts for a teamsheet:\n\t'{accounts}'")

        self.twitter_stream.filter(
            follow=self._accounts.values()
        )

    def get_config(self):
        return self._configs
