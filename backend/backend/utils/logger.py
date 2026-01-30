import inspect
import logging

def console_log(msg: str, *args, **kwargs):
    # Récupère la frame de l'appelant
    frame = inspect.currentframe().f_back
    module = inspect.getmodule(frame)
    caller_name = module.__name__ if module else "<unknown>"

    logger = logging.getLogger(caller_name)
    # On garde la capacité native de logger.info
    logger.info("✅ %s: " + msg, caller_name, *args, **kwargs)
