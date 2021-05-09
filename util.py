import io
import json
import os
import random
import string

import discord
from discord import User
from PIL import Image

from image.manipulator import draw_field_outlines
from image.types import Template


def random_string_generator(str_size):
    return ''.join(random.choice(string.ascii_letters) for _ in range(str_size))


def is_ascii(s: str):
    try:
        s.encode('ascii')
    except UnicodeEncodeError:
        return False
    else:
        return True


async def send_moderator_info(moderators, bot, submitter, file, template: Template):
    for mod in moderators:
        mod_user: User = bot.get_user(mod)
        embed = discord.Embed(title=f"{submitter} has submitted a new template")
        embed.set_image(url=f"attachment://image.jpg")
        embed.add_field(name="Text fields", value=str(len(template.fields["text"])))
        embed.add_field(name="Image fields", value=str(len(template.fields["images"])))
        embed.add_field(name="Name", value=template.name)
        embed.add_field(name="User", value=f"{submitter} • {str(submitter.id)}", inline=False)
        embed.description = f"Use `.t accept {template.name}` to accept this template.\n\n"
        embed.description += f"Use `.t decline {template.name}` to decline this template."

        await mod_user.send(file=file, embed=embed)


def delete_template(file):
    with open(f"assets/templates/{file}") as tem:
        tem_json = json.loads(tem.read())
        os.remove(f"assets/templates/images/{tem_json['image']}")
    os.remove(f"assets/templates/{file}")


def remove_templates_from_index(remove_from_index):
    with open("assets/templates/index.json") as c:
        json_ = json.loads(c.read())
    with open("assets/templates/index.json", "w") as c:
        json_ = [x for x in json_ if x["name"] not in remove_from_index]
        c.write(json.dumps(json_, indent=2))
