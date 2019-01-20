import math
import pygame
import random

SCREEN_DIM = (800, 600)


class Vec2d:
    def __init__(self, x, y=None):
        if y is None and len(x) == 2:
            self.vector = tuple(x)
        elif len(x) == 2 and len(y) == 2:
            self.vector = (x[0] - y[0], x[1] - y[1])
        else:
            raise ValueError(f'Input must be 2-D array(s), but x={x}, y={y}')

    def __getitem__(self, key):
        if key in [0, 1]:
            return self.vector[key]
        else:
            raise KeyError(f'In {key}, but must be key 0 or 1')

    def __add__(self, other):
        return Vec2d([self[0] + other[0],
                      self[1] + other[1]])

    def __sub__(self, other):
        return Vec2d([self[0] - other[0],
                      self[1] - other[1]])

    def __len__(self):
        return int(math.sqrt(self[0] * self[0] +
                             self[1] * self[1]))

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Vec2d([self[0] * other,
                          self[1] * other])
        if isinstance(other, (list, tuple,)):
            return (self[0] * other[0] +
                    self[1] * other[1])

    def int_pair(self):
        return (int(self[0]),
                int(self[1]))


class Polyline:

    def __init__(self, points=None, speeds=None):
        if points is None and speeds is None:
            self.points = []
            self.speeds = []
        else:
            self.points = points
            self.speeds = speeds

    def append(self, point, speed):
        point = Vec2d(point)
        speed = Vec2d(speed)
        self.points.append(point)
        self.speeds.append(speed)

    def set_points(self):
        ln = len(self.points)
        for p in range(ln):
            self.points[p] += self.speeds[p]
            check_h = (self.points[p][0] > SCREEN_DIM[0] or
                       self.points[p][0] < 0)
            if check_h:
                self.speeds[p] = (-self.speeds[p][0],
                                  self.speeds[p][1])

            check_w = (self.points[p][1] > SCREEN_DIM[1] or
                       self.points[p][1] < 0)
            if check_w:
                self.speeds[p] = (self.speeds[p][0],
                                  -self.speeds[p][1])

    def draw_points(self, width=3, color=None):
        color = color or (255, 255, 255)
        for p in self.points:
            pygame.draw.circle(gameDisplay,
                               color,
                               p.int_pair(),
                               width)


class Knot(Polyline):

    def __init__(self, points=None, speeds=None, steps=35, hue=0):
        super(Knot, self).__init__(points, speeds)
        self.steps = steps
        self.curve = []
        self.hue = hue
        self.color = pygame.Color(0)

    def get_point(self, base_points, alpha, deg=None):
        if deg is None:
            deg = len(base_points) - 1
        if deg == 0:
            return base_points[0]
        return ((base_points[deg] * alpha) +
                (self.get_point(base_points, alpha, deg - 1) * (1 - alpha)))

    def get_points(self, base_points, count):

        alpha = 1 / count
        res = []
        for i in range(count):
            res.append(self.get_point(base_points, i * alpha))
        return res

    def get_knot(self):
        if len(self.points) < 3:
            self.curve = []
            return
        self.curve = []
        for i in range(-2, len(self.points) - 2):
            ptn = list()
            ptn.append((self.points[i] + self.points[i + 1]) * 0.5)
            ptn.append(self.points[i + 1])
            ptn.append((self.points[i + 1] + self.points[i + 2]) * 0.5)
            self.curve.extend(self.get_points(ptn, self.steps))

    def set_points(self):
        super(Knot, self).set_points()
        self.get_knot()

    def append(self, point, speed):
        super(Knot, self).append(point, speed)
        self.get_knot()

    def draw_points(self, width=3, color=None):
        super(Knot, self).draw_points(width=width, color=color)
        self.hue = (self.hue + 1) % 360
        self.color.hsla = (self.hue, 100, 50, 100)
        color = color or self.color
        ln = len(self.curve)
        for p_n in range(-1, ln - 1):
            pygame.draw.line(gameDisplay,
                             color,
                             self.curve[p_n].int_pair(),
                             self.curve[p_n + 1].int_pair(),
                             width)


def draw_help(steps):
    gameDisplay.fill((50, 50, 50))
    font1 = pygame.font.SysFont("courier", 24)
    font2 = pygame.font.SysFont("serif", 24)
    data = list()
    data.append(["F1", "Show Help"])
    data.append(["R", "Restart"])
    data.append(["P", "Pause/Play"])
    data.append(["Num+", "More points"])
    data.append(["Num-", "Less points"])
    data.append(["", ""])
    data.append([str(steps), "Current points"])

    pygame.draw.lines(gameDisplay, (255, 50, 50, 255), True, [
                      (0, 0), (800, 0), (800, 600), (0, 600)], 5)
    for i, text in enumerate(data):
        gameDisplay.blit(font1.render(
            text[0], True, (128, 128, 255)), (100, 100 + 30 * i))
        gameDisplay.blit(font2.render(
            text[1], True, (128, 128, 255)), (200, 100 + 30 * i))


if __name__ == "__main__":
    pygame.init()
    gameDisplay = pygame.display.set_mode(SCREEN_DIM)
    pygame.display.set_caption("MyScreenSaver")

    working = True
    pnts_knot = Knot()
    show_help = False
    pause = True

    while working:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                working = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    working = False
                if event.key == pygame.K_r:
                    pnts_knot = Knot()
                if event.key == pygame.K_p:
                    pause = not pause
                if event.key == pygame.K_KP_PLUS:
                    pnts_knot.steps += 1
                if event.key == pygame.K_F1:
                    show_help = not show_help
                if event.key == pygame.K_KP_MINUS:
                    pnts_knot.steps -= 1 if pnts_knot.steps > 1 else 1

            if event.type == pygame.MOUSEBUTTONDOWN:
                pnts_knot.append(event.pos,
                                 (random.random() * 2, random.random() * 2))

        gameDisplay.fill((0, 0, 0))
        pnts_knot.draw_points()
        if not pause:
            pnts_knot.set_points()
        if show_help:
            draw_help(pnts_knot.steps)

        pygame.display.flip()

    pygame.display.quit()
    pygame.quit()
    exit(0)
