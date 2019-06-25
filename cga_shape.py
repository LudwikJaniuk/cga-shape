import bpy
import bmesh
import copy
from math import radians
from time import time
from statistics import mean
from mathutils import Vector, Matrix

# TODO
# size following in all scope changes
# Set size of scope?
#   WIll need size in STSATE
#   Could deactivate scale rule to avoid confunsion
#   This has no effect on instantiate (does it?) don't want to think about fitting stuff in the scope
#   Should be able to use size coords as parameter
#   Seems subdiv will use ut heavily so let's gor for  that
# Subdivision
# Relative size values
#   Relativity seems to be computed as all the relative ones share the same cake, after the absoutes have eaten
# Repeat rule
# Roofs
# Comp
# Extrusion (implicit?)
# Textures
    

# NOTES
# Subdiv seems like it's just syntax sugar around applying translations and scalings

# "To go back to higher dimensions we can simply use the size command S with a non-zero 
# value in the correspond- ing dimension (e.g. to extrude a face shape along its 
# normal and therefore transforming it into a volumetric shape)."
#   So setting absolute size instead of scale might be valuable...
#   They're also necessary for then computing relative values off of them


#####################################################
### RULES AREA
rules = [
    {
        "id": "rule1",
        "pred": "koob",
        "effect": lambda o : [
            (Subdiv, "Y", [1,2,3,4,5], ["F", "F", "F", "F", "F"]),
#            (Symbol, "V", { "level" : 0 }),
            ]
    }, {
        "id": "rule2",
        "pred": "V",
        "cond": lambda o : GET(o, "level") > 0,
        "effect": lambda o : [
            Push,
            (Translate, Vector((GET(o, "level")*3,0,0))),
            (Symbol, "V", { "level" : GET(o, "level")-1 }),
            Pop,
            Push,
            (Translate, Vector((-GET(o, "level")*3,0,0))),
            (Symbol, "V", { "level" : GET(o, "level")-1 }),
            Pop,
            Push,
            (Translate, Vector((0, GET(o, "level")*3,0))),
            (Symbol, "V", { "level" : GET(o, "level")-1 }),
            Pop,
            Push,
            (Translate, Vector((0, -GET(o, "level")*3,0))),
            (Symbol, "V", { "level" : GET(o, "level")-1 }),
            Pop,
            ]
    }, {
        "id": "rule3",
        "pred": "F",
        "effect": lambda o : [
            (Instantiate, "Cube"),
            ]
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
        "transform": Matrix(),
        "size": Vector((1,1,1)),
}

stack = []

def GET(o, param_name):
    # CGA user values
    name_safe = "CGAU_" + param_name
    return o[name_safe]

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
    print(s)
    assert(type(s) == str)
    obj["symbol"] = s

def get_symbol(obj):
    assert(obj["symbol"])
    return obj["symbol"]

def set_size(obj, size):
    obj["CGA_size"] = [size.x, size.y, size.z]

def get_size(obj):
    assert(obj["CGA_size"])
    return Vector(obj["CGA_size"])

def d_l2n(letter):
    if letter == "X":
            return 0
    if letter == "Y":
            return 1
    if letter == "Z":
            return 2
    assert(False)

def apply_state(obj):
    global state
    obj.matrix_world = copy.deepcopy(state["transform"])
    set_size(obj, copy.deepcopy(state["size"]))

def extract_state(obj):
    return {
            "transform": copy.deepcopy(obj.matrix_world),
            "size" : get_size(obj)
    }

def Symbol(name, data):
    global inp
    global state
    o = new_obj("symbol")
    set_symbol(o, name)
    if data:
        for k, v in data.items():
            assert(k != "symbol")
            k_safe = "CGAU_" + k
            o[k_safe] = v

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

def Size(val):
    state["size"] = copy.deepcopy(val)

def Subdiv(axis, sizes, names):
    dim = d_l2n(axis)
    assert(len(sizes) == len(names))
    cum_size = 0
    for i in range(len(sizes)):
        size = sizes[i]
        name = names[i]

        curr_size = copy.deepcopy(state["size"])
        curr_size[dim] = size
        Size(curr_size)

        t = Vector((0,0,0))
        t[dim] = cum_size
        Translate(t)

        Symbol(name, {})

        cum_size += size

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
        print("RUle pred: ", p)
        for o in inp.children:
            symb = get_symbol(o)
            print("Child symbol: ", symb)
            if symb == p and (("cond" not in r) or r["cond"](o)):
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
        set_size(c, Vector((10, 10, 10)))
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
