# Meshy rigs

`source/` holds each character as it was before auto-rigging (mesh, textures, spring bones and the approved custom clips).
`rigs/<name>/` holds what Meshy returned for it: `rigged.glb` (standard humanoid skeleton + skin weights) and the
animation sets (`anim_a.glb`, `anim_b.glb`). Rebuild the shipped models with:

    SRC_DIR=art/3d/meshy/source INSTALL=1 python3 tools/meshy/build_all.py art/3d/meshy/rigs

`tools/meshy/build_game.py` documents the steps (frame alignment, weight transfer, arm/leg separation, anti-stretch pass,
clip transfer, world-aligned bone normalisation). `tools/verify_models.py` must pass afterwards.
