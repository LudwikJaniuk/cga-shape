import bpy
import bmesh
from time import time
from statistics import mean
from mathutils import Vector

DIMS = range(3)


def processa_malla(me):
    pass


# Ok, so hoow this is gonna work is,
# We're gonna have one object named "CGA_INPUT", one named "CGA_INST".
# If they exist on start we operate on them, if not we create them and then ask for a restart (TODO).
# We operate on their children as the necesary input to the algorithm.
def main():
    # Retrieve the active object (the last one selected)
    inp = bpy.data.objects["CGA_INPUT"]
    assert(inp != None)
    inst = bpy.data.objects["CGA_INST"]
    assert(inst != None)

    bpy.ops.mesh.primitive_cube_add()
    cube = bpy.context.object
    assert(cube != None)
    bpy.ops.mesh.primitive_torus_add()
    torus = bpy.context.object
    assert(torus != None)

    cube.parent = inp
    torus.parent = inst

    # Get current time
    t = time()

    # Function that does all the work
    processa_malla()

    # Uncomment to do animation
    # precompute_for_animation(mesh)
    # bpy.app.handlers.frame_change_pre.append(animation_handler)

    # Report performance...
    print("Script took %6.2f secs.\n\n" % (time() - t))

# Uncomment if running in blender text editor
main()
