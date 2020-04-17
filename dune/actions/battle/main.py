from copy import deepcopy
from logging import getLogger

from dune.actions.action import Action
from dune.actions import args
from dune.actions.common import get_faction_order
from dune.state.rounds import battle
from dune.exceptions import IllegalAction, BadCommand
from dune.actions.battle import ops

logger = getLogger(__name__)


class StartBattle(Action):
    name = "start-battle"
    ck_round = "battle"
    ck_stage = "setup"
    su = True

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)

        new_game_state.round_state.faction_turn = get_faction_order(game_state)[0]
        new_game_state.round_state.battles = ops.find_battles(new_game_state)
        new_game_state.round_state.stage = "main"

        return new_game_state


class PickBattle(Action):
    name = "pick-battle"
    ck_round = "battle"
    ck_stage = "main"

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.Battle();

    @classmethod
    def parse_args(cls, faction, args):
        (defender, space, min_sector) = args.split(" ")
        return PickBattle(faction, space, min_sector, defender)

    def __init__(self, faction, space, min_sector, defender):
        self.faction = faction
        self.battle_id = (faction, defender, space, int(min_sector))
        self.defender = defender

    @classmethod
    def _check(cls, game_state, faction):
        cls.check_turn(game_state, faction)

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)

        if self.battle_id not in game_state.round_state.battles:
            raise BadCommand("There is no fight there")

        (_, defender, s, msec) = self.battle_id
        space = game_state.map_state[s]

        if self.faction not in space.forces:
            raise BadCommand("You have no battle to fight in {}".format(space.name))
        if self.defender not in space.forces:
            raise BadCommand("You cannot fight {} when they aren't around".format(self.defender))

        new_game_state.round_state.stage_state = battle.BattleStage()
        new_game_state.round_state.stage_state.battle = self.battle_id
        return new_game_state


class AutoPickBattle(Action):
    name = "auto-pick-battle"
    ck_round = "battle"
    ck_stage = "main"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if len(game_state.round_state.battles) > 1:
            battle_1 = game_state.round_state.battles[0]
            battle_2 = game_state.round_state.battles[1]
            if battle_1[0] == battle_2[0] == game_state.round_state.faction_turn:
                if ops.validate_battle(game_state, battle_1):
                    if ops.validate_battle(game_state, battle_2):
                        raise IllegalAction("There are choices to be made")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)

        to_prune = []
        for b in new_game_state.round_state.battles:
            if not ops.validate_battle(game_state, b):
                to_prune.append(b)
        for b in to_prune:
            new_game_state.round_state.battles.remove(b)
        if not new_game_state.round_state.battles:
            new_game_state.round = "collection"
            return new_game_state

        battle_1 = game_state.round_state.battles[0]
        if battle_1[0] == game_state.round_state.faction_turn:
            new_game_state.round_state.stage_state = battle.BattleStage()
            new_game_state.round_state.stage_state.battle = battle_1
            logger.info("Starting {}".format(battle_1))
        else:
            new_game_state.round_state.faction_turn = battle_1[0]
        return new_game_state
