# Exploring Maxwell's Daemon
Sep 19th, 2026 \
Jaden Wang 

### Maxwell's Daemon and the 2nd Law of Thermodynamics

This lecture introduced Maxwell's Daemon, a thermodynamics principle explores by James Clark Maxwell in 1867. The premise is that there is a room filled with gas molecules. The room is seperated into 2 halves by a wall, and on the wall there is a hole. Covering the hole is a sliding door, which is controlled by the daemon.

The daemon's goal is to open and close the door to move all of the hot molecules to one side, and the cold molecules to the other. In doing so, the daemon creates a great amount of energy, seemingly without doing any work. This creates a paradoxical situation that seemingly violates the 2nd Law of Thermodynamics. 

Isaac Chuang lists 3 potential reasons this could be impossible:
- The energy needed to move the door makes up for it
- The measurement of the molecules disrupts the paradox
- The need for intelligence disputes the claim

Chuang then explain's the real reason (Szilard's engine and Laurderer's exorcism of Maxwell's daemon) in the following module.

### My Implementation

To simulate this, I have created a physics-based simulation by scratch, displaying the particles using pygame. In the simulation, you are the daemon, and your goal is to fully separate the screen into hot particles on one side and cold particles on the other. 

With this, I have turned Maxwell's daemon into a fully functional game you can play (since I have always loved designing games). The particles are initialized with random speeds, directions, temperatures, and locations; and they bounce off walls with a random offset. Can you do it? [It's not easy being Maxwell's daemon!]

