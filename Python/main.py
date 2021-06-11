import argparse
import sys
import os

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", default="False")
    args = parser.parse_args()

    debug = True if args.debug == "True" else False

    current_dir = os.path.dirname(os.path.realpath(__file__))
    parent_dir = os.path.dirname(current_dir)
    sys.path.append(parent_dir)

    """
    import your bot here e.g. from FootBot.FootBot import FootBot
    """
    from FootBot.FootBot import FootBot

    bot = FootBot(debug=debug)
    bot.start_bot()
    input("Press Enter to close the bot..\n")
    bot.stop_bot()