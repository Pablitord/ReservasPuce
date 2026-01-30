from datetime import date as date_module, timedelta
from typing import Optional, Dict, Any, List, Tuple
import re

from app.services.space_service import SpaceService
from app.services.reservation_service import ReservationService
from app.services.class_schedule_service import ClassScheduleService


class ChatbotService:
    """
    Chatbot rule-based básico para consultas de disponibilidad, ocupación y capacidad.
    """

    def __init__(self):
        self.space_service = SpaceService()
        self.reservation_service = ReservationService()
        self.class_schedule_service = ClassScheduleService()
        self.months = {
            "enero": 1, "ene": 1,
            "febrero": 2, "feb": 2,
            "marzo": 3, "mar": 3,
            "abril": 4, "abr": 4,
            "mayo": 5, "may": 5,
            "junio": 6, "jun": 6,
            "julio": 7, "jul": 7,
            "agosto": 8, "ago": 8,
            "septiembre": 9, "sep": 9, "set": 9,
            "octubre": 10, "oct": 10,
            "noviembre": 11, "nov": 11,
            "diciembre": 12, "dic": 12,
        }

    def _parse_date(self, text: str) -> Optional[str]:
        t = text.lower()
        if "hoy" in t:
            return date_module.today().isoformat()
        if "mañana" in t:
            return (date_module.today() + timedelta(days=1)).isoformat()
        if "pasado mañana" in t:
            return (date_module.today() + timedelta(days=2)).isoformat()
        # YYYY-MM-DD exacto (buscar primero para evitar falsos positivos)
        for token in t.replace("/", "-").split():
            if len(token) == 10 and token[4] == "-" and token[7] == "-":
                try:
                    # Validar que sea una fecha válida
                    parts = token.split("-")
                    if len(parts) == 3:
                        y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
                        if 2000 <= y <= 2100 and 1 <= m <= 12 and 1 <= d <= 31:
                            return date_module(y, m, d).isoformat()
                except Exception:
                    pass
        # "29 de enero" etc. - buscar en cualquier parte del texto
        m2 = re.search(r"(\d{1,2})\s+de\s+([a-záéíóúñ]+)", t)
        if m2:
            d = int(m2.group(1))
            mo_name = m2.group(2).replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
            mo = self.months.get(mo_name)
            if mo:
                y = date_module.today().year
                try:
                    parsed_date = date_module(y, mo, d)
                    # Si la fecha es del pasado, asumir año siguiente
                    if parsed_date < date_module.today():
                        parsed_date = date_module(y + 1, mo, d)
                    return parsed_date.isoformat()
                except Exception:
                    pass
        # "miércoles 28"
        m3 = re.search(r"(lunes|martes|miercoles|miércoles|jueves|viernes|sabado|sábado|domingo)\s+(\d{1,2})", t)
        if m3:
            d = int(m3.group(2))
            y = date_module.today().year
            mo = date_module.today().month
            try:
                cand = date_module(y, mo, d)
                if cand < date_module.today():
                    if mo == 12:
                        cand = date_module(y + 1, 1, d)
                    else:
                        cand = date_module(y, mo + 1, d)
                return cand.isoformat()
            except Exception:
                pass
        # dd/mm/yyyy o dd-mm-yyyy (solo si no parece ser parte de un nombre de espacio)
        # Evitar interpretar "A010" o "A-002" como fechas
        # Buscar patrones que NO empiecen con letra seguida de número
        m = re.search(r"(?<![a-z])(\d{1,2})[\/\-](\d{1,2})(?:[\/\-](\d{2,4}))?(?![a-z0-9])", t)
        if m:
            d = int(m.group(1))
            mo = int(m.group(2))
            y = int(m.group(3)) if m.group(3) else date_module.today().year
            if y < 100:  # yy -> 20yy
                y = 2000 + y
            # Validar que sea una fecha razonable
            if 2000 <= y <= 2100 and 1 <= mo <= 12 and 1 <= d <= 31:
                try:
                    return date_module(y, mo, d).isoformat()
                except Exception:
                    pass
        return None

    def _find_space(self, text: str) -> Optional[Dict[str, Any]]:
        spaces = self.space_service.get_all_spaces()
        def norm(s: str) -> str:
            return re.sub(r"[^a-z0-9]", "", (s or "").lower())
        t = (text or "").lower()
        t_norm = norm(text)

        # coincidencia exacta o contenida con normalización
        for sp in spaces:
            name = (sp.get("name") or "").lower()
            if name in t or t in name or name.startswith(t) or t.startswith(name):
                return sp
            if t_norm and t_norm == norm(name):
                return sp
            if t_norm and t_norm in norm(name):
                return sp

        # intento por palabras normalizadas
        tokens = [tok for tok in t.split() if tok and len(tok) >= 3]
        for sp in spaces:
            name = (sp.get("name") or "").lower()
            name_norm = norm(name)
            if any(tok and tok in name for tok in tokens):
                return sp
            if any(tok and norm(tok) in name_norm for tok in tokens):
                return sp
        return None

    def _format_intervals(self, items: List[Tuple[str, str, str]]) -> str:
        # items: (tipo, start, end)
        if not items:
            return "No hay ocupación en ese día."
        parts = []
        for kind, start, end in sorted(items, key=lambda x: x[1]):
            parts.append(f"{start}-{end} ({kind})")
        return "; ".join(parts)

    def _get_occupancy(self, space_id: str, date_str: str) -> Dict[str, Any]:
        # Clases
        weekday = None
        try:
            weekday = date_module.fromisoformat(date_str).weekday()
        except Exception:
            weekday = None
        schedules = self.class_schedule_service.get_schedules(space_id, weekday) if weekday is not None else []
        class_intervals = [
            ("clase", str(s.get("start_time"))[:5], str(s.get("end_time"))[:5]) for s in schedules
        ]
        # Reservas (pending/approved)
        reservations = self.reservation_service.get_reservations_by_space_and_date(space_id, date_str)
        res_intervals = [
            ("reserva", str(r.get("start_time"))[:5], str(r.get("end_time"))[:5])
            for r in reservations
            if r.get("status") in ["pending", "approved"]
        ]
        all_intervals = class_intervals + res_intervals
        # Bloques libres en rango 07:00-22:00
        day_start = "07:00"
        day_end = "22:00"
        intervals_sorted = sorted(all_intervals, key=lambda x: x[1])
        free_blocks = []
        cursor = day_start
        for _, s, e in intervals_sorted:
            if s > cursor:
                free_blocks.append((cursor, s))
            if e > cursor:
                cursor = e
        if cursor < day_end:
            free_blocks.append((cursor, day_end))
        return {
            "classes": class_intervals,
            "reservations": res_intervals,
            "all": all_intervals,
            "summary": self._format_intervals(all_intervals),
            "free_blocks": free_blocks,
            "classes_txt": "; ".join([f"{s}-{e}" for _, s, e in class_intervals]) if class_intervals else "",
            "reservas_txt": "; ".join([f"{s}-{e}" for _, s, e in res_intervals]) if res_intervals else "",
        }

    def _get_free_spaces(self, date_str: str) -> List[Dict[str, Any]]:
        spaces = self.space_service.get_all_spaces()
        weekday = None
        try:
            weekday = date_module.fromisoformat(date_str).weekday()
        except Exception:
            weekday = None
        free = []
        for sp in spaces:
            sid = sp.get("id")
            schedules = self.class_schedule_service.get_schedules(sid, weekday) if weekday is not None else []
            if schedules:
                continue
            reservations = self.reservation_service.get_reservations_by_space_and_date(sid, date_str)
            active = [r for r in reservations if r.get("status") in ["pending", "approved"]]
            if not active:
                free.append(sp)
        return free

    def _clarify(self, message: str, chips: List[Dict[str, str]]):
        return {"answer": message, "type": "clarify", "chips": chips, "data": {}}

    def answer(self, question: str, context: Optional[Dict[str, Any]] = None, page: int = 1, page_size: int = 8) -> Dict[str, Any]:
        q = (question or "").strip()
        if not q:
            return {"answer": "No entendí la pregunta.", "data": {}}
        ql = q.lower()
        last_date = (context or {}).get("last_date")
        last_space = (context or {}).get("last_space")
        last_intent = (context or {}).get("last_intent")
        is_libres_intent = any(k in ql for k in ["libre", "disponible", "libres", "disponibles", "disponibilidad"]) or (last_intent == "libres")
        
        # Primero intentar parsear la fecha de la pregunta actual
        # IMPORTANTE: Parsear ANTES de buscar el espacio para evitar interferencias
        date_str = self._parse_date(ql)
        
        # Buscar espacio después de parsear la fecha
        sp_check = self._find_space(ql)
        
        # Solo usar last_date del contexto si:
        # 1. No se encontró fecha en la pregunta actual Y
        # 2. Es parte del mismo flujo continuo (disponibilidad_especifica después de espacios libres)
        if not date_str:
            # Solo usar last_date si es parte del flujo continuo de "disponibilidad_especifica"
            # (cuando se pregunta por un espacio específico después de listar espacios libres)
            if sp_check and last_date and last_intent == "libres" and "disponibilidad" in ql:
                date_str = last_date
            # NO usar last_date en otros casos - si no hay fecha, pedirla

        # Ayuda
        if any(k in ql for k in ["ayuda", "ayudar", "qué haces", "que haces", "ayúdame", "ayudame"]):
            return {
                "answer": "Consultas rápidas: capacidad, ocupación y espacios libres. Ej: 'capacidad A-002', 'ocupación A-002 hoy', 'espacios libres mañana'.",
                "data": {},
            }

        # Intent: capacidad
        if any(k in ql for k in ["capacidad", "cuántas personas", "cuantos caben", "cuántos caben"]):
            sp = self._find_space(ql)
            if not sp:
                return {"answer": "No encontré el espacio, especifica el nombre (ej: A-002).", "data": {}}
            answer = (
                f"{sp.get('name')}: capacidad {sp.get('capacity', 'desconocida')}, "
                f"tipo {sp.get('type', '-')}, piso {sp.get('floor', '-')}"
            )
            return {"answer": answer, "data": {"space": sp}, "context": {"last_space": sp}}

        # Intent: ocupación / reservas / disponibilidad
        if any(k in ql for k in ["ocupado", "ocupación", "reservas", "reservado", "bloques", "horario", "disponibilidad"]):
            sp = self._find_space(ql) or last_space
            if not sp:
                return {"answer": "No encontré el espacio, especifica el nombre (ej: A-002).", "data": {}}
            # Si es parte del flujo de "libres" (después de listar espacios libres), usar la fecha guardada
            if not date_str and last_intent == "libres" and last_date:
                date_str = last_date
            # Si no hay fecha parseada ni en contexto, pedirla
            if not date_str:
                # Solo usar last_date si es parte del mismo flujo continuo (no nuevo flujo)
                if last_space and last_space.get("id") == sp.get("id") and last_date:
                    date_str = last_date
                else:
                    return self._clarify("¿Para qué fecha? (hoy, mañana, 29/01/2026)", [{"label": "Hoy", "value": "hoy"}, {"label": "Mañana", "value": "mañana"}])
            # Validar que date_str sea una fecha válida
            if not date_str or len(date_str) < 8:
                return self._clarify("¿Para qué fecha? (hoy, mañana, 29/01/2026)", [{"label": "Hoy", "value": "hoy"}, {"label": "Mañana", "value": "mañana"}])
            occ = self._get_occupancy(sp["id"], date_str)
            if not occ["all"]:
                return {"answer": f"{sp.get('name')} está libre el {date_str} (todo el día).", "data": occ, "context": {"last_date": date_str, "last_space": sp}}
            free_blocks = occ.get("free_blocks", [])
            if free_blocks and len(free_blocks) == 1 and free_blocks[0] == ("07:00", "22:00"):
                return {
                    "answer": f"{sp.get('name')} está libre el {date_str} (todo el día: 07:00-22:00).",
                    "data": occ,
                    "context": {"last_date": date_str, "last_space": sp},
                }
            if free_blocks:
                libres_txt = "; ".join([f"{a}-{b}" for a, b in free_blocks])
                occ_text = f"Bloques ocupados en {sp.get('name')} el {date_str}: {occ['summary']}. Libre: {libres_txt}"
            else:
                occ_text = f"Bloques ocupados en {sp.get('name')} el {date_str}: {occ['summary']}"
            return {
                "answer": occ_text,
                "data": occ,
                "context": {"last_date": date_str, "last_space": sp},
            }

        # Intent: libres
        if is_libres_intent:
            # solo tomar espacio si viene en esta consulta, no por contexto
            # Reutilizar sp_check si ya lo tenemos, sino buscarlo
            sp_specific = sp_check if sp_check else self._find_space(ql)
            if sp_specific:
                # Si es parte del flujo continuo de "libres" (después de listar espacios libres), usar la fecha guardada
                if not date_str and last_intent == "libres" and last_date:
                    date_str = last_date
                # Si no hay fecha parseada ni en contexto, pedirla
                if not date_str:
                    res = self._clarify("¿Para qué fecha? (hoy, mañana, 29/01/2026)", [{"label": "Hoy", "value": "hoy"}, {"label": "Mañana", "value": "mañana"}])
                    res["context"] = {"last_intent": "libres", "last_space": sp_specific}
                    return res
                occ = self._get_occupancy(sp_specific["id"], date_str)
                if not occ["all"]:
                    # Mantener el contexto del flujo de "libres" con la fecha
                    return {"answer": f"{sp_specific.get('name')} está libre el {date_str}.", "data": occ, "context": {"last_date": date_str, "last_space": sp_specific, "last_intent": "libres"}}
                fb = occ.get("free_blocks", [])
                if fb and len(fb) == 1 and fb[0] == ("07:00", "22:00"):
                    return {"answer": f"{sp_specific.get('name')} está libre el {date_str} (todo el día: 07:00-22:00).", "data": occ, "context": {"last_date": date_str, "last_space": sp_specific, "last_intent": "libres"}}
                libres_txt = "; ".join([f"{a}-{b}" for a, b in occ.get("free_blocks", [])]) or "sin bloques libres"
                answer = f"{sp_specific.get('name')} ({date_str}): Ocupado: {occ['summary']}. Libre: {libres_txt}"
                # Mantener el contexto del flujo de "libres" con la fecha
                return {"answer": answer, "data": occ, "context": {"last_date": date_str, "last_space": sp_specific, "last_intent": "libres"}}
            if not date_str:
                res = self._clarify("¿Para qué fecha quieres ver espacios libres? (hoy, mañana, 29/01/2026)", [{"label": "Hoy", "value": "hoy"}, {"label": "Mañana", "value": "mañana"}])
                res["context"] = {"last_intent": "libres"}
                return res
            # filtros simples por tipo/piso/capacidad
            free = self._get_free_spaces(date_str)
            # type filter
            if "laboratorio" in ql:
                free = [sp for sp in free if (sp.get("type") or "").lower() == "laboratorio"]
            if "aula" in ql:
                free = [sp for sp in free if (sp.get("type") or "").lower() == "aula"]
            if "auditorio" in ql:
                free = [sp for sp in free if (sp.get("type") or "").lower() == "auditorio"]
            if "piso 1" in ql or "piso1" in ql:
                free = [sp for sp in free if (sp.get("floor") or "").lower() == "piso_1"]
            if "piso 2" in ql or "piso2" in ql:
                free = [sp for sp in free if (sp.get("floor") or "").lower() == "piso_2"]
            if "capacidad 30" in ql or "30+" in ql:
                free = [sp for sp in free if sp.get("capacity", 0) >= 30]
            total = len(free)
            if not free:
                return {"answer": f"No encontré espacios libres en {date_str}.", "data": {}}
            # agrupar por piso
            order = ["planta_baja", "piso_1", "piso_2", "sin_piso"]
            labels = {
                "planta_baja": "Planta baja",
                "piso_1": "Piso 1",
                "piso_2": "Piso 2",
                "sin_piso": "Sin piso",
            }
            grouped_lines = []
            for floor in order:
                group = [sp for sp in free if (sp.get("floor") or "sin_piso") == floor]
                if not group:
                    continue
                items = "\n".join([f"  • {sp.get('name','-')} (cap {sp.get('capacity','-')})" for sp in group])
                grouped_lines.append(f"{labels.get(floor, floor)}:\n{items}")
            answer = f"Libres el {date_str} ({total}):\n" + "\n".join(grouped_lines)
            # IMPORTANTE: Guardar la fecha y el intent "libres" para usar en consultas específicas posteriores
            return {
                "answer": answer,
                "data": {"free_spaces": free, "total": total, "ask_specific": True},
                "context": {"last_date": date_str, "last_intent": "libres"},
            }

        # Fallback
        return {"answer": "Consultas rápidas: 'capacidad A-002', 'ocupación A-002 hoy', 'espacios libres mañana'.", "data": {}}
