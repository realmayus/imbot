import base64
import io
import json
import time
from configparser import ConfigParser

from PIL import Image
import discord
from discord import Attachment
from discord.ext import commands
from discord.ext.commands import Context

from bot.PagedListEmbed import PagedListEmbed
from image import manipulator
from image.manipulator import draw_field_outlines
from image.template import TemplateManager
from image.types import Template
from util import random_string_generator, send_moderator_info, delete_template, remove_templates_from_index, is_ascii


class BotMain(commands.Cog):
    def __init__(self, bot, template_manager):
        cp = ConfigParser()
        cp.read("config.ini")
        self.moderators = [int(x) for x in cp["settings"]["moderators"].split(",")]

        self.bot: commands.Bot = bot
        self.template_manager: TemplateManager = template_manager

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"✅ Logged in as {self.bot.user}")

    @commands.command()
    async def intro(self, ctx: Context):
        embed1 = discord.Embed(title="Thanks for adding me!")

        embed1.description = "Hello, everyone!" + "\n"
        embed1.description += "IMbot (**i**mage **m**anipulation bot) is a versatile meme creation bot for discord which allows you to create and use image templates for creating memes on the fly." + "\n" + "\n"
        embed1.description += "There are two 'spaces' where templates are stored:" + "\n" + "\n"
        embed1.description += "**The public space**" + "\n"
        embed1.description += "Meme templates that are in the public space can be used by everyone, no matter which server they're on. You can submit suggestions for the public space." + "\n" + "\n"
        embed1.description += "**The guild space**" + "\n"
        embed1.description += "Since you can create custom templates, and the available meme names are limited if shared between servers, there is a second space which is for your guild (server) only. You can add your own templates, without having to adhere to a naming scheme or running out of available names. These templates are only visible to your guild." + "\n" + "\n"

        embed2 = discord.Embed(title="How to add templates")
        embed2.description = "**Add to your guild space** (instant)" + "\n"
        embed2.description += "• Go to https://imbot.realmayus.xyz to open a designer application which allows you to create the template." + "\n"
        embed2.description += "• Select your base image for the template" + "\n"
        embed2.description += "• Add fields and arrange them" + "\n"
        embed2.description += "• Download the template file (click on 'Serialize')" + "\n"
        embed2.description += "• Go to discord, attach the file *and* enter this command:\n  `.t add <name>`" + "\n" + "\n"
        embed2.description += "[**Submit suggestions for the public space**](https://imbot.realmayus.xyz/submit-public) (this takes time to verify)" + "\n"

        embed3 = discord.Embed(title="How to create memes based on a template")
        embed3.description = "**Add to your guild space** (instant)" + "\n"

        await ctx.send(embed=embed1)
        await ctx.send(embed=embed2)
        await ctx.send(embed=embed3)

    @commands.Cog.listener()
    async def on_guild_join(self, ctx: Context):
        await self.intro(ctx)

    async def list_templates(self, ctx: Context):
        paged_list = PagedListEmbed(f"{len(self.template_manager.templates)} templates loaded", [f"• {t.name}" for t in self.template_manager.templates], ctx, self.bot)
        await paged_list.send(paged_list.get())

    async def reload_templates(self, ctx: Context):
        self.template_manager.load_templates()
        await ctx.send("✅ Done!")

    async def add_template(self, ctx: Context, name: str):
        if len(ctx.message.attachments) != 1:
            await ctx.send("❌ Please attach exactly one template file.")

        if not is_ascii(name):
            await ctx.send("❌ The name cannot contain non-ASCII characters.")
            return

        try:
            att: Attachment = ctx.message.attachments[0]
            f = await att.read()
            decoded = f.decode("utf8")
            json_templ = json.loads(decoded)
            image_b64: str = json_templ["image"]
            b = io.BytesIO()
            b.write(base64.b64decode(image_b64))
            b.seek(0)
        except Exception:
            await ctx.send("❌ Not able to read template file.")
            return

        if json_templ["imageMIME"] == "image/jpeg":
            ext = ".jpg"
        elif json_templ["imageMIME"] == "image/png":
            ext = ".png"
        else:
            await ctx.send("MIME type not supported! D:")
            return

        with open("assets/templates/index.json") as c:
            json_ = json.loads(c.read())
            if name in [x["name"] for x in json_]:
                await ctx.send("❌ Name already taken. Please choose a different name.")
                return

            filename = random_string_generator(15) + ext
            print(filename)
            with open("assets/templates/images/" + filename, "wb") as img:
                img.write(b.read())

            json_templ["image"] = filename
            filename = random_string_generator(15)
            json_templ["name"] = name
            json_templ["id"] = filename
            json_templ["creator"] = ctx.message.author.id
            json_templ["createdAt"] = time.time()


            with open("assets/templates/" + filename + ".json", "w") as tem:
                tem.write(json.dumps(json_templ, indent=2))
            print(json_)
        json_.append({"file": filename + ".json", "name": name, "verified": False})
        with open("assets/templates/index.json", "w") as c:
            c.write(json.dumps(json_, indent=2))

        b.seek(0)
        templ = self.template_manager.parse_template(json_templ)
        await send_moderator_info(self.moderators, self.bot, ctx.author, self.highlight(templ), templ)
        await ctx.send("✅  Thanks for your submission. A moderator will review it and we'll notify you.")

    @staticmethod
    async def cleanup(ctx: Context):
        remove_from_index = []  # list of names to remove from index.json
        cleanup_count = 0
        with open("assets/templates/index.json") as c:
            json_ = json.loads(c.read())
            for template in json_:
                try:
                    if not template["verified"]:
                        delete_template(template["file"])
                        remove_from_index.append(template["name"])
                        cleanup_count += 1
                except Exception:
                    pass
        remove_templates_from_index(remove_from_index)
        await ctx.send(f"✅  Removed {cleanup_count} unapproved templates incl. images.")

    @commands.command()
    async def im(self, ctx: Context, template_name: str, *args):
        template = self.template_manager.find_template(template_name)
        if template is None:
            suggestions = self.template_manager.search_template(template_name)
            if len(suggestions) > 0:
                embed = discord.Embed(title="Search Results")
                embed.description = f"Couldn't find any templates with the name `{template_name}`,\n but found these similarly named ones:\n\n"
                embed.description += "\n".join([f"• **{x[0]}**" for x in suggestions])
                await ctx.send(embed=embed)
            else:
                await ctx.send("😕 Couldn't find template.")
            return
        print(f"./assets/templates/images/{template.file}")

        text = ' '.join(args)

        with open(f"./assets/templates/images/{template.file}", "rb") as f:
            arr = io.BytesIO()
            print(template.fields["text"])
            lines = text.split(";")
            if len(args) == 0:
                im = Image.open(f)
                for i in range(len(template.fields["text"])):
                    im = manipulator.add_text(im, template.fields["text"][i], f"Field #{i}")
            else:
                if len(template.fields["text"]) < text.count(';') + 1:
                    await ctx.send(f"😕 This template has {len(template.fields['text'])} fields. Make sure to separate the lines by using semicolons (;)!")
                    return
                im = Image.open(f)
                for i, line in enumerate(lines):
                    line = line.strip()
                    if line == "_":
                        continue
                    print(i, line)
                    im = manipulator.add_text(im, template.fields["text"][i], line.strip())
            im = im.convert('RGB')
            im.save(arr, format='JPEG')
            arr.seek(0)
            await ctx.send(f"❓ Make sure to fill in all {len(template.fields['text'])} fields by using semicolons!" if len(args) == 0 else None,
                           file=discord.File(arr, filename=f"{template.name}.jpg"))


    async def template_accept(self, ctx, name):
        with open("assets/templates/index.json") as c:
            json_ = json.loads(c.read())
        obj = next(x for x in json_ if x["name"] == name)
        json_ = [x for x in json_ if x["name"] != name]
        obj["verified"] = True
        json_.append(obj)
        with open("assets/templates/index.json", "w") as c:
            c.write(json.dumps(json_, indent=2))
        self.template_manager.load_templates()
        await ctx.message.add_reaction("✅")

    async def template_decline(self, ctx, name):
        with open("assets/templates/index.json") as c:
            json_ = json.loads(c.read())
        obj = next(x for x in json_ if x["name"] == name)
        delete_template(obj["file"])
        remove_templates_from_index([obj["name"]])
        self.template_manager.load_templates()
        await ctx.message.add_reaction("✅")

    async def template_rename(self, ctx, name, newname):
        with open("assets/templates/index.json") as c:
            json_ = json.loads(c.read())
        if next((x for x in json_ if x["name"] == newname), None) is not None:
            await ctx.send("❌ A template with this name already exists.")
            return
        if not is_ascii(newname):
            await ctx.send("❌ The new name cannot contain non-ASCII characters.")
            return

        # Modifying index.json
        obj = next(x for x in json_ if x["name"] == name)
        json_ = [x for x in json_ if x["name"] != name]
        obj["name"] = newname
        json_.append(obj)
        with open("assets/templates/index.json", "w") as c:
            c.write(json.dumps(json_, indent=2))

        # Modifying template json
        with open(f"assets/templates/{obj['file']}", "r") as t:
            template = json.loads(t.read())

        template["name"] = newname

        with open(f"assets/templates/{obj['file']}", "w") as t:
            t.write(json.dumps(template, indent=2))

        self.template_manager.load_templates()
        await ctx.message.add_reaction("✅")

    def highlight(self, template: Template) -> discord.File:
        with open(f"./assets/templates/images/{template.file}", "rb") as f:
            arr = io.BytesIO()
            print(template.fields["text"])
            im = Image.open(f)
            im = im.convert('RGB')
            im = draw_field_outlines(im, template)
            for i in range(len(template.fields["text"])):
                im = manipulator.add_text(im, template.fields["text"][i], f"Field #{i}")
            im.save(arr, format='JPEG')
            arr.seek(0)
        return discord.File(arr, filename=f"image.jpg")


    @commands.command(aliases=["temp", "t", "tl"])
    async def template(self, ctx, mode=None, *args):
        """Unified command that lets you add, accept, decline, reload, cleanup, list and rename templates."""

        if mode not in ["add", "list", "accept", "decline", "delete", "remove", "reload", "cleanup", "search", "rename", "highlight"]:
            await ctx.send("❌ This subcommand doesn't exist. See the help for all subcommands.")
            return

        if mode == "add":
            if not len(args) == 1:
                await ctx.send("❌ You need to specify a name for your template.")
                return
            await self.add_template(ctx, args[0])
        elif mode == "list":
            await self.list_templates(ctx)
        elif mode == "search":
            self.template_manager.search_template(args[0])
        elif mode == "highlight":
            await ctx.send(file=self.highlight(self.template_manager.find_template(args[0])))
        else:
            if ctx.author.id not in self.moderators:
                await ctx.send("❌ You don't have permission to execute this command.")
                return
            if mode == "accept":
                if not len(args) == 1:
                    await ctx.send("❌ You need to specify a name for the template to accept.")
                    return
                await self.template_accept(ctx, args[0])
            elif mode == "decline" or mode == "delete" or mode == "remove":
                if not len(args) == 1:
                    await ctx.send("❌ You need to specify a name for the template to decline/delete.")
                    return
                await self.template_decline(ctx, args[0])
            elif mode == "reload":
                await self.reload_templates(ctx)
            elif mode == "cleanup":
                await self.cleanup(ctx)
            elif mode == "rename":
                if not len(args) == 2:
                    await ctx.send("❌ You need to specify the name of the template to rename, and the new name.")
                    return
                await self.template_rename(ctx, args[0], args[1])
