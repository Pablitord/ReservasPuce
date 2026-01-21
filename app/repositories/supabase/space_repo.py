from app.repositories.supabase.client import get_supabase_client
from typing import Optional, Dict, Any, List

class SpaceRepository:
    """Repositorio para operaciones de espacios"""
    
    def __init__(self):
        self.client = get_supabase_client()
        self.table = 'spaces'
    
    def get_all_spaces(self) -> List[Dict[str, Any]]:
        """Obtiene todos los espacios"""
        try:
            response = self.client.table(self.table).select('*').order('name').execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error obteniendo espacios: {e}")
            return []
    
    def get_space_by_id(self, space_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un espacio por ID"""
        try:
            response = self.client.table(self.table).select('*').eq('id', space_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error obteniendo espacio por ID: {e}")
            return None
    
    def get_spaces_by_type(self, space_type: str) -> List[Dict[str, Any]]:
        """Obtiene espacios por tipo (aula, laboratorio, auditorio)"""
        try:
            response = self.client.table(self.table).select('*').eq('type', space_type).order('name').execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error obteniendo espacios por tipo: {e}")
            return []
    
    def create_space(
        self,
        name: str,
        type: str,
        capacity: int,
        description: str = '',
        floor: str = 'planta_baja',
        lab_category: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Crea un nuevo espacio"""
        try:
            data = {
                'name': name,
                'type': type,
                'floor': floor,
                'capacity': capacity,
                'description': description
            }
            if lab_category:
                data['lab_category'] = lab_category
            response = self.client.table(self.table).insert(data).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error creando espacio: {e}")
            return None
