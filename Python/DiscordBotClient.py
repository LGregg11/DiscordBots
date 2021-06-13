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

    @staticmethod
    def correct_arg_list(arg_list):
        """
        Corrects a list of white-spaced strings, and merges any strings between quotations.

        TODO: Tidy up the if/else section.

        :param arg_list: a list of white-spaced args
        :return: a corrected list of arguments
        """

        quotation_types = ["\"", "\'"]
        quotation_type_used = ""
        quoted_args = []
        corrected_arg_list = []
        for arg in arg_list:
            # Checking the args surrounded with quotes
            if not quotation_type_used and arg.startswith(tuple(quotation_types)):
                quotation_type_used = arg[0]
                if len(arg) > 1:
                    if arg.endswith(quotation_type_used):
                        corrected_arg_list.append(arg.replace(quotation_type_used, ""))
                        quotation_type_used = ""
                    else:
                        quoted_args.append(arg.removeprefix(quotation_type_used))
                continue

            if quotation_type_used and arg.startswith(quotation_type_used):
                corrected_arg_list.append(" ".join(quoted_args))
                arg = arg.removeprefix(quotation_type_used)
                quoted_args = []

            if quotation_type_used and not arg.endswith(quotation_type_used):
                quoted_args.append(arg)
            elif quotation_type_used and arg.endswith(quotation_type_used):
                quoted_args.append(arg.removesuffix(quotation_type_used))
                corrected_arg_list.append(" ".join(quoted_args))

                # Reset quote type and args list
                quoted_args = []
                quotation_type_used = ""
            else:
                corrected_arg_list.append(arg)

        if quoted_args:
            corrected_arg_list.append(" ".join(quoted_args) if len(quoted_args) > 1 else quoted_args[0])
        return corrected_arg_list

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
