import logging

def setup_logger(cfg):
    logger = logging.getLogger()
    logger.setLevel(cfg["logging"]["level"])

    if not logger.handlers:
        fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

        file_handler = logging.FileHandler(cfg["logging"]["file"])
        file_handler.setFormatter(fmt)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(fmt)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
