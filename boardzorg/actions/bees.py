from copy import deepcopy

from boardzorg.actions import args
from boardzorg.actions.action import Action
from boardzorg.actions.battle import ops
from boardzorg.actions.provisions import discard_provisions
from boardzorg.exceptions import IllegalAction
from boardzorg.state.rounds import hunny


def destroy_in_path(game_state, sectors):
    for space in game_state.map_state.values():
        if not set(space.sectors).isdisjoint(set(sectors)):
            if space.type == "meadow" or ("umbrellaed" in space.type and not game_state.umbrella_wall):
                ops.lost_all_minions(game_state, space.name, restrict_sectors=sectors, half_christopher_robbin=True)
                if space.hunny_sector and space.hunny_sector in sectors:
                    space.hunny = 0


def do_bees_round(game_state, advance):
    previous_bees_position = game_state.bees_position
    game_state.bees_position = (game_state.bees_position + advance) % 18

    sectors_to_destroy = list(range(previous_bees_position, game_state.bees_position + 1))

    destroy_in_path(game_state, sectors_to_destroy)

    game_state.round_state = hunny.HunnyRound()

    game_state.balloons = []
    pigletsHouse = game_state.map_state["PigletsHouse"]
    owlsHouse = game_state.map_state["OwlsHouse"]
    if pigletsHouse.forces:
        game_state.balloons.append(list(pigletsHouse.forces.keys())[0])
    if owlsHouse.forces:
        game_state.balloons.append(list(owlsHouse.forces.keys())[0])


class Bees(Action):
    name = "bees"
    ck_round = "bees"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if len(game_state.round_state.bee_keeping_passes) != len(game_state.faction_state):
            raise IllegalAction("Weather control passes not complete, can't proceed as normal")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        do_bees_round(new_game_state, new_game_state.bees_deck.pop(0))
        return new_game_state


class BeeKeeping(Action):
    name = "bee-keeping"
    ck_round = "bees"
    ck_provisions = "Bee-Keeping"

    @classmethod
    def parse_args(cls, faction, args):
        return BeeKeeping(faction, int(args))

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.Integer(min=0, max=10)

    @classmethod
    def _check(cls, game_state, faction):
        if faction in game_state.round_state.bee_keeping_passes:
            raise IllegalAction("Already passed, it's too late!")

    def __init__(self, faction, advance):
        self.faction = faction
        self.advance = advance

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.bees_deck.pop(0)
        do_bees_round(new_game_state, self.advance)
        discard_provisions(new_game_state, self.faction, "Bee-Keeping")
        return new_game_state


class PassBeeKeeping(Action):
    name = "pass-bee-keeping"
    ck_round = "bees"

    @classmethod
    def parse_args(cls, faction, args):
        return PassBeeKeeping(faction)

    def __init__(self, faction):
        self.faction = faction

    @classmethod
    def _check(cls, game_state, faction):
        if faction in game_state.round_state.bee_keeping_passes:
            raise IllegalAction("Already passed")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.bee_keeping_passes.append(self.faction)
        return new_game_state
