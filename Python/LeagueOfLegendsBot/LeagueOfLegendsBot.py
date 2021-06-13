from Python.DiscordBotClient import DiscordBotClient
from Python.LeagueOfLegendsBot.LolAPIWrapper.LolAPIWrapper import LolAPIWrapper
import pathlib

CONFIGS = {
    "bot_name": "LeagueOfLegendsBot",
    "file_path": pathlib.Path(__file__).parent.absolute(),
    "command_prefix": "-"
}


class LeagueOfLegendsBot(DiscordBotClient):
    """
    A Discord bot to return instant information and details on players and matches

    on_message is only used to defer to the correct 'command' functions.
    these command functions must send the details to the discord channel.

    """

    def __init__(self, command_prefix=None, debug=False):
        super().__init__(
            CONFIGS["bot_name"],
            CONFIGS["file_path"],
            CONFIGS["command_prefix"] if not command_prefix else command_prefix,
            debug
        )
        self.lol_api_wrapper = LolAPIWrapper()
        self.commands = {
            "help": {
                "function": self.get_help,
                "help": f"{self.command_prefix}help"
            },
            "rank": {
                "function": self.get_summoner_rank,
                "help": f"{self.command_prefix}rank \"name 1\" name2 ... \'name n\'",
            }
        }

    async def on_message(self, ctx):
        if not ctx.content.startswith(self.command_prefix):
            return

        full_command = ctx.content.removeprefix(self.command_prefix)

        if " " in full_command:
            command = full_command.split(" ")[0]
            args = self.arg_split(" ".join(full_command.split(" ")[1:]))
        else:
            command = full_command
            args = []

        func = self.commands.get(command.lower(), {"function": self.invalid_command})["function"]
        await func(ctx.channel, *args)

    async def invalid_command(self, channel):
        """
        The default command returned if the command requested is invalid
        :param channel: The discord channel that the command was sent from.
        """

        await channel.send(f"Invalid command\nType {self.command_prefix}help for list of commands!")

    async def get_help(self, channel):
        """
        The help command, listing all the commands available in the class (self.commands.keys())
        :param channel: The discord channel that the command was sent from.
        """

        join_str = f"\n\t"
        command_help_list = []
        for command in self.commands.keys():
            command_help_list.append(self.commands[command]["help"])

        await channel.send(f"```list of commands:{join_str}" + join_str.join(command_help_list) + "```")

    async def get_summoner_rank(self, channel, *summoner_names):
        """
        Input a list of summoner names, using the LolAPIWrapper to access LoL Summoner rank details.
        Details include: Rank, Division, LP, whether the summoner is on a hot streak, a veteran etc.
        :param channel: The discord channel that the command was sent from.
        :param summoner_names: list of summoner names to check each summoner's rank details.
        """

        import json

        for summoner_name in summoner_names:
            try:
                summoner_rank_json = self.lol_api_wrapper.get_summoner_rank_by_name(summoner_name)
                print(json.dumps(summoner_rank_json, indent=4, sort_keys=True))
                if not summoner_rank_json or len(summoner_rank_json) == 0:
                    summoner_rank = f"{summoner_name} does not have a rank"
                else:
                    summoner_rank_json = summoner_rank_json[0]
                    summoner_rank = f"{summoner_name} is in {summoner_rank_json['tier']} {summoner_rank_json['rank']}"
                await channel.send(summoner_rank)
            except Exception as ex:
                await channel.send(str(ex))
