import numpy as np
import pygame
import math
import csv
import os

from lite import LiteModel

pygame.init()

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Car properties
CAR_WIDTH = 10
CAR_HEIGHT = 20
CAR_MAX_SPEED = 5
CAR_ACC = 0.02
ROTATION_SPEED = 1
SENSOR_LENGTH = 300

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Car learns to drive")
clock = pygame.time.Clock()

class Car:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0  # Angle in degrees
        self.rect = pygame.Rect(x, y, CAR_WIDTH, CAR_HEIGHT)
        self.speed = 0
        self.moving = False  # flag for space bar control
        
    def move(self, up, left, right, down):
        if not self.moving: 
            return
            
        if left:
            self.angle -= ROTATION_SPEED
        if right:
            self.angle += ROTATION_SPEED
        
        self.speed += CAR_ACC if up else -CAR_ACC if down else 0
        self.speed = max(0, min(self.speed, CAR_MAX_SPEED)) # Clamp speed

        # Move forward in the direction we're facing
        rad = math.radians(self.angle)
        self.x += math.sin(rad) * self.speed
        self.y -= math.cos(rad) * self.speed
        
        self.rect.center = (self.x, self.y)
        
    def draw(self, surface):
        car_surface = pygame.Surface((CAR_WIDTH, CAR_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(car_surface, RED, (0, 0, CAR_WIDTH, CAR_HEIGHT))
        
        rotated_surface = pygame.transform.rotate(car_surface, -self.angle)
        # Get the new rect for the rotated surface
        rotated_rect = rotated_surface.get_rect(center=(self.x, self.y))
        
        # Draw the rotated surface
        surface.blit(rotated_surface, rotated_rect)
        
    def get_corners(self):
        """Get the four corners of the rotated rectangle"""
        rad = math.radians(self.angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        half_width = CAR_WIDTH / 2
        half_height = CAR_HEIGHT / 2
        
        corners = []
        for xm, ym in [(-half_width, -half_height), 
                      (half_width, -half_height),
                      (half_width, half_height),
                      (-half_width, half_height)]:
            x = self.x + (xm * cos_a - ym * sin_a)
            y = self.y + (xm * sin_a + ym * cos_a)
            corners.append((x, y))
        return corners

class Track:
    def __init__(self, name):

        if name is None:
            name = "track1"

        import importlib
        tr = importlib.import_module(f"tracks.{name}")
        
        self.outer_walls = tr.outer_walls

        self.inner_walls = tr.inner_walls

        self.car_start = tr.car_start

    def draw(self, surface):
        pygame.draw.lines(surface, WHITE, True, self.outer_walls, 2)
        pygame.draw.lines(surface, WHITE, True, self.inner_walls, 2)
        
    def get_walls(self):
        walls = []
        for i in range(len(self.outer_walls)-1):
            walls.append((self.outer_walls[i], self.outer_walls[i+1]))
        for i in range(len(self.inner_walls)-1):
            walls.append((self.inner_walls[i], self.inner_walls[i+1]))
        return walls
        
    def check_collision(self, car):
        """Check if car collides with any wall"""
        car_corners = car.get_corners()
        
        # Check each car edge against each wall
        for i in range(len(car_corners)):
            car_p1 = car_corners[i]
            car_p2 = car_corners[(i + 1) % 4]
            
            for wall in self.get_walls():
                if get_intersection(car_p1, car_p2, wall[0], wall[1]):
                    return True
        return False

def get_intersection(p1, p2, p3, p4):
    """Return intersection point of two line segments if it exists"""
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4
    
    denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if denominator == 0:
        return None
        
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denominator
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denominator
    
    if 0 <= t <= 1 and 0 <= u <= 1:
        x = x1 + t * (x2 - x1)
        y = y1 + t * (y2 - y1)
        return (x, y)
    return None

def get_sensor_distances(car, track, surface=None):
    """Get distances to walls for front, left and right sensors"""
    angles = [0, -15, 15, -30, 30, -45, 45, -60, 60, -75, 75, -90, 90]  # Sensor angles relative to car
    distances = []
    
    for angle in angles:
        # Calculate sensor end point
        sensor_angle = math.radians(car.angle + angle)
        sensor_x = car.x + math.sin(sensor_angle) * SENSOR_LENGTH
        sensor_y = car.y - math.cos(sensor_angle) * SENSOR_LENGTH
        
        # Find closest intersection with walls
        min_dist = SENSOR_LENGTH
        closest_point = (sensor_x, sensor_y)
        
        for wall in track.get_walls():
            intersection = get_intersection(
                (car.x, car.y),
                (sensor_x, sensor_y),
                wall[0],
                wall[1]
            )
            
            if intersection:
                dist = math.sqrt(
                    (car.x - intersection[0])**2 + 
                    (car.y - intersection[1])**2
                )
                if dist < min_dist:
                    min_dist = dist
                    closest_point = intersection
        
        if surface:  # Draw sensor lines if surface is provided
            pygame.draw.line(surface, GREEN, (car.x, car.y), closest_point, 2)
        
        distances.append(min_dist)
    
    return distances

def main():
    track_num = 5
    track = Track("track5")
    car = Car(*track.car_start)

    recording = False
    data = []
    game_over = False
    nn_running = False
    nn_model = LiteModel('model.tflite')

    show_sensors = False


    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    recording = not recording
                    if not recording and data:  # Save data when stopping recording
                        with open('racing_data.csv', 'w', newline='') as f:
                            writer = csv.writer(f)
                            writer.writerow(['speed', 'dist_front', 'dist_left_15', 'dist_right_15','dist_left_30', 'dist_right_30','dist_left_45', 'dist_right_45', 'dist_left_60', 'dist_right_60', 'dist_left_75', 'dist_right_75', 'dist_left_90', 'dist_right_90', 'left_pressed', 'right_pressed', 'down_pressed', 'up_pressed'])
                            writer.writerows(data)
                        print("Data saved to racing_data.csv")
                        data = []
                elif event.key == pygame.K_n:
                    nn_running = not nn_running
                elif event.key == pygame.K_s:
                    show_sensors = not show_sensors
                elif event.key == pygame.K_SPACE:
                    car.moving = not car.moving
                elif event.key == pygame.K_TAB:
                    track_num = ((track_num) % (len(os.listdir('tracks')) - 1)) + 1
                    track = Track(f"track{track_num}")
                    car = Car(*track.car_start)
                elif event.key == pygame.K_RETURN and game_over:  # Reset game
                    car = Car(*track.car_start)
                    game_over = False
        
        if not game_over:
            distances = get_sensor_distances(car, track)

            if not nn_running:
                keys = pygame.key.get_pressed()
                up_pressed = keys[pygame.K_UP]
                left_pressed = keys[pygame.K_LEFT]
                right_pressed = keys[pygame.K_RIGHT]
                down_pressed = keys[pygame.K_DOWN]
            else:
                input_data = np.array([[car.speed, *distances]])
                input_data[:, 1:] = input_data[:, 1:] / SENSOR_LENGTH  # Normalize input data

                predictions = nn_model.predict(input_data, verbose = 0)
                left_pressed = predictions[0][0] > 0.5
                right_pressed = predictions[0][1] > 0.5
                down_pressed = predictions[0][2] > 0.5
                up_pressed = predictions[0][3] > 0.5

            car.move(up_pressed, left_pressed, right_pressed, down_pressed)
            
            if track.check_collision(car):
                game_over = True
                car.moving = False
            
            if recording:
                data.append([
                    car.speed,
                    *distances,
                    int(left_pressed),
                    int(right_pressed),
                    int(down_pressed),
                    int(up_pressed)
                ])
        
        screen.fill(BLACK)
        track.draw(screen)        
        # Draw sensors
        get_sensor_distances(car, track, screen if show_sensors else None)
                
        car.draw(screen)

        # Draw track number on top right
        font = pygame.font.Font(None, 24)
        text = font.render(f"Track: {track_num}", True, WHITE)
        speed_text = font.render(f"Speed: {car.speed:.2f}", True, WHITE)
        screen.blit(speed_text, (WINDOW_WIDTH - 100, 40))
        screen.blit(text, (WINDOW_WIDTH - 100, 10))

        if recording:
            pygame.draw.circle(screen, RED, (30, 30), 10)

        if nn_running:
            pygame.draw.circle(screen, GREEN, (30, 60), 10)
            font = pygame.font.Font(None, 36)
            text = font.render(f'Left: {predictions[0][0]:.2f}, Right: {predictions[0][1]:.2f}, Brake: {predictions[0][2]:.2f}, Accel: {predictions[0][3]:.2f}', True, WHITE)
            screen.blit(text, (10, 10))


        # Draw game over message
        if game_over:
            font = pygame.font.Font(None, 74)
            text = font.render('Game Over!', True, RED)
            text_rect = text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
            screen.blit(text, text_rect)
            
            font = pygame.font.Font(None, 36)
            text = font.render('Press ENTER to restart', True, WHITE)
            text_rect = text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 50))
            screen.blit(text, text_rect)
        elif not car.moving:
            font = pygame.font.Font(None, 42)
            text = font.render('Press SPACE to start', True, RED)
            text_rect = text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
            screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()