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
        self.rotation += angle
        self.rotation_axis = axis

        # Convert rotation axis to a numpy array for matrix multiplication
        rotation_axis_np = np.array(axis)

        # Translate the cube to the rotation point
        translation_matrix = np.identity(4)
        translation_matrix[:3, 3] = -np.array(rotation_point)
        
        # Rotate the cube
        rotation_matrix = np.identity(4)
        quaternion = np.array([np.cos(np.radians(angle / 2))] + list(np.sin(np.radians(angle / 2)) * rotation_axis_np))
        rotation_matrix[:3, :3] = self.quaternion_to_matrix(quaternion)

        # Translate the cube back to its original position
        inverse_translation_matrix = np.identity(4)
        inverse_translation_matrix[:3, 3] = np.array(rotation_point)

        # Combine the transformation matrices
        transformation_matrix = np.dot(inverse_translation_matrix, np.dot(rotation_matrix, translation_matrix))

        # Update cube position by applying the transformation matrix
        self.position = np.dot(transformation_matrix[:3, :3], np.array(self.position)) + transformation_matrix[:3, 3]

    @staticmethod
    def quaternion_to_matrix(quaternion):
        w, x, y, z = quaternion
        rotation_matrix = np.array([
            [1 - 2*y**2 - 2*z**2, 2*x*y - 2*w*z, 2*x*z + 2*w*y],
            [2*x*y + 2*w*z, 1 - 2*x**2 - 2*z**2, 2*y*z - 2*w*x],
            [2*x*z - 2*w*y, 2*y*z + 2*w*x, 1 - 2*x**2 - 2*y**2]
        ])
        return rotation_matrix
    
class MagicCube:
    def __init__(self, size, spacing = 2):

        self.cubes = []
        #offset to keep cube in center
        offset = size+(spacing-2)
        for x in range(0, size):
            for y in range(0, size):
                for z in range(0, size):
                    colors = ALL_COLORS
                    cube = Cube(position=(x * spacing - offset, y * spacing - offset, z * spacing - offset), colors=colors)
                    self.cubes.append(cube)

        #get index in cubes of slices on each axis
        self.x_slices = [[x * size * size + y * size + z for y in range(size) for z in range(size)] for x in range(size)]
        self.y_slices = [[x * size * size + y * size + z for x in range(size) for z in range(size)] for y in range(size)]
        self.z_slices = [[x * size * size + y * size + z for x in range(size) for y in range(size)] for z in range(size)]

    def draw(self):
        glPushMatrix()
        for cube in self.cubes:
            cube.draw()
        glPopMatrix()

    def rotate_face(self, axis = (1,0,0), slice_no = 0, angle = 1):
        match axis:
            case (1,0,0):
                cubes_to_rotate = self.x_slices[slice_no]
            case (0,1,0):
                cubes_to_rotate = self.y_slices[slice_no]
            case (0,0,1):
                cubes_to_rotate = self.z_slices[slice_no]

        position_of_rotation_center = self.cubes[cubes_to_rotate[4]].position
        axis_of_rotation = axis
        for idx in cubes_to_rotate:
            self.cubes[idx].rotate(angle, axis_of_rotation, position_of_rotation_center)

# Create rubiks cube
rubiks_cube = MagicCube(size=3)

# Initialise pygame window with opengl
pygame.init()
display = (WIDTH, HEIGHT)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
pygame.display.set_caption('Rubiks')
clock = pygame.time.Clock()
TARGET_FPS = 30

# Position perspective
gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
glTranslatef(0.0, 0.0, -20)

# Enable depth testing so only correct faces are drawn
glEnable(GL_DEPTH_TEST)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    # Rotation for the entire MagicCube
    glRotatef(0.5, 1, 1, 1)

    # Rotate specific face
    rubiks_cube.rotate_face(axis = (0,0,1), slice_no = 1, angle = 1)

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    rubiks_cube.draw()
    pygame.display.flip()
    clock.tick(TARGET_FPS)

