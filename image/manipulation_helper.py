from typing import Tuple

from PIL import ImageColor
from PIL.ImageDraw import ImageDraw
from PIL.ImageFont import FreeTypeFont
from PIL import ImageFont


def wrap_text(text: str, width: int, font: FreeTypeFont) -> Tuple[str, int, int]:
    text_lines = []
    text_line = []
    words = text.split()

    line_height = 0
    line_width = 0

    for word in words:
        text_line.append(word)
        w, h = font.getsize(' '.join(text_line))
        line_height = h
        line_width = max(line_width, w)
        if w > width:
            text_line.pop()
            text_lines.append(' '.join(text_line))
            text_line = [word]

    if len(text_line) > 0:
        text_lines.append(' '.join(text_line))

    text_height = line_height * len(text_lines)
    return "\n".join(text_lines), line_width, text_height


def fit_width_height(wrapped, field_width, field_height, fontsize, font_path, jumpsize, max_size):
    font = ImageFont.truetype(font_path, fontsize)
    while jumpsize > 1:
        # wrapped, line_width, line_height = wrap_text(text, field_width, font)
        line_width, line_height = font.getsize_multiline(wrapped)
        jumpsize = round(jumpsize)
        if line_height < field_height and line_width < field_width and fontsize + jumpsize < max_size:
            fontsize += jumpsize
        else:
            jumpsize = jumpsize // 2
            if fontsize > jumpsize:
                fontsize -= jumpsize
            else:
                fontsize = 0
        font = ImageFont.truetype(font_path, fontsize)
    return fontsize, font


def get_font_size_and_wrapped(max_size, field_width, field_height, font_path: str, text) -> Tuple[FreeTypeFont, int, str]:
    field_height = round(field_height)
    fontsize = max_size
    jumpsize = 75
    font = ImageFont.truetype(font_path, max_size)
    wrapped, line_width, line_height = wrap_text(text, field_width, font)
    i = 0
    while i < 3:
        fontsize, font = fit_width_height(wrapped, field_width, field_height, fontsize, font_path, jumpsize, max_size)
        wrapped, line_width, line_height = wrap_text(text, field_width, font)
        i += 1

    return font, fontsize, wrapped


def draw_center_text(text: str, draw: ImageDraw, font: FreeTypeFont, f_width: int, x: int, y: int, color: Tuple[int, int, int], outline_percentage, outline_color, fontsize) -> Tuple[int, int]:
    text_width = font.getsize(text)[0]
    off_x = f_width / 2 - (text_width/ 2)
    draw.text((x + off_x, y), text, color, font, stroke_width=round(outline_percentage * 0.01 * fontsize), stroke_fill=outline_color)
    return font.getsize(text)


def draw_right_text(text: str, draw: ImageDraw, font: FreeTypeFont, f_width: int, x: int, y: int, color: Tuple[int, int, int], outline_percentage, outline_color, fontsize) -> Tuple[int, int]:
    text_width = font.getsize(text)[0]
    off_x = f_width - text_width
    draw.text((x + off_x, y), text, color, font, stroke_width=round(outline_percentage * 0.01 * fontsize), stroke_fill=outline_color)
    return font.getsize(text)


def convert_hex(hex_color: str) -> Tuple[int, int, int]:
    return ImageColor.getcolor(hex_color, "RGB")

