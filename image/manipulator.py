import random

from PIL.Image import Image
from PIL import ImageFont
from PIL import ImageDraw

from image.manipulation_helper import wrap_text, draw_center_text, draw_right_text, convert_hex
from image.types import TextField, Align, Template


def add_text(im: Image, field: TextField, text: str) -> Image:
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype("./assets/fonts/NotoSans-Regular.ttf", round(field.font_size))
    print(field.align)
    wrapped = wrap_text(text, field.width, font)
    off_y = 0
    for line in wrapped.split("\n"):
        _, line_height = font.getsize(line)

        if Align(field.align) is Align.CENTER:
            draw_center_text(line, draw, font, field.width, field.posX, field.posY + off_y, convert_hex(field.color))
        elif Align(field.align) is Align.LEFT:
            draw.text((field.posX, field.posY + off_y), line, (0, 0, 0), font)
        elif Align(field.align) is Align.RIGHT:
            draw_right_text(line, draw, font, field.width, field.posX, field.posY + off_y, convert_hex(field.color))
        off_y += line_height
    return im


def get_random_color() -> str:
    return '#%02X%02X%02X' % (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


def draw_field_outlines(im, template: Template) -> Image:
    draw = ImageDraw.Draw(im)
    for field in template.fields["text"]:
        draw.rectangle((field.posX, field.posY, field.posX + field.width, field.posY + field.height), fill=get_random_color())

    for field in template.fields["images"]:
        draw.rectangle((field.posX, field.posY, field.posX + field.width, field.posY + field.height), fill=get_random_color())

    return im
