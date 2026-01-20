from app.repositories.supabase.space_repo import SpaceRepository
from typing import List, Dict, Any, Optional

class SpaceService:
    """Servicio para operaciones de espacios"""
    
    def __init__(self):
        self.space_repo = SpaceRepository()

    def _resolve_floor(self, space: Dict[str, Any]) -> str:
        """Resuelve piso basado en floor o en el prefijo del nombre"""
        floor = space.get('floor')
        if floor:
            return floor
        name = (space.get('name') or '').upper()
        if name.startswith('A-0'):
            return 'planta_baja'
        if name.startswith('A-1'):
            return 'piso_1'
        if name.startswith('A-2'):
            return 'piso_2'
        if (space.get('type') or '').lower() == 'auditorio':
            return 'planta_baja'
        return 'sin_piso'
    
    def get_all_spaces(self) -> List[Dict[str, Any]]:
        """Obtiene todos los espacios"""
        return self.space_repo.get_all_spaces()
    
    def get_space_by_id(self, space_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un espacio por ID"""
        return self.space_repo.get_space_by_id(space_id)
    
    def get_spaces_by_type(self, space_type: str) -> List[Dict[str, Any]]:
        """Obtiene espacios por tipo"""
        return self.space_repo.get_spaces_by_type(space_type)
    
    def get_spaces_grouped_by_floor(self) -> List[Dict[str, Any]]:
        """Obtiene espacios agrupados por piso para selects"""
        spaces = self.space_repo.get_all_spaces()
        floor_order = ['planta_baja', 'piso_1', 'piso_2']
        floor_labels = {
            'planta_baja': 'Planta baja',
            'piso_1': 'Piso 1',
            'piso_2': 'Piso 2'
        }
        grouped = {floor: [] for floor in floor_order}
        other_spaces = []
        for space in spaces:
            floor = self._resolve_floor(space)
            space['resolved_floor'] = floor
            if floor in grouped:
                grouped[floor].append(space)
            else:
                other_spaces.append(space)
        
        result = []
        for floor in floor_order:
            result.append({
                'key': floor,
                'label': floor_labels.get(floor, floor),
                'spaces': sorted(grouped[floor], key=lambda s: s.get('name', ''))
            })
        if other_spaces:
            result.append({
                'key': 'sin_piso',
                'label': 'Sin piso',
                'spaces': sorted(other_spaces, key=lambda s: s.get('name', ''))
            })
        return result
    
    def create_space(
        self,
        name: str,
        type: str,
        capacity: int,
        description: str = '',
        floor: str = 'planta_baja'
    ) -> Optional[Dict[str, Any]]:
        """Crea un nuevo espacio"""
        return self.space_repo.create_space(name, type, capacity, description, floor)
