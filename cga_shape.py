import bpy
import bmesh
import copy
from math import radians
from time import time
from statistics import mean
from mathutils import Vector, Matrix

# TODO
# Roofs
# subdivision
# Comp
# Extrusion (implicit?)
# Textures
# Relative size values


#####################################################
### RULES AREA
rules = [
    {
        "id": "rule1",
        "pred": "koob",
        "effect": lambda o : [
            Push,
            (Translate, Vector((3,0,0))),
            (Instantiate, "Cube"),
            Pop,
            Push,
            (Translate, Vector((-2,0,0))),
            (Instantiate, "Cube"),
            Pop,
            (RotZ, 45),
            Push,
            (Translate, Vector((1,3,0))),
            (Instantiate, "Cube"),
            Pop,
            (Scale, Vector((1, 1, 2))),
            Push,
            (Translate, Vector((0,-3,0))),
            (Instantiate, "Cube"),
            Pop,
            ],
        "cond": lambda o : o.location.x > 5
    }
]

### END OF RULES
#####################################################

DIMS = range(3)
inp = None
inac = None

state = {
        "translation": Vector((0,0,0)),
        "rot_x": 0,
        "rot_y": 0, 
        "rot_z": 0,
        "scale": Vector((1,1,1)),
        "transform": Matrix()
}

stack = []

def new_obj(name):
    o = bpy.data.objects.new(name, None)
    bpy.context.scene.objects.link(o)
    return o

def get_by_name(name):
    if name in bpy.data.objects:
        return bpy.data.objects[name]
    return None

def select(obj):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.scene.objects.active = obj
    obj.select = True

def get_active():
    return bpy.context.scene.objects.active

def duplicate(obj):
    select(obj)
    bpy.ops.object.duplicate()
    return get_active()

def set_symbol(obj, s):
    obj["symbol"] = s

def get_symbol(obj):
    assert(obj["symbol"])
    return obj["symbol"]

def apply_state(obj):
    global state
    obj.matrix_world = copy.deepcopy(state["transform"])

def extract_state(obj):
    return {
            "transform": copy.deepcopy(obj.matrix_world)
    }

def Nonterminal(name):
    global inp
    global state
    o = new_obj("symbol")
    set_symbol(o, name)
    apply_state(o)
    o.parent = inp

def Instantiate(name):
    obj = get_by_name(name)
    assert(obj != None)
    cpy = duplicate(obj)
    apply_state(cpy)
    set_symbol(cpy, "TERMINAL")
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
    d = Matrix.Translation(dCoords)
    state["transform"] *= d

def RotX(delta):
    d = Matrix.Rotation(radians(delta), 4, "X")
    state["transform"] *= d

def RotY(delta):
    d = Matrix.Rotation(radians(delta), 4, "Y")
    state["transform"] *= d

def RotZ(delta):
    d = Matrix.Rotation(radians(delta), 4, "Z")
    state["transform"] *= d

def Scale(mult):
    d = Matrix.Scale(mult[0], 4, Vector((1, 0, 0))) * Matrix.Scale(mult[1], 4, Vector((0, 1, 0))) * Matrix.Scale(mult[2], 4, Vector((0, 0, 1)))
    state["transform"] *= d

def execute(instructions):
    for inst in instructions:
        if callable(inst):
            inst()
            continue
        assert(type(inst) == tuple)

        l = len(inst)
        assert(l != 0)
        if l == 1:
            inst[0]()
        if l == 2:
            inst[0](inst[1])
        if l == 3:
            inst[0](inst[1], inst[2])
        if l == 4:
            inst[0](inst[1], inst[2], inst[3])

def ApplyRule(r, obj):
    global inp
    global inac
    global state
    assert(obj.parent == inp)
    assert(get_symbol(obj) == r["pred"])

    Push()
    state = extract_state(obj)
    print("STATE: ", state)
    instructions = r["effect"](obj)
    execute(instructions)
    Pop()

    obj.parent = inac

def ApplyOne():
    global inp
    global inac
    global rules
    for r in rules:
        p = r["pred"]
        print("RUle pred: " + p)
        for o in inp.children:
            symb = get_symbol(o)
            print("Child symbol: " + symb)
            if symb == p and r["cond"](o):
                ApplyRule(r, o)
                return True
            else:
                print(o.name)
    return False

def prepare():
    global inp
    global inac
    global state

    scene_was_prepped = True

    inp = get_by_name("CGA_INPUT")
    if(inp == None):
        new_obj("CGA_INPUT")
        scene_was_prepped = False

    inac = get_by_name("CGA_INACTIVE")
    if(inac == None):
        new_obj("CGA_INACTIVE")
        scene_was_prepped = False

    if not scene_was_prepped:
        return False

    for c in inp.children:
        set_symbol(c, c.name)
    return True

# Ok, so hoow this is gonna work is,
# We're gonna have one object named "CGA_INPUT"
# If it exist on start we operate on it, if not we create  and ask for a restart (TODO).
# We operate on children as the necesary input to the algorithm.
# INderesting, blender duplicate operation has problems with hierarchies. Recommend to only do simple objects.
def main():
    global inp
    if not prepare():
        return

    # Get current time
    t = time()

    # Function that does all the work
    i = 0
    while ApplyOne():
        i += 1
        print(i)

    # Uncomment to do animation
    # precompute_for_animation(mesh)
    # bpy.app.handlers.frame_change_pre.append(animation_handler)

    # Report performance...
    print("Script took %6.2f secs.\n\n" % (time() - t))

# Uncomment if running in blender text editor
main()
