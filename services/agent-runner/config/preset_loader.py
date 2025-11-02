import json
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class PresetLoader:
    def __init__(self):
        self.presets_dir = os.path.join(os.path.dirname(__file__), "presets")
        self.presets_cache = {}
        
    def load_preset(self, preset_name: str) -> Optional[Dict[str, Any]]:
        """
        Load a preset configuration by name
        
        Args:
            preset_name: Name of the preset (e.g., "acu", "apl")
            
        Returns:
            Preset configuration dictionary or None if not found
        """
        # Check cache first
        if preset_name in self.presets_cache:
            return self.presets_cache[preset_name]
        
        preset_file = os.path.join(self.presets_dir, f"{preset_name}.json")
        
        try:
            if os.path.exists(preset_file):
                with open(preset_file, 'r', encoding='utf-8') as f:
                    preset_data = json.load(f)
                    self.presets_cache[preset_name] = preset_data
                    logger.info(f"Loaded preset: {preset_name}")
                    return preset_data
            else:
                logger.error(f"Preset file not found: {preset_file}")
                return None
                
        except Exception as e:
            logger.error(f"Error loading preset {preset_name}: {e}")
            return None
    
    def get_available_presets(self) -> Dict[str, str]:
        """
        Get list of available presets
        
        Returns:
            Dictionary of preset names to display names
        """
        presets = {}
        try:
            for filename in os.listdir(self.presets_dir):
                if filename.endswith('.json'):
                    preset_name = filename[:-5]  # Remove .json extension
                    preset_data = self.load_preset(preset_name)
                    if preset_data:
                        presets[preset_name] = preset_data.get('name', preset_name)
        except Exception as e:
            logger.error(f"Error listing presets: {e}")
        
        return presets
    
    def validate_preset(self, preset_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and set default values for preset configuration
        
        Args:
            preset_data: Raw preset data
            
        Returns:
            Validated preset data with defaults
        """
        validated = preset_data.copy()
        
        # Set defaults for required fields
        defaults = {
            "send_cap_per_run": 20,
            "daily_send_cap": 200,
            "model": "gpt-4o",
            "channels": {"email": True},
            "geo": {"radius_km": 50, "center_city": "", "state": ""},
            "keywords": [],
            "target_roles": ["Business Owner", "Manager"],
            "exclude_domains": ["gmail.com", "yahoo.com", "hotmail.com"]
        }
        
        for key, default_value in defaults.items():
            if key not in validated or not validated[key]:
                validated[key] = default_value
        
        # Ensure from_email is set
        if "from_email" not in validated or not validated["from_email"]:
            validated["from_email"] = "info@nofabusinessconsulting.com"
        
        # Ensure from_name is set
        if "from_name" not in validated or not validated["from_name"]:
            validated["from_name"] = "NOFA BC"
        
        return validated
    
    def merge_preset_with_overrides(self, preset_name: str, overrides: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge preset configuration with runtime overrides
        
        Args:
            preset_name: Name of the base preset
            overrides: Runtime configuration overrides
            
        Returns:
            Merged configuration
        """
        base_preset = self.load_preset(preset_name)
        if not base_preset:
            logger.error(f"Base preset not found: {preset_name}")
            return self.validate_preset(overrides)
        
        # Deep merge - overrides take precedence
        merged = base_preset.copy()
        
        for key, value in overrides.items():
            if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
                # Recursively merge dictionaries
                merged[key] = {**merged[key], **value}
            else:
                # Override with new value
                merged[key] = value
        
        return self.validate_preset(merged)

# Global preset loader instance
preset_loader = PresetLoader()

# Preload common presets
def initialize_presets():
    """Preload common presets on startup"""
    common_presets = ["acu", "apl"]
    for preset_name in common_presets:
        preset_loader.load_preset(preset_name)
    logger.info("Presets initialized")

# Initialize on import
initialize_presets()
