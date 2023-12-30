import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

#define screen dimensions
WIDTH = 1920
HEIGHT = 1080

#define colors
WHITE = (255,255,255)
RED = (137,18,20)
BLUE = (13,72,172)
ORANGE = (255,85,37)
GREEN = (25,155,76)
YELLOW = (254,213,47)

all_colors = np.array([WHITE, GREEN, YELLOW, BLUE, RED, ORANGE])/255

class Cube:
    def __init__(self, position, colors):
        self.vertices = (
            (1, -1, -1),
            (1, 1, -1),
            (-1, 1, -1),
            (-1, -1, -1),
            (1, -1, 1),
            (1, 1, 1),
            (-1, -1, 1),
            (-1, 1, 1)
        )

        self.surfaces = (
            (0, 1, 2, 3),
            (3, 2, 7, 6),
            (6, 7, 5, 4),
            (4, 5, 1, 0),
            (1, 5, 7, 2),
            (4, 0, 3, 6)
        )

        self.colors = colors
        self.position = position

    def draw(self):
        glBegin(GL_QUADS)

        for i, surface in enumerate(self.surfaces):
            for vertex in surface:
                glColor3fv(self.colors[i])  # Set the unique color for each face
                glVertex3fv((self.vertices[vertex][0] + self.position[0],
                             self.vertices[vertex][1] + self.position[1],
                             self.vertices[vertex][2] + self.position[2]))

        glEnd()

class CubeSet:
    def __init__(self, size, spacing):
        self.cubes = []

        for x in range(0, size):
            for y in range(0, size):
                for z in range(0, size):
                    colors = all_colors
                    cube = Cube(position=(x * spacing, y * spacing, z * spacing), colors=colors)
                    self.cubes.append(cube)

    def draw(self):
        for cube in self.cubes:
            cube.draw()

#Initialise pygame window with opengl
pygame.init()
display = (WIDTH, HEIGHT)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
pygame.display.set_caption('Rubiks')

#Position perspective
gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
glTranslatef(0.0, 0.0, -20)

# Enable depth testing so only correct faces are drawn
glEnable(GL_DEPTH_TEST)

# Create a set of cubes with the original spacing
cube_set = CubeSet(size=3, spacing=2)

clock = pygame.time.Clock()
fps = 30

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    glRotatef(1, 3, 1, 1)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    cube_set.draw()
    pygame.display.flip()
    clock.tick(fps)