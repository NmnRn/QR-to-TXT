"""
Minimal i18n layer.

Call set_language("tr") or set_language("en") once at startup.
Then use tr("key") everywhere to get the localised string.
Language change takes effect after app restart.
"""

from ._en import STRINGS as _EN

_strings: dict[str, str] = dict(_EN)

LANGUAGES: dict[str, str] = {
    "en": "English",
    "tr": "Türkçe",
}


def set_language(lang: str) -> None:
    global _strings
    if lang == "tr":
        from ._tr import STRINGS as _TR
        _strings = dict(_TR)
    else:
        _strings = dict(_EN)


def tr(key: str) -> str:
    return _strings.get(key, key)
