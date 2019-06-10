import random
import settings
import pygame
import colors

class Cell:
    def __init__(self, x,y,size):
        self.x = x
        self.y = y
        self.pos = (x,y)
        self.width = size
        self.height = size
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(colors.WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        self.neighbours = []
        self.walls = [1,1,1,1]
        self.wall_thickness = max(size // 10, 1)
        self.occupied = False
        self.traversed = False

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        if self.walls[0]: # N
            pygame.draw.rect(
                surface,
                colors.GREY,
                (self.x, self.y, self.width, self.wall_thickness)
            )
        if self.walls[1]: # S
            pygame.draw.rect(
                surface,
                colors.GREY,
                (self.x, self.y + self.height - self.wall_thickness, self.width, self.wall_thickness)
            )
        if self.walls[2]: # E
            pygame.draw.rect(
                surface,
                colors.GREY,
                (self.x + self.width - self.wall_thickness, self.y, self.wall_thickness, self.height)
            )
        if self.walls[3]: # W
            pygame.draw.rect(
                surface,
                colors.GREY,
                (self.x, self.y, self.wall_thickness, self.height)
            )

        if self.traversed:
            r = pygame.Rect(0,0, self.width // 2,  self.height // 2)
            r.center = (self.x + self.width // 2, self.y + self.height // 2)

            pygame.draw.rect(
                surface,
                colors.BLUE,
                r
            )

        if self.occupied:
            r = pygame.Rect(0,0, self.width // 2,  self.height // 2)
            r.center = (self.x + self.width // 2, self.y + self.height // 2)

            pygame.draw.rect(
                surface,
                colors.RED,
                r
            )

    def remove_walls(self, other):
        if self.x < other.x and self.y == other.y:
            self.walls[2] = 0
            other.walls[3] = 0
        if self.y < other.y and self.x == other.x:
            self.walls[1] = 0
            other.walls[0] = 0
        if self.x > other.x and self.y == other.y:
            self.walls[3] = 0
            other.walls[2] = 0
        if self.y > other.y and self.x == other.x:
            self.walls[0] = 0
            other.walls[1] = 0



    def __str__(self):
        return f'Cell({self.x},{self.y})'

    def __repr__(self):
        return f'Cell({self.x},{self.y})'



class Walker:
    def __init__(self):
        self.current_cell = None
        self.path = []
        self.walking = False

    def walk_to(self, cell):
        self.current_cell.remove_walls(cell)
        if self.current_cell:
            self.current_cell.occupied = False

        self.current_cell = cell

        self.current_cell.occupied = True
        self.current_cell.traversed = True
        self.path.append(cell)

    def walk_back(self):
        if self.path:
            step_back = self.path.pop()
            self.current_cell.occupied = False
            self.current_cell = step_back
            self.current_cell.occupied = True
            return True
        return False


    def walk(self):
        neighbours = [n for n in self.current_cell.neighbours if not n.traversed]
        if neighbours:
            cell = random.choice(neighbours)
            self.walk_to(cell)
        else:
            if not self.walk_back():
                return False
        return True

    def pause(self):
        self.walking = False

    def unpause(self):
        self.walking = True

    def set_start(self, start):
        self.current_cell = start
        start.occupied = True
        start.traversed = True


def play():
    pygame.init()
    pygame.font.init()

    screen = pygame.display.set_mode(settings.SCREEN_SIZE)
    pygame.display.set_caption("a-maze-ing")

    running = True
    clock = pygame.time.Clock()

    size = 20
    cells = {}
    num_rows = settings.SCREEN_SIZE[0] // size
    num_cols = settings.SCREEN_SIZE[1] // size
    for i in range(num_rows):
        for j in range(num_cols):
            cell = Cell(i*size,j*size,size)
            cells[cell.pos] = cell

    for (x,y), cell in cells.items():
        neighbour_pos = [
            (x - size, y),
            (x + size, y),
            (x, y - size),
            (x, y + size),
        ]
        for pos in neighbour_pos:
            if pos in cells:
                cell.neighbours.append(cells[pos])

    starting_cell = random.choice(list(cells.values()))

    wally = Walker()
    wally.walking = False
    wally.set_start(starting_cell)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if wally.walking:
                    wally.pause()
                else:
                    wally.unpause()


        if wally.walking:
            walked = wally.walk()

            if not walked:
                for cell in cells.values():
                    cell.traversed = False
                wally.walking = False

        screen.fill(colors.BLACK)

        for cell in cells.values():
            cell.draw(screen)

        pygame.display.flip()
        clock.tick(settings.FPS)

if __name__ == '__main__':
    play()
