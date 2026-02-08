from datetime import date as date_module, timedelta
from typing import Optional, Dict, Any, List, Tuple
import re

from flask import current_app

from app.services.space_service import SpaceService
from app.services.reservation_service import ReservationService
from app.services.class_schedule_service import ClassScheduleService


def _get_deepseek_slots(question: str, context: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Extrae intent + slots con DeepSeek. Si falla (créditos, red, etc.) retorna None."""
    try:
        from app.services.chatbot_deepseek_client import extract_slots_deepseek
        return extract_slots_deepseek(question, context)
    except Exception:
        return None


def _normalize_for_intent(text: str) -> str:
    """Quita acentos para que 'cuántas' y 'cuantas' coincidan al detectar intents."""
    if not text:
        return ""
    t = text.lower()
    for a, b in [("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ñ", "n")]:
        t = t.replace(a, b)
    return t


class ChatbotService:
    """
    Chatbot híbrido: DeepSeek interpreta la pregunta (intent + slots); si falla o sin API key
    se usa rule-based. La IA nunca decide disponibilidad; la respuesta final siempre sale de Supabase.
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

        # intento por palabras normalizadas (quitar signos de puntuación para "auditorio?" -> "auditorio")
        raw_tokens = [tok.strip(".,?!;:()") for tok in t.split() if tok]
        tokens = [tok for tok in raw_tokens if len(tok) >= 3]
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

    def _is_help_like(self, text: str) -> bool:
        t = (text or "").lower()
        patterns = [
            r"\b(hola|buenas|buenos dias|buenas tardes|buenas noches)\b",
            r"\b(quien eres|quién eres|que eres|qué eres)\b",
            r"\b(que haces|qué haces|que hace|qué hace)\b",
            r"\b(para que sirve|para qué sirve|como funciona|cómo funciona)\b",
            r"\b(que puedo hacer|qué puedo hacer|que puedo preguntar|qué puedo preguntar)\b",
            r"\b(como uso|cómo uso|como se usa|cómo se usa)\b",
            r"\b(ayuda|ayudame|ayúdame|ayudar)\b",
        ]
        return any(re.search(p, t) for p in patterns)

    def _help_reply(self, text: str) -> str:
        t = (text or "").lower()
        examples = "Ej: 'capacidad A-002', 'ocupación A-002 hoy', 'espacios libres mañana'."
        if re.search(r"\b(hola|buenas|buenos dias|buenas tardes|buenas noches)\b", t):
            return f"Hola, soy el asistente de consultas. Puedo ayudarte con capacidad, ocupación y espacios libres. {examples}"
        if re.search(r"\b(quien eres|quién eres|que eres|qué eres)\b", t):
            return f"Soy el asistente de consultas de reservas. Te ayudo con capacidad, ocupación y espacios libres. {examples}"
        if re.search(r"\b(como funciona|cómo funciona|como se usa|cómo se usa|como uso|cómo uso)\b", t):
            return f"Escribe lo que necesitas: capacidad, ocupación o espacios libres. También puedes usar los botones. {examples}"
        if re.search(r"\b(que puedo hacer|qué puedo hacer|que puedo preguntar|qué puedo preguntar)\b", t):
            return f"Puedo responder consultas rápidas sobre espacios. {examples}"
        return f"Consultas rápidas: capacidad, ocupación y espacios libres. {examples}"

    def _resolve_intent_and_slots(
        self,
        question: str,
        context: Optional[Dict[str, Any]],
    ) -> Tuple[Optional[str], Optional[str], Optional[Dict[str, Any]], Dict[str, Any], Dict[str, Any], Optional[str]]:
        """
        Resuelve intent + slots: primero DeepSeek; si falla o confianza baja, parser rule-based.
        Retorna (intent, date_str, space_obj, filters, context_merge, secondary_intent).
        """
        q = (question or "").strip()
        ql = q.lower()
        last_date = (context or {}).get("last_date")
        last_space = (context or {}).get("last_space")
        last_intent = (context or {}).get("last_intent")
        context_merge = {"last_date": last_date, "last_space": last_space, "last_intent": last_intent}
        secondary_intent: Optional[str] = None

        threshold = 0.6
        try:
            if current_app:
                threshold = float(current_app.config.get("DEEPSEEK_CHATBOT_CONFIDENCE_THRESHOLD", 0.6))
        except Exception:
            pass

        nlp = _get_deepseek_slots(question, context)
        if nlp and nlp.get("confidence", 0) >= threshold and nlp.get("intent"):
            intent = nlp.get("intent")
            secondary_intent = nlp.get("secondary_intent")
            # Siempre priorizar la fecha calculada en el servidor desde el texto del usuario
            date_str = self._parse_date(ql)
            if not date_str:
                date_str = (nlp.get("date") or "").strip() or None
                if date_str and (len(date_str) != 10 or date_str.count("-") != 2):
                    date_str = self._parse_date(date_str) or date_str
            space_name = (nlp.get("space") or "").strip() or None
            space_obj = self._find_space(space_name) if space_name else self._find_space(ql)
            filters = isinstance(nlp.get("filters"), dict) and nlp["filters"] or {}
            return (intent, date_str, space_obj, filters, context_merge, secondary_intent)

        # Fallback rule-based
        date_str = self._parse_date(ql)
        sp_check = self._find_space(ql)
        if not date_str and sp_check and last_date and last_intent == "libres" and "disponibilidad" in ql:
            date_str = last_date

        if self._is_help_like(ql):
            return ("ayuda", date_str, sp_check, {}, context_merge, None)
        # Capacidad: muchas formas de preguntar (con y sin acentos)
        ql_norm = _normalize_for_intent(ql)
        capacidad_keys = [
            "capacidad", "cuantas personas", "cuántas personas", "cuantos caben", "cuántos caben",
            "personas caben", "cuantas caben", "cuántas caben", "cuantos entran", "cuántos entran",
            "cuantas entran", "cuántas entran", "capacidad del", "capacidad de la", "capacidad de",
            "que capacidad", "qué capacidad", "cuantos personas", "cuántos personas",
            "cuantos caben", "cuál es la capacidad", "cual es la capacidad", "cuanta capacidad",
            "cuánta capacidad", "tiene capacidad", "cuantos asientos", "cuántos asientos",
        ]
        if any(k in ql_norm for k in capacidad_keys):
            return ("capacidad", date_str, self._find_space(ql), {}, context_merge, None)
        # Ocupación
        ocupacion_keys = [
            "ocupado", "ocupacion", "ocupación", "reservas", "reservado", "bloques", "horario",
            "disponibilidad", "esta libre", "está libre", "esta ocupado", "está ocupado",
            "tiene reservas", "hay reservas", "que horarios", "qué horarios", "en que horario",
            "en qué horario", "horarios del", "horarios de la", "disponible el", "disponible la",
        ]
        if any(k in ql_norm for k in ocupacion_keys):
            sp = sp_check or last_space
            if not date_str and last_intent == "libres" and last_date:
                date_str = last_date
            return ("ocupacion", date_str, sp, {}, context_merge, None)
        # Espacios libres
        libres_keys = [
            "libre", "disponible", "libres", "disponibles", "disponibilidad",
            "que espacios", "qué espacios", "espacios libres", "espacios disponibles",
            "que hay libre", "qué hay libre", "cuales estan libres", "cuáles están libres",
            "que aulas", "qué aulas", "aulas libres", "salas libres",
        ]
        is_libres = any(k in ql_norm for k in libres_keys) or (last_intent == "libres")
        if is_libres:
            sp_specific = sp_check or self._find_space(ql)
            if not date_str and last_intent == "libres" and last_date:
                date_str = last_date
            filters = {}
            if "laboratorio" in ql:
                filters["type"] = "laboratorio"
            elif "aula" in ql:
                filters["type"] = "aula"
            elif "auditorio" in ql:
                filters["type"] = "auditorio"
            if "piso 1" in ql or "piso1" in ql:
                filters["floor"] = "piso_1"
            elif "piso 2" in ql or "piso2" in ql:
                filters["floor"] = "piso_2"
            if "capacidad 30" in ql or "30+" in ql:
                filters["min_capacity"] = 30
            return ("libres", date_str, sp_specific, filters, context_merge, None)
        return (None, date_str, sp_check, {}, context_merge, None)

    def answer(self, question: str, context: Optional[Dict[str, Any]] = None, page: int = 1, page_size: int = 8) -> Dict[str, Any]:
        q = (question or "").strip()
        if not q:
            return {"answer": "No entendí la pregunta.", "data": {}}
        ql = q.lower()
        last_date = (context or {}).get("last_date")
        last_space = (context or {}).get("last_space")
        last_intent = (context or {}).get("last_intent")

        intent, date_str, space_obj, filters, ctx_merge, secondary_intent = self._resolve_intent_and_slots(question, context)
        last_date = ctx_merge.get("last_date")
        last_space = ctx_merge.get("last_space")
        last_intent = ctx_merge.get("last_intent")

        def _append_secondary_hint(msg: str) -> str:
            if not secondary_intent or secondary_intent == intent:
                return msg
            hint = {"capacidad": "capacidad del espacio", "ocupacion": "ocupación/horarios", "libres": "espacios libres"}
            label = hint.get(secondary_intent, secondary_intent)
            return f"{msg}\n\nTambién preguntaste por {label}. Puedes preguntarlo en otro mensaje."

        if intent == "ayuda":
            return {
                "answer": self._help_reply(ql),
                "data": {},
            }

        if intent == "capacidad":
            sp = space_obj or self._find_space(ql)
            if not sp:
                return {"answer": "No encontré el espacio, especifica el nombre (ej: A-002).", "data": {}}
            answer = (
                f"{sp.get('name')}: capacidad {sp.get('capacity', 'desconocida')}, "
                f"tipo {sp.get('type', '-')}, piso {sp.get('floor', '-')}"
            )
            return {"answer": _append_secondary_hint(answer), "data": {"space": sp}, "context": {"last_space": sp}}

        if intent == "ocupacion":
            sp = space_obj or last_space
            if not sp:
                return {"answer": "No encontré el espacio, especifica el nombre (ej: A-002).", "data": {}}
            if not date_str and last_intent == "libres" and last_date:
                date_str = last_date
            if not date_str:
                if last_space and last_space.get("id") == sp.get("id") and last_date:
                    date_str = last_date
                else:
                    return self._clarify("¿Para qué fecha? (hoy, mañana, 29/01/2026)", [{"label": "Hoy", "value": "hoy"}, {"label": "Mañana", "value": "mañana"}])
            if not date_str or len(date_str) < 8:
                return self._clarify("¿Para qué fecha? (hoy, mañana, 29/01/2026)", [{"label": "Hoy", "value": "hoy"}, {"label": "Mañana", "value": "mañana"}])
            occ = self._get_occupancy(sp["id"], date_str)
            if not occ["all"]:
                ans = f"{sp.get('name')} está libre el {date_str} (todo el día)."
                return {"answer": _append_secondary_hint(ans), "data": occ, "context": {"last_date": date_str, "last_space": sp}}
            free_blocks = occ.get("free_blocks", [])
            if free_blocks and len(free_blocks) == 1 and free_blocks[0] == ("07:00", "22:00"):
                ans = f"{sp.get('name')} está libre el {date_str} (todo el día: 07:00-22:00)."
                return {"answer": _append_secondary_hint(ans), "data": occ, "context": {"last_date": date_str, "last_space": sp}}
            if free_blocks:
                libres_txt = "; ".join([f"{a}-{b}" for a, b in free_blocks])
                occ_text = f"Bloques ocupados en {sp.get('name')} el {date_str}: {occ['summary']}. Libre: {libres_txt}"
            else:
                occ_text = f"Bloques ocupados en {sp.get('name')} el {date_str}: {occ['summary']}"
            return {"answer": _append_secondary_hint(occ_text), "data": occ, "context": {"last_date": date_str, "last_space": sp}}

        if intent == "libres":
            sp_specific = space_obj if space_obj else self._find_space(ql)
            if sp_specific:
                if not date_str and last_intent == "libres" and last_date:
                    date_str = last_date
                if not date_str:
                    res = self._clarify("¿Para qué fecha? (hoy, mañana, 29/01/2026)", [{"label": "Hoy", "value": "hoy"}, {"label": "Mañana", "value": "mañana"}])
                    res["context"] = {"last_intent": "libres", "last_space": sp_specific}
                    return res
                occ = self._get_occupancy(sp_specific["id"], date_str)
                if not occ["all"]:
                    ans = f"{sp_specific.get('name')} está libre el {date_str}."
                    return {"answer": _append_secondary_hint(ans), "data": occ, "context": {"last_date": date_str, "last_space": sp_specific, "last_intent": "libres"}}
                fb = occ.get("free_blocks", [])
                if fb and len(fb) == 1 and fb[0] == ("07:00", "22:00"):
                    ans = f"{sp_specific.get('name')} está libre el {date_str} (todo el día: 07:00-22:00)."
                    return {"answer": _append_secondary_hint(ans), "data": occ, "context": {"last_date": date_str, "last_space": sp_specific, "last_intent": "libres"}}
                libres_txt = "; ".join([f"{a}-{b}" for a, b in occ.get("free_blocks", [])]) or "sin bloques libres"
                answer = f"{sp_specific.get('name')} ({date_str}): Ocupado: {occ['summary']}. Libre: {libres_txt}"
                return {"answer": _append_secondary_hint(answer), "data": occ, "context": {"last_date": date_str, "last_space": sp_specific, "last_intent": "libres"}}
            if not date_str:
                res = self._clarify("¿Para qué fecha quieres ver espacios libres? (hoy, mañana, 29/01/2026)", [{"label": "Hoy", "value": "hoy"}, {"label": "Mañana", "value": "mañana"}])
                res["context"] = {"last_intent": "libres"}
                return res
            free = self._get_free_spaces(date_str)
            if filters.get("type") == "laboratorio":
                free = [s for s in free if (s.get("type") or "").lower() == "laboratorio"]
            elif filters.get("type") == "aula":
                free = [s for s in free if (s.get("type") or "").lower() == "aula"]
            elif filters.get("type") == "auditorio":
                free = [s for s in free if (s.get("type") or "").lower() == "auditorio"]
            if filters.get("floor") == "piso_1":
                free = [s for s in free if (s.get("floor") or "").lower() == "piso_1"]
            elif filters.get("floor") == "piso_2":
                free = [s for s in free if (s.get("floor") or "").lower() == "piso_2"]
            if filters.get("min_capacity"):
                free = [s for s in free if s.get("capacity", 0) >= filters["min_capacity"]]
            total = len(free)
            if not free:
                return {"answer": f"No encontré espacios libres en {date_str}.", "data": {}}
            order = ["planta_baja", "piso_1", "piso_2", "sin_piso"]
            labels = {"planta_baja": "Planta baja", "piso_1": "Piso 1", "piso_2": "Piso 2", "sin_piso": "Sin piso"}
            grouped_lines = []
            for floor in order:
                group = [s for s in free if (s.get("floor") or "sin_piso") == floor]
                if not group:
                    continue
                items = "\n".join([f"  • {s.get('name','-')} (cap {s.get('capacity','-')})" for s in group])
                grouped_lines.append(f"{labels.get(floor, floor)}:\n{items}")
            answer = f"Libres el {date_str} ({total}):\n" + "\n".join(grouped_lines)
            return {
                "answer": _append_secondary_hint(answer),
                "data": {"free_spaces": free, "total": total, "ask_specific": True},
                "context": {"last_date": date_str, "last_intent": "libres"},
            }

        # Sin intent: pregunta que no es sobre espacios/reservas o no se entendió
        return {
            "answer": "Solo puedo ayudarte con consultas de espacios: capacidad de un aula, ocupación en una fecha o espacios libres. Ej: 'capacidad A-002', 'ocupación A-002 mañana', 'espacios libres el viernes'. ¿Qué necesitas?",
            "data": {},
        }
