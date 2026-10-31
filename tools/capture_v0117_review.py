"""Blender 4.3.2 visual review: bind/idle/move/run/roll and human idle/walk/run."""
import bpy
import json
import sys
from pathlib import Path
from mathutils import Vector

args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
root = Path(args[0]) if args else Path(__file__).resolve().parents[1]
out = Path(args[1]) if len(args) > 1 else root / 'docs/verification-v017/after'
out.mkdir(parents=True, exist_ok=True)
characters = [args[2]] if len(args) > 2 else ['bilge', 'ates', 'kral', 'hellgate', 'ay', 'zeynos']
views = {'front': (0, -5, 0), 'side': (5, 0, 0), 'back': (0, 5, 0)}
shots = []

scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'TEXTURE'
scene.display.shading.show_shadows = True
scene.display.shading.show_cavity = True
scene.render.resolution_x = scene.render.resolution_y = 240
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.world.color = (.035, .045, .055)

for character in characters:
    for form in ('wolf', 'human'):
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        stem = character if form == 'wolf' else f'human-{character}'
        bpy.ops.import_scene.gltf(filepath=str(root / f'app/src/main/assets/models/{stem}.glb'))
        rig = next(obj for obj in scene.objects if obj.type == 'ARMATURE')
        meshes = [obj for obj in scene.objects if obj.type == 'MESH' and not obj.name.startswith('FPArms')]
        for mesh in meshes:
            mesh.hide_render = False
        for obj in scene.objects:
            if obj.name.startswith('FPArms'):
                obj.hide_render = True
        low = Vector((1e9, 1e9, 1e9)); high = Vector((-1e9, -1e9, -1e9))
        for mesh in meshes:
            for corner in mesh.bound_box:
                point = mesh.matrix_world @ Vector(corner)
                low.x = min(low.x, point.x); low.y = min(low.y, point.y); low.z = min(low.z, point.z)
                high.x = max(high.x, point.x); high.y = max(high.y, point.y); high.z = max(high.z, point.z)
        center = (low + high) * .5
        height = max(1.5, high.z - low.z, high.y - low.y)
        bpy.ops.object.light_add(type='AREA', location=(3, -4, center.z + 3)); key = bpy.context.object; key.data.energy = 700; key.data.shape = 'DISK'; key.data.size = 4
        key.rotation_euler = (center - key.location).to_track_quat('-Z', 'Y').to_euler()
        bpy.ops.object.light_add(type='AREA', location=(-3, 2, center.z + 1)); fill = bpy.context.object; fill.data.energy = 450; fill.data.size = 3
        fill.rotation_euler = (center - fill.location).to_track_quat('-Z', 'Y').to_euler()
        bpy.ops.object.camera_add(); camera = bpy.context.object; scene.camera = camera; camera.data.type = 'ORTHO'; camera.data.ortho_scale = height * 1.25
        tracks = {track.name: track for track in (rig.animation_data.nla_tracks if rig.animation_data else [])}
        clips = [('BindRest', None, 0)]
        if form == 'wolf': clips += [('WolfIdle', 'WolfIdle', .5), ('WolfMove', 'WolfMove', .5), ('WolfRunQuad', 'WolfRunQuad', .5), ('WolfRoll', 'WolfRoll', .5)]
        else: clips += [('HumanIdle', 'HumanIdle', .5), ('HumanWalk', 'HumanWalk', .5), ('HumanRun', 'HumanRun', .5)]
        for label, clip, fraction in clips:
            if clip and clip in tracks:
                for track in tracks.values(): track.mute = track.name != clip
                action = tracks[clip].strips[0].action
                lo, hi = action.frame_range
                frame = lo + (hi - lo) * fraction
                scene.frame_set(int(frame), subframe=frame % 1)
            else:
                for track in tracks.values(): track.mute = True
                scene.frame_set(0)
            for view, direction in views.items():
                camera.location = center + Vector(direction) * (height * .9)
                camera.rotation_euler = (center - camera.location).to_track_quat('-Z', 'Y').to_euler()
                name = f'{stem}-{label}-{view}.png'
                scene.render.filepath = str(out / name)
                bpy.ops.render.render(write_still=True)
                shots.append(name)
(out / 'manifest.json').write_text(json.dumps({'root': str(root), 'shots': shots}, indent=2) + '\n')
print('rendered', len(shots), 'frames to', out)
