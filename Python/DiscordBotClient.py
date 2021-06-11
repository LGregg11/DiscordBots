from threading import Thread
import discord
import sys
import json

CONFIG = {
    "bot_details_filename": "BotDetails.json"
}


class DiscordBotClient(discord.Client):
    def __init__(self, name, bot_dir, command_prefix="!", debug=False):
        super().__init__()
        self.debug = debug
        self.name = name
        self.bot_dir = bot_dir
        self.bot_details_filename = CONFIG["bot_details_filename"]
        self.command_prefix = command_prefix
        self._bot_details = self.get_file_details(self.bot_details_filename)
        self.bot_thread = Thread(target=self.start_bot_thread, daemon=True, name="Bot Thread")

    def get_file_details(self, filename):
        return json.load(open(f"{self.bot_dir}\\{filename}"))

    def _get_token(self):
        if "token" not in self._bot_details.keys():
            raise Exception("token does not exist")

        return self._bot_details["token"]

    def start_bot_thread(self):
        print("Starting bot thread..\n")
        self.run(self._get_token())

    def start_bot(self):
        debug = " (debug mode)" if self.debug else ""
        print(f"{self.name}{debug} has started..")
        print(f"{self.name} command prefix: '{self.command_prefix}'")
        self.bot_thread.start()

    def stop_bot(self):
        print(f"{self.name} is closing..")
        sys.exit()

    async def on_ready(self):
        print(f"{self.user} has connected to Discord!")
