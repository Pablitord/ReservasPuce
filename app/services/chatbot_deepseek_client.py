"""
Cliente DeepSeek para interpretar la pregunta del usuario (intent + slots).
Solo interpreta; la disponibilidad/respuesta final siempre la decide Supabase.
Si DeepSeek falla (créditos, red, timeout) retorna None y el chatbot usa rule-based.
"""

import json
import urllib.request
import urllib.error
from typing import Optional, Dict, Any


SYSTEM_PROMPT = """Eres un clasificador para un sistema de reservas de espacios.
Tu única tarea es interpretar la pregunta del usuario y devolver un JSON con:
- intent: uno de "capacidad", "ocupacion", "libres", "ayuda", o "unknown" si no aplica.
- date: fecha en YYYY-MM-DD si el usuario menciona una (hoy, mañana, 5 de febrero, 29/01/2026, etc.). null si no hay.
- space: nombre del espacio/aula si se menciona (ej: A-002, A002, aula 107). null si no.
- filters: objeto con type (aula|laboratorio|auditorio), floor (piso_1|piso_2|planta_baja), min_capacity (número). Solo incluir keys que el usuario pida. {} si ninguno.
- confidence: número entre 0 y 1. Usa confianza baja (ej. 0.3) si la pregunta no es sobre reservas/espacios o es ambigua.
- secondary_intent: si el usuario pide DOS cosas distintas en una frase (ej. "capacidad del A-002 y cuándo está libre"), pon aquí el segundo intent ("capacidad", "ocupacion", "libres"). null si solo pide una cosa.

Reglas:
- capacidad = preguntar cuántas personas caben o datos del espacio.
- ocupacion = preguntar si está ocupado, horarios, bloques, reservas de un espacio en una fecha.
- libres = listar espacios libres (puede ser en una fecha; opcionalmente filtrar por tipo/piso).
- ayuda = pedir ayuda o qué puede hacer el bot.
- unknown = la pregunta no es sobre espacios, reservas, capacidad u ocupación (ej. tiempo, deportes, otra cosa). Pon confidence baja.
Responde ÚNICAMENTE con un JSON válido, sin markdown ni texto extra."""


def _build_messages(question: str, context: Optional[Dict[str, Any]]) -> list:
    ctx = context or {}
    user_content = f"Pregunta del usuario: {question}"
    if ctx.get("last_date") or ctx.get("last_intent"):
        user_content += f"\nContexto: last_date={ctx.get('last_date')}, last_intent={ctx.get('last_intent')}"
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]


def extract_slots_deepseek(question: str, context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """
    Llama a DeepSeek para extraer intent + slots. Retorna None si no hay API key,
    falla la red, se acaban créditos (429) o la respuesta no es JSON válido.
    """
    try:
        from flask import current_app
        api_key = (current_app.config.get("DEEPSEEK_API_KEY") or "").strip() if current_app else ""
        url = (current_app.config.get("DEEPSEEK_API_URL") or "https://api.deepseek.com/v1/chat/completions").strip()
    except RuntimeError:
        api_key = ""
        url = "https://api.deepseek.com/v1/chat/completions"
    if not api_key:
        return None

    payload = {
        "model": "deepseek-chat",
        "messages": _build_messages(question, context),
        "response_format": {"type": "json_object"},
        "max_tokens": 256,
        "temperature": 0.1,
    }
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
        out = json.loads(body)
        choice = (out.get("choices") or [None])[0]
        if not choice:
            return None
        content = (choice.get("message") or {}).get("content")
        if not content or not content.strip():
            return None
        # Por si DeepSeek envuelve en markdown
        raw = content.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        parsed = json.loads(raw)
        intent = (parsed.get("intent") or "").strip().lower() or None
        if intent == "unknown":
            intent = None
        if intent and intent not in ("capacidad", "ocupacion", "libres", "ayuda"):
            intent = None
        date_val = parsed.get("date")
        if date_val is not None and isinstance(date_val, str):
            date_val = date_val.strip() or None
        else:
            date_val = None
        space_val = parsed.get("space")
        if space_val is not None and isinstance(space_val, str):
            space_val = space_val.strip() or None
        else:
            space_val = None
        filters = parsed.get("filters")
        if not isinstance(filters, dict):
            filters = {}
        confidence = float(parsed.get("confidence", 0.0))
        sec = (parsed.get("secondary_intent") or "").strip().lower() or None
        if sec and sec not in ("capacidad", "ocupacion", "libres", "ayuda"):
            sec = None
        return {
            "intent": intent,
            "date": date_val,
            "space": space_val,
            "filters": filters,
            "confidence": max(0.0, min(1.0, confidence)),
            "secondary_intent": sec,
        }
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError, TypeError, ValueError):
        return None
