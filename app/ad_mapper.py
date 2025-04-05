def map_objects_to_ad_category(objects):
    category_map = {
        "shoes": "Footwear",
        "phone": "Electronics",
        "car": "Automobile"
    }
    return [category_map.get(obj, "General") for obj in objects]
