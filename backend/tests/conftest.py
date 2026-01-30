import pytest
import sys
import json
import difflib
import re
from heapq import nlargest
import psycopg2
import os

# couleurs
GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# stockage global
RESULTS = {"passed": 0, "failed": 0, "skipped": 0}
CURRENT_NODEID = None
DIFFS = {}       # nodeid -> list[str] unified diff lines
DURATIONS = {}   # nodeid -> float
TREE = {"_children": {}, "_tests": []}
TOP_SLOW_COUNT = 5

def _print(s: str = ""):
    sys.stdout.write(s + "\n")
    sys.stdout.flush()

def _clean(name: str) -> str:
    if not name:
        return ""
    name = re.sub(r'^(Test|test)', '', name)
    name = name.replace('_', ' ')
    parts = re.findall(r'[A-Z]+(?=[A-Z][a-z]|[0-9]|\b)|[A-Z]?[a-z]+|[0-9]+', name)
    return " ".join(parts).strip().lower() or name.lower()

def _pretty(obj):
    try:
        if isinstance(obj, (dict, list, tuple)):
            return json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False)
        return json.dumps(obj, indent=2, ensure_ascii=False)
    except Exception:
        try:
            from pprint import pformat
            return pformat(obj, width=80, compact=False, sort_dicts=True)
        except Exception:
            return repr(obj)

def _colored_diff(lines, indent_spaces):
    indent = " " * indent_spaces
    for s in lines:
        if s.startswith("+") and not s.startswith("+++"):
            _print(f"{indent}{GREEN}{s}{RESET}")
        elif s.startswith("-") and not s.startswith("---"):
            _print(f"{indent}{RED}{s}{RESET}")
        else:
            _print(f"{indent}{s}")

# fake terminal reporter to satisfy config.get_terminal_writer when -p no:terminal
def pytest_configure(config):
    # fake terminal writer si le terminalreporter n'est pas présent,
    # mais on n'enregistre PAS sous le nom "terminalreporter" pour éviter le conflit
    class _FakeTW:
        def _highlight(self, text):
            return text
        def write(self, s, **kwargs):
            return

    class _FakeTerminalReporter:
        def __init__(self):
            self._tw = _FakeTW()
        def get_terminal_writer(self):
            return self._tw

    if config.pluginmanager.get_plugin("terminalreporter") is None:
        # utilise un nom unique pour éviter ValueError si pytest change son timing
        try:
            config.pluginmanager.register(_FakeTerminalReporter(), "fake_terminalreporter")
        except Exception:
            # en cas d'erreur, ne pas planter la configuration pytest
            pass

# collect diffs
def pytest_runtest_call(item):
    global CURRENT_NODEID
    CURRENT_NODEID = item.nodeid

def pytest_assertrepr_compare(config, op, left, right):
    # on ne traite que les égalités pour produire un diff lisible
    if op != "==":
        return None
    left_str = _pretty(left).splitlines()
    right_str = _pretty(right).splitlines()
    diff = list(difflib.unified_diff(left_str, right_str, fromfile="expected", tofile="actual", lineterm=""))
    # stocker le diff pour usage ultérieur dans notre reporting personnalisé
    if CURRENT_NODEID:
        DIFFS[CURRENT_NODEID] = diff
    # retourner None pour éviter que pytest ajoute automatiquement son propre diff au longrepr
    return None

def _ensure_path(root, parts):
    node = root
    for p in parts:
        if not p:
            continue
        if p not in node["_children"]:
            node["_children"][p] = {"_children": {}, "_tests": []}
        node = node["_children"][p]
    return node

def pytest_runtest_logreport(report):
    if report.when != "call":
        return

    DURATIONS[report.nodeid] = getattr(report, "duration", None)
    parts = report.nodeid.split("::")[1:]
    clean_parts = [_clean(p) for p in parts]
    class_path = clean_parts[:-1]
    test_name = clean_parts[-1] if clean_parts else "<unknown>"
    node = _ensure_path(TREE, class_path)

    lineno = None
    message = None
    expr_line = ""
    try:
        if hasattr(report, "longrepr") and hasattr(report.longrepr, "reprcrash"):
            lineno = getattr(report.longrepr.reprcrash, "lineno", None)
            message = getattr(report.longrepr.reprcrash, "message", None)
    except Exception:
        lineno = None
        message = None

    tb = getattr(getattr(report, "longrepr", None), "reprtraceback", None)
    if tb and getattr(tb, "reprentries", None):
        try:
            last_entry = tb.reprentries[-1]
            loc = getattr(last_entry, "reprfileloc", None)
            if loc and getattr(loc, "message", None):
                expr_line = loc.message
        except Exception:
            expr_line = ""

    status = "passed" if report.passed else "failed" if report.failed else "skipped"

    node["_tests"].append({
        "nodeid": report.nodeid,
        "name": test_name,
        "status": status,
        "lineno": lineno,
        "message": message,
        "expr": expr_line,
        "duration": DURATIONS.get(report.nodeid),
        "diff": DIFFS.get(report.nodeid, []),
    })

    if status == "passed":
        RESULTS["passed"] += 1
    elif status == "failed":
        RESULTS["failed"] += 1
    elif status == "skipped":
        RESULTS["skipped"] += 1

    # affichage immédiat : n'afficher qu'une seule fois et éviter duplication du diff
    if report.when == "call" and report.failed:
        try:
            longrepr = getattr(report, "longrepr", None)

            _print("")  # séparation visuelle
            _print(f"{RED}--- Immediate failure for {report.nodeid} ---{RESET}")

            # Si on a un diff enregistré pour ce nodeid, afficher celui-ci (unique, déjà unifié)
            diff = DIFFS.get(report.nodeid)
            if diff:
                _print("")  # ligne vide avant diff
                _colored_diff(diff, indent_spaces=2)
                _print("")  # ligne vide après diff
            else:
                # sinon afficher la représentation longue (préférer longrepr.text si présent)
                longrepr_text = None
                if hasattr(longrepr, "text") and getattr(longrepr, "text"):
                    longrepr_text = str(longrepr.text)
                else:
                    longrepr_text = str(longrepr) if longrepr is not None else "<no longrepr>"

                for line in longrepr_text.splitlines():
                    _print(line)

            # information de localisation si disponible
            if lineno is not None or message:
                file_path = report.nodeid.split("::")[0] or "<unknown file>"
                if expr_line:
                    _print(f"{RED}Location:{RESET} {file_path}:{lineno}: {message or ''} → {expr_line}")
                else:
                    _print(f"{RED}Location:{RESET} {file_path}:{lineno}: {message or ''}")

            _print(f"{RED}--- end immediate failure ---{RESET}")
            _print("")  # espace après
        except Exception:
            import traceback
            _print("Failed to print immediate error:")
            for line in traceback.format_exc().splitlines():
                _print(line)

def _print_tree_node(node, depth=0):
    for t in node.get("_tests", []):
        t_indent = "  " * depth
        dur = t.get("duration")
        if dur is None:
            t_str = ""
        elif dur < 0.001:
            t_str = f" ({dur*1_000_000:.1f} µs)"
        elif dur < 1:
            t_str = f" ({dur*1000:.1f} ms)"
        else:
            t_str = f" ({dur:.2f} s)"

        if t["status"] == "passed":
            _print(f"{t_indent}{YELLOW}{t['name']}{RESET} {GREEN}✅{RESET}{t_str}")
        elif t["status"] == "failed":
            _print(f"{t_indent}{YELLOW}{t['name']}{RESET} {RED}❌{RESET}{t_str}")
            if t["lineno"] is not None and t["message"]:
                file_path = t.get("nodeid", "").split("::")[0] or "<unknown file>"
                expr = t["expr"]
                if expr:
                    _print(f"{t_indent}  {RED}{file_path}:{t['lineno']}: {t['message']} → {expr}{RESET}")
                else:
                    _print(f"{t_indent}  {RED}{file_path}:{t['lineno']}: {t['message']}{RESET}")
            if t["diff"]:
                _print("")
                _colored = t["diff"]
                _colored_diff(_colored, indent_spaces=(depth + 1) * 2)
                _print("")

    for name in sorted(node.get("_children", {}).keys()):
        data = node["_children"][name]
        indent = "  " * depth
        _print(f"{indent}{BLUE}{name}{RESET}")
        _print_tree_node(data, depth + 1)

def pytest_sessionfinish(session, exitstatus):
    _print("")
    for name in sorted(TREE["_children"].keys()):
        _print(f"{BLUE}{name}{RESET}")
        _print_tree_node(TREE["_children"][name], depth=1)

    passed = RESULTS["passed"]
    failed = RESULTS["failed"]
    skipped = RESULTS["skipped"]
    _print("")
    if failed:
        _print(f"{RED}{failed} failed{RESET}, {GREEN}{passed} passed{RESET}" + (f", {YELLOW}{skipped} skipped{RESET}" if skipped else ""))
    else:
        _print(f"{GREEN}{passed} passed{RESET}" + (f", {YELLOW}{skipped} skipped{RESET}" if skipped else ""))

    if DURATIONS:
        _print("")
        _print(f"{YELLOW}Top slow tests (max {TOP_SLOW_COUNT}):{RESET}")
        slow = nlargest(TOP_SLOW_COUNT, DURATIONS.items(), key=lambda kv: kv[1] or 0.0)
        for nodeid, dur in slow:
            parts = [p for p in nodeid.split("::")[1:]]
            title = " / ".join(_clean(p) for p in parts)
            if dur < 0.001:
                t_str = f"{dur*1_000_000:.1f} µs"
            elif dur < 1:
                t_str = f"{dur*1000:.1f} ms"
            else:
                t_str = f"{dur:.2f} s"
            _print(f"  {t_str} — {title}")

DSN = os.getenv(
    "TEST_DSN",
    "postgresql://postgres:postgres@postgres_test:5432/ezplantparent_test",
)

@pytest.fixture(scope="function")
def db_conn():
    conn = psycopg2.connect(DSN)
    try:
        conn.autocommit = False
        with conn.cursor() as cur:
            cur.execute("BEGIN;")
        yield conn
        # rollback garanti après le test
        conn.rollback()
    finally:
        conn.close()

from infrastructure.database import Database, set_db
from infrastructure.pgpool import init_pool, close_pool

@pytest.fixture(scope="function")
def tests_database(db_conn):
    db = Database(conn=db_conn, commit_on_execute=False)
    set_db(db, global_fallback=True)
    try:
        yield db
    finally:
        set_db(None, global_fallback=True)

@pytest.fixture(scope="session", autouse=True)
def pg_pool_session():
    dsn = "host=postgres_test port=5432 dbname=ezplantparent_test user=postgres password=postgres"
    init_pool(minconn=1, maxconn=5, dsn=dsn)
    try:
        yield
    finally:
        close_pool()