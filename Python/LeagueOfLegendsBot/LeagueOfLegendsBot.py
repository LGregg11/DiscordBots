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
            "help": self.get_help,
            "rank": self.get_summoner_rank,
        }

    async def on_message(self, ctx):
        if not ctx.content.startswith(self.command_prefix):
            return

        full_command = ctx.content[len(self.command_prefix):]

        if " " in full_command:
            command = full_command.split(" ")[0]
            args = full_command.split(" ")[1:]
        else:
            command = full_command
            args = []

        func = self.commands.get(command.lower(), lambda: f"Invalid command\n" +
                                                          "Type {self.command_prefix}help for list of commands!")
        await ctx.channel.send(func(*args))

    def get_help(self):
        join_str = f"\n\t{self.command_prefix}"
        return f"```list of commands:{join_str}" + join_str.join(self.commands.keys()) + "```"

    def get_summoner_rank(self, *args):
        rank_list = []
        for summoner_name in args:
            rank_list.append(self.lol_api_wrapper.get_summoner_rank_by_name(summoner_name))
        return "\n".join(rank_list)
