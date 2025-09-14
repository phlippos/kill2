extends TileMap

@export var collision_layer: int = 0  # Hangi layer'daki tile'ları alacağız
@export var tile_source_id: int = 0   # TileSet source ID

var platforms: Array = []

func _ready():
	extract_platforms()
	send_platforms_to_server()

func extract_platforms():
	"""
	TileMap'ten platform verilerini çıkarır
	"""
	platforms.clear()
	
	var used_cells = get_used_cells(collision_layer)
	var grouped_platforms = group_adjacent_tiles(used_cells)
	
	for platform_group in grouped_platforms:
		var platform_rect = calculate_platform_bounds(platform_group)
		platforms.append(platform_rect)
	
	print("Toplam platform sayısı: ", platforms.size())
	for platform in platforms:
		print("Platform: ", platform)

func group_adjacent_tiles(cells: Array) -> Array:
	"""
	Yan yana olan tile'ları gruplar (optimization için)
	"""
	var groups: Array = []
	var processed: Array = []
	
	for cell in cells:
		if cell in processed:
			continue
			
		var group = [cell]
		var queue = [cell]
		processed.append(cell)
		
		# BFS ile adjacent tile'ları bul
		while not queue.is_empty():
			var current = queue.pop_front()
			var neighbors = get_adjacent_cells(current, cells)
			
			for neighbor in neighbors:
				if neighbor not in processed:
					group.append(neighbor)
					queue.append(neighbor)
					processed.append(neighbor)
		
		groups.append(group)
	
	return groups

func get_adjacent_cells(cell: Vector2i, all_cells: Array) -> Array:
	"""
	Bir cell'in yan yana komşularını bulur (sadece yatay)
	"""
	var adjacent = []
	var directions = [Vector2i(1, 0), Vector2i(-1, 0)]  # Sadece yatay
	
	for direction in directions:
		var neighbor = cell + direction
		if neighbor in all_cells:
			adjacent.append(neighbor)
	
	return adjacent

func calculate_platform_bounds(tile_group: Array) -> Dictionary:
	"""
	Tile grubu için platform boundary'lerini hesaplar
	"""
	if tile_group.is_empty():
		return {}
	
	var tile_size = tile_set.tile_size
	var min_x = tile_group[0].x
	var max_x = tile_group[0].x
	var min_y = tile_group[0].y
	var max_y = tile_group[0].y
	
	# Min/max koordinatları bul
	for tile_pos in tile_group:
		min_x = min(min_x, tile_pos.x)
		max_x = max(max_x, tile_pos.x)
		min_y = min(min_y, tile_pos.y)
		max_y = max(max_y, tile_pos.y)
	
	# World koordinatlarına çevir
	var world_pos = to_global(map_to_local(Vector2i(min_x, min_y)))
	var width = (max_x - min_x + 1) * tile_size.x
	var height = (max_y - min_y + 1) * tile_size.y
	
	return {
		"x": world_pos.x,
		"y": world_pos.y,
		"width": width,
		"height": height,
		"tile_count": tile_group.size()
	}

func get_individual_tiles() -> Array:
	"""
	Her tile'ı ayrı platform olarak döndürür (gruplamadan)
	"""
	var individual_platforms = []
	var used_cells = get_used_cells(collision_layer)
	var tile_size = tile_set.tile_size
	
	for cell in used_cells:
		var world_pos = to_global(map_to_local(cell))
		individual_platforms.append({
			"x": world_pos.x,
			"y": world_pos.y,
			"width": tile_size.x,
			"height": tile_size.y
		})
	
	return individual_platforms

func send_platforms_to_server():
	"""
	Platform verilerini server'a gönderir
	"""
	var platform_data = {
		"type": "map_data",
		"data": {
			"platforms": platforms,
			"map_name": get_tree().current_scene.scene_file_path.get_file(),
			"tile_size": tile_set.tile_size
		}
	}
	# Network üzerinden gönder
	if Network.has_method("send_map_data"):
		Network.send_map_data(platform_data)
	else:
		print("Network.send_map_data metodu bulunamadı!")
		print("Platform data: ", JSON.stringify(platform_data))

# Debug için manual çağırma
func _input(event):
	if event is InputEventKey and event.pressed:
		if event.keycode == KEY_P:  # P tuşuna basınca platform verilerini yeniden çıkar
			extract_platforms()
			send_platforms_to_server()

# Alternatif: Sadece collision body'leri olan tile'ları al
func extract_collision_platforms():
	"""
	Sadece collision body'si olan tile'ları platform olarak alır
	"""
	platforms.clear()
	var used_cells = get_used_cells(collision_layer)
	var tile_size = tile_set.tile_size
	
	for cell in used_cells:
		var tile_data = get_cell_tile_data(collision_layer, cell)
		
		# Eğer tile'da collision varsa
		if tile_data and tile_data.get_collision_polygons_count(0) > 0:
			var world_pos = to_global(map_to_local(cell))
			platforms.append({
				"x": world_pos.x,
				"y": world_pos.y,
				"width": tile_size.x,
				"height": tile_size.y
			})
	
	print("Collision platformları: ", platforms.size())
