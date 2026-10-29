extends SceneTree
const Library = preload("res://scripts/animation/gif_atlas_library.gd")
func _initialize():
 for spec in [["moxie", 97, 80], ["crapit", 24, 100], ["urguro", 47, 90]]:
  var item = Library.create_approved_animation(spec[0])
  if item.is_empty() or item.frames.get_frame_count("source") != spec[1] or item.target_height_px != spec[2]:
   push_error("Invalid approved animation: " + spec[0])
   quit(1)
   return
  print("PASS ", spec[0], " ", spec[1], " frames ", spec[2], " px")
 quit(0)
