import bpy
import bmesh
from time import time
from statistics import mean
from mathutils import Vector

DIMS = range(3)
inp = None

def processa_malla(me):
    pass

def select(obj):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.scene.objects.active = obj
    obj.select = True

def Instantiate(name):
    obj = bpy.data.objects[name]
    assert(obj != None)
    select(obj)
    bpy.ops.object.duplicate()
    cpy = bpy.context.scene.objects.active
    cpy.parent = inp

    
# Ok, so hoow this is gonna work is,
# We're gonna have one object named "CGA_INPUT"
# If it exist on start we operate on it, if not we create  and ask for a restart (TODO).
# We operate on children as the necesary input to the algorithm.
# INderesting, blender duplicate operation has problems with hierarchies. Recommend to only do simple objects.
def main():
    global inp
    # Retrieve the active object (the last one selected)
    inp = bpy.data.objects["CGA_INPUT"]
    assert(inp != None)
    inst = bpy.data.objects["CGA_INST"]
    assert(inst != None)

    Instantiate("Cube");

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
