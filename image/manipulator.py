import random

from PIL.Image import Image
from PIL import ImageDraw

from image.manipulation_helper import draw_center_text, draw_right_text, convert_hex, get_font_size_and_wrapped
from image.types import TextField, Align, Template


def get_font_path(bold: bool) -> str:
    if bold:
        return "./assets/fonts/NotoSans-Bold.ttf"
    else:
        return "./assets/fonts/NotoSans-Regular.ttf"


def add_text(im: Image, field: TextField, text: str) -> Image:
    draw = ImageDraw.Draw(im)
    font, fontsize, wrapped = get_font_size_and_wrapped(round(field.font_size), field.width, field.height, get_font_path(field.bold), text)
    off_y = 0
    for line in wrapped.split("\n"):
        _, line_height = font.getsize(line)

        if Align(field.align) is Align.CENTER:
            draw_center_text(line, draw, font, field.width, field.posX, field.posY + off_y, convert_hex(field.color), int(field.outlinePercentage), field.outlineColor, fontsize)
        elif Align(field.align) is Align.LEFT:
            draw.text((field.posX, field.posY + off_y), line, (0, 0, 0), font, stroke_width=round(int(field.outlinePercentage) * 0.01 * fontsize), stroke_fill=field.outlineColor)
        elif Align(field.align) is Align.RIGHT:
            draw_right_text(line, draw, font, field.width, field.posX, field.posY + off_y, convert_hex(field.color), int(field.outlinePercentage), field.outlineColor, fontsize)
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
