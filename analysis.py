import enum


class Cells(enum.Enum):
    bg_green=None
    bg_flower="bg_flower"
    clock_gold="C"
    clarity_blue="M"
    flag="X"
    bg_brown=0
    num_1=1
    num_2=2
    num_3=3
    num_4=4
    num_5=5

def analyse_pixel(rgb, colour_counts):
    r, g, b = rgb

    if (
            70 <= r <= 84 and
            80 <= g <= 110 and
            25 <= b <= 40
    ):
        colour_counts[Cells.bg_green] += 1
    elif (
            205 <= r <= 210 and
            65 <= g <= 70 and
            90 <= b <= 100
    ):
        colour_counts[Cells.flag] += 1
    elif (
            71 <= r <= 90 and
            50 <= g <= 80 and
            30 <= b <= 48
    ):
        colour_counts[Cells.bg_brown] += 1
    elif (
            85 <= r <= 100 and
            100 <= g <= 110 and
            30 <= b <= 50
    ):
        colour_counts[Cells.bg_flower] += 1
    elif (
            194 <= r <= 195 and
            169 <= g <= 170 and
            100 <= b <= 115
    ) or (
            rgb == (0, 0, 0)
    ):
        colour_counts[Cells.clock_gold] += 1
    elif (
            rgb in [
        (50, 58, 104),
        (72, 72, 105),
        (94, 92, 108),
        (33, 176, 225),
        (82, 92, 153),
        (0, 82, 162),
    ]
    ):
        colour_counts[Cells.clarity_blue] += 1
    elif (
            111 <= r <= 117 and
            150 <= g <= 155 and
            44 <= b <= 48
    ):
        colour_counts[Cells.num_1] += 1
    elif rgb == (174, 197, 42):
        colour_counts[Cells.num_2] += 1
    elif (
            208 <= r <= 212 and
            185 <= g <= 188 and
            0 <= b <= 15
    ):
        colour_counts[Cells.num_3] += 1
    elif (
            223 <= r <= 227 and
            142 <= g <= 148 and
            0 <= b <= 15
    ):
        colour_counts[Cells.num_4] += 1
    elif (
            223 <= r <= 227 and
            82 <= g <= 88 and
            0 <= b <= 15
    ):
        colour_counts[Cells.num_5] += 1
    else:
        colour_counts[rgb] += 1