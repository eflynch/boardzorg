import logging
import json

from dune.actions.action import Action
from dune.exceptions import BadCommand, IllegalAction
from dune.state.game import GameState

logger = logging.getLogger(__name__)


class Session:
    def __init__(self, init_state, seed=None):
        self.seed = seed
        self.game_log = [init_state]
        self.action_log = []
        self.command_log = []

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
        self.game_log.append(new_state)
        self.action_log.append(action)
        self.execute_supervisor()

    def handle_cmd(self, faction, cmd):
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
        print(action)
        self.execute_action(action)
        self.command_log.append((faction, cmd))

    def get_visible_state(self, faction):
        return self.game_log[-1].visible(faction)

    def get_valid_actions(self, faction):
        return Action.get_valid_actions(self.game_log[-1], faction)

    @staticmethod
    def new_session(factions=None, treachery_deck=None, seed=None):
        init_state = GameState.new_shuffle(factions, treachery_deck, seed)
        return Session(init_state=init_state, seed=seed)

    @staticmethod
    def serialize(session):
        init_state = session.game_log[0]
        to_json = {
            "seed": session.seed,
            "factions": init_state.factions,
            "treachery_deck": init_state.treachery_deck,
            "spice_deck": init_state.spice_deck,
            "traitor_deck": init_state.traitor_deck,
            "storm_deck": init_state.storm_deck,
            "command_log": session.command_log
        }
        return json.dumps(to_json)

    @staticmethod
    def realize(serialized_session):
        from_json = json.loads(serialized_session)
        init_state = GameState(
            factions=from_json["factions"],
            treachery_deck=from_json["treachery_deck"],
            spice_deck=from_json["spice_deck"],
            traitor_deck=list(map(tuple, from_json["traitor_deck"])),
            storm_deck=from_json["storm_deck"]
        )
        session = Session(init_state, from_json["seed"])

        for f, cmd in from_json["command_log"]:
            try:
                session.handle_cmd(f, cmd)
            except BadCommand as e:
                print(e)
            except IllegalAction as e:
                print(e)

        return session
