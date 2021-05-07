from typing import Tuple

from PIL import ImageColor
from PIL.ImageDraw import ImageDraw
from PIL.ImageFont import FreeTypeFont


def wrap_text(text: str, width: int, font: FreeTypeFont) -> str:
    text_lines = []
    text_line = []
    words = text.split()


    for word in words:
        print(word)
        text_line.append(word)
        w, h = font.getsize(' '.join(text_line))
        if w > width:
            text_line.pop()
            text_lines.append(' '.join(text_line))
            text_line = [word]

    if len(text_line) > 0:
        text_lines.append(' '.join(text_line))

    return "\n".join(text_lines)


def draw_center_text(text: str, draw: ImageDraw, font: FreeTypeFont, f_width: int, x: int, y: int, color: Tuple[int, int, int]) -> Tuple[int, int]:
    text_width = font.getsize(text)[0]
    off_x = f_width / 2 - (text_width/ 2)
    draw.text((x + off_x, y), text, color, font)
    return font.getsize(text)


def draw_right_text(text: str, draw: ImageDraw, font: FreeTypeFont, f_width: int, x: int, y: int, color: Tuple[int, int, int]) -> Tuple[int, int]:
    text_width = font.getsize(text)[0]
    off_x = f_width - text_width
    draw.text((x + off_x, y), text, color, font)
    return font.getsize(text)


def convert_hex(hex_color: str) -> Tuple[int, int, int]:
    return ImageColor.getcolor(hex_color, "RGB")


# if __name__ == "__main__":
#     from PIL import ImageFont
#     font = ImageFont.truetype("../assets/fonts/NotoSans-Regular.ttf", 30)
#     res = wrap_text("I am once again asking for your financial support.", 20, font)
#     print("> Result:\n" + res)