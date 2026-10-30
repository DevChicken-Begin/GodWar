extends SceneTree
const Library = preload("res://scripts/animation/gif_atlas_library.gd")
func _initialize():
 var expected = {"Aquamen":[65,75],"Diorai":[84,80],"Evenl":[89,75],"Moregorn":[51,70],"Moresword":[89,75]}
 for id in expected:
  var item = Library.create_measured_pilot(id)
  if item.is_empty():
   push_error("Unable to load " + id)
   quit(1)
   return
  var meta = JSON.parse_string(FileAccess.get_file_as_string("res://Asset/Character/measured_atlas_pilots/%s/candidate.json" % id))
  var sf = item.frames
  if sf.get_frame_count("source") != expected[id][0] or abs(item.display_scale * meta.reference_height_px - expected[id][1]) > 0.001:
   push_error("Wrong count or scale: " + id)
   quit(1)
   return
  for i in range(sf.get_frame_count("source")):
   if sf.get_frame_texture("source", i) == null or abs(sf.get_frame_duration("source", i) / sf.get_animation_speed("source") * 1000.0 - float(meta.frames[i].duration_ms)) > 0.001:
    push_error("Wrong texture or timing: " + id)
    quit(1)
    return
  print("PASS ", id, " ", expected[id][0], " frames ", expected[id][1], " px")
 quit(0)
