import random

import pygame

CELL_SIZE = 20
CELLS_X = 32
CELLS_Y = 24
WIDTH = CELL_SIZE * CELLS_X
HEIGHT = CELL_SIZE * CELLS_Y

BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

LEFT = (-1, 0)
RIGHT = (1, 0)
UP = (0, -1)
DOWN = (0, 1)

DIRECTION_MAP = {
    (pygame.K_LEFT, RIGHT): RIGHT,
    (pygame.K_RIGHT, LEFT): LEFT,
    (pygame.K_UP, DOWN): DOWN,
    (pygame.K_DOWN, UP): UP,
    (pygame.K_LEFT, UP): LEFT,
    (pygame.K_LEFT, DOWN): LEFT,
    (pygame.K_RIGHT, UP): RIGHT,
    (pygame.K_RIGHT, DOWN): RIGHT,
    (pygame.K_UP, LEFT): UP,
    (pygame.K_UP, RIGHT): UP,
    (pygame.K_DOWN, LEFT): DOWN,
    (pygame.K_DOWN, RIGHT): DOWN,
}

ALL_CELLS = {
    (x * CELL_SIZE, y * CELL_SIZE)
    for x in range(CELLS_X)
    for y in range(CELLS_Y)
}


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, position, body_color):
        """Инициализирует позицию и цвет объекта."""
        self.position = position
        self.body_color = body_color

    def draw(self, surface):
        """Абстрактный метод для отрисовки объекта."""
        pass

    def draw_cell(self, surface, position, color):
        """Отрисовывает одну ячейку по указанным координатам и цвету."""
        rect = pygame.Rect(position[0], position[1], CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, color, rect)


class Apple(GameObject):
    """Класс, описывающий яблоко."""

    def __init__(self, occupied_cells):
        """Задаёт цвет яблока и устанавливает начальную позицию."""
        super().__init__(None, RED)
        self.randomize_position(occupied_cells)

    def randomize_position(self, occupied_cells):
        """Устанавливает случайное положение яблока на игровом поле."""
        free_cells = list(ALL_CELLS - occupied_cells)
        if free_cells:
            self.position = random.choice(free_cells)
        else:
            self.position = random.choice(list(ALL_CELLS))

    def draw(self, surface):
        """Отрисовывает яблоко на игровой поверхности."""
        self.draw_cell(surface, self.position, self.body_color)


class Snake(GameObject):
    """Класс, описывающий змейку и её поведение."""

    def __init__(self):
        """Инициализирует начальное состояние змейки."""
        start_pos = (
            WIDTH // 2 // CELL_SIZE * CELL_SIZE,
            HEIGHT // 2 // CELL_SIZE * CELL_SIZE,
        )
        super().__init__(start_pos, GREEN)
        self.length = 1
        self.positions = [start_pos]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def update_direction(self):
        """Обновляет направление движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Обновляет позицию змейки, добавляя новую голову."""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        new_head = (
            head_x + dx * CELL_SIZE,
            head_y + dy * CELL_SIZE,
        )

        new_head = (new_head[0] % WIDTH, new_head[1] % HEIGHT)

        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self, surface):
        """Отрисовывает все сегменты змейки на экране."""
        for position in self.positions:
            self.draw_cell(surface, position, self.body_color)

        if self.last:
            self.draw_cell(surface, self.last, BLACK)

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        start_pos = (
            WIDTH // 2 // CELL_SIZE * CELL_SIZE,
            HEIGHT // 2 // CELL_SIZE * CELL_SIZE,
        )
        self.length = 1
        self.positions = [start_pos]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def grow(self):
        """Увеличивает длину змейки на один сегмент."""
        self.length += 1


def handle_keys(snake):
    """Обрабатывает нажатия клавиш для смены направления."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit

            new_direction = DIRECTION_MAP.get(
                (event.key, snake.direction)
            )
            if new_direction:
                snake.next_direction = new_direction


def main():
    """Основной игровой цикл."""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Изгиб Питона')
    clock = pygame.time.Clock()

    record_length = 1

    snake = Snake()
    apples = [Apple(set(snake.positions)) for _ in range(3)]

    while True:
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        head_position = snake.get_head_position()

        if head_position in snake.positions[1:]:
            snake.reset()
            apples = [Apple(set(snake.positions)) for _ in range(3)]
            screen.fill(BLACK)
            continue

        for apple in apples[:]:
            if head_position == apple.position:
                snake.grow()
                apples.remove(apple)
                occupied = set(snake.positions) | {
                    a.position for a in apples
                }
                apples.append(Apple(occupied))
                if snake.length > record_length:
                    record_length = snake.length

        screen.fill(BLACK)
        for apple in apples:
            apple.draw(screen)
        snake.draw(screen)

        title = f'Изгиб Питона | Рекорд: {record_length}'
        pygame.display.set_caption(title)
        pygame.display.update()
        clock.tick(5)


if __name__ == '__main__':
    main()

    