from app.repositories.supabase.space_repo import SpaceRepository
from typing import List, Dict, Any, Optional

class SpaceService:
    """Servicio para operaciones de espacios"""
    
    def __init__(self):
        self.space_repo = SpaceRepository()
    
    def get_all_spaces(self) -> List[Dict[str, Any]]:
        """Obtiene todos los espacios"""
        return self.space_repo.get_all_spaces()
    
    def get_space_by_id(self, space_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un espacio por ID"""
        return self.space_repo.get_space_by_id(space_id)
    
    def get_spaces_by_type(self, space_type: str) -> List[Dict[str, Any]]:
        """Obtiene espacios por tipo"""
        return self.space_repo.get_spaces_by_type(space_type)
    
    def create_space(self, name: str, type: str, capacity: int, description: str = '') -> Optional[Dict[str, Any]]:
        """Crea un nuevo espacio"""
        return self.space_repo.create_space(name, type, capacity, description)
