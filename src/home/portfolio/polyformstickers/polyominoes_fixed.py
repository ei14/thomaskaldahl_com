from itertools import product

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

for n in range(2, 5+1):
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

            new_nominoes.add(new_nomino)

    nominoes.append(new_nominoes)



CLEAR = (0, 0, 0, 0)
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)
DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
for n in range(1, 5+1):
    for nomino in nominoes[n]:
        size = (max(pt[0] for pt in nomino) + 1, max(pt[1] for pt in nomino) + 1)
        origin = scale(4, sub((5, 5), size))

        im = Image.new("RGBA", (41, 41), CLEAR)
        draw = ImageDraw.Draw(im)

        for pt in nomino:
            draw.rectangle(
                [add(scale(8, pt), origin), add(add(scale(8, pt), (8, 8)), origin)],
                fill=BLACK,
                outline=WHITE,
                width=1,
            )

        im = im.resize((492, 492), resample=Image.Resampling.NEAREST)
        im_scaled = Image.new("RGBA", (512, 512), CLEAR)
        im_scaled.paste(im, (10, 10, 502, 502))
        im = im_scaled

        name_chars = [0 for _ in range(5)]
        for pt in nomino:
            name_chars[pt[0] + pt[1]] += 1 << pt[1]
        name = "".join(DIGITS[name_char] for name_char in reversed(name_chars))
        name = str(n) + "_" + name

        #print(name)
        #im.show()
        #input()

        print(name)
        im.save(name + ".webp", format="WebP", lossless=True)
