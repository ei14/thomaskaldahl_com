from itertools import product, combinations
from math import pi, sqrt, floor, log10

import cairo

from cint import *

N = 5

# Each polyhex is a frozenset of Eisensten integers.
# No negative coordinates allowed.
# Must contain at least one real point and one real multiple of ω.
polyhexes = [{frozenset()}, {frozenset({Eis(0)})}]

def describe(polyhex):
    description = [0 for _ in range(N)]
    for pt in polyhex:
        description[pt.a] += 1 << pt.b
    return description

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

            nhexes.add(new_hex)

    polyhexes.append(nhexes)

for n in range(N+1):
    polyhexes[n] = list(sorted(polyhexes[n], key=describe))


CLEAR = (0, 0, 0, 0)
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)
DIGITS = "0123456789abcdefghijkLmnopqrstuvwxyz"
for n in range(1, N+1):
    for hex_i, nhex in enumerate(polyhexes[n]):
        #origin = complex(sum(nhex)) / n
        #round_scale = 100
        #while Eis.num_closest(origin * round_scale, 1e-3) > 1:
        #    round_scale += 1
        #origin = complex(Eis.closest(origin * round_scale)) / round_scale
        #origin *= 3

        origin = (min(pt.real() for pt in nhex) + max(pt.real() for pt in nhex)) / 2 \
            + (min(pt.imag() for pt in nhex) + max(pt.imag() for pt in nhex)) / 2 * 1j
        if nhex in {frozenset({1, W, 1+W, 2+2*W}), frozenset({0, 1+W, 2+W, 1+2*W})}:
            origin2 = complex(sum(nhex)) / n
            origin = 0.5 * (origin + origin2)
        origin *= 3

        surface = cairo.ImageSurface(cairo.Format.ARGB32, 512, 512)
        ctx = cairo.Context(surface)

        #ctx.rectangle(0, 0, 512, 512)
        #ctx.set_source_rgba(0x62/0xff, 0, 1)
        #ctx.fill()

        ctx.translate(256, 256)
        ctx.scale(512/15.4, 512/15.4)
        ctx.translate(-origin.real, -origin.imag)

        edges = set()
        ctx.set_source_rgba(0, 0, 0)
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
            ctx.fill()

            for i in range(6):
                v1 = verts[i]
                v2 = verts[(i + 1) % 6]

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
        ctx.set_line_width(0.25)
        ctx.set_line_join(cairo.LineJoin.MITER)
        ctx.stroke()

        ctx.set_line_cap(cairo.LineCap.BUTT)
        for edge in int_edges:
            v1, v2 = edge
            ctx.move_to(v1.real(), v1.imag())
            ctx.line_to(v2.real(), v2.imag())
            ctx.stroke()

        name_chars = [0 for _ in range(N)]
        for pt in nhex:
            name_chars[pt.a] += 1 << pt.b
        assert max(name_chars) <= 0xff
        #name = "".join(f"{name_char:02x}" for name_char in name_chars)
        name = "".join(DIGITS[name_char] for name_char in name_chars)
        name = f"{n}_{hex_i:0{1 + floor(log10(len(polyhexes[n])))}}_{name}"

        surface.write_to_png(name + ".png")
        print(name)
