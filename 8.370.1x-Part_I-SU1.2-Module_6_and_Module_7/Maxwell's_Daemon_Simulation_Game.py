import math

import pygame
import random
from typing import Literal

# --------------------------------------------------
# CONFIGURATIONS

side_of_hot_molecules = "RIGHT" # You can also set this to "LEFT"

faster_particles = False
thinner_wall_display = False
smaller_particles_display = False

temperature_dependant_particle_speeds = False
even_hot_and_cold_distribution = False

door_size_string = "Normal" # "Normal", "Small", "Large", "Full Size"
particle_amount = 20 # 20, 10
# --------------------------------------------------

class Molecule:
    def __init__(self, dir, vel, temp: Literal["HOT", "COLD"], x, y):
        self.dir = dir
        self.vel = vel
        self.temp = temp
        self.x = x
        self.y = y

        self.radius = 10
        if smaller_particles_display:
            self.radius = 5

        if temperature_dependant_particle_speeds:
            if self.temp == "HOT":
                self.vel = random.gauss(mean_speed + 1, 1)
            else:
                self.vel = random.gauss(mean_speed - 1, 1)

    def move(self, walls):
        new_x = self.x + math.cos(self.dir) * self.vel
        new_y = self.y + math.sin(self.dir) * self.vel

        for wall in walls:
            if wall.passed_through((self.x, self.y, new_x, new_y)):
                new_x, new_y = wall.reflect(new_x, new_y)
                self.dir = wall.redirect(self.dir)

        self.x = new_x
        self.y = new_y

    def display(self):
        if self.temp == "HOT":
            pygame.draw.circle(screen, "red", (self.x, self.y), self.radius)
        else:
            pygame.draw.circle(screen, "blue", (self.x, self.y), self.radius)

class Wall:
    roughness = 0.05

    def __init__(self, x, y, length, orientation: Literal["HORIZONTAL", "VERTICAL"]):
        self.x = x
        self.y = y
        self.length = length
        self.orientation = orientation

        self.width = 20
        if thinner_wall_display:
            self.width = 10

    def passed_through(self, distance_tuple):

        x_initial, y_initial, x_final, y_final = distance_tuple
        
        if self.orientation == "HORIZONTAL":   
            if y_initial == y_final:
                return False        
                   
            if (y_initial - self.y) * (y_final - self.y) < 0:
                cotan = (x_initial - x_final) / (y_initial - y_final)
                intercept_x = x_initial + cotan * (self.y - y_initial)

                if 0 <= intercept_x - self.x < self.length:
                    return True
                
        else: 
            if x_initial == x_final:
                return False     

            if (x_initial - self.x) * (x_final - self.x) < 0:
                tan = (y_initial - y_final) / (x_initial - x_final)
                intercept_y = y_initial + tan * (self.x - x_initial)

                if 0 <= intercept_y - self.y < self.length:
                    return True
                
        return False

    def reflect(self, x, y):
        if self.orientation == "HORIZONTAL":
            return x, self.y + (self.y - y)

        return self.x + (self.x - x), y

    def redirect(self, dir):
        if self.orientation == "HORIZONTAL":
            new_dir = (-dir) % (2 * math.pi)
            offset = random.gauss(0, self.roughness)

            while math.sin(new_dir + offset) * math.sin(new_dir) <= 0:
                offset = random.gauss(0, self.roughness)

            return new_dir + offset

        else:
            new_dir = (math.pi - dir) % (2 * math.pi)
            offset = random.gauss(0, self.roughness)

            while math.cos(new_dir + offset) * math.cos(new_dir) <= 0:
                offset = random.gauss(0, self.roughness)

            return new_dir + offset

    def display(self):
        if self.orientation == "HORIZONTAL":
            pygame.draw.rect(screen, "black", (self.x, self.y - self.width / 2, self.length, self.width))

        else:
            pygame.draw.rect(screen, "black", (self.x - self.width / 2, self.y, self.width, self.length))

class SlidingDoor(Wall):
    def __init__(self, x, y, length, orientation):
        super().__init__(x, y, length, orientation)
        self.is_open = False

    def toggle(self):
        self.is_open = not self.is_open

    def passed_through(self, distance_tuple):
        if self.is_open:
            return False
        
        return super().passed_through(distance_tuple)

    def display(self):
        if not self.is_open:
            if self.orientation == "HORIZONTAL":
                pygame.draw.rect(screen, "green", (self.x, self.y - self.width / 2, self.length, self.width))

            else:
                pygame.draw.rect(screen, "green", (self.x - self.width / 2, self.y, self.width, self.length))

# Start game
opposite_side = {"LEFT": "RIGHT", "RIGHT": "LEFT"}

# Screen dimensions
dimensions = left, right, up, down = (0, 1280, 0, 720)
size = width, height = (right - left, down - up)
center = center_x, center_y = (left + width / 2, up + height / 2)

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()

font = pygame.font.Font(None, 200)
text_surface = font.render("You win!", False, "orange")
text_rect = text_surface.get_rect()
text_rect.center = center

# Runtime variables
amount = particle_amount
mean_speed = 4
if faster_particles:
    mean_speed = 5
if not even_hot_and_cold_distribution:
    molecules = [
        Molecule(
            random.uniform(0, 2 * math.pi), 
            random.gauss(mean_speed, 1), 
            random.choice(["HOT", "COLD"]), 
            random.randint(left + 51, right - 50),
            random.randint(up + 51, down - 50),
        ) for _ in range(amount)
    ]
else:
    cold_molecules = [
        Molecule(
            random.uniform(0, 2 * math.pi), 
            random.gauss(mean_speed, 1), 
            "COLD", 
            random.randint(left + 51, right - 50),
            random.randint(up + 51, down - 50),
        ) for _ in range(amount // 2)
    ]
    hot_molecules = [
        Molecule(
            random.uniform(0, 2 * math.pi), 
            random.gauss(mean_speed, 1), 
            "HOT", 
            random.randint(left + 51, right - 50),
            random.randint(up + 51, down - 50),
        ) for _ in range(amount // 2)
    ]
    molecules = cold_molecules + hot_molecules

door_size_dict = {"Small": 180, "Normal": 240, "Large": 480, "Full Size": 720}
door_size = door_size_dict[door_size_string] # 1/2, 1/3, or 1/4 of the height
door_frame_size = (height - door_size) / 2
walls = [
    # Horizontal Walls
    Wall(left, up, width, "HORIZONTAL"),
    Wall(left, down, width, "HORIZONTAL"),

    # Vertical Walls
    Wall(left, up, height, "VERTICAL"),
    Wall(right, up, height, "VERTICAL"),

    # Doorway
    Wall(center_x, up, door_frame_size, "VERTICAL"),
    Wall(center_x, center_y + door_size / 2, door_frame_size, "VERTICAL"),
]

sliding_door = SlidingDoor(center_x, center_y - door_size / 2, door_size, "VERTICAL")
walls.append(sliding_door)

# Core loop
running = True
has_won = False

input(f"\nYour goal is to get the hot particles to the {side_of_hot_molecules.lower()} and the cold particles to the {opposite_side[side_of_hot_molecules].lower()}. Press 'c' to operate the sliding door. Ready? ")
print()

while running:
 
    # Event handling
    toggle_triggered = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                toggle_triggered = True

    # Logic
    if toggle_triggered:
        sliding_door.toggle()

    for molecule in molecules:
        molecule.move(walls)

    perfectly_split = True
    for molecule in molecules:
        if side_of_hot_molecules == "RIGHT":
            if molecule.temp == "HOT":
                if molecule.x < sliding_door.x:
                    perfectly_split = False
            else:
                if molecule.x > sliding_door.x:
                    perfectly_split = False
        else:
            if molecule.temp == "HOT":
                if molecule.x > sliding_door.x:
                    perfectly_split = False
            else:
                if molecule.x < sliding_door.x:
                    perfectly_split = False

    if perfectly_split:
        has_won = True

    # Rendering
    screen.fill("yellow")

    for wall in walls:
        wall.display()

    for molecule in molecules:
        molecule.display()

    if has_won:
        screen.blit(text_surface, text_rect)

    pygame.display.flip()

    # Frame rate control
    clock.tick(60)

pygame.quit()