from copy import deepcopy
import math

from exceptions import IllegalAction, BadCommand

from actions.action import Action


class Shipment(Action):
    def parse_args(faction, args):
        parts = args.split(" ")
        if len(parts) != 3:
            raise BadCommand("Shipment Requires Different Arguments")

        units, space, sector = parts
        units = [int(i) for i in units.split(",")]
        sector = int(sector)

        return Shipment(faction, units, space, sector)

    def __init__(self, faction, units, space, sector, karama=False):
        self.faction = faction
        self.units = units
        self.space = space
        self.sector = sector
        self.karama = karama

    def _calculate_spice_cost(self, game_state):
        num_units = len(self.units)
        space = game_state.board_state.map_state[self.space]

        if self.karama:
            spice_cost = 0

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

    def _move_units(self, game_state):
        space = game_state.board_state.map_state[self.space]
        for u in self.units:
            if u not in game_state.faction_state[self.faction].reserve_units:
                raise IllegalAction("Cannot ship unit which is unavailable")
            game_state.faction_state[self.faction].reserve_units.remove(u)
            if self.faction not in space.forces:
                space.forces[self.faction] = {}
            if self.sector not in space.forces[self.faction]:
                space.forces[self.faction][self.sector] = []
            space.forces[self.faction][self.sector].append(u)

    def execute(self, game_state):
        self.check_round(game_state, "movement")
        self.check_turn(game_state)
        new_game_state = deepcopy(game_state)

        space = new_game_state.board_state.map_state[self.space]
        if space.is_stronghold and len(space.forces) > 1 and self.faction not in space.forces:
            raise IllegalAction("Cannot ship into stronghold with 2 enemy factions")

        if self.sector not in space.sectors:
            raise IllegalAction("You ain't going nowhere")

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

        self._move_units(new_game_state)

        if self.faction != "guild":
            new_game_state.faction_state[self.faction].spice -= spice_cost
            if "guild" in new_game_state.faction_state:
                new_game_state.faction_state["guild"].spice += spice_cost

        return new_game_state
