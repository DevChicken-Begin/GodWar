extends SceneTree
const Library = preload("res://scripts/animation/gif_atlas_library.gd")
func _initialize():
 var heights = {"samset":80,"kikontai":80,"hecpoirt":70,"uopon":80,"isorat":75,"ompan":85,"combra":90,"maxoi":80,"osiris":85,"thorn":80,"onaon":70,"cornra":90,"ison":90,"charmia":80,"Kungteng":90,"cons":90,"isis":80,"omega":80,"oset":80,"pandung":85}
 for id in heights:
  var item = Library.create_measured_pilot(id)
  if item.is_empty():
   push_error("Cannot load " + id)
   quit(1)
   return
  var meta = JSON.parse_string(FileAccess.get_file_as_string("res://Asset/Character/measured_atlas_pilots/%s/candidate.json" % id))
  if item.frames.get_frame_count("source") != meta.frames.size() or abs(item.display_scale * meta.reference_height_px - heights[id]) > 0.001:
   push_error("Frame or scale mismatch " + id)
   quit(1)
   return
  for i in range(meta.frames.size()):
   if item.frames.get_frame_texture("source", i) == null or abs(item.frames.get_frame_duration("source", i) / item.frames.get_animation_speed("source") * 1000.0 - float(meta.frames[i].duration_ms)) > 0.001:
    push_error("Frame/timing mismatch " + id)
    quit(1)
    return
  print("PASS ",id," ",meta.frames.size()," frames ",heights[id],"px")
 quit(0)
