import bpy
import bmesh
import copy
from time import time
from statistics import mean
from mathutils import Vector

# TODO
# COnditionals
# Other transforms
# Textures


#####################################################
### RULES AREA
def define_rules():
    def rule1(o):
        Nonterminal("VV");
        Translate(Vector((8,0,0)))
        Nonterminal("VV");
    rule1.pred = "koob"
    RULE(rule1)

    def rule11(o):
        Nonterminal("V");
        Translate(Vector((0,8,0)))
        Nonterminal("V");
    rule11.pred = "VV"
    RULE(rule11)

    def rule2(o):
        Push()
        Translate(Vector((1,0,0)))
        Instantiate("Cube");
        Pop()
        Push()
        Translate(Vector((-1,0,0)))
        Instantiate("Cube");
        Pop()
        Push()
        Translate(Vector((0,1,0)))
        Instantiate("Cube");
        Pop()
        Push()
        Translate(Vector((0,-1,0)))
        Instantiate("Cube");
        Pop()
    rule2.pred = "V"
    RULE(rule2)

### END OF RULES
#####################################################

DIMS = range(3)
inp = None
inac = None
rules = []

state = {
        "translation": Vector((0,0,0))
}

stack = []

def RULE(r):
    rules.append(r)

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
    obj["symbol"] = s;

def get_symbol(obj):
    assert(obj["symbol"]);
    return obj["symbol"];

def apply_state(obj):
    global state
    obj.location = state["translation"]

def extract_state(obj):
    return {
            "translation": copy.deepcopy(obj.location)
    }

def Nonterminal(name):
    global inp
    global state
    o = new_obj("symbol");
    set_symbol(o, name);
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
    state["translation"] += dCoords

def ApplyRule(r, obj):
    global inp
    global inac
    global state
    assert(obj.parent == inp)
    assert(get_symbol(obj) == r.pred)

    Push()
    state = extract_state(obj)
    print("STATE: ", state)
    r(obj)
    Pop()
    obj.parent = inac




def ApplyOne():
    global inp
    global inac
    global rules
    for r in rules:
        p = r.pred
        print("RUle pred: " + p)
        for o in inp.children:
            symb = get_symbol(o)
            print("Child symbol: " + symb)
            if symb == p:
                ApplyRule(r, o)
                return True;
            else:
                print(o.name)
    return False;

def prepare():
    global inp
    global inac
    global state

    scene_was_prepped = True

    inp = get_by_name("CGA_INPUT")
    if(inp == None):
        new_obj("CGA_INPUT")
        scene_was_prepped = False
        return False

    inac = get_by_name("CGA_INACTIVE")
    if(inac == None):
        new_obj("CGA_INACTIVE")
        scene_was_prepped = False
        return False

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
    define_rules()

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
