from jsonpath_ng import parse
from copy import deepcopy
from typing import Any

def _normalize_expr(e: str) -> str:
    return e if e.startswith("$") else "$." + e

def _prune_empty_dicts(obj: Any) -> Any:
    if isinstance(obj, dict):
        new = {}
        for k, v in obj.items():
            cleaned = _prune_empty_dicts(v)
            if not (isinstance(cleaned, dict) and len(cleaned) == 0):
                new[k] = cleaned
        return new
    if isinstance(obj, list):
        return [_prune_empty_dicts(i) for i in obj]
    return obj

def omit(obj: dict, *paths: str, remove_empty: bool = True) -> dict:
    """
    Supprime toutes les correspondances JSONPath fournies en arguments.
    Usage:
      omit(data, "adresse.ville")
      omit(data, "adresse.ville", "adresse.rue")
      omit(data, "$.items[*].adresse.ville", "id")
    """
    out = deepcopy(obj)
    for p in paths:
        expr = _normalize_expr(p)
        jsonpath = parse(expr)
        matches = list(jsonpath.find(out))
        for match in matches:
            parent = out
            path = match.full_path
            text = str(path)
            segments = []
            for part in text.split("."):
                if part.startswith("[") and part.endswith("]"):
                    segments.append(part[1:-1])
                else:
                    segments.append(part)
            # atteindre le parent du noeud ciblé
            for seg in segments[:-1]:
                if isinstance(parent, list):
                    try:
                        idx = int(seg)
                        parent = parent[idx]
                    except Exception:
                        parent = {}
                        break
                elif isinstance(parent, dict):
                    parent = parent.get(seg, {})
                else:
                    parent = {}
                    break
            last = segments[-1]
            if isinstance(parent, dict):
                parent.pop(last, None)
            elif isinstance(parent, list):
                try:
                    idx = int(last)
                    if 0 <= idx < len(parent):
                        parent[idx] = {}
                except Exception:
                    pass
    if remove_empty:
        out = _prune_empty_dicts(out)
    return out