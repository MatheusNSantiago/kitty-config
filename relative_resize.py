# pyright: reportMissingImports=false
# REF: https://github.com/chancez/dotfiles/commit/52da974ecd561afaf97de66a3f1c41ae1fe5165e
# Tambem tem esse aqui (mas ta dando erro): https://github.com/megalithic/dotfiles/blob/main/config/kitty/relative_resize.py

from kittens.tui.handler import result_handler

AMMOUNT = 1.2


def main(args):
    pass


@result_handler(no_ui=True)
def handle_result(args, result, target_window_id, boss):
    window = boss.window_id_map.get(target_window_id)
    if window is None:
        return

    direction = args[1]

    neighbor_direction = direction
    if direction == "up":
        neighbor_direction = "top"
    if direction == "down":
        neighbor_direction = "bottom"

    neighbor = boss.active_tab.neighboring_group_id(neighbor_direction)

    if direction == "left" or direction == "right":
        if neighbor is None:
            boss.active_tab.resize_window("narrower", AMMOUNT)
        else:
            boss.active_tab.resize_window("wider", AMMOUNT)

    if direction == "up" or direction == "down":
        if neighbor is None:
            boss.active_tab.resize_window("shorter", AMMOUNT)
        else:
            boss.active_tab.resize_window("taller", AMMOUNT)
