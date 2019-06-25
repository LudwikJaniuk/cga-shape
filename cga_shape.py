import bpy
import bmesh
import copy
from time import time
from statistics import mean
from mathutils import Vector


#####################################################
### RULES AREA
def rule1(o):
    Push()
    Instantiate("Cube");
    Translate(Vector((3,0,0)))
    Instantiate("Cube");
    Pop()
    Translate(Vector((0,3,0)))
    Instantiate("Cube");
rule1.src = "koob"



rules = [rule1]
### END OF RULES
#####################################################

DIMS = range(3)
inp = None

state = {
        "translation": Vector((0,0,0))
}

stack = []

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
    cpy.location = state["translation"]
    cpy.parent = inp

def Push():
    global stack
    global state
    stack.append(copy.deepcopy(state))

def Pop():
    global stack
    global state
    assert(len(stack) >= 1)
    state = stack.pop()

# Accepts a vector
def Translate(dCoords):
    state["translation"] += dCoords

def ApplyOne():
    global inp
    global rules
    for r in rules:
        s = r.src
        for o in inp.children:
            if o.name == s:
                r(o)
                return True;
            else:
                print(o.name)
    return False;

    
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


    # Get current time
    t = time()

    # Function that does all the work
    assert(ApplyOne())

    # Uncomment to do animation
    # precompute_for_animation(mesh)
    # bpy.app.handlers.frame_change_pre.append(animation_handler)

    # Report performance...
    print("Script took %6.2f secs.\n\n" % (time() - t))

# Uncomment if running in blender text editor
main()
