# HANDOFF PAYLOAD — DESK LAMP BUILD
**Prompt version:** v1.0 | **Authored by:** Claude Fable 5 (Anthropic) | **Date:** 2026-07-16
**Target executor:** Hermes agent (local, RTX 5090 workstation) via Blender MCP

---

## 1. SYSTEM CONTEXT (initialization string for local model)

```
You are an automated Blender MCP execution agent. Execute the following pipeline strictly and in order. Do not improvise geometry, names, or values. Do not skip verification steps. Log every MCP tool response. If a tool call returns an error, record the error message verbatim in the log, retry the call once, and if it fails again, halt and report.
```

## 2. TARGET STATE

An articulated desk lamp of exactly 10 mesh objects, parented in a chain terminating at `Lamp_Base`, with 3 materials assigned. Default scene Camera and Light must remain untouched. Lamp stands on the world origin plane (Z=0).

**Expected final object list (MESH type, exact names):**

| # | Object | Primitive |
|---|--------|-----------|
| 1 | Lamp_Base | cylinder |
| 2 | Lamp_Column | cylinder |
| 3 | Lamp_Joint_Lower | sphere |
| 4 | Lamp_Arm_Lower | cylinder |
| 5 | Lamp_Joint_Upper | sphere |
| 6 | Lamp_Arm_Upper | cylinder |
| 7 | Lamp_Head | cone |
| 8 | Lamp_Bulb | sphere |

(8 lamp meshes; plus any pre-existing default Cube — see Step 0 — Camera and Light are non-mesh and excluded from the mesh count.)

**Parent hierarchy (child → parent):**
```
Lamp_Bulb → Lamp_Head → Lamp_Arm_Upper → Lamp_Joint_Upper → Lamp_Arm_Lower → Lamp_Joint_Lower → Lamp_Column → Lamp_Base
```

**Materials:**

| Material | Objects | RGBA | Metallic | Roughness |
|----------|---------|------|----------|-----------|
| MAT_BrushedSteel | Lamp_Base, Lamp_Column, Lamp_Arm_Lower, Lamp_Arm_Upper, Lamp_Joint_Lower, Lamp_Joint_Upper | [0.55, 0.56, 0.58, 1.0] | 0.9 | 0.35 |
| MAT_ShadeBlack | Lamp_Head | [0.02, 0.02, 0.02, 1.0] | 0.0 | 0.6 |
| MAT_BulbEmissive | Lamp_Bulb | [1.0, 0.95, 0.8, 1.0] | 0.0 | 0.2 |

## 3. EXECUTION STEPS

Execute sequentially. All locations are absolute world coordinates. All rotations are degrees, XYZ Euler.

### Step 0 — Preflight
1. `check_blender_connection` — must return responsive.
2. `get_scene_summary` — record baseline object list in log.
3. If an object named `Cube` exists: `delete_object {"name": "Cube"}`. Do not delete `Camera` or `Light`.

### Step 1 — Base and column
```json
create_cylinder {"name": "Lamp_Base",   "radius": 1.2,  "depth": 0.15, "vertices": 48, "location": [0, 0, 0.075]}
create_cylinder {"name": "Lamp_Column", "radius": 0.12, "depth": 0.5,  "vertices": 32, "location": [0, 0, 0.4]}
```
**CHECKPOINT A:** `capture_viewport` — save as `screenshot_A_base_column.png`. Log it.

### Step 2 — Lower arm assembly
```json
create_sphere   {"name": "Lamp_Joint_Lower", "radius": 0.15, "segments": 32, "rings": 16, "location": [0, 0, 0.65]}
create_cylinder {"name": "Lamp_Arm_Lower", "radius": 0.08, "depth": 1.4, "vertices": 32, "location": [0.35, 0, 1.256]}
rotate_object   {"name": "Lamp_Arm_Lower", "rotation": [0, 30, 0]}
```

### Step 3 — Upper arm assembly
```json
create_sphere   {"name": "Lamp_Joint_Upper", "radius": 0.15, "segments": 32, "rings": 16, "location": [0.7, 0, 1.862]}
create_cylinder {"name": "Lamp_Arm_Upper", "radius": 0.08, "depth": 1.2, "vertices": 32, "location": [1.279, 0, 1.707]}
rotate_object   {"name": "Lamp_Arm_Upper", "rotation": [0, 105, 0]}
```
**CHECKPOINT B:** `capture_viewport` — save as `screenshot_B_arms.png`. Log it.

### Step 4 — Head and bulb
```json
create_cone   {"name": "Lamp_Head", "radius1": 0.45, "radius2": 0.12, "depth": 0.5, "vertices": 48, "location": [1.98, 0, 1.43]}
rotate_object {"name": "Lamp_Head", "rotation": [0, 135, 0]}
create_sphere {"name": "Lamp_Bulb", "radius": 0.14, "segments": 24, "rings": 12, "location": [2.09, 0, 1.32]}
```

### Step 5 — Materials
```json
create_and_assign_material {"object_name": "Lamp_Base",        "material_name": "MAT_BrushedSteel", "color": [0.55, 0.56, 0.58, 1.0], "metallic": 0.9, "roughness": 0.35}
create_and_assign_material {"object_name": "Lamp_Column",      "material_name": "MAT_BrushedSteel", "color": [0.55, 0.56, 0.58, 1.0], "metallic": 0.9, "roughness": 0.35}
create_and_assign_material {"object_name": "Lamp_Joint_Lower", "material_name": "MAT_BrushedSteel", "color": [0.55, 0.56, 0.58, 1.0], "metallic": 0.9, "roughness": 0.35}
create_and_assign_material {"object_name": "Lamp_Arm_Lower",   "material_name": "MAT_BrushedSteel", "color": [0.55, 0.56, 0.58, 1.0], "metallic": 0.9, "roughness": 0.35}
create_and_assign_material {"object_name": "Lamp_Joint_Upper", "material_name": "MAT_BrushedSteel", "color": [0.55, 0.56, 0.58, 1.0], "metallic": 0.9, "roughness": 0.35}
create_and_assign_material {"object_name": "Lamp_Arm_Upper",   "material_name": "MAT_BrushedSteel", "color": [0.55, 0.56, 0.58, 1.0], "metallic": 0.9, "roughness": 0.35}
create_and_assign_material {"object_name": "Lamp_Head",        "material_name": "MAT_ShadeBlack",   "color": [0.02, 0.02, 0.02, 1.0], "metallic": 0.0, "roughness": 0.6}
create_and_assign_material {"object_name": "Lamp_Bulb",        "material_name": "MAT_BulbEmissive", "color": [1.0, 0.95, 0.8, 1.0],  "metallic": 0.0, "roughness": 0.2}
```
Note: if the tool errors on re-using `MAT_BrushedSteel` for the second and subsequent objects, use `assign_material {"object_name": <name>, "material_name": "MAT_BrushedSteel"}` instead for those objects and log the substitution.

### Step 6 — Parenting (order matters: leaf to root)
```json
set_parent {"child": "Lamp_Bulb",        "parent": "Lamp_Head"}
set_parent {"child": "Lamp_Head",        "parent": "Lamp_Arm_Upper"}
set_parent {"child": "Lamp_Arm_Upper",   "parent": "Lamp_Joint_Upper"}
set_parent {"child": "Lamp_Joint_Upper", "parent": "Lamp_Arm_Lower"}
set_parent {"child": "Lamp_Arm_Lower",   "parent": "Lamp_Joint_Lower"}
set_parent {"child": "Lamp_Joint_Lower", "parent": "Lamp_Column"}
set_parent {"child": "Lamp_Column",      "parent": "Lamp_Base"}
```

### Step 7 — Verification (mandatory)
1. `list_objects {"type_filter": "MESH"}` — record full list verbatim in log.
2. `get_scene_summary` — record verbatim in log.
3. **CHECKPOINT C:** `capture_viewport` — save as `screenshot_C_final.png`. Log it.
4. Assert: exactly 8 objects named `Lamp_*` exist with the exact names in Section 2. Any deviation is a FAIL — record which names differ.

### Fallback — single bpy script (only if per-tool calls are unavailable)
If the MCP bridge exposes `execute_blender_code` instead of granular tools, submit this equivalent script in one call and still perform Step 7 verification:

```python
import bpy, math

def cyl(name, r, d, v, loc, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, vertices=v, location=loc,
        rotation=[math.radians(a) for a in rot])
    bpy.context.active_object.name = name

def sph(name, r, loc):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc)
    bpy.context.active_object.name = name

if "Cube" in bpy.data.objects:
    bpy.data.objects.remove(bpy.data.objects["Cube"], do_unlink=True)

cyl("Lamp_Base", 1.2, 0.15, 48, (0,0,0.075))
cyl("Lamp_Column", 0.12, 0.5, 32, (0,0,0.4))
sph("Lamp_Joint_Lower", 0.15, (0,0,0.65))
cyl("Lamp_Arm_Lower", 0.08, 1.4, 32, (0.35,0,1.256), (0,30,0))
sph("Lamp_Joint_Upper", 0.15, (0.7,0,1.862))
cyl("Lamp_Arm_Upper", 0.08, 1.2, 32, (1.279,0,1.707), (0,105,0))
bpy.ops.mesh.primitive_cone_add(radius1=0.45, radius2=0.12, depth=0.5, vertices=48,
    location=(1.98,0,1.43), rotation=(0, math.radians(135), 0))
bpy.context.active_object.name = "Lamp_Head"
sph("Lamp_Bulb", 0.14, (2.09,0,1.32))

def mat(name, rgba, metallic, rough, objs):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = rgba
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = rough
    for o in objs:
        ob = bpy.data.objects[o]
        ob.data.materials.clear()
        ob.data.materials.append(m)

mat("MAT_BrushedSteel", (0.55,0.56,0.58,1.0), 0.9, 0.35,
    ["Lamp_Base","Lamp_Column","Lamp_Joint_Lower","Lamp_Arm_Lower","Lamp_Joint_Upper","Lamp_Arm_Upper"])
mat("MAT_ShadeBlack", (0.02,0.02,0.02,1.0), 0.0, 0.6, ["Lamp_Head"])
mat("MAT_BulbEmissive", (1.0,0.95,0.8,1.0), 0.0, 0.2, ["Lamp_Bulb"])

pairs = [("Lamp_Bulb","Lamp_Head"),("Lamp_Head","Lamp_Arm_Upper"),
         ("Lamp_Arm_Upper","Lamp_Joint_Upper"),("Lamp_Joint_Upper","Lamp_Arm_Lower"),
         ("Lamp_Arm_Lower","Lamp_Joint_Lower"),("Lamp_Joint_Lower","Lamp_Column"),
         ("Lamp_Column","Lamp_Base")]
for c, p in pairs:
    child, parent = bpy.data.objects[c], bpy.data.objects[p]
    child.parent = parent
    child.matrix_parent_inverse = parent.matrix_world.inverted()

print([o.name for o in bpy.data.objects if o.type == 'MESH'])
```

## 4. CONSTRAINTS

- Do not modify or delete the default `Camera` or `Light`.
- Do not change render settings, world settings, or add HDRIs.
- Do not rename any object after creation; names are assigned at creation time.
- Do not apply modifiers, subdivision, or smoothing — raw primitives only (this keeps geometry comparison deterministic).
- Every MCP tool call counts as one round-trip. Maintain a running count.
- Record every error message verbatim, including errors that were resolved by retry.
- The three viewport captures (A, B, C) are mandatory log artifacts.
- On completion, fill in the Hermes column of `metrics_log_desk_lamp.md`.
