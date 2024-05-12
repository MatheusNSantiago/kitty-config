# pyright: reportMissingImports=false
# REF: https://github.com/nosvagor/dotfiles/blob/main/config/kitty/tab_bar.py

from os import getlogin, uname
from kitty.fast_data_types import Screen, get_options
from kitty.utils import color_as_int
from kitty.tab_bar import (
    DrawData,
    ExtraData,
    Formatter,
    TabBarData,
    as_rgb,
    draw_attributed_string,
    draw_title,
)

opts = get_options()

if opts.tab_bar_background is None:
    tab_background = 0
else:
    tab_background = opts.tab_bar_background

FG = as_rgb(color_as_int(opts.background))
# BG = as_rgb(color_as_int(opts.color4))
BG = as_rgb(color_as_int(opts.color1))  # RED
ACCENT = as_rgb(color_as_int(opts.selection_background))

BAR_BG = as_rgb(color_as_int(tab_background))
ACTIVE_BG = as_rgb(color_as_int(opts.active_tab_background))

ACTIVE_FG = BG
INACTIVE_FG = as_rgb(0xFF7492EF)  # #7492EF

SEPARATOR_SYMBOL, SOFT_SEPARATOR_SYMBOL = ("", "")
SEPARATOR_SYMBOL_RIGHT = ""
ICON, ICON_USER, ICON_DIR = ("  ", " ", "  ")
TRUNCATION_SYMBOL = "  //"

RIGHT_MARGIN = -4
REFRESH_TIME = 1
right_status_length = -1


def _draw(screen: Screen, text: str, bg = None, fg = None):
    prev_fg, prev_bg = screen.cursor.fg, screen.cursor.bg

    if bg is not None:
        screen.cursor.bg = bg
    if fg is not None:
        screen.cursor.fg = fg

    screen.draw(text)
    screen.cursor.fg, screen.cursor.bg = prev_fg, prev_bg

def _draw_icon(title: str, screen: Screen, index: int) -> int:
    if index != 1:
        return 0
    fg, bg = screen.cursor.fg, screen.cursor.bg
    screen.cursor.fg, screen.cursor.bg = FG, BG

    if title.startswith("v") or title.startswith("nvim"):
        # _draw(screen, " ", fg = as_rgb(0xFF252539)) # #252539 
        _draw(screen, "  ", fg = as_rgb(0xFF252539)) # #252539 
    else:
        screen.draw(ICON)

    screen.cursor.fg, screen.cursor.bg = BG, bg
    screen.draw(SEPARATOR_SYMBOL)
    screen.cursor.fg, screen.cursor.bg = fg, bg
    screen.cursor.x = len(ICON + SEPARATOR_SYMBOL)
    return screen.cursor.x


def _draw_left_status(
    draw_data: DrawData,
    screen: Screen,
    tab: TabBarData,
    index: int,
    extra_data: ExtraData,
) -> int:
    if screen.cursor.x >= screen.columns - right_status_length:
        return screen.cursor.x

    tab_bg, tab_fg = screen.cursor.bg, screen.cursor.fg

    if index == 1:
        screen.cursor.fg, screen.cursor.bg = tab_bg, BAR_BG
        screen.draw(SEPARATOR_SYMBOL_RIGHT)
        screen.cursor.bg = tab_bg

    default_bg = as_rgb(int(draw_data.default_bg))

    if extra_data.next_tab:  # Tudo que estiver atras da minha ultima tab
        next_tab_bg = as_rgb(draw_data.tab_bg(extra_data.next_tab))
        needs_soft_separator = next_tab_bg == tab_bg
    else:  # Ultima tab
        next_tab_bg = default_bg
        needs_soft_separator = False

    if screen.cursor.x <= len(ICON):
        screen.cursor.x = len(ICON)

    screen.cursor.bg = tab_bg
    if tab.is_active:
        screen.cursor.fg = ACTIVE_FG
    else:
        screen.cursor.fg = INACTIVE_FG

    screen.draw(" ")
    draw_title(draw_data, screen, tab, index)

    if not needs_soft_separator:
        screen.draw(" ")
        screen.cursor.fg = tab_bg
        screen.cursor.bg = next_tab_bg
        screen.draw(SEPARATOR_SYMBOL)
    else:
        prev_fg = screen.cursor.fg
        if tab_bg == tab_fg:
            screen.cursor.fg = default_bg
        elif tab_bg != default_bg:
            c1 = draw_data.inactive_bg.contrast(draw_data.default_bg)
            c2 = draw_data.inactive_bg.contrast(draw_data.inactive_fg)
            if c1 < c2:
                screen.cursor.fg = default_bg
        screen.draw(" " + SOFT_SEPARATOR_SYMBOL)
        screen.cursor.fg = prev_fg
    end = screen.cursor.x
    return end


def _draw_right_status(screen: Screen, is_last: bool, cells: list) -> int:
    if not is_last:
        screen.cursor.bg = FG
        return screen.cursor.x
    draw_attributed_string(Formatter.reset, screen)
    screen.cursor.x = screen.columns - right_status_length
    screen.cursor.fg = 0
    screen.cursor.bg = 0
    for color_fg, color_bg, status in cells:
        screen.cursor.fg = color_fg
        screen.cursor.bg = color_bg
        screen.draw(status)
    return screen.cursor.x


def draw_tab(
    draw_data: DrawData,
    screen: Screen,
    tab: TabBarData,
    before: int,  # Not accessed, but things break without it?
    max_title_length: int,  # Not accessed, but things break without it?
    index: int,
    is_last: bool,
    extra_data: ExtraData,
) -> int:
    global right_status_length
    app = ICON_USER + getlogin() + " " + SEPARATOR_SYMBOL_RIGHT
    host = uname()[1] + " "
    cells = []
    cells.append((ACTIVE_BG, BAR_BG, SEPARATOR_SYMBOL_RIGHT))
    cells.append((BG, ACTIVE_BG, app))
    cells.append((FG, BG, host))
    # right_status_length = RIGHT_MARGIN + 2
    right_status_length = RIGHT_MARGIN - 2
    for cell in cells:
        right_status_length += len(str(cell[1]))

    _draw_icon(tab.title,screen, index)
    # _draw_cwd(screen, index)
    _draw_left_status(
        draw_data,
        screen,
        tab,
        index,
        extra_data,
    )
    _draw_right_status(
        screen,
        is_last,
        cells,
    )
    return screen.cursor.x
