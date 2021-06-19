from Python.DiscordBotClient import DiscordBotClient
from Python.ProClubsBot.ProClubsWebScraper import ProClubsWebScraper
import pathlib
import json
import pandas as pd

CONFIGS = {
    "bot_name": "ProClubsBot",
    "file_path": pathlib.Path(__file__).parent.absolute(),
    "command_prefix": "-"
}


class ProClubsBot(DiscordBotClient):
    def __init__(self, team_name="AntiFun", command_prefix=None, debug=False):
        super().__init__(
            CONFIGS["bot_name"],
            CONFIGS["file_path"],
            CONFIGS["command_prefix"] if not command_prefix else command_prefix,
            debug
        )
        self.team_name = team_name
        self.discord_emotes |= {
            "star": ":star:"
        }
        self.commands = {
            "help": {
                "function": self.get_help,
                "help": f"{self.command_prefix}help"
            },
            "club": {
                "function": self.get_club,
                "help": f"{self.command_prefix}club    \"team name\"* *(default: 'AntiFun'')"
            },
            "season": {
                "function": self.get_season,
                "help": f"{self.command_prefix}season  \"team name\"*"
            },
            "members": {
                "function": self.get_members,
                "help": f"{self.command_prefix}members \"team name\"*"
            },
            "membertotals": {
                "function": self.get_member_totals,
                "help": f"{self.command_prefix}membertotals \"team name\"*"
            },
            "memberaverages": {
                "function": self.get_member_averages,
                "help": f"{self.command_prefix}memberaverages \"team name\"*"
            }
        }

        self.pro_clubs_web_scraper = ProClubsWebScraper()

    def _get_team_name(self, *args):
        if len(args) == 1:
            return args[0]
        return self.team_name

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

    async def get_club(self, channel, *args):
        team_name = self._get_team_name(*args)
        response = self.pro_clubs_web_scraper.get_club(team_name)

        stats = response[list(response.keys())[0]]

        match_history = self.get_match_history(stats)

        s = f"""```Team: {stats["clubInfo"]["name"]}
Matches played: {stats["totalGames"]}
Wins: {stats["wins"]}
Draws: {stats["ties"]}
Losses: {stats["losses"]}
Current Division: {stats["currentDivision"]}
Best Division: {stats["bestDivision"]}
Skill rating: {int(stats["starLevel"])/2.0} stars
Match History: {match_history}
All-Time Goals: {stats["alltimeGoals"]}
All-Time Goals against: {stats["alltimeGoalsAgainst"]}```"""

        await channel.send(s)

    async def get_season(self, channel, *args):
        team_name = self._get_team_name(*args)
        response = self.pro_clubs_web_scraper.get_club(team_name)

        stats = response[list(response.keys())[0]]
        played = int(stats["gamesPlayed"])
        match_history = self.get_match_history(stats)[-played:] + "-" * (10-played)

        s = f"""```Team: {stats["clubInfo"]["name"]}
Division: {stats["currentDivision"]}
Matches played: {stats["gamesPlayed"]} ({match_history.count("W")}W-{match_history.count("D")}D-{match_history.count("L")}L)
Match History: {match_history}
Current Points: {stats["points"]} (Projected: {stats["projectedPoints"]})```"""

        await channel.send(s)

    async def get_member_totals(self, channel, *args):
        """
        TODO - Allow users to 'order by'. Add '^' to the column name that is being sorted by
        :param channel:
        :param args:
        :return:
        """
        sort_by = "Name"
        team_name = self._get_team_name(*args)
        members = self.pro_clubs_web_scraper.get_members(team_name)

        columns = {
            "proName": "Name",
            "gamesPlayed": "Apps",
            "goals": "Goals",
            "assists": "Assists",
            "passesMade": "Passes",
            "tacklesMade": "Tackles",
            "redCards": "Red cards",
            "manOfTheMatch": "MOTM Awards",
        }

        table = pd.DataFrame().from_dict(members)
        table = table[list(columns.keys())].rename(columns=columns)
        numeric_columns = list(table)[1:]
        table[numeric_columns] = table[numeric_columns].apply(pd.to_numeric)
        table = table.sort_values(
            sort_by,
            ascending=str(table[sort_by].dtype) != "int64"
        ).rename(
            columns={sort_by: f"{sort_by}^"}
        )

        await channel.send(f"```{team_name} member total stats:\n{table.to_string(index=False)}```")

    async def get_member_averages(self, channel, *args):
        """
        TODO - Allow users to 'order by'. Add '^' to the column name that is being sorted by
        :param channel:
        :param args:
        :return:
        """

        def get_average(dict, stat, per_game_key="gamesPlayed", dp=2):
            return round(float(dict[stat]) / float(dict[per_game_key]), dp)

        sort_by = "Name"
        team_name = self._get_team_name(*args)
        members = self.pro_clubs_web_scraper.get_members(team_name)

        members_avg_stats = []
        for member_dict in members:
            members_avg_stats.append({
                "Name": member_dict["proName"],
                "Apps": member_dict["gamesPlayed"],
                "Goals": get_average(member_dict, "goals"),
                "Assists": get_average(member_dict, "assists"),
                "Goal Inv.": get_average(member_dict, "goals") + get_average(member_dict, "assists"),
                "Passes": get_average(member_dict, "passesMade"),
                "Tackles": get_average(member_dict, "tacklesMade"),
                "Tackle success(%)": member_dict["tackleSuccessRate"],
                "Shot success (%)": member_dict["shotSuccessRate"]
            })

        table = pd.DataFrame().from_dict(members_avg_stats)
        table = table.sort_values(
            sort_by,
            ascending=str(table[sort_by].dtype) != "int64" or str(table[sort_by].dtype) != "float"
        ).rename(
            columns={sort_by: f"{sort_by}^"}
        )

        await channel.send(f"```{team_name} member average stats:\n{table.to_string(index=False)}```")

    async def get_members(self, channel, *args):
        """
        TODO - Use tables to add some 'nicknames' for the members based off their stats: i.e. 'Bagsman' if the member
        TODO - has the most goals scored etc. When a user has a nickname append a nickname to the original name.
        TODO - If a user has no nickname, give them a 'participation award' nickname..
        :param channel:
        :param args:
        :return:
        """

        team_name = self._get_team_name(*args)
        members = self.pro_clubs_web_scraper.get_members(team_name)

        member_names = []
        for member in members:
            member_names.append(f"{member['name']}: {member['proName']}")

        join_string = "\n\t- "
        return_string = f"```{team_name} members:{join_string}" + join_string.join(member_names) + "```"
        await channel.send(return_string)

    @staticmethod
    def get_match_history(stats):
        result_map = {
            "2": "W",
            "1": "D",
            "0": "L"
        }
        match_history = []
        for i in reversed(range(10)):
            match_history.append(result_map[stats[f"lastMatch{i}"]])

        return "".join(match_history)
