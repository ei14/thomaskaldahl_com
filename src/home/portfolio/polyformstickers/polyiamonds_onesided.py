from pathlib import Path
from itertools import product, combinations
from math import pi, sqrt, floor

import cairo

from cint import *

# Each polyiamond is a frozenset of Eisensten integers, none divisible by ω-1.
# No negative coordinates allowed.
# Must contain at least one real coordinate.
# Must be shifted in the -1 direction as much as possible.
polyiamonds = [{frozenset()}, {frozenset({Eis(1)})}]

#for b in range(19, -1, -1):
#    print((20-b)*" ", end="")
#    for a in range(20):
#        print(["⏺ ", "  "][int((W-1).divides(Eis(a, b)))], end="")
#    print()

def describe(iamond):
    desc = [0 for _ in range(10)]
    for pt in iamond:
        desc[pt.a] += 1 << pt.b
    return tuple(desc)

def normalize(iamond):
    normalized = iamond

    min_b = min(pt.b for pt in normalized)
    normalized = frozenset(pt - min_b*(2+W) for pt in normalized)

    min_a = min(pt.a for pt in normalized)
    min_a_round = min_a // 3 * 3
    normalized = frozenset(pt - min_a_round for pt in normalized)

    return normalized

def rotate(iamond):
    return normalize(frozenset((1+W)*pt for pt in iamond))

for n in range(2, 8+1):
    niamonds = set()

    for prev_iamond in polyiamonds[n-1]:
        for root, direction in product(prev_iamond, [1, W, -1-W]):
            if root.congruent(2, W-1):
                direction *= 1+W
            new_pt = root + direction

            if new_pt in prev_iamond:
                continue
            new_iamond = prev_iamond | {new_pt}

            new_iamond = normalize(new_iamond)

            rotated = new_iamond.copy()
            for _ in range(5):
                rotated = rotate(rotated)
                if describe(rotated) < describe(new_iamond):
                    new_iamond = rotated

            niamonds.add(new_iamond)
            #print(f"{root}\t{direction}\t\t{new_iamond}")

    polyiamonds.append(niamonds)



Path("frames").mkdir(exist_ok=True)

CLEAR = (0, 0, 0, 0)
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)

DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

for n in range(1, 8+1):
    for iamond in polyiamonds[n]:
        name_chars = describe(iamond)
        assert max(name_chars) <= 0xff
        name = "".join(f"{name_char:02x}" for name_char in name_chars)
        #name = "".join(DIGITS[name_char] for name_char in name_chars)
        name = str(n) + "_" + name

        Path(f"frames/{name}").mkdir(exist_ok=True)

        for frame in range(180):
            angle = frame*pi/90

            origin = complex(sum(iamond)) / n
            round_scale = 1
            while Eis.num_closest(origin * round_scale, 1e-3) > 1:
                round_scale += 1
            origin = complex(Eis.closest(origin * round_scale)) / round_scale

            surface = cairo.ImageSurface(cairo.Format.ARGB32, 512, 512)
            ctx = cairo.Context(surface)

            #ctx.rectangle(0, 0, 512, 512)
            #ctx.set_source_rgba(0x62/0xff, 0, 1)
            #ctx.fill()

            ctx.set_matrix(cairo.Matrix(0, 1, 1, 0, 0, 0)) # Flip across y=x
            ctx.translate(256, 256)
            ctx.rotate(-angle)
            ctx.scale(512/8, 512/8)
            ctx.translate(-origin.real, -origin.imag)

            edges = set()
            for pt in iamond:
                if pt.congruent(1, W-1):
                    pt_verts = [pt - 1, pt - W, pt + 1+W]
                else:
                    pt_verts = [pt + 1, pt + W, pt + -1-W]

                ctx.move_to(pt_verts[0].real(), pt_verts[0].imag())
                ctx.line_to(pt_verts[1].real(), pt_verts[1].imag())
                ctx.line_to(pt_verts[2].real(), pt_verts[2].imag())
                ctx.close_path()

                ctx.set_source_rgba(0, 0, 0)
                ctx.fill()

                for i in range(3):
                    v1 = pt_verts[i]
                    v2 = pt_verts[(i + 1) % 3]

                    edges.add((v1, v2))

            ext_edges = set(edge for edge in edges if (edge[1], edge[0]) not in edges)
            next_vert = dict(ext_edges)
            int_edges = set(frozenset(edge) for edge in edges if edge not in ext_edges)

            first_vert = next(iter(next_vert))
            ctx.move_to(first_vert.real(), first_vert.imag())
            cur_vert = next_vert[first_vert]
            while cur_vert != first_vert:
                ctx.line_to(cur_vert.real(), cur_vert.imag())
                cur_vert = next_vert[cur_vert]
            ctx.close_path()

            ctx.set_source_rgba(1, 1, 1)
            ctx.set_line_width(0.125)
            ctx.set_line_join(cairo.LineJoin.MITER)
            ctx.stroke()

            ctx.set_line_cap(cairo.LineCap.BUTT)
            for edge in int_edges:
                v1, v2 = edge
                ctx.move_to(v1.real(), v1.imag())
                ctx.line_to(v2.real(), v2.imag())
                ctx.stroke()

            surface.write_to_png(f"frames/{name}/{frame:03}.png")
            print(name, frame)
