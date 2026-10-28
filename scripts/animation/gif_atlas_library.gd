class_name GifAtlasLibrary
extends RefCounted
## Loads one source GIF's decoded atlas pages as a Godot SpriteFrames resource.
## The animation is named "source" because its action has not been classified.

const CATALOG_PATH := "res://Asset/Character/extracted/catalog.json"
const SPLIT_CATALOG_PATH := "res://Asset/Character/extracted/split-catalog.json"
const COMPOSITE_CATALOG_PATH := "res://Asset/Character/extracted/composite-catalog.json"
const ATLAS_ROOT := "res://Asset/Character/extracted"

## Loads a motion or reconstructed review candidate. Candidate metadata owns
## its timeline and regions; it must not be paired with the source catalog.
static func create_animation_candidate(asset_id: String, candidate_kind: String) -> Dictionary:
    if candidate_kind not in ["motion_v2_candidates", "repaired_candidates", "repaired_v2_candidates", "repaired_v5_candidates", "scene_spot_candidates", "revision_candidates"]:
        push_error("Unknown candidate kind: " + candidate_kind)
        return {}
    if asset_id.is_empty() or "/" in asset_id or "\\" in asset_id or asset_id == "..":
        push_error("Invalid candidate asset id")
        return {}
    var root := "res://Asset/Character/%s/%s" % [candidate_kind, asset_id]
    var file := FileAccess.open(root + "/candidate.json", FileAccess.READ)
    if file == null:
        push_error("Cannot open animation candidate: " + asset_id)
        return {}
    var entry: Variant = JSON.parse_string(file.get_as_text())
    if not entry is Dictionary or not entry.has("frames") or entry.frames.is_empty():
        push_error("Invalid animation candidate: " + asset_id)
        return {}
    var result := SpriteFrames.new()
    result.rename_animation("default", "source")
    result.set_animation_speed("source", 10.0)
    result.set_animation_loop("source", entry.loop != null)
    var pages: Dictionary = {}
    for frame in entry.frames:
        var page: int = frame.atlas
        if not pages.has(page):
            var texture: Texture2D = load("%s/atlas_%03d.png" % [root, page])
            if texture == null:
                push_error("Cannot load animation candidate atlas: " + asset_id)
                return {}
            pages[page] = texture
        var region: Array = frame.region
        var atlas := AtlasTexture.new()
        atlas.atlas = pages[page]
        atlas.region = Rect2(region[0], region[1], region[2], region[3])
        result.add_frame("source", atlas, maxf(float(frame.duration_ms) / 100.0, 0.001))
    var canvas_size := Vector2(entry.frames[0].region[2], entry.frames[0].region[3])
    var display_size := canvas_size
    if entry.has("display_size"):
        display_size = Vector2(entry.display_size[0], entry.display_size[1])
    return {"frames": result, "canvas_size": canvas_size, "display_scale": display_size / canvas_size}

## Loads a separately packed review candidate and reports the scale needed to
## keep the same displayed canvas as the source. The caller decides whether to
## use this unreviewed variant and applies display_scale to its sprite.
static func create_detail130_candidate(asset_id: String) -> Dictionary:
    var root := "res://Asset/Character/detail_130_atlases/%s" % asset_id
    var file := FileAccess.open(root + "/candidate.json", FileAccess.READ)
    if file == null:
        push_error("Cannot open detail candidate: " + asset_id)
        return {}
    var entry: Variant = JSON.parse_string(file.get_as_text())
    if not entry is Dictionary or not entry.has("frames") or not entry.has("display_size") or not entry.has("frame_size"):
        push_error("Invalid detail candidate: " + asset_id)
        return {}
    var result := SpriteFrames.new()
    result.rename_animation("default", "source")
    result.set_animation_speed("source", 10.0)
    result.set_animation_loop("source", entry.loop != null)
    var pages: Dictionary = {}
    for frame in entry.frames:
        var page: int = frame.atlas
        if not pages.has(page):
            var texture: Texture2D = load("%s/atlas_%03d.png" % [root, page])
            if texture == null:
                push_error("Cannot load detail atlas for: " + asset_id)
                return {}
            pages[page] = texture
        var region: Array = frame.region
        var atlas := AtlasTexture.new()
        atlas.atlas = pages[page]
        atlas.region = Rect2(region[0], region[1], region[2], region[3])
        result.add_frame("source", atlas, maxf(float(frame.duration_ms) / 100.0, 0.001))
    var display: Array = entry.display_size
    var detail: Array = entry.frame_size
    if detail[0] <= 0 or detail[1] <= 0:
        push_error("Invalid detail size: " + asset_id)
        return {}
    return {"frames": result, "display_scale": Vector2(float(display[0]) / detail[0], float(display[1]) / detail[1])}

static func create_sprite_frames(asset_id: String, first_frame: int = 0, last_frame: int = -1, atlas_root: String = ATLAS_ROOT) -> SpriteFrames:
    var file := FileAccess.open(CATALOG_PATH, FileAccess.READ)
    if file == null:
        push_error("Cannot open GIF catalog: " + CATALOG_PATH)
        return null
    var catalog: Variant = JSON.parse_string(file.get_as_text())
    if not catalog is Dictionary or not catalog.has("assets"):
        push_error("Invalid GIF catalog")
        return null
    var entry: Dictionary = {}
    for asset in catalog.assets:
        if asset.id == asset_id:
            entry = asset
            break
    for extra_path in [SPLIT_CATALOG_PATH, COMPOSITE_CATALOG_PATH]:
        if not entry.is_empty():
            break
        if FileAccess.file_exists(extra_path):
            var extra_file := FileAccess.open(extra_path, FileAccess.READ)
            if extra_file != null:
                var extra_catalog: Variant = JSON.parse_string(extra_file.get_as_text())
                if extra_catalog is Dictionary and extra_catalog.has("assets"):
                    for asset in extra_catalog.assets:
                        if asset.id == asset_id:
                            entry = asset
                            break
    if entry.is_empty():
        push_error("Unknown GIF asset: " + asset_id)
        return null
    var frame_count: int = entry.frames.size()
    if last_frame == -1:
        last_frame = frame_count - 1
    if first_frame < 0 or last_frame < first_frame or last_frame >= frame_count:
        push_error("Invalid frame range for GIF asset: " + asset_id)
        return null
    var result := SpriteFrames.new()
    result.rename_animation("default", "source")
    # Frame duration is expressed relative to this base rate.
    result.set_animation_speed("source", 10.0)
    result.set_animation_loop("source", entry.loop != null)
    var pages: Dictionary = {}
    for index in range(first_frame, last_frame + 1):
        var frame: Dictionary = entry.frames[index]
        var page: int = frame.atlas
        if not pages.has(page):
            var path := "%s/%s/atlas_%03d.png" % [atlas_root, asset_id, page]
            var texture: Texture2D = load(path)
            if texture == null:
                push_error("Cannot load GIF atlas: " + path)
                return null
            pages[page] = texture
        var region: Array = frame.region
        var atlas := AtlasTexture.new()
        atlas.atlas = pages[page]
        atlas.region = Rect2(region[0], region[1], region[2], region[3])
        # A zero-delay frame is retained with Godot's minimum positive duration.
        result.add_frame("source", atlas, maxf(float(frame.duration_ms) / 100.0, 0.001))
    return result
