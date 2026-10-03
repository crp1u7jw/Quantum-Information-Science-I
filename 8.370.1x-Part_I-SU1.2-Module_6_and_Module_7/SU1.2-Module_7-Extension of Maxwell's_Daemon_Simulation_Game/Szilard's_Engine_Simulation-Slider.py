import math

import pygame
import pygame_widgets
from pygame_widgets.slider import Slider
import random
from typing import Literal

# --------------------------------------------------
# CONFIGURATIONS

faster_particles = False
thinner_wall_display = False
smaller_particles_display = False

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
    roughness = 0.1

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
    def __init__(self, x, y, length, orientation: Literal["HORIZONTAL", "VERTICAL"]):
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

class Piston(Wall):
    def __init__(self, x, y, length, orientation: Literal["HORIZONTAL", "VERTICAL"], direction_facing: Literal["UP", "DOWN", "LEFT", "RIGHT"], range=600, time=150):

        super().__init__(x, y, length, orientation)
        
        self.state = "NEUTRAL" # ["NEUTRAL", "LOCKED", "EXPANDING"] 
        self.direction_facing = direction_facing

        self.timer = 0
        self.extended_distance = 0

        self.max_timer = time
        self.speed = range / time
        self.range = range

        self.starting_x = x
        self.starting_y = y

        self.collisions = []

    def passed_through(self, distance_tuple):
        collided = super().passed_through(distance_tuple)
        
        if collided:
            if self.state == "NEUTRAL":
                self.collisions.append(distance_tuple)

        return collided

    def expand(self):
        self.state = "EXPANDING"
        self.timer = self.max_timer

    def run(self):
        if self.state == "EXPANDING":
            self.extended_distance += self.speed
            self.extended_distance = max(0, min(self.range, self.extended_distance))
            self.update_position()

            self.timer -= 1
            if self.timer == 0:
                self.state = "NEUTRAL"

        if self.state == "NEUTRAL":
            for collision in self.collisions:
                directional_dict = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}
                x_initial, y_initial, x_final, y_final = collision
                x_direction, y_direction = directional_dict[self.direction_facing]

                #  ⌄ direction of particle
                #     direction of piston ⌄           ⌄ match / does not match
                if (x_initial - x_final) * x_direction < 0:
                    self.extended_distance += 120
                if (x_initial - x_final) * x_direction > 0:
                    self.extended_distance -= 120
                if (y_initial - y_final) * y_direction < 0:
                    self.extended_distance += 120
                if (y_initial - y_final) * y_direction > 0:
                    self.extended_distance -= 120

                self.extended_distance = max(0, min(self.range, self.extended_distance))

                self.update_position()

            self.collisions = []
                
    def update_position(self):
        if self.direction_facing == "UP":
            self.y = self.starting_y - self.extended_distance
        elif self.direction_facing == "DOWN":
            self.y = self.starting_y + self.extended_distance
        elif self.direction_facing == "LEFT":
            self.x = self.starting_x - self.extended_distance
        elif self.direction_facing == "RIGHT":
            self.x = self.starting_x + self.extended_distance

    def display(self):
        if self.orientation == "HORIZONTAL":
            # pygame.draw.rect(screen, "black", (self.starting_x, self.starting_y - self.width / 2, self.length, self.width))
            pygame.draw.rect(screen, "red", (self.x, self.y - self.width / 2, self.length, self.width))
        else:
            # pygame.draw.rect(screen, "black", (self.starting_x - self.width / 2, self.starting_y, self.width, self.length))
            pygame.draw.rect(screen, "red", (self.x - self.width / 2, self.y, self.width, self.length))

# Start game
opposite_side = {"LEFT": "RIGHT", "RIGHT": "LEFT"}

# Screen dimensions
border_size = 50
dimensions = left, right, up, down = (border_size, 1280 + border_size, border_size, 720 + border_size)
size = width, height = (right - left, down - up)
center = center_x, center_y = (left + width / 2, up + height / 2)

display_size = display_width, display_height = (2 * border_size + right - left, 2 * border_size + down - up)

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode(display_size)
clock = pygame.time.Clock()

font = pygame.font.Font(None, 59)
text_surface = font.render(" LEFT  -  NONE  -  RIGHT", False, "orange")
text_rect = text_surface.get_rect()
text_rect.center = (center_x, up + 40)

slider_width = 360
slider = Slider(screen, center_x - slider_width / 2, up + 80, slider_width, 60, min=0, max=slider_width, step=1)

# Runtime variables
mean_speed = 20
if faster_particles:
    mean_speed = 25
molecules = [Molecule(
    random.uniform(0, 2 * math.pi), 
    random.gauss(mean_speed, 1), 
    random.choice(["HOT", "COLD"]), 
    random.randint(left + 51, right - 50),
    random.randint(up + 51, down - 50),
)]

door_size = 720 # 1/2, 1/3, or 1/4 of the height
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
pistons = {
    # Side Pistons
    "LEFT": Piston(left + 20, up, height, "VERTICAL", "RIGHT", 600, 150),
    "RIGHT": Piston(right - 20, up, height, "VERTICAL", "LEFT", 600, 150),
}
walls += pistons.values()

# Core loop
running = True
molecule_side = None

while running:
 
    # Event handling
    toggle_triggered = False
    mouse_lifted = False

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                toggle_triggered = True

        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_lifted = True

    # Logic
    piston_animation = False
    for piston in pistons.values():
        if piston.state == "EXPANDING":
            piston_animation = True
            
    if toggle_triggered and not piston_animation:
        sliding_door.toggle()

    for molecule in molecules:
        molecule.move(walls)

    if toggle_triggered and not sliding_door.is_open and not piston_animation:
        if molecule_side is None:
            if molecules[0].x <= sliding_door.x:
                molecule_side = "LEFT"
                slider.setValue(0)
            elif molecules[0].x > sliding_door.x:
                molecule_side = "RIGHT"
                slider.setValue(slider_width)
            pistons[opposite_side[molecule_side]].expand()

    for piston in pistons.values():
        piston.run()
    
    pygame_widgets.update(events)

    if mouse_lifted:
        slider_value = slider.getValue()
        if slider_value <= slider_width / 4:
            slider.setValue(0)
        elif slider_value < slider_width * 3 / 4:
            slider.setValue(slider_width / 2)
        else:
            slider.setValue(slider_width)

        slider_value = slider.getValue()
        slider_value_dict = {0: "LEFT", slider_width / 2: None, slider_width: "RIGHT"}
        molecule_side = slider_value_dict[slider_value]

    # Rendering
    screen.fill("yellow")

    for wall in walls:
        wall.display()

    for molecule in molecules:
        molecule.display()

    screen.blit(text_surface, text_rect)

    pygame_widgets.update(events)

    pygame.display.flip()

    # Frame rate control
    clock.tick(60)

a = pygame_widgets
pygame.quit()