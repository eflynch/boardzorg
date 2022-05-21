import random
import logging

from boardzorg.session import Session
from boardzorg.exceptions import IllegalAction, BadCommand

logger = logging.getLogger(__name__)


def translate_faction(faction):
    return {
        "b": "rabbit",
        "a": "owl",
        "f": "christopher_robbin",
        "h": "piglet",
        "e": "eeyore",
        "g": "kanga"
    }[faction]


def run_console(seed=0, provisions_cards=None, factions_playing=None, output_file=None, log_level=logging.INFO):
    logging.basicConfig(level=log_level)
    random.seed(seed)

    session = Session.new_session(provisions_deck=provisions_cards, factions=factions_playing)

    while True:
        parts = input("100_aker_wood > ").split("! ")
        if "quit!" in parts:
            with open(output_file, "w") as f:
                f.write(session.serialize(session))
            break
        if "load!" in parts:
            with open(output_file) as f:
                session = session.realize(f.read())
            continue

        if len(parts) != 2:
            continue

        faction, cmd = parts
        logger.info(list(session.get_valid_actions(translate_faction(faction)).keys()))
        try:
            session.handle_cmd(translate_faction(faction), cmd)
        except IllegalAction as e:
            logger.error("     IllegalAction: {}".format(e))
        except BadCommand as e:
            logger.error("     BadCommand: {}".format(e))
        except Exception as e:
            logger.error("Unhandled exception: {}".format(e))
            with open(output_file, "w") as f:
                f.write(session.serialize(session))
