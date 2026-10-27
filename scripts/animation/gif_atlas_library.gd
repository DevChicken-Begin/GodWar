class_name GifAtlasLibrary
extends RefCounted
## Loads one source GIF's decoded atlas pages as a Godot SpriteFrames resource.
## The animation is named "source" because its action has not been classified.

const CATALOG_PATH := "res://Asset/Character/extracted/catalog.json"
const SPLIT_CATALOG_PATH := "res://Asset/Character/extracted/split-catalog.json"
const ATLAS_ROOT := "res://Asset/Character/extracted"

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
    if entry.is_empty() and FileAccess.file_exists(SPLIT_CATALOG_PATH):
        var split_file := FileAccess.open(SPLIT_CATALOG_PATH, FileAccess.READ)
        if split_file != null:
            var split_catalog: Variant = JSON.parse_string(split_file.get_as_text())
            if split_catalog is Dictionary and split_catalog.has("assets"):
                for asset in split_catalog.assets:
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
