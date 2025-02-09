import pygame
from pygame.math import Vector2
from quadtree import QuadTree
from intersect import quadtree_intersect, make_quadtree


def r(x, y, w, h):
    return x, 612 - y - h, w, h


def p(x, y):
    return x, 612 - y


def main():
    # Create a quadtree
    qt = make_quadtree()

    ray_start = Vector2(-10, 5)
    ray_dir = Vector2(0.4, 0.9)

    t = quadtree_intersect(qt, ray_start, ray_dir)

    # Create a display
    pygame.init()
    screen = pygame.display.set_mode((612, 612))
    pygame.display.set_caption("Quadtree")

    # Main loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    print(ray_start, ray_dir)
                    return

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mpos = p(*pygame.mouse.get_pos())
                    ray_start = Vector2(mpos[0] - 50, mpos[1] - 50)

        # Change the ray
        mpos = p(*pygame.mouse.get_pos())
        ray_dir = Vector2(mpos[0] - 50, mpos[1] - 50) - ray_start
        if ray_dir != Vector2(0, 0):
            ray_dir.normalize_ip()
        else:
            ray_dir = Vector2(0, 1)

        t = quadtree_intersect(
            qt,
            Vector2(ray_start.x, ray_start.y),
            Vector2(ray_dir.x, ray_dir.y),
        )

        if t < 0:
            t = 1000

        ray_end = ray_start + ray_dir * t

        # Draw everything
        screen.fill((0, 0, 0))

        stack = [qt]
        while len(stack) > 0:
            node = stack.pop()

            if node.is_leaf:
                pygame.draw.rect(
                    screen,
                    (0, 255, 0),
                    r(50 + node.x0, 50 + node.y0, node.x1 - node.x0, node.y1 - node.y0),
                )

            pygame.draw.rect(
                screen,
                (255, 255, 255),
                r(50 + node.x0, 50 + node.y0, node.x1 - node.x0, node.y1 - node.y0),
                1,
            )

            if node.is_leaf:
                continue

            if node.c0 is not None:
                stack.append(node.c0)
            if node.c1 is not None:
                stack.append(node.c1)
            if node.c2 is not None:
                stack.append(node.c2)
            if node.c3 is not None:
                stack.append(node.c3)

        pygame.draw.line(
            screen,
            (255, 0, 0),
            p(50 + ray_start[0], 50 + ray_start[1]),
            p(50 + ray_end[0], 50 + ray_end[1]),
            1,
        )
        pygame.draw.circle(
            screen, (255, 0, 0), p(50 + ray_start[0], 50 + ray_start[1]), 5
        )
        pygame.draw.circle(screen, (255, 0, 0), p(50 + ray_end[0], 50 + ray_end[1]), 5)

        pygame.display.flip()


if __name__ == "__main__":
    main()
