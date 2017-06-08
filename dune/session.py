import logging
import pickle
import codecs

from dune.actions.action import Action
from dune.exceptions import BadCommand
from dune.state.game import GameState

logger = logging.getLogger(__name__)


class Session:
    def __init__(self, treachery_cards=None, factions_playing=None):
        self.game_log = [GameState(treachery_cards, factions_playing)]
        self.action_log = []

    def execute_supervisor(self):
        supervisor_actions = Action.get_valid_actions(self.game_log[-1], None)
        if len(supervisor_actions) > 1:
            logger.critical("SUPERVISOR ERROR:", supervisor_actions)
        for s in supervisor_actions:
            self.execute_action(supervisor_actions[s]())

    def execute_action(self, action):
        old_state = self.game_log[-1]
        new_state = action.execute(game_state=old_state)
        logger.debug("Executing: {}".format(action))
        new_state.assert_valid()
        self.game_log.append(new_state)
        self.action_log.append(action)
        self.execute_supervisor()

    def handle_cmd(self, faction, cmd):
        logger.info("CMD: {} {}".format(faction, cmd))
        valid_actions = Action.get_valid_actions(self.game_log[-1], faction)
        action_type = cmd.split(" ")[0]
        args = " ".join(cmd.split(" ")[1:])
        if action_type not in valid_actions:
            action = Action.get_action(action_type)
            if action:
                action.check(self.game_log[-1], faction)
            else:
                raise BadCommand("Not a known action")
        action = valid_actions[action_type].parse_args(faction, args)
        self.execute_action(action)

    def get_visible_state(self, faction):
        return self.game_log[-1].visible(faction)

    def get_valid_actions(self, faction):
        return Action.get_valid_actions(self.game_log[-1], faction)

    @staticmethod
    def serialize(session):
        return codecs.encode(pickle.dumps(session), "base64").decode()

    @staticmethod
    def realize(serialized_session):
        return pickle.loads(codecs.decode(serialized_session.encode(), "base64"))
