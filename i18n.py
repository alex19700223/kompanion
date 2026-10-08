import json
import os

LOCALES_DIR = os.path.join(os.path.dirname(__file__), "locales")
DEFAULT_LANGUAGE = "de"
SUPPORTED_LANGUAGES = ["ru", "de", "en", "fr", "uk", "tr", "ar", "it"]

_cache: dict = {}


def _load(lang: str) -> dict:
    if lang in _cache:
        return _cache[lang]
    path = os.path.join(LOCALES_DIR, f"{lang}.json")
    if not os.path.exists(path):
        path = os.path.join(LOCALES_DIR, f"{DEFAULT_LANGUAGE}.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    _cache[lang] = data
    return data


def t(key: str, lang: str = DEFAULT_LANGUAGE) -> str:
    if lang not in SUPPORTED_LANGUAGES:
        lang = DEFAULT_LANGUAGE
    data = _load(lang)
    return data.get(key, key)
