from dune.state import State


class RoundState(State):
    def assert_valid(self):
        if hasattr(self, "stage_state"):
            if not self.stage_state.assert_valid():
                return False
        return True

    def visible(self, game_state, faction):
        visible = super().visible(game_state, faction)
        visible["round"] = self.round
        return visible


class StageState(State):
    def assert_valid(self):
        if hasattr(self, "substage_state"):
            if not self.substage_state.assert_valid():
                return False
        return True

    def visible(self, game_state, faction):
        visible = super().visible(game_state, faction)
        visible["stage"] = self.stage
        return visible


class SubStageState(State):
    def assert_valid(self):
        return True

    def visible(self, game_state, faction):
        visible = super().visible(game_state, faction)
        visible["substage"] = self.substage
        return visible
