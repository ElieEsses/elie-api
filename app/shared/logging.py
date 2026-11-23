import logging
import sys


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s:     %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
