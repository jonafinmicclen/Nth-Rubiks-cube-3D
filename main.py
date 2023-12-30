import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import random

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

ALL_COLORS = np.array([WHITE, GREEN, YELLOW, BLUE, RED, ORANGE])/255

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
        self.rotation = 0
        self.rotation_axis = (0, 0, 0)

    def draw(self):
        glPushMatrix()

        glTranslatef(self.position[0], self.position[1], self.position[2])
        glRotatef(self.rotation, *self.rotation_axis)

        glBegin(GL_QUADS)
        for i, surface in enumerate(self.surfaces):
            for vertex in surface:
                glColor3fv(self.colors[i])
                glVertex3fv((self.vertices[vertex][0], self.vertices[vertex][1], self.vertices[vertex][2]))
        glEnd()

        glPopMatrix()

    def rotate(self, angle, axis, rotation_point):
        # Update rotation
        self.rotation -= angle
        self.rotation_axis = axis

        # Convert rotation axis to a numpy array for matrix multiplication
        rotation_axis_np = np.array(axis)

        # Translate the cube to the rotation point
        translation_matrix = np.identity(4)
        translation_matrix[:3, 3] = -np.array(rotation_point)
        
        # Rotate the cube
        rotation_matrix = np.identity(4)
        rotation_matrix[:3, :3] = np.dot(rotation_matrix[:3, :3], np.cos(np.radians(angle / 2)))
        rotation_matrix[:3, :3] = rotation_matrix[:3, :3] + 2 * np.sin(np.radians(angle / 2)) * np.cross(rotation_axis_np, np.eye(3)) + 2 * np.power(np.sin(np.radians(angle / 2)), 2) * np.outer(rotation_axis_np, rotation_axis_np)

        # Translate the cube back to its original position
        inverse_translation_matrix = np.identity(4)
        inverse_translation_matrix[:3, 3] = np.array(rotation_point)

        # Combine the transformation matrices
        transformation_matrix = np.dot(inverse_translation_matrix, np.dot(rotation_matrix, translation_matrix))

        # Update cube position by applying the transformation matrix
        self.position = np.dot(transformation_matrix[:3, :3], np.array(self.position)) + transformation_matrix[:3, 3]




class CubeSet:
    def __init__(self, size, spacing):
        self.cubes = []

        for x in range(0, size):
            for y in range(0, size):
                for z in range(0, size):
                    colors = ALL_COLORS
                    cube = Cube(position=(x * spacing, y * spacing, z * spacing), colors=colors)
                    self.cubes.append(cube)

    def draw(self):
        glPushMatrix()

        for cube in self.cubes:
            cube.draw()

        glPopMatrix()

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

# Cube set creation
cube_set = CubeSet(size=3, spacing=2)

# Specify the indices of cubes you want to rotate separately
cubes_to_rotate = [0, 1, 2, 9, 10, 11, 18, 19, 20]  # Replace with the actual indices you want to rotate

clock = pygame.time.Clock()
fps = 30

print(cube_set.cubes[10].position)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    # Rotation for the entire CubeSet
    glRotatef(1, 3, 1, 1)

    # Rotation for specific cubes
    for idx in cubes_to_rotate:
        cube_set.cubes[idx].rotate(1, (0, 1, 0), cube_set.cubes[10].position)

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    cube_set.draw()
    pygame.display.flip()
    clock.tick(fps)