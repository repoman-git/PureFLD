"""Model Registry"""
import json
from pathlib import Path
from datetime import datetime

class ModelRegistry:
    """Registry for ML models and strategies"""
    
    def __init__(self, registry_path: str = "meridian_local/registry"):
        self.path = Path(registry_path)
        self.path.mkdir(exist_ok=True)
    
    def register_model(self, name: str, metadata: dict):
        """Register a model"""
        metadata['registered_at'] = datetime.now().isoformat()
        filepath = self.path / f"{name}.json"
        with open(filepath, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def get_model(self, name: str) -> dict:
        """Retrieve model metadata"""
        filepath = self.path / f"{name}.json"
        if filepath.exists():
            with open(filepath) as f:
                return json.load(f)
        return {}
    
    def list_models(self) -> list:
        """List all registered models"""
        return [f.stem for f in self.path.glob("*.json")]

registry = ModelRegistry()

