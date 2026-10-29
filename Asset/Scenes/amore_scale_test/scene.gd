extends Node2D

const LIBRARY = preload("res://scripts/animation/gif_atlas_library.gd")
const MAP = preload("res://Asset/Scenes/amore_scale_test/map.png")
const ZOOM := 0.7
const MAP_SCALE := 1920.0 / 512.0 * ZOOM
const MAP_X := (1920.0 - 512.0 * MAP_SCALE) / 2.0
const MAP_Y := (1080.0 - 352.0 * MAP_SCALE) / 2.0
const GROUND_Y := MAP_Y + 194.0 * MAP_SCALE
var actor: AnimatedSprite2D

func _ready() -> void:
    get_tree().root.content_scale_size = Vector2i(1920, 1080)
    DisplayServer.window_set_size(Vector2i(1280, 720))
    texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    actor = AnimatedSprite2D.new()
    var pilot := LIBRARY.create_measured_pilot("amore")
    if pilot.is_empty():
        push_error("Cannot load Amore test animation")
        return
    actor.sprite_frames = pilot.frames
    actor.centered = false
    actor.offset = -pilot.anchor_px
    actor.scale = Vector2.ONE * pilot.display_scale
    actor.position = Vector2(MAP_X + 215.0 * MAP_SCALE, GROUND_Y)
    add_child(actor)
    actor.play("source")
    for foot in [Vector2(46, 254), Vector2(160, 286), Vector2(330, 94), Vector2(441, 127), Vector2(485, 158)]:
        var sample := AnimatedSprite2D.new()
        sample.sprite_frames = actor.sprite_frames
        sample.centered = false
        sample.offset = actor.offset
        sample.scale = actor.scale
        sample.position = Vector2(MAP_X + foot.x * MAP_SCALE, MAP_Y + foot.y * MAP_SCALE)
        add_child(sample)
        sample.play("source")

func _draw() -> void:
    draw_rect(Rect2(0, 0, 1920, 1080), Color("78a6cf"))
    draw_texture_rect(MAP, Rect2(MAP_X, MAP_Y, 512.0 * MAP_SCALE, 352.0 * MAP_SCALE), false)

func _process(delta: float) -> void:
    if actor == null:
        return
    var move := Input.get_axis("ui_left", "ui_right")
    actor.position.x = clampf(actor.position.x + move * 220.0 * delta, MAP_X + 195.0 * MAP_SCALE, MAP_X + 245.0 * MAP_SCALE)
