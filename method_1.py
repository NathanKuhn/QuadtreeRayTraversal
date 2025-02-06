# from https://research.nvidia.com/sites/default/files/pubs/2010-02_Efficient-Sparse-Voxel/laine2010tr1_paper.pdf
import struct
from quadtree import QuadTree
from pygame.math import Vector2

EPSILON = 1e-6


def float_to_bits(f: float) -> int:
    s = struct.pack(">f", f)
    return struct.unpack(">l", s)[0]


def bits_to_float(b: int) -> float:
    s = struct.pack(">l", b)
    return struct.unpack(">f", s)[0]


def quadtree_intersect(
    qt: QuadTree, ray_start: Vector2, ray_dir: Vector2, debug_print=False
) -> float:

    # Get rid of any zero components
    ray_dir.x = ray_dir.x if abs(ray_dir.x) > EPSILON else EPSILON
    ray_dir.y = ray_dir.y if abs(ray_dir.y) > EPSILON else EPSILON

    # Precompute t equation components
    tx_coef = 1 / -abs(ray_dir.x)
    ty_coef = 1 / -abs(ray_dir.y)

    tx_bias = tx_coef * ray_start.x
    ty_bias = ty_coef * ray_start.y

    # Select quadrant mask to mirror the ray to make the ray direction negative
    quadrant_mask = 3
    if ray_dir.x > 0:
        quadrant_mask ^= 1
        tx_bias = (qt.x0 + qt.x1) * tx_coef - tx_bias
    if ray_dir.y > 0:
        quadrant_mask ^= 2
        ty_bias = (qt.y0 + qt.y1) * ty_coef - ty_bias

    # Initialize t range values
    t_min = max(qt.x1 * tx_coef - tx_bias, qt.y1 * ty_coef - ty_bias)
    t_max = min(qt.x0 * tx_coef - tx_bias, qt.y0 * ty_coef - ty_bias)
    print(t_min, t_max)
    h = t_max
    t_min = max(t_min, 0)
    t_max = min(t_max, 1000)

    # Initialize current voxel to the first child of the root
    parent = qt
    idx = 0
    pos = Vector2(1, 1)

    s_max = 23
    scale = s_max - 1
    scale_exp2 = 0.5
    stack = [None] * (s_max + 1)

    root_mid = Vector2((qt.x0 + qt.x1) / 2, (qt.y0 + qt.y1) / 2)
    if root_mid.x * tx_coef - tx_bias > t_min:
        idx ^= 1
        pos.x = root_mid.x
    if root_mid.y * ty_coef - ty_bias > t_min:
        idx ^= 2
        pos.y = root_mid.y

    # Traverse voxels along the ray as long as the current voxel stays within the quadtree
    i = 0
    while scale < s_max and i < 10:
        i += 1
        print(scale)
        # Determine maximum t value for the cube
        tx_corner = pos.x * tx_coef - tx_bias
        ty_corner = pos.y * ty_coef - ty_bias
        tc_max = min(tx_corner, ty_corner)

        child_shift = idx ^ quadrant_mask

        if parent is not None and t_min <= t_max:

            # if voxel is small enough, terminate at t_min?

            # INTERSECT
            tv_max = min(t_max, tc_max)
            half = scale_exp2 / 2
            tx_center = half * tx_coef + tx_corner
            ty_center = half * ty_coef + ty_corner

            if t_min <= tv_max:
                if parent.is_leaf:
                    if debug_print:
                        print("leaf", scale)
                    return t_min

                # PUSH
                if tc_max < h:
                    stack[scale] = (parent, t_max)
                h = tc_max

                parent = parent.get_child(child_shift)
                if parent is None:
                    if debug_print:
                        print("no child", child_shift, scale)
                    break

                # Select child voxel ray enters first
                idx = 0
                scale -= 1
                scale_exp2 = half

                if tx_center > t_min:
                    idx ^= 1
                    pos.x += scale_exp2
                if ty_center > t_min:
                    idx ^= 2
                    pos.y += scale_exp2

                t_max = tv_max
                continue

        # ADVANCE
        step_mask = 0
        if tx_corner < tc_max:
            step_mask ^= 1
            pos.x -= scale_exp2
        if ty_corner < tc_max:
            step_mask ^= 2
            pos.y -= scale_exp2

        # Update t range and child index
        t_min = tc_max
        idx ^= step_mask

        if idx & step_mask != 0:

            # POP
            differing_bits = 0
            if step_mask & 1:
                differing_bits |= float_to_bits(pos.x) ^ float_to_bits(
                    pos.x + scale_exp2
                )
            if step_mask & 2:
                differing_bits |= float_to_bits(pos.y) ^ float_to_bits(
                    pos.y + scale_exp2
                )

            parent, t_max = stack[scale]

            shx = float_to_bits(pos.x) >> scale
            shy = float_to_bits(pos.y) >> scale

            pos.x = bits_to_float(shx << scale)
            pos.y = bits_to_float(shy << scale)

            idx = (shx & 1) | ((shy & 1) << 1)

            h = 0

    if scale >= s_max or t_min < 0:
        return 1000

    return t_min
