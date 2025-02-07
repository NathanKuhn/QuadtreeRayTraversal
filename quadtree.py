class QuadTree:
    def __init__(self, x0, y0, x1, y1, leaf=False):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1

        self.is_leaf = leaf

        self.c0 = None
        self.c1 = None
        self.c2 = None
        self.c3 = None

    def get_child_dim(self, index):
        mx = (self.x0 + self.x1) / 2
        my = (self.y0 + self.y1) / 2

        if index == 0:
            return (self.x0, self.y0, mx, my)
        elif index == 1:
            return (mx, self.y0, self.x1, my)
        elif index == 2:
            return (self.x0, my, mx, self.y1)
        elif index == 3:
            return (mx, my, self.x1, self.y1)
        else:
            raise ValueError("Invalid index")

    def add_child(self, index, leaf=False):
        x0, y0, x1, y1 = self.get_child_dim(index)

        if index == 0:
            self.c0 = QuadTree(x0, y0, x1, y1, leaf=leaf)
            return self.c0

        elif index == 1:
            self.c1 = QuadTree(x0, y0, x1, y1, leaf=leaf)
            return self.c1

        elif index == 2:
            self.c2 = QuadTree(x0, y0, x1, y1, leaf=leaf)
            return self.c2

        elif index == 3:
            self.c3 = QuadTree(x0, y0, x1, y1, leaf=leaf)
            return self.c3

        else:
            raise ValueError("Invalid index")

    def get_child(self, index, shift=0):
        if index > 3:
            raise ValueError("Invalid index")

        index = (index + shift) % 4
        if index == 0:
            return self.c0
        elif index == 1:
            return self.c1
        elif index == 2:
            return self.c2
        else:
            return self.c3

    def contains_point(self, x, y):
        return self.x0 <= x < self.x1 and self.y0 <= y < self.y1

    def get_child_from_point(self, x, y):
        if not self.contains_point(x, y):
            return None

        mx = (self.x0 + self.x1) / 2
        my = (self.y0 + self.y1) / 2

        if x < mx:
            if y < my:
                return self.c0
            else:
                return self.c2
        else:
            if y < my:
                return self.c1
            else:
                return self.c3

    def __str__(self):
        return (
            f"QuadTree({self.x0}, {self.y0}, {self.x1}, {self.y1}, leaf={self.is_leaf})"
        )

    def __repr__(self):
        return str(self)
