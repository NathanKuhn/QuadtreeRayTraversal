# from https://github.com/DavidWilliams81/cubiquity/blob/master/src/application/commands/view/glsl/pathtracing.frag#L333
import struct
from quadtree import QuadTree
from pygame.math import Vector2


def float_to_bits(f: float) -> int:
    s = struct.pack(">f", f)
    return struct.unpack(">l", s)[0]


def bits_to_float(b: int) -> float:
    s = struct.pack(">l", b)
    return struct.unpack(">f", s)[0]


def vec_mul(a: Vector2, b: Vector2) -> Vector2:
    return Vector2(a.x * b.x, a.y * b.y)


def find_first_child(
    node_entry: float, ray_origin: Vector2, ray_inv_dir: Vector2, node_center: Vector2
) -> int:
    node_tm = vec_mul((node_center - ray_origin), ray_inv_dir)
    child_node = 0

    if node_tm.x < node_entry:
        child_node += 1
    if node_tm.y < node_entry:
        child_node += 2

    if node_entry <= 0:
        if ray_origin.x < node_center.x:
            child_node |= 1
        if ray_origin.y < node_center.y:
            child_node |= 2

    return child_node


def quadtree_intersect(qt: QuadTree, ro: Vector2, rd: Vector2) -> float:
    ro = ro.copy()
    rd = rd.copy()

    start_height = 9  # 512x512 quadtree

    node_pos = Vector2(qt.x0, qt.y0)
    node_size = Vector2(qt.x1 - qt.x0, qt.y1 - qt.y0)

    if abs(rd.x) < 1e-6:
        rd.x = 1e-6 * (1 if rd.x > 0 else -1)
    if abs(rd.y) < 1e-6:
        rd.y = 1e-6 * (1 if rd.y > 0 else -1)

    child_id_flip = 0
    if rd.x < 0:
        child_id_flip |= 1
    if rd.y < 0:
        child_id_flip |= 2

    ray_dir_sign = Vector2(1 if rd.x >= 0 else -1, 1 if rd.y >= 0 else -1)
    ro += Vector2(0.5, 0.5)
    ro -= Vector2(256, 256)
    ro = vec_mul(ro, ray_dir_sign)
    ro += Vector2(256, 256)
    rd = Vector2(abs(rd.x), abs(rd.y))

    inv_ray_dir = Vector2(1 / rd.x, 1 / rd.y)
    node_t0 = vec_mul((node_pos - ro), inv_ray_dir)
    node_t1 = vec_mul((node_pos + node_size - ro), inv_ray_dir)

    node_entry = max(node_t0.x, node_t0.y)
    node_exit = min(node_t1.x, node_t1.y)

    if node_entry > node_exit or node_exit < 0:
        return -1

    child_node_size = node_size / 2
    child_id = find_first_child(node_entry, ro, inv_ray_dir, node_pos + child_node_size)
    child_pos = node_pos + vec_mul(
        Vector2(child_id & 1, (child_id & 2) >> 1), child_node_size
    )
    child_node = qt.get_child(child_id)

    last_exit = node_exit
    node_stack = [None] * (start_height + 1)
    node_height = start_height
    node = qt

    while node_height <= start_height:
        child_t1 = vec_mul((child_pos + child_node_size - ro), inv_ray_dir)
        t_child_exit = min(child_t1.x, child_t1.y)
        child_node = node.get_child(child_id ^ child_id_flip)

        if child_node is not None:
            child_t0 = vec_mul((child_pos - ro), inv_ray_dir)
            t_child_entry = max(child_t0.x, child_t0.y)

            if not child_node.is_leaf:
                if t_child_exit < last_exit:
                    node_stack[node_height] = node

                last_exit = t_child_exit

                node_height -= 1
                node = child_node
                child_node_size /= 2

                child_id = find_first_child(
                    t_child_entry, ro, inv_ray_dir, child_pos + child_node_size
                )
                child_node = node.get_child(child_id)
                child_pos += vec_mul(
                    Vector2(child_id & 1, (child_id & 2) >> 1), child_node_size
                )

            else:
                return t_child_entry

        else:
            old_child_pos = child_pos.copy()
            flip_bits = 0

            if child_t1.x <= t_child_exit:
                flip_bits |= 1
                child_pos.x += child_node_size.x

            if child_t1.y <= t_child_exit:
                flip_bits |= 2
                child_pos.y += child_node_size.y

            child_id ^= flip_bits

            if (child_id & flip_bits) != flip_bits:
                differing_bits = 0
                differing_bits |= int(old_child_pos.x) ^ int(child_pos.x)
                differing_bits |= int(old_child_pos.y) ^ int(child_pos.y)
                msb = differing_bits.bit_length() - 1

                node_height = msb + 1

                if node_height > start_height:
                    break

                node = node_stack[node_height]

                if node is None:
                    break

                child_node_size = Vector2(1 << msb, 1 << msb)

                child_id = 0
                child_id |= int(child_pos.x) >> msb & 1
                child_id |= int(child_pos.y) >> (msb - 1) & 2

                old_child_pos = child_pos.copy()
                child_pos = Vector2(0, 0)
                child_pos.x = (int(old_child_pos.x) >> node_height) << node_height
                child_pos.y = (int(old_child_pos.y) >> node_height) << node_height

                child_pos += vec_mul(
                    Vector2(child_id & 1, (child_id & 2) >> 1), child_node_size
                )

                last_exit = 0.0

    return -1


def make_quadtree():
    qt = QuadTree(0, 0, 512, 512)
    qt.add_child(2).add_child(3, leaf=True)
    m = qt.add_child(1)
    m.add_child(3, leaf=True)
    m.add_child(0, leaf=True)

    m = qt.add_child(3)
    m.add_child(3).add_child(0, leaf=True)
    m.add_child(1, leaf=True)
    b = m.add_child(2).add_child(0)
    b.add_child(0, leaf=True)
    b.add_child(1).add_child(1, leaf=True)

    m = qt.add_child(0)
    m.add_child(1, leaf=True)

    return qt


def run_test():
    qt = make_quadtree()

    ray_start = Vector2(209, 545)
    ray_dir = Vector2(0.52, -0.85)

    t = quadtree_intersect(qt, ray_start, ray_dir)

    print("\n===== Test Results: =====\n")
    if t == -1:
        print("No intersection")
    else:
        print(t)


if __name__ == "__main__":
    run_test()
