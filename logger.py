import logging, sys, os

def mask_email(email: str) -> str:
    try:
        user, domain = email.split("@", 1)
        if len(user) <= 2:
            mu = user[0] + "*"
        else:
            mu = user[:2] + "*" * max(1, len(user)-4) + user[-2:]
        return f"{mu}@{domain}"
    except Exception:
        return email

def get_logger(name="app"):
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger.setLevel(level)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s:%(name)s:%(message)s"))
    fh = logging.FileHandler("發文紀錄.txt", encoding="utf-8")
    fh.setLevel(level)
    fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s:%(message)s"))
    logger.addHandler(ch)
    logger.addHandler(fh)
    return logger
