from pathlib import Path
from itertools import product, combinations
from math import pi, sqrt, floor, log10

import cairo

from cint import *

N = 6

# Each polyhex is a frozenset of Eisensten integers.
# No negative coordinates allowed.
# Must contain at least one real point and one real multiple of ω.
polyhexes = [{frozenset()}, {frozenset({Eis(0)})}]

def describe(polyhex):
    description = [0 for _ in range(N)]
    for pt in polyhex:
        description[pt.a] += 1 << pt.b
    return description

def normalize(iamond):
    normalized = iamond

    min_b = min(pt.b for pt in normalized)
    normalized = frozenset(pt - min_b*W for pt in normalized)

    min_a = min(pt.a for pt in normalized)
    normalized = frozenset(pt - min_a for pt in normalized)

    return normalized

def rotate(iamond):
    return normalize(frozenset((1+W)*pt for pt in iamond))

for n in range(2, N+1):
    nhexes = set()

    for prev_hex in polyhexes[n-1]:
        for root, direction in product(prev_hex, [1, 1+W, W, -1, -1-W, -W]):
            new_pt = root + direction

            if new_pt in prev_hex:
                continue
            new_hex = prev_hex | {new_pt}

            if new_pt.a < 0:
                new_hex = frozenset(pt + 1 for pt in new_hex)
            if new_pt.b < 0:
                new_hex = frozenset(pt + W for pt in new_hex)

            rotated = new_hex.copy()
            for _ in range(5):
                rotated = rotate(rotated)
                if describe(rotated) < describe(new_hex):
                    new_hex = rotated

            nhexes.add(new_hex)

    polyhexes.append(nhexes)

for n in range(N+1):
    polyhexes[n] = list(sorted(polyhexes[n], key=describe))



Path("frames").mkdir(exist_ok=True)

CLEAR = (0, 0, 0, 0)
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)

DIGITS = "0123456789abcdefghijkLmnopqrstuvwxyz"

for n in range(N, 0, -1):
    for hex_i, nhex in enumerate(polyhexes[n]):
        name_chars = describe(nhex)
        name = "".join(DIGITS[name_char] for name_char in name_chars)
        name = f"{n}_{hex_i:0{1 + floor(log10(len(polyhexes[n])))}}_{name}"

        Path(f"frames/{name}").mkdir(exist_ok=True)



        origin = complex(sum(nhex)) / n
        round_scale = 2
        while Eis.num_closest(origin * round_scale, 1e-3) > 1:
            round_scale += 1
        origin = complex(Eis.closest(origin * round_scale)) / round_scale
        origin *= 3



        edges = set()
        for pt in nhex:
            verts = []
            vert_displace = 2+W
            for _ in range(6):
                verts.append(3*pt + vert_displace)
                vert_displace *= 1+W

            for i in range(6):
                v1 = verts[i]
                v2 = verts[(i + 1) % 6]

                edges.add((v1, v2))

        ext_edges = set(edge for edge in edges if (edge[1], edge[0]) not in edges)
        next_vert = dict(ext_edges)
        int_edges = set(frozenset(edge) for edge in edges if edge not in ext_edges)



        for frame in range(180):
            angle = frame * pi / 90

            surface = cairo.ImageSurface(cairo.Format.ARGB32, 512, 512)
            ctx = cairo.Context(surface)

            #ctx.rectangle(0, 0, 512, 512)
            #ctx.set_source_rgba(0x62/0xff, 0, 1)
            #ctx.fill()

            ctx.translate(256, 256)
            ctx.rotate(angle)
            ctx.scale(512/18.5, 512/18.5)
            ctx.translate(-origin.real, -origin.imag)



            for pt in nhex:
                verts = []
                vert_displace = 2+W
                for _ in range(6):
                    verts.append(3*pt + vert_displace)
                    vert_displace *= 1+W

                ctx.move_to(verts[0].real(), verts[0].imag())
                for vert in verts[1:]:
                    ctx.line_to(vert.real(), vert.imag())
                ctx.close_path()

                ctx.set_source_rgba(0, 0, 0)
                ctx.fill_preserve()
                ctx.set_source_rgba(1, 1, 1)
                ctx.set_line_width(0.25)
                ctx.set_line_join(cairo.LineJoin.MITER)
                ctx.stroke()



            surface.write_to_png(f"frames/{name}/{frame:03}.png")
            print(f"{name}/{frame:03}")
