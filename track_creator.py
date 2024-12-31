import pygame
import sys

WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
FPS = 60

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Track Creator")
clock = pygame.time.Clock()

outer_walls = []
inner_walls = []
car_start = None

MODES = ["outer", "inner", "start"]
current_mode = 0


def save_to_file():
    """Save the track data to a Python file."""
    def close_loop(points):
        """Ensure the last point connects to the first."""
        if len(points) > 1 and points[-1] != points[0]:
            points.append(points[0])
    
    close_loop(outer_walls)
    close_loop(inner_walls)
    
    with open("track_output.py", "w") as file:
        file.write("outer_walls = [\n")
        for point in outer_walls:
            file.write(f"    {point},\n")
        file.write("]\n\n")
        
        file.write("inner_walls = [\n")
        for point in inner_walls:
            file.write(f"    {point},\n")
        file.write("]\n\n")
        
        if car_start:
            file.write(f"car_start = {car_start}\n")
        else:
            file.write("car_start = None\n")
    print("Track saved to track_output.py")


def draw_points(points, color):
    """Draw points and lines connecting them."""
    if len(points) > 1:
        pygame.draw.lines(screen, color, False, points, 2)  # False ensures no auto-closure during drawing
    for point in points:
        pygame.draw.circle(screen, color, point, 5)


running = True
while running:
    screen.fill(WHITE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if current_mode == 0:  # Outer walls
                outer_walls.append(event.pos)
            elif current_mode == 1:  # Inner walls
                inner_walls.append(event.pos)
            elif current_mode == 2:  # Car start
                car_start = event.pos
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:  # Switch mode
                current_mode = (current_mode + 1) % len(MODES)
            elif event.key == pygame.K_s:  # Save and exit
                save_to_file()
                running = False
            elif event.key == pygame.K_c:  # Clear all points
                outer_walls.clear()
                inner_walls.clear()
                car_start = None

    draw_points(outer_walls, RED)
    draw_points(inner_walls, GREEN)
    if car_start:
        pygame.draw.circle(screen, BLUE, car_start, 8)

    font = pygame.font.SysFont(None, 36)
    mode_text = font.render(f"Mode: {MODES[current_mode]}", True, BLACK)
    screen.blit(mode_text, (10, 10))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
