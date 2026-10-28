"""Prepare an editable, metre-scaled working mesh without inventing a rig.

Run with Blender:
  blender -b -t 2 --python tools/prepare_character_source.py -- INPUT.glb OUTPUT_DIR

The downloaded source stays unchanged. Coincident import vertices are welded
while preserving UV corners and custom normals. No holes are filled blindly.
"""
import argparse
import bmesh
import bpy
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

from mathutils import Vector
from mathutils.kdtree import KDTree


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def surface_signature(mesh):
    """Compare position/UV/material corners without relying on vertex indices."""
    uv = mesh.uv_layers.active
    corners = Counter()
    for face in mesh.polygons:
        for index in face.loop_indices:
            position = mesh.vertices[mesh.loops[index].vertex_index].co
            texture = uv.data[index].uv if uv else ()
            corners[(tuple(round(x, 6) for x in position),
                     tuple(round(x, 6) for x in texture),
                     face.material_index)] += 1
    return corners


def connected_components(mesh):
    bm = bmesh.new()
    bm.from_mesh(mesh)
    remaining = set(bm.verts)
    sizes = []
    while remaining:
        stack = [remaining.pop()]
        size = 0
        while stack:
            vertex = stack.pop()
            size += 1
            for edge in vertex.link_edges:
                other = edge.other_vert(vertex)
                if other in remaining:
                    remaining.remove(other)
                    stack.append(other)
        sizes.append(size)
    result = {
        "count": len(sizes),
        "largest_vertex_counts": sorted(sizes, reverse=True)[:20],
        "boundary_edges": sum(edge.is_boundary for edge in bm.edges),
        "nonmanifold_nonboundary_edges": sum(
            not edge.is_manifold and not edge.is_boundary for edge in bm.edges
        ),
    }
    bm.free()
    return result


def prepare(source, output, height):
    output.mkdir(parents=True, exist_ok=True)
    original_hash = sha256(source)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(source))
    scene = bpy.context.scene
    if any(obj.type == "ARMATURE" for obj in scene.objects):
        raise RuntimeError("This preparation is for the unrigged source; preserve existing rigs separately")
    meshes = [obj for obj in scene.objects if obj.type == "MESH"]
    if not meshes:
        raise RuntimeError("No mesh in source")

    report = {
        "source_name": source.name,
        "source_sha256": original_hash,
        "source_preserved": False,
        "height_m": height,
        "rigged": False,
        "animation_clips": [],
        "ready_for_game": False,
        "meshes": [],
        "open_work": [
            "Natural hand pose and finger articulation",
            "Controlled mane silhouette",
            "Inspect actual torso boundary holes; do not seal eyes/mouth/fur blindly",
            "Jaw and mouth interior articulation",
            "Rig, skin weights, animation authoring and GLB deformation review",
        ],
    }
    for obj in meshes:
        mesh = obj.data
        before = surface_signature(mesh)
        source_normals = [normal.vector.copy() for normal in mesh.corner_normals]
        source_positions = [vertex.co.copy() for vertex in mesh.vertices]
        source_vertices = len(mesh.vertices)
        bm = bmesh.new()
        bm.from_mesh(mesh)
        normal_layer = bm.loops.layers.float_vector.new("_source_corner_normal")
        for face, original_face in zip(bm.faces, mesh.polygons):
            for loop, index in zip(face.loops, original_face.loop_indices):
                loop[normal_layer] = source_normals[index]
        # Only exact import duplicates. A 1e-5 merge collapsed a tiny source
        # triangle, so that broader cleanup is diagnostic only, never applied.
        bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=0.00000001)
        normals = [loop[normal_layer].copy() for face in bm.faces for loop in face.loops]
        bm.to_mesh(mesh)
        bm.free()
        attribute = mesh.attributes.get("_source_corner_normal")
        if attribute:
            mesh.attributes.remove(attribute)
        mesh.update()
        if len(normals) != len(mesh.loops):
            raise RuntimeError("Corner count changed; do not silently lose normal data")
        mesh.normals_split_custom_set(normals)
        if surface_signature(mesh) != before:
            raise RuntimeError("Welding altered a position/UV/material corner")
        tree = KDTree(len(mesh.vertices))
        for vertex in mesh.vertices:
            tree.insert(vertex.co, vertex.index)
        tree.balance()
        displacement = max(tree.find(position)[2] for position in source_positions)
        if displacement > 0.000000011:
            raise RuntimeError(f"Welding moved source geometry excessively: {displacement}")
        error = max((mesh.corner_normals[i].vector - normal).length
                    for i, normal in enumerate(normals))
        # Blender re-encodes custom normals in the welded loop's normal space.
        # Allow <0.3 degrees of quantization, and record the actual deviation.
        if error > 0.005:
            raise RuntimeError(f"Corner normal preservation failed: {error}")
        mesh.calc_loop_triangles()
        report["meshes"].append({
            "name": obj.name,
            "source_vertices": source_vertices,
            "welded_vertices": len(mesh.vertices),
            "triangles": len(mesh.loop_triangles),
            "face_corner_uv_material_preserved": True,
            "max_source_vertex_displacement": displacement,
            "max_corner_normal_error": error,
            "topology": connected_components(mesh),
        })

    # Apply the imported coordinate system before establishing metre scale.
    bpy.ops.object.select_all(action="DESELECT")
    for obj in meshes:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    points = [obj.matrix_world @ vertex.co for obj in meshes for vertex in obj.data.vertices]
    low = Vector(tuple(min(point[i] for point in points) for i in range(3)))
    high = Vector(tuple(max(point[i] for point in points) for i in range(3)))
    centre = Vector(((low.x + high.x) / 2, (low.y + high.y) / 2, low.z))
    factor = height / (high.z - low.z)
    for obj in meshes:
        transform = obj.matrix_world.copy()
        for vertex in obj.data.vertices:
            vertex.co = (transform @ vertex.co - centre) * factor
        obj.parent = None
        obj.matrix_world.identity()
        obj.name = "GreyWolf_Working" if len(meshes) == 1 else obj.name
        obj["source_sha256"] = original_hash
        obj["production_status"] = "UNRIGGED_WORKING_MESH"
        obj["target_height_m"] = height
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene["production_status"] = "SOURCE_PREPARATION_ONLY_NOT_ANIMATION_APPROVED"
    bpy.ops.file.pack_all()

    notes = bpy.data.texts.new("READ_ME_PRODUCTION_STATUS")
    notes.write(
        "Editable source preparation only. No rig or animation approval.\n"
        "Original GLB is preserved separately. UV corners and normals verified.\n"
        "Height: 2.4 m, feet at Z=0, front toward -Y.\n"
        "Do not auto-fill fur/mouth/eye boundaries. Natural hands, mane, jaw,\n"
        "rig, skin weights and all authored clips remain open work.\n"
    )
    # Set a useful startup angle without adding render helpers to the export.
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                area.spaces.active.region_3d.view_location = (0, 0, height / 2)
                area.spaces.active.region_3d.view_distance = height * 1.6
                area.spaces.active.shading.type = "MATERIAL"
    blend_path = output / "grey-wolf-working.blend"
    glb_path = output / "grey-wolf-working.glb"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    bpy.ops.export_scene.gltf(
        filepath=str(glb_path), export_format="GLB", use_selection=True,
        export_animations=False, export_extras=True,
    )
    report["source_preserved"] = sha256(source) == original_hash
    report["blend"] = blend_path.name
    report["glb"] = glb_path.name
    report["total_triangles"] = sum(entry["triangles"] for entry in report["meshes"])
    report["triangle_budget_pass"] = report["total_triangles"] <= 15000
    # Reimport the exported file; validate the actual delivery, not just memory.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(glb_path))
    roundtrip = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    points = [obj.matrix_world @ vertex.co for obj in roundtrip for vertex in obj.data.vertices]
    floor_z = min(point.z for point in points)
    actual_height = max(point.z for point in points) - floor_z
    report["roundtrip"] = {
        "height_m": actual_height,
        "feet_z_m": floor_z,
        "has_uv": all(obj.data.uv_layers for obj in roundtrip),
        "textured_materials": all(
            any(node.type == "TEX_IMAGE" and node.image for node in mat.node_tree.nodes)
            for obj in roundtrip for mat in obj.data.materials
        ),
        "has_armature": any(obj.type == "ARMATURE" for obj in bpy.context.scene.objects),
    }
    if abs(actual_height - height) > 0.0001 or abs(floor_z) > 0.0001:
        raise RuntimeError("Exported model has incorrect scale or floor origin")
    if not report["source_preserved"] or not report["roundtrip"]["has_uv"]:
        raise RuntimeError("Source or UV verification failed")
    (output / "preparation-report.json").write_text(json.dumps(report, indent=2) + "\n")
    print("PREPARATION_OK", json.dumps(report))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--height", type=float, default=2.4)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    if args.height <= 0:
        parser.error("Height must be positive")
    prepare(args.source.resolve(), args.output.resolve(), args.height)
