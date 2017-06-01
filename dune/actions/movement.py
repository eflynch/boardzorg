# KaramaBlockGuildTurnChoice, KaramaPassBlockGuildTurnChoice
# GuildPassTurn
# TURN:
    # KaramaCheapShipment, Ship, CrossPlanetShip, Movement

from copy import deepcopy
import math

from dune.actions.action import Action
from dune.exceptions import IllegalAction, BadCommand


def ship_units(game_state, faction, units, space, sector):
    if sector not in space.sectors:
        raise BadCommand("You ain't going nowhere")
    for u in units:
        if u not in game_state.faction_state[faction].reserve_units:
            raise BadCommand("Cannot place a unit which is unavailable")
        game_state.faction_state[faction].reserve_units.remove(u)
        if faction not in space.forces:
            space.forces[faction] = {}
        if sector not in space.forces[faction]:
            space.forces[faction][sector] = []
        space.forces[faction][sector].append(u)


def move_units(game_state, faction, units, space_a, sector_a, space_b, sector_b):
    if sector_b not in space_b.sectors:
        raise BadCommand("You ain't going nowhere")

    if sector_a not in sector_a.sectors:
        raise BadCommand("You ain't coming from nowhere")

    if faction not in space_b.forces:
        space_b.forces[faction] = {}
    if sector_b not in space_b.forces[faction]:
        space_b.forces[faction][sector_b] = []

    for u in units:
        if u not in space_a.forces[faction][sector_a]:
            raise BadCommand("You ain't got the troops")
        space_a.forces[faction][sector_a].remove(u)
        space_b.forces[faction][sector_a].append(u)

    if all(space_a.forces[faction][s] == [] for s in space_a.forces[faction]):
        del space_a.forces[faction]


class KaramaBlockGuildTurnChoice(Action):
    name = "karama-block-guild-turn-choice"
    ck_round = "movement"

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round_state.faction_turn is not None:
            raise IllegalAction("Movement round already started")
        if game_state.round_state.block_guild_turn_karama_used:
            raise IllegalAction("This has already been done")
        if faction in game_state.round_state.block_guild_turn_karama_pass:
            raise IllegalAction("You have already passed this option")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.block_guild_turn_karama_used = True
        # new_game_state.round_state.faction_turn = get_faction_order(game_state)[0]
        return new_game_state


class KaramaPassBlockGuildTurnChoice(Action):
    name = "karama-pass-block-guild-turn-choice"
    ck_round = "movement"

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round_state.faction_turn is not None:
            raise IllegalAction("Movement round already started")
        if game_state.round_state.block_guild_turn_karama_used:
            raise IllegalAction("This has already been done")
        if faction in game_state.round_state.block_guild_turn_karama_pass:
            raise IllegalAction("You have already passed this option")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.block_guild_turn_karama_pass.append(self.faction)
        return new_game_state


class StartMovement(Action):
    name = "start-movemen"
    ck_round = "movement"

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round_state.faction_turn is not None:
            raise IllegalAction("Movement round already started")
        if len(game_state.round_state.block_guild_turn_karama_pass) < 5:
            raise IllegalAction("Waiting for karama passes")

    def _execute(self, game_state):
        pass


class Ship(Action):
    name = "ship"
    ck_round = "movement"

    def parse_args(faction, args):
        parts = args.split(" ")
        if len(parts) != 3:
            raise BadCommand("Shipment Requires Different Arguments")

        units, space, sector = parts
        units = [int(i) for i in units.split(",")]
        sector = int(sector)

        return Ship(faction, units, space, sector)

    def __init__(self, faction, units, space, sector):
        self.faction = faction
        self.units = units
        self.space = space
        self.sector = sector

    def _calculate_spice_cost(self, game_state):
        num_units = len(self.units)
        space = game_state.board_state.map_state[self.space]

        if self.faction == "guild" or "guild" in game_state.alliances[self.faction]:
            if space.is_stronghold:
                spice_cost = math.ceil(num_units/2)
            else:
                spice_cost = num_units
        else:
            if space.is_stronghold:
                spice_cost = num_units
            else:
                spice_cost = 2 * num_units

        return spice_cost

    @classmethod
    def _check(cls, game_state, faction):
        cls.check_turn(game_state, faction)

    def execute(self, game_state):
        new_game_state = deepcopy(game_state)

        space = new_game_state.board_state.map_state[self.space]
        if space.is_stronghold and len(space.forces) > 1 and self.faction not in space.forces:
            raise BadCommand("Cannot ship into stronghold with 2 enemy factions")

        if new_game_state.board_state.storm_position == self.sector:
            if self.faction == "fremen":
                surviving_units = sorted(self.units)[:math.floor(len(self.units)/2)]
                tanked_units = sorted(self.units)[math.floor(len(self.units)/2):]
                self.units = surviving_units
                new_game_state.faction_state["fremen"].tanked_units.extend(tanked_units)
            else:
                raise IllegalAction("Only the Fremen can ship into the storm")

        spice_cost = self._calculate_spice_cost(new_game_state)

        if new_game_state.faction_state[self.faction].spice < spice_cost:
            raise IllegalAction("Insufficient spice for this shipment")

        ship_units(new_game_state, self.faction, self.units, space, self.sector)

        if self.faction != "guild":
            new_game_state.faction_state[self.faction].spice -= spice_cost
            if "guild" in new_game_state.faction_state:
                new_game_state.faction_state["guild"].spice += spice_cost

        return new_game_state
