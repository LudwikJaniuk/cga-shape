import bpy
import bmesh
import copy
from math import radians
from time import time
from statistics import mean
from mathutils import Vector, Matrix, Quaternion

# TODO
# Comp
# floorpring ground truth
#   How do we do this? This, and comps like "sidewalls" seems like they require some more syntactic stuff, need me to code it.
#   Think starting with comp is the most reasonable tho
# Roofs
# Extrusion (implicit?)
# Textures
# Parametric primitives? 
#   Because see default cube is actually size 2...
# Data in the subdivs?
# Document size stuff

    

# NOTES
# Subdiv seems like it's just syntax sugar around applying translations and scalings
#   WIll need size in STSATE
#   Could deactivate scale rule to avoid confunsion
#   This has no effect on instantiate (does it?) don't want to think about fitting stuff in the scope
#   Should be able to use size coords as parameter
#   Seems subdiv will use ut heavily so let's gor for  that

# "To go back to higher dimensions we can simply use the size command S with a non-zero 
# value in the correspond- ing dimension (e.g. to extrude a face shape along its 
# normal and therefore transforming it into a volumetric shape)."
#   So setting absolute size instead of scale might be valuable...
#   They're also necessary for then computing relative values off of them

# Fuck it blender has super weird scale handling we're just keeping scale at identity all the time and thats that
# In terminals we can set their scale to respect scope or something if we want but &tra

# Inverting is out if order so it kind would make sene that it's wrong

#####################################################
### RULES AREA
rules = [
    {
        "id": "rule1",
        "pred": "koob",
        "effect": lambda o : [
            #(Subdiv, "Y", [r(1),1, 1, r(1)], ["F", "F", "F", "F"]),
            #(Repeat, "Y", 3, "F"),
            (Comp, "faces", 3, "F"),
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
            #(Scale, get_size(o)/10),
            (Instantiate, "Cube"),
            ]
    }
]

### END OF RULES
#####################################################

DIMS = range(3)
inp = None
inac = None
curr_obj = None

state = {
        "location": Vector((0,0,0)),
        "rotation": Quaternion((1,0,0), 0),
        "size": Vector((1,1,1)),
}

stack = []

def r(n):
    return (n, "r")

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

def cpy(x):
    return copy.deepcopy(x)

def apply_state(obj):
    global state

    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = cpy(state["rotation"])
    obj.location = cpy(state["location"])

    set_size(obj, copy.deepcopy(state["size"]))

def extract_state(obj):
    st = {
            "location": cpy(obj.location),
            "rotation": cpy(obj.rotation_quaternion),
            "size" : get_size(obj)
    }
    return st

def Symbol(name, data = {}):
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
    state["location"] += dCoords

def RotX(delta):
    q = Quaternion((1, 0, 0), radians(delta))
    state["rotation"] *= d

def RotY(delta):
    q = Quaternion((0, 1, 0), radians(delta))
    state["rotation"] *= d

def RotZ(delta):
    q = Quaternion((0, 0, 1), radians(delta))
    state["rotation"] *= d

#def Scale(mult):
#    d = Matrix.Scale(mult[0], 4, Vector((1, 0, 0))) * Matrix.Scale(mult[1], 4, Vector((0, 1, 0))) * Matrix.Scale(mult[2], 4, Vector((0, 0, 1)))
#    state["transform"] *= d

def Size(val):
    state["size"] = copy.deepcopy(Vector(val))

def absolutize(sizes, dim):
    sTot = state["size"][dim]
    absSum = 0
    rSum = 0
    for size in sizes:
        if type(size) == tuple:
            assert(size[1] == "r")
            rSum += size[0]
        else:
            absSum += size

    for i in range(len(sizes)):
        s = sizes[i] 
        if type(s) == tuple:
            sizes[i] = s[0]*(sTot - absSum)/rSum
    
    return sizes


def Subdiv(axis, sizes, names):
    dim = d_l2n(axis)
    assert(len(sizes) == len(names))

    sizes = absolutize(sizes, dim)

    cum_size = 0
    for i in range(len(sizes)):
        size = sizes[i]
        name = names[i]

        Push()
        curr_size = copy.deepcopy(state["size"])
        curr_size[dim] = size
        Size(curr_size)

        t = Vector((0,0,0))
        t[dim] = cum_size
        Translate(t)

        Symbol(name)
        Pop()

        cum_size += size

def Repeat(axis, size, name):
    dim = d_l2n(axis)
    sTot = state["size"][dim]
    reps = int(sTot/size)

    sizes = []
    names = []
    for i in range(reps):
        sizes.append(size)
        names.append(name)

    Subdiv(axis, sizes, names)

# I just want to make the right matrix for popping things in.
# It should have the translation I give it, and the rotation so that z is pointing in the direction of the notmal
def makeMatrix(location, normal):
    t = Matrix.Translation(location)

    up = Vector((0,0,1))
    rdiff = up.rotation_difference(normal)
    print("RDIFF", rdiff)
    dmat = rdiff.to_matrix().to_4x4()

    return t * dmat

def Comp(shape_type, param, name):
    # TODO use param
    global curr_obj
    ob = curr_obj

    if shape_type == "faces":
        # Check that it is indeed a mesh
        if not ob or ob.type != 'MESH':
            print(ob)
            assert(False)
            return
        # If we are in edit mode, return to object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        # Retrieve the mesh data
        mesh = ob.data
        polys = mesh.polygons

        for poly in polys:
            n = poly.normal
            verts = [mesh.vertices[i] for i in poly.vertices]
            # TODO use

            c = poly.center
            Push()
            state["location"] = cpy(c)
            up = Vector((0,0,1))
            rdiff = up.rotation_difference(n)
            state["rotation"] = cpy(rdiff)
            Size((state["size"].x, state["size"].y, 0))
            Symbol(name)
            Pop()


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
    global curr_obj
    assert(obj.parent == inp)
    assert(get_symbol(obj) == r["pred"])

    Push()
    state = extract_state(obj)

    curr_obj = obj
    instructions = r["effect"](obj)
    execute(instructions)
    curr_obj = None
    Pop()

    obj.parent = inac

def ApplyOne():
    global inp
    global inac
    global rules
    for r in rules:
        p = r["pred"]
        for o in inp.children:
            symb = get_symbol(o)
            if symb == p and (("cond" not in r) or r["cond"](o)):
                ApplyRule(r, o)
                return True
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
        c.rotation_mode = "QUATERNION"
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
