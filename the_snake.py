import random

import pygame

# Константы с точными именами, которые требует тест
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
BOARD_BACKGROUND_COLOR = (0, 0, 0)

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Глобальные переменные (тест требует их наличия на уровне модуля)
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов."""

    # Добавляем значения по умолчанию, чтобы тест мог вызвать GameObject()
    def __init__(self, position=None, body_color=None):
        """Инициализирует позицию и цвет объекта."""
        self.position = position
        self.body_color = body_color

    def draw(self, surface):
        """Абстрактный метод для отрисовки объекта."""
        pass

    def draw_cell(self, surface, position, color):
        """Отрисовывает одну ячейку по указанным координатам и цвету."""
        rect = pygame.Rect(position[0], position[1], GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(surface, color, rect)


class Apple(GameObject):
    """Класс, описывающий яблоко."""

    # Добавляем значение по умолчанию для occupied_cells
    def __init__(self, occupied_cells=None):
        """Задаёт цвет яблока и устанавливает начальную позицию."""
        super().__init__(None, (255, 0, 0))
        self.randomize_position(occupied_cells)

    def randomize_position(self, occupied_cells=None):
        """Устанавливает случайное положение яблока на игровом поле."""
        if occupied_cells is None:
            occupied_cells = set()

        all_cells = {
            (x * GRID_SIZE, y * GRID_SIZE)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
        }
        free_cells = list(all_cells - occupied_cells)

        if free_cells:
            self.position = random.choice(free_cells)
        else:
            self.position = random.choice(list(all_cells))

    def draw(self, surface):
        """Отрисовывает яблоко на игровой поверхности."""
        self.draw_cell(surface, self.position, self.body_color)


class Snake(GameObject):
    """Класс, описывающий змейку и её поведение."""

    def __init__(self):
        """Инициализирует начальное состояние змейки."""
        start_pos = (
            SCREEN_WIDTH // 2 // GRID_SIZE * GRID_SIZE,
            SCREEN_HEIGHT // 2 // GRID_SIZE * GRID_SIZE,
        )
        super().__init__(start_pos, (0, 255, 0))
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
            head_x + dx * GRID_SIZE,
            head_y + dy * GRID_SIZE,
        )

        # Телепортация сквозь стены
        new_head = (new_head[0] % SCREEN_WIDTH, new_head[1] % SCREEN_HEIGHT)

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
            self.draw_cell(surface, self.last, BOARD_BACKGROUND_COLOR)

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        start_pos = (
            SCREEN_WIDTH // 2 // GRID_SIZE * GRID_SIZE,
            SCREEN_HEIGHT // 2 // GRID_SIZE * GRID_SIZE,
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

            if event.key == pygame.K_LEFT and snake.direction != RIGHT:
                snake.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and snake.direction != LEFT:
                snake.next_direction = RIGHT
            elif event.key == pygame.K_UP and snake.direction != DOWN:
                snake.next_direction = UP
            elif event.key == pygame.K_DOWN and snake.direction != UP:
                snake.next_direction = DOWN


def main():
    """Основной игровой цикл."""
    pygame.display.set_caption('Изгиб Питона')

    record_length = 1

    snake = Snake()
    # Создаем несколько яблок (как вы просили в начале)
    apples = [Apple(set(snake.positions)) for _ in range(3)]

    while True:
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        head_position = snake.get_head_position()

        if head_position in snake.positions[1:]:
            snake.reset()
            apples = [Apple(set(snake.positions)) for _ in range(3)]
            screen.fill(BOARD_BACKGROUND_COLOR)
            continue

        for apple in apples[:]:
            if head_position == apple.position:
                snake.grow()
                apples.remove(apple)
                occupied = set(snake.positions) | {a.position for a in apples}
                apples.append(Apple(occupied))
                if snake.length > record_length:
                    record_length = snake.length

        screen.fill(BOARD_BACKGROUND_COLOR)
        for apple in apples:
            apple.draw(screen)
        snake.draw(screen)

        title = f'Изгиб Питона | Рекорд: {record_length}'
        pygame.display.set_caption(title)
        pygame.display.update()
        clock.tick(5)


if __name__ == '__main__':
    main()
