#!/usr/bin/env python

from docopt import docopt
from json import load
from bots import GenericBot
import logging

__doc__ = """\
A cli tool to have bots write your Pelican posts for you.

Usage:
    botpost.py auto CONFIG_FILE
    botpost.py print CONFIG_FILE
    botpost.py check CONFIG_FILE
    
"""

if __name__ == "__main__":
    opts = docopt(__doc__)

    with open(opts["CONFIG_FILE"]) as f:
        config = load(f)

    logging.basicConfig(level=logging.DEBUG)

    # for test stuff only
    config["title"] = "Autobots, REPRESENT!"
    bot = GenericBot(config=config)

    if opts["auto"]:

        if bot.check_feed():
            bot.clone_repo()
            bot.write_post()
            bot.commit_post()
            bot.push_repo()
        else:
            logging.info("Last post less than {} days ago: Nothing to do.".format(bot.config["timeout"]))
    elif opts["print"]:
        print(bot.build_post())

    elif opts["check"]:
        logging.info("Seems everything worked out alright, maybe?")