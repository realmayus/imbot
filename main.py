import os.path
from configparser import ConfigParser

import discord
from discord.ext.commands import Bot
from bot.bot import BotMain
from image.template import TemplateManager

dev = os.path.isfile("./dev")

if not os.path.isfile("config.ini"):
    with open("config.ini", "w") as f:
        f.write("[secret]\ntoken = \n\n[settings]\nmoderators = ")
    print("➡️  Please enter your discord token and user id in config.ini (it was just created)")
    exit(1)


if not os.path.isdir("assets"):
    os.mkdir("assets")
    os.mkdir("assets/fonts")
    os.mkdir("assets/templates")
    os.mkdir("assets/templates/images")
    print("ℹ️️  Created asset directories")

if not os.path.isfile("assets/fonts/NotoSans-Regular.ttf") and not os.path.isfile("assets/fonts/NotoSans-Bold.ttf"):
    print("➡️  Please download NotoSans-Regular.ttf and NotoSans-Bold.ttf and place them in assets/fonts/")
    exit(1)


if not os.path.isfile("assets/templates/index.json"):
    with open("assets/templates/index.json", "w") as f:
        f.write("[]")
    print("ℹ️️  Created index.json")


cp = ConfigParser()
cp.read("config.ini")
token = cp["secret"]["token"]

template_manager = TemplateManager()

template_manager.load_templates()

print("⏳ Logging in…")
bot = Bot(command_prefix=".")

bot.add_cog(BotMain(bot, template_manager))
bot.run(token)
