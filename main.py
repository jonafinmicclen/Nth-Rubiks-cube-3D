import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math
import random

# define screen dimensions
WIDTH = 1920
HEIGHT = 1080
WINDOW_NAME = 'Rubiks Cube Sim'
TARGET_FPS = 30

# define colors
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
        self.rotations = [[0,[0,0,0]]]

    def draw(self):
        glPushMatrix()

        glTranslatef(self.position[0], self.position[1], self.position[2])
        r = self.rotations[::-1]
        for angle, axis in r:
            glRotatef(angle, *axis)

        glBegin(GL_QUADS)
        for i, surface in enumerate(self.surfaces):
            for vertex in surface:
                glColor3fv(self.colors[i])
                glVertex3fv((self.vertices[vertex][0], self.vertices[vertex][1], self.vertices[vertex][2]))
        glEnd()

        glPopMatrix()

    def rotate(self, angle, axis, rotation_point):

        if self.rotations[-1][0] == axis: #Can add other list reduction measures and eventually it will not infinitly leak
            self.rotations[-1][1]+=angle
        else:
            self.rotations.append([angle,axis]) 

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
    def __init__(self, size, spacing = 2, offset = [0,0,0]):

        self.cubes = []
        self.size = size

        for x in range(0, size):
            for y in range(0, size):
                for z in range(0, size):
                    colors = ALL_COLORS
                    cube = Cube(position=(x * spacing + offset[0], y * spacing + offset[1], z * spacing + offset[2]), colors=colors)
                    self.cubes.append(cube)

        self.x_slices = [[x * size * size + y * size + z for y in range(size) for z in range(size)] for x in range(size)]
        self.y_slices = [[x * size * size + y * size + z for x in range(size) for z in range(size)] for y in range(size)]
        self.z_slices = [[x * size * size + y * size + z for x in range(size) for y in range(size)] for z in range(size)]
        self.x_y_z_slices = [self.x_slices, self.y_slices, self.z_slices]

        self.current_turn = {
            "turning": False,
            "totalAngle": 0,
            "currentAngle": 0,
            "axis":None,
            "slice_no":None,
            "speed":1
        }

    def draw(self):
        glPushMatrix()
        for cube in self.cubes:
            cube.draw()
        glPopMatrix()

    def rotate_slice(self, axis = (1,0,0), slice_no = 0, angle = 1, updateIndex = False):
        cubes_to_rotate = self.get_cubes_in_slice(axis, slice_no)
        self.rotate_cubes(angle, axis, cubes_to_rotate)
        if updateIndex == True:
            self.rotate_cube_indicies(cubes_to_rotate, axis, angle)

    def rotate_cubes(self, angle, axis, cubes_to_rotate):
        position_of_rotation_center = (np.asarray(self.cubes[cubes_to_rotate[0]].position) + np.asarray(self.cubes[cubes_to_rotate[-1]].position))/2
        for cube_index in cubes_to_rotate:
            self.cubes[cube_index].rotate(angle, axis, position_of_rotation_center)

    def get_cubes_in_slice(self, axis, slice_no):
        match axis:
            case (1,0,0):
                cubes_to_rotate = self.x_slices[slice_no]
            case (0,1,0):
                cubes_to_rotate = self.y_slices[slice_no]
            case (0,0,1):
                cubes_to_rotate = self.z_slices[slice_no]
        return cubes_to_rotate
    
    def rotate_cube_indicies(self, cubes_to_rotate, axis, angle):
        #Direction can only be 0 cw or 1 acw
        #Rotating on different axis has different effect on cube index
        if angle > 0:
            if axis[1] == 1:
                direction = 1
            else:
                direction = 0
        else:
            if axis[1] == 1:
                direction = 0
            else:
                direction = 1

        if angle % 90 != 0:
            raise Exception('Cannot rotate as not right angled')

        turns = int(abs(angle)/90)

        cubes_to_rotate = np.reshape(cubes_to_rotate, (self.size, self.size))
        rotated_array = self.rotate2DArray(cubes_to_rotate, direction, turns)
        rotated_array = rotated_array.flatten().tolist()

        rotator_array = []
        rotator_index = 0
        for i in range(self.size**3):
            if i in rotated_array:
                rotator_array.append(rotated_array[rotator_index])
                rotator_index += 1
            else:
                rotator_array.append(i)

        cubes_old = self.cubes.copy()
        self.cubes = [cubes_old[i] for i in rotator_array]

    def scramble(self, scramble_length):
        potential_axis = [(0,0,1),(0,1,0),(1,0,0)]
        potential_angle = [-180,180, 90, -90]
        potential_slice_no = [i for i in range(self.size)]
        for _ in range(scramble_length):
            self.rotate_slice(axis=random.choice(potential_axis.copy()), slice_no=random.choice(potential_slice_no.copy()), angle=random.choice(potential_angle), updateIndex=True)

    def update(self):
        if self.current_turn["turning"] and abs(self.current_turn["currentAngle"]) < abs(self.current_turn["totalAngle"]):
            self.rotate_slice(axis=self.current_turn["axis"], slice_no=self.current_turn["slice_no"], angle=self.current_turn["speed"])
            self.current_turn["currentAngle"] += self.current_turn["speed"]
        else:
            self.current_turn["turning"] = False
            #Current fix for index in animated turn
            cubess = self.get_cubes_in_slice(self.current_turn["axis"], self.current_turn["slice_no"])
            self.rotate_cube_indicies(cubess, self.current_turn["axis"], self.current_turn["totalAngle"])
            self.random_animated_turn()

    def animated_turn(self, axis = (1,0,0), slice_no = 0, angle = 90, speed = 1): #Speed must be divisible by 90, should add snap function to correct for this
        if self.current_turn["turning"] == True:
            print('Could not begin turn as already turning')
        else:
            self.current_turn["turning"] = True
            self.current_turn["currentAngle"] = 0
            self.current_turn["speed"] = speed
            #h
            self.current_turn["totalAngle"] = angle
            self.current_turn["axis"] = axis
            self.current_turn["slice_no"] = slice_no

    def random_animated_turn(self):
        potential_axis = [(0,0,1),(0,1,0),(1,0,0)]
        potential_angle = [-90, 90, 180, -180]
        angle = random.choice(potential_angle)
        speed = math.copysign(6, angle)
        potential_slice_no = [i for i in range(self.size)]
        self.animated_turn(axis=random.choice(potential_axis.copy()), slice_no=random.choice(potential_slice_no.copy()), angle=angle, speed=speed)
        

    @staticmethod
    def rotate2DArray(array, direction, turns):
        for _ in range(turns):
            array = np.flip(array.T, axis=direction)
        return array

def main():

    # Initialise pygame window with opengl
    pygame.init()
    display = (WIDTH, HEIGHT)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption(WINDOW_NAME)
    clock = pygame.time.Clock()

    # Position perspective
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -40)

    # Enable depth testing so only correct faces are drawn
    glEnable(GL_DEPTH_TEST)

    # Create rubiks cubes
    rubiks_cube = MagicCube(size=7, offset=[-4,-2,0], spacing=2.1)
    rubiks_cube1 = MagicCube(size=2, offset=[-4,0,0], spacing=2.2)
    rubiks_cube2 = MagicCube(size=4, offset=[-15,0,0], spacing=2.2)

    #rubiks_cube.scramble(50)
    rubiks_cube1.scramble(100)
    rubiks_cube2.scramble(1000)

    #rubiks_cube.animated_turn(axis = (1,0,0), slice_no = 0, angle = 180, speed = 1)
    rubiks_cube.random_animated_turn()
    
    while True:
        handle_events()

        glRotatef(0.5, 0, 1, 1)

        rubiks_cube.update()

        render_frame(rubiks_cube)
        pygame.display.flip()
        clock.tick(TARGET_FPS)

def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

def render_frame(*cubes):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    for cube in cubes:
        cube.draw()

if __name__ == "__main__":
    main()