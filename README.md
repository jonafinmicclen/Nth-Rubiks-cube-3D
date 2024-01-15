Rubiks cube simulator. OpenGL/PyGame.

https://github.com/jonafinmicclen/Nth-Rubiks-cube-3D/assets/142181218/7dbb55bb-ca67-4dfb-9a33-ad2b0338845e


Features:
- Any size 3D rubiks cube, random shuffle then solve.
- No UI yet
- Reasonably optimised (good enough for rubiks cube)



Example use:

`rubiks_cube = MagicCube(size=19, offset=[-30,-30,-30], spacing=2)`

`rubiks_cube.animated_turn(axis = (1,0,0), slice_no = 0, angle = 180, speed = 1)`

`rubiks_cube.playMoveSet()`

Ensure to update the cube every frame (:.
You can directly create custom movesets, they are in the format axis(x,y,z) turns, direction.

Please note that the optimisation approach is quite naive and it was rushed, done in about 30 seconds.



