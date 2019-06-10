import math
import random
import settings
import pygame
import colors

STEPS = [
    (0,  -1), (0,  1),
    (-1,  0), (1,  0),
    (-1, -1), (1,  1),
    (-1,  1), (1, -1),
]

class PathPoint:
    def __init__(self, x, y, parent=None):
        self.x = x
        self.y = y
        self.parent = parent

    @property
    def pos(self):
        return (x,y)

    @property
    def rect(self):
        return pygame.Rect(
            self.x, self.y,
            20, 20
        )

    def __str__(self):
        return f"Point({self.x}, {self.y})"

    def __repr__(self):
        return self.__str__()

class Block(pygame.sprite.Sprite):
    color = colors.WHITE
    size = 50

    def __init__(self, x,y):
        self.width = self.size
        self.height = self.size
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        super().__init__()

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    @property
    def x(self):
        return self.rect.x

    @x.setter
    def x(self, value):
        self.rect.x = value

    @property
    def y(self):
        return self.rect.y

    @y.setter
    def y(self, value):
        self.rect.y = value

    @property
    def pos(self):
        return (self.rect.x, self.rect.y)

    def __str__(self):
        return f'Block({self.x},{self.y})'

    def __repr__(self):
        return f'Block({self.x},{self.y})'

class Target(Block):
    color = colors.GREEN
    size = 20

class Player(Block):
    color = colors.RED
    speed = 3
    size = 20

    def __init__(self, x, y):
        super().__init__(x, y)
        self.manual = True
        self.target = None
        self.path = []

    def move(self, keys, obstacles):
        new_x, new_y = self.x, self.y
        if keys[pygame.K_s]:
            new_y = self.y + self.speed
        if keys[pygame.K_a]:
            new_x = self.x - self.speed
        if keys[pygame.K_d]:
            new_x = self.x + self.speed
        if keys[pygame.K_w]:
            new_y = self.y - self.speed

        if self.validate_new_pos(new_x, new_y, obstacles):
            self.x = new_x
            self.y = new_y

    def validate_new_pos(self, x, y, obstacles):
        out_of_bounds = self.check_bounds(x, y)
        colliding = self.check_collisions(x, y, obstacles)

        if not colliding and not out_of_bounds:
            return True
        return False


    def check_bounds(self, x, y):
        max_x = settings.WIDTH - self.size
        max_y = settings.HEIGHT - self.size
        if x < 0 or x > max_x or y < 0 or y > max_y:
            return True
        return False

    def check_collisions(self, x, y, obstacles):
        new_pos_rect = pygame.Rect(x, y, self.rect.width, self.rect.height)
        for obstacle in obstacles:
            collision = new_pos_rect.colliderect(obstacle.rect)
            if collision:
                return True
        return False


    def update(self, *args):
        keys = args[0]
        toggle_manual = args[1]
        obstacles = args[2] or []

        if toggle_manual:
            self.manual = not self.manual

        if self.manual and keys:
            self.path = []
            self.move(keys, obstacles)

        if not self.manual and self.target:
            self.pathfind(obstacles)

    def distance_from_target(self, x, y):
        return ((self.target.x - x)**2 + (self.target.y - y)**2)**0.5

    def pathfind(self, obstacles):

        if self.path:
            point = self.path.pop(0)
            self.x = point.x
            self.y = point.y
            return

        visited = set([])
        start = PathPoint(self.x, self.y)
        searching = [start]
        while searching:

            current = searching.pop(0)

            if current.rect.colliderect(self.target.rect):
                self.path = []
                while current is not start:
                    self.path.append(current)
                    current = current.parent
                self.path = list(reversed(self.path))
                return

            for step_x, step_y in STEPS:
                dx, dy = step_x * self.speed, step_y * self.speed
                new_x, new_y = current.x + dx, current.y + dy

                if (new_x, new_y) in visited:
                    continue

                if not self.validate_new_pos(new_x, new_y, obstacles):
                    continue

                visited.add((new_x, new_y))

                newPoint = PathPoint(new_x, new_y, parent=current)
                searching.append(newPoint)

def play():
    pygame.init()
    pygame.font.init()

    screen = pygame.display.set_mode(settings.SCREEN_SIZE)
    pygame.display.set_caption("pathfinder")

    running = True
    clock = pygame.time.Clock()

    blocks = pygame.sprite.Group()
    player = Player(0,0)
    target = Target(settings.WIDTH - 20, settings.HEIGHT - 20)
    player.target = target

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                x -= x % Block.size
                y -= y % Block.size
                potential = Block(x,y)
                collisions = pygame.sprite.spritecollide(potential, blocks, True)
                if not collisions:
                    blocks.add(potential)

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                player.update(None, True, blocks)

        player.update(pygame.key.get_pressed(), None, blocks)

        screen.fill(colors.BLACK)

        player.draw(screen)
        target.draw(screen)

        blocks.draw(screen)

        pygame.display.flip()
        clock.tick(settings.FPS)

if __name__ == '__main__':
    play()
