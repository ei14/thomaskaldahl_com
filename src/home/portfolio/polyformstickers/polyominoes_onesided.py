from itertools import product

import numpy as np
from PIL import Image, ImageDraw, ImageOps

# Each polyomino is a frozenset of coordinates.
# No negative coordinates allowed.
# There must be at least one point (0, y) and at least one point (x, 0).
nominoes = [{frozenset()}, {frozenset([(0, 0)])}]

def add(pt0, pt1):
    return (pt0[0] + pt1[0], pt0[1] + pt1[1])
def sub(pt1, pt0):
    return (pt1[0] - pt0[0], pt1[1] - pt0[1])
def scale(scalar, pt):
    return (scalar*pt[0], scalar*pt[1])

def rotate_omino(omino):
    max_y = max(pt[1] for pt in omino)
    return frozenset((max_y - pt[1], pt[0]) for pt in omino)

def omino_desc(omino, max_n, naming=False):
    desc = [0 for _ in range(max_n)]
    for pt in omino:
        if naming:
            desc[pt[0]] += 1 << pt[1]
        else:
            desc[max_n - 1 - pt[1]] += 1 << pt[0]
    if naming:
        while desc[-1] == 0:
            desc = desc[:-1]
    return tuple(desc)

for n in range(2, 7+1):
    new_nominoes = set()

    for prev_nomino in nominoes[n-1]:
        for root, direction in product(prev_nomino, [(1, 0), (0, 1), (-1, 0), (0, -1)]):
            new_pt = add(root, direction)
            if new_pt in prev_nomino:
                continue
            new_nomino = prev_nomino | {new_pt}

            if new_pt[0] == -1:
                new_nomino = frozenset(add(pt, (1, 0)) for pt in new_nomino)
            elif new_pt[1] == -1:
                new_nomino = frozenset(add(pt, (0, 1)) for pt in new_nomino)

            rotated = new_nomino
            for _ in range(3):
                rotated = rotate_omino(rotated)
                if omino_desc(rotated, 7) < omino_desc(new_nomino, 7):
                    new_nomino = rotated

            new_nominoes.add(new_nomino)

    nominoes.append(new_nominoes)



CLEAR = (0, 0, 0, 0)
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)
DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

FPS = 60
DUR = 3
COLOR_DEPTH = 1
#PALETTE = tuple((255, 255, 255, 255//COLOR_DEPTH * i) for i in range(COLOR_DEPTH + 1)) \
#    + tuple((255//COLOR_DEPTH * i,)*3 + (255,) for i in range(COLOR_DEPTH-1, -1, -1))
#print(PALETTE)
palette = (
    (255, 255, 255, 0),
    (255, 255, 255, 128),
    (255, 255, 255, 255),
    (0, 0, 0, 255),
)
palette = Image.fromarray(np.array((palette,), dtype=np.uint8), mode="RGBA")
palette = palette.quantize(4)

for n in range(1, 7+1):
    for nomino in nominoes[n]:
        center = tuple(0.5 * round(2 * sum(pt[i] for pt in nomino) / n) for i in [0, 1])
        #center = (np.median([pt[0] for pt in nomino]), np.median([pt[1] for pt in nomino]))
        origin = scale(8, sub((3, 3), center))

        src_img = Image.new("RGBA", (57, 57), CLEAR)
        draw = ImageDraw.Draw(src_img)

        for pt in nomino:
            draw.rectangle(
                [add(scale(8, pt), origin), add(add(scale(8, pt), (8, 8)), origin)],
                fill=BLACK,
                outline=WHITE,
                width=1,
            )

        src_img = src_img.resize((570, 570), resample=Image.Resampling.NEAREST)

        frames = []
        for i in range(DUR*FPS):
            frames.append(
                src_img
                    .rotate(i * -360/DUR/FPS, resample=Image.Resampling.BILINEAR, translate=(-29, -29))
                    .crop((0, 0, 512, 512))
                    .resize((256, 256))
                    .quantize(4)
            )

        name = "".join(DIGITS[name_char] for name_char in omino_desc(nomino, 7, naming=True))
        name = str(n) + "_" + name

        #print(name)
        #frames[30].show()
        #input()

        print(name)
        frames[0].save(
            name + ".png",
            format="PNG",
            save_all=True,
            append_images=frames[1:],
            duration=1000/FPS,
            bits=2,
        )
