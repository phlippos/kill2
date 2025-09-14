class Validation:
    @staticmethod
    def validate_platform_data(platform):
        """
        Platform data'sını validate eder ve temizler
        
        Args:
            platform (dict): Raw platform data
            
        Returns:
            dict: Validated platform data veya None
        """
        try:
            # Required fields kontrolü
            required_fields = ["x", "y", "width", "height"]
            for field in required_fields:
                if field not in platform:
                    print(f"Missing required field: {field}")
                    return None
            
            # Numeric değerleri float'a çevir
            validated = {
                "x": float(platform["x"]),
                "y": float(platform["y"]),
                "width": float(platform["width"]),
                "height": float(platform["height"])
            }
            
            # Minimum boyut kontrolü
            if validated["width"] <= 0 or validated["height"] <= 0:
                print(f"Invalid platform dimensions: {validated}")
                return None
            
            # Optional fields
            if "tile_count" in platform:
                validated["tile_count"] = int(platform["tile_count"])
            
            return validated
            
        except (ValueError, TypeError) as e:
            print(f"Platform validation error: {e}")
            return None