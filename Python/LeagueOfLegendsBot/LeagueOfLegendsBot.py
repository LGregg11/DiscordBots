from Python.DiscordBotClient import DiscordBotClient
from Python.LeagueOfLegendsBot.LolAPIWrapper.LolAPIWrapper import LolAPIWrapper
from Python.LeagueOfLegendsBot.LoLWebScraper import LoLWebScraper
import pathlib
import pandas as pd

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
        self.discord_emotes |= {
            "veteran": ":older_adult:",
            "blood": ":drop_of_blood:",
            "inactive": ":sleeping:",
            "W": ":white_check_mark:",
            "L": ":x:",
            "N": ":shrug:"
        }

        self.ranks = {
            "IRON": "Wood",
            "SILVER": "Silver",
            "GOLD": "Gold",
            "PLATINUM": "Plat",
            "DIAMOND": "Diamond",
            "MASTER": "Master",
            "GRANDMASTER": "GM",
            "CHALLENGER": "Challenger"
        }
        self.divisions = {
            "I": "1",
            "II": "2",
            "III": "3",
            "IV": "4"
        }
        self.commands = {
            "help": {
                "function": self.get_help,
                "help": f"{self.command_prefix}help"
            },
            "rank": {
                "function": self.get_rank,
                "help": f"{self.command_prefix}rank \"<name 1>\" <name2> ... \'<name n>\'"
            },
            "winloss": {
                "function": self.get_ranked_win_loss,
                "help": f"{self.command_prefix}winloss \"<name 1>\" <name2> ... \'<name n>\'"
            },
            "champs": {
                "function": self.get_ranked_champs,
                "help": f"{self.command_prefix}champs name season*%s* - optional (default: current season)" % ("\t"*15)
            }
        }

        self.lol_api_wrapper = LolAPIWrapper()
        self.lol_web_scraper = LoLWebScraper()

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

    async def invalid_command(self, channel, *args):
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

    async def get_rank(self, channel, *summoner_names):
        """
        Input a list of summoner names, using the LolAPIWrapper to access LoL Summoner rank details.
        Details include: Rank, Division, LP, whether the summoner is on a hot streak, a veteran etc.
        :param channel: The discord channel that the command was sent from.
        :param summoner_names: list of summoner names to check each summoner's rank details.
        """

        def get_rank_details(summoner_name, rank_dict):
            if not rank_dict or len(rank_dict) == 0:
                return f"{summoner_name} - no rank"
            s = f"{summoner_name} - {self.ranks[rank_dict['tier']]} {self.divisions[rank_dict['rank']]}, {rank_dict['leaguePoints']}lp"

            if "miniSeries" in rank_dict.keys():
                progress = rank_dict["miniSeries"]["progress"].replace(
                    "W", self.discord_emotes["W"]).replace(
                    "L", self.discord_emotes["L"]).replace(
                    "N", self.discord_emotes["N"])
                s += f" (promos: {progress})"
            if "hotStreak" in rank_dict.keys() and rank_dict["hotStreak"]:
                s += f" {self.discord_emotes['fire']}"
            if "veteran" in rank_dict.keys() and rank_dict["veteran"]:
                s += f" {self.discord_emotes['veteran']}"
            if "freshBlood" in rank_dict.keys() and rank_dict["freshBlood"]:
                s += f" {self.discord_emotes['blood']}"
            if "inactive" in rank_dict.keys() and rank_dict["inactive"]:
                s += f" {self.discord_emotes['inactive']}"
            return s

        summoner_rank_list = []
        for summoner_name in summoner_names:
            try:
                summoner_rank_json = self.lol_api_wrapper.get_summoner_rank_by_name(summoner_name)
                summoner_rank_list.append(get_rank_details(summoner_name, summoner_rank_json[0]))
            except Exception as ex:
                summoner_rank_list.append(str(ex))
        await channel.send("\n".join(summoner_rank_list))

    async def get_ranked_win_loss(self, channel, *summoner_names):
        win_loss_list = []
        for summoner_name in summoner_names:
            try:
                rank_summary = self.lol_web_scraper.get_winloss(summoner_name)
                if not rank_summary["wins"]:
                    raise RuntimeError(f"{summoner_name} - Could not find summoner in {self.lol_web_scraper.region}")
                win_loss_list.append(
                    f"{summoner_name} - {rank_summary['wins']} {rank_summary['losses']} ({rank_summary['ratio']})"
                )
            except RuntimeError as ex:
                print(str(ex))
                win_loss_list.append(str(ex))
        await channel.send("\n".join(win_loss_list))

    async def get_ranked_champs(self, channel, *args):
        if len(args) == 1:
            summoner_name = args[0]

            season = "2021"
        elif len(args) == 2:
            summoner_name, season = args
        else:
            await channel.send(f"Unexpected number of arguments given, use {self.command_prefix}help!")
            return
        try:
            table = self.lol_web_scraper.get_most_played_champs(season, summoner_name)
            table_squashed = table[["#", "Champion", "Played", "KDA"]].to_string(index=False)
            await channel.send(f"```{table_squashed}```")
        except RuntimeError as ex:
            await channel.send(str(ex))
