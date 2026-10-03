import math

import pygame
import pygame_widgets
from pygame_widgets.button import Button
import random
from typing import Literal

# --------------------------------------------------
# CONFIGURATIONS

thinner_wall_display = False
smaller_particles_display = False

much_faster_particles_and_less_piston_movement = False

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

    def in_starting_state(self):
        return self.starting_x == self.x and self.starting_y == self.y

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

                piston_movement = 120
                if much_faster_particles_and_less_piston_movement:
                    piston_movement = 100

                #  ⌄ direction of particle
                #     direction of piston ⌄           ⌄ match / does not match
                if (x_initial - x_final) * x_direction < 0:
                    self.extended_distance += piston_movement
                if (x_initial - x_final) * x_direction > 0:
                    self.extended_distance -= piston_movement
                if (y_initial - y_final) * y_direction < 0:
                    self.extended_distance += piston_movement
                if (y_initial - y_final) * y_direction > 0:
                    self.extended_distance -= piston_movement

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

font = pygame.font.Font(None, 50)

button_state = {"text": ""}
def clear_button(button_state_dict):
    button.setText("")
    button_state_dict["text"] = ""

button_color = "orange"     #   ⌄ distance from border
                            #        ⌄ width of button
                            #              ⌄ width of piston
button = Button(screen, right - 50 - 100 - 20, up + 50, 100, 100, text="", fontSize=75, inactiveColour=button_color, hoverColour=button_color, pressedColour=button_color, margin=10, onClick=clear_button, onClickParams=[button_state])

# Runtime variables
mean_speed = 20
if much_faster_particles_and_less_piston_movement:
    mean_speed = 30
    
molecules = [Molecule(
    math.pi / 4, 
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
sliding_door.is_open = False
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

message = "" 
message_timer = 0
message_display_duration = 120

explaination_printed = False
first_button_click = True # Checks if the button has ever been clicked before

explaination = """\033[33m\033[4mLandauer's Principle\033[24m

This is where the energy is lost- you have to clear the memory, 
either 0 or 1, which causes a flow of entropy because
you don't know what state it will be in when you clear it.

This is the core of Landauer's principle- 
that erasure of information is a \033[3mdissipative process\033[23m.

I chose to have the user clear this manually to express how extra energy 
is required to erase a random state- even though you don't actually have to 
act differently here for the two cases. 

In the real world, the total entropy of a system must always remain constant 
(the 2nd law of thermodynamics), so the entropy generated by the random 
closing of the door must be dissipated into the environment, consuming energy.

This is why Maxwell's Daemon does not generate energy with no cost, and why 
Szilard's Engine does not generate infinite energy.\033[0m

--------------------------------------------------"""
introduction = f"""
\033[4mSzilard's Engine\033[24m

This is Szilard's engine. It is intended to be an infinite energy generator,
just like Maxwell's Daemon, harvesting infinite energy off of gas particles.
However both of these examples actual have a critical error, as they lose 
energy over time. 

Here are the steps to operate Szilard's Engine:
    1) Close the sliding door by pressing 'c'. This traps the particle on one side.
    2) Activate the piston on the empty side by pressing 'r'. It will automatically scan 
    which side the particle is on and record this in the scratchpad. This is allowed
    as does not take up too much energy.
    3) The side the particle is not on will automatically compress.
    Compressing this side does not cost any energy it is a vacuum 
    (there are no particles there).
    4) Now, release the sliding door (by pressing 'c' again). This gas particle will slowly
    push the piston back to it's original state, generating energy as the piston is moved.
    (The movements are sped up for the purpose of the simulation)
    5) Clear the scratchpad by clicking on it. This is an essential step, and is the core
    of this demonstration. If you don't click on it, the engine will not be able to automatically
    map the current state to the side the particle is on free of energy cost.
    
If you want to learn more about this, you can visit these links:
- https://en.wikipedia.org/wiki/Landauer%27s_principle
- https://en.wikipedia.org/wiki/Entropy_in_thermodynamics_and_information_theory#Szilard's_engine
Or check the explaination of Landauer's Priniciple at the end of the simulation.

Press 'c' to operate the sliding door, press 'r' to begin the piston expansion, 
and click on the scratchpad to clear it. If you would like the explaination of 
Landauer's Priniciple now, type 'y' here: """

print()
print("-" * 50)

choice = input(introduction)
print()

print("-" * 50)
print()

if choice:
    print(explaination)
    explaination_printed = True

while running:
    # Event handling
    toggle_triggered = False
    pistons_triggered = False
    mouse_down = False

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                toggle_triggered = True
            if event.key == pygame.K_r:
                pistons_triggered = True

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_down = True

    # Logic
    piston_animation = False
    for piston in pistons.values():
        if piston.state == "EXPANDING":
            piston_animation = True

    pistons_reset = True
    for piston in pistons.values():
        if not piston.in_starting_state():
            pistons_reset = False
    
    for molecule in molecules:
        molecule.move(walls)

    if toggle_triggered:
        if piston_animation:
            message = "Cannot open door during piston expantion!"
            message_timer = message_display_duration
        else:
            sliding_door.toggle()

    if pistons_triggered:
        if sliding_door.is_open:
            message = "Cannot expand pistons with door open!"
            message_timer = message_display_duration
        elif piston_animation:
            message = "Cannot expand pistons; pistons are already expanding."
            message_timer = message_display_duration
        elif not pistons_reset:
            message = "Cannot expand pistons; pistons are not in initial state!"
            message_timer = message_display_duration
        elif molecule_side is not None:
            message = "Scratchpad must be cleared before you can expand the pistons! Check the console for why."
            message_timer = message_display_duration       
            if not explaination_printed:
                print(explaination)
                explaination_printed = True
        else:
            if molecules[0].x <= sliding_door.x:
                molecule_side = "LEFT"
                button.setText("L")
                button_state["text"] = "L"
            elif molecules[0].x > sliding_door.x:
                molecule_side = "RIGHT"
                button.setText("R")
                button_state["text"] = "R"
            pistons[opposite_side[molecule_side]].expand()

    for piston in pistons.values():
        piston.run()

    pygame_widgets.update(events)
    
    if mouse_down:
        if button_state["text"] == "":
            molecule_side = None

            if first_button_click: 
                message = "You just cleared the memory. Why does that matter? Check the console output for more details!"
                message_timer = message_display_duration * 2
                
                if not explaination_printed:
                    print(explaination)
                    explaination_printed = True

                first_button_click = False

        elif button_state["text"] == "L":
            molecule_side = "LEFT"
        elif button_state["text"] == "R":
            molecule_side = "RIGHT"

    # Rendering
    screen.fill("yellow")

    for wall in walls:
        wall.display()

    for molecule in molecules:
        molecule.display()

    pygame_widgets.update(events)

    if message_timer > 0:
        text_surface = font.render(message, False, "orange", wraplength=800)
        text_rect = text_surface.get_rect()
        text_rect.center = center

        message_timer -= 1

        screen.blit(text_surface, text_rect)

    pygame.display.flip()

    # Frame rate control
    clock.tick(60)

pygame.quit()