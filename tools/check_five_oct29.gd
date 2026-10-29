extends SceneTree
const Library = preload("res://scripts/animation/gif_atlas_library.gd")
func _initialize():
 for spec in [["Mythos",80],["Tracker",85],["Epicti",80],["Nemotront",80],["Kanhosst",90]]:
  var item = Library.create_approved_animation(spec[0])
  if item.is_empty() or item.frames.get_frame_count("source") != 120 or item.target_height_px != spec[1]:
   push_error("Invalid profile: " + spec[0]); quit(1); return
  for i in range(120):
   if item.frames.get_frame_texture("source",i) == null or abs(item.frames.get_frame_duration("source",i) / item.frames.get_animation_speed("source") * 1000.0 - 70.0) > 0.01:
    push_error("Invalid frame: %s %s" % [spec[0],i]); quit(1); return
  print("PASS ", spec[0], " 120 frames ", spec[1], " px")
 quit(0)
