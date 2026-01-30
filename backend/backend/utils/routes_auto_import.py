import pathlib, importlib.util
import logging
logger = logging.getLogger(__name__)

def import_sub_routes(target):
    ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent
    USECASES_DIR = ROOT_DIR / "usecases"

    for path in USECASES_DIR.rglob("*.py"):
        if path.name.lower() not in {"controller.py", "route.py"}:
            continue

        # Reconstruire le nom de module relatif à ROOT_DIR
        relative_path = path.relative_to(ROOT_DIR)
        module_name = ".".join(relative_path.with_suffix("").parts)

        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, "router"):
            target.include_router(module.router)
            logger.info(f"✅ Router included from {path.relative_to(ROOT_DIR)}")