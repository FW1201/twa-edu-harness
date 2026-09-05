"""教學文件的品牌色票。

色值沿用 tw-edu-skills v3.x，改動會影響所有既有教案 / 試卷 / 學習單的外觀，
不要在沒有明確需求時調整。
"""
from __future__ import annotations

from docx.shared import RGBColor

BLUE_DEEP = RGBColor(0x1A, 0x52, 0x76)
BLUE_MID = RGBColor(0x24, 0x71, 0xA3)
BLUE_LIGHT = RGBColor(0xEB, 0xF5, 0xFB)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GRAY_LIGHT = RGBColor(0xF8, 0xF9, 0xFA)
DARK_TEXT = RGBColor(0x1C, 0x2A, 0x35)
GREEN = RGBColor(0x1E, 0x84, 0x49)
GOLD = RGBColor(0xD4, 0xAC, 0x0D)
ORANGE = RGBColor(0xCA, 0x6F, 0x1E)
RED_SOFT = RGBColor(0xA9, 0x3A, 0x26)

MUTED_TEXT = RGBColor(0x7F, 0x8C, 0x8D)


def rgb_hex(c) -> str:
    """RGBColor → 六位十六進位字串（Word XML 的 w:fill / w:color 用）。"""
    return "{:02X}{:02X}{:02X}".format(c[0], c[1], c[2])
