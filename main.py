import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

class Cube:
    def __init__(self, position):
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

        # Each face has 9 distinct colors
        self.colors = [
            [(1, 0, 0), (1, 0, 0), (1, 0, 0), (1, 0, 0), (1, 0, 0), (1, 0, 0), (1, 0, 0), (1, 0, 0), (1, 0, 0)],  # Colors for the first face
            [(0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0)],  # Colors for the second face
            [(0, 0, 1), (0, 0, 1), (0, 0, 1), (0, 0, 1), (0, 0, 1), (0, 0, 1), (0, 0, 1), (0, 0, 1), (0, 0, 1)],  # Colors for the third face
            [(1, 1, 0), (1, 1, 0), (1, 1, 0), (1, 1, 0), (1, 1, 0), (1, 1, 0), (1, 1, 0), (1, 1, 0), (1, 1, 0)],  # Colors for the fourth face
            [(1, 0, 1), (1, 0, 1), (1, 0, 1), (1, 0, 1), (1, 0, 1), (1, 0, 1), (1, 0, 1), (1, 0, 1), (1, 0, 1)],  # Colors for the fifth face
            [(0, 1, 1), (0, 1, 1), (0, 1, 1), (0, 1, 1), (0, 1, 1), (0, 1, 1), (0, 1, 1), (0, 1, 1), (0, 1, 1)]   # Colors for the sixth face
        ]

        self.position = position

    def draw(self):
        glBegin(GL_QUADS)

        for i, surface in enumerate(self.surfaces):
            for j, vertex in enumerate(surface):
                glColor3fv(self.colors[i][j])  # Set color for each vertex in the current face
                glVertex3fv((self.vertices[vertex][0] + self.position[0],
                             self.vertices[vertex][1] + self.position[1],
                             self.vertices[vertex][2] + self.position[2]))

        glEnd()

pygame.init()
display = (800, 600)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
pygame.display.set_caption('Colored Cubes')

gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
glTranslatef(0.0, 0.0, -15)  # Adjust the initial translation

# Enable depth testing
glEnable(GL_DEPTH_TEST)

# Create a 3x3x3 grid of cubes with the original spacing
cubes = []
spacing = 2  # Set the spacing back to its original value
for x in range(-1, 2):
    for y in range(-1, 2):
        for z in range(-1, 2):
            cube = Cube(position=(x * spacing, y * spacing, z * spacing))
            cubes.append(cube)

clock = pygame.time.Clock()
fps = 60

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    glRotatef(1, 3, 1, 1)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    for cube in cubes:
        cube.draw()

    pygame.display.flip()
    clock.tick(fps)