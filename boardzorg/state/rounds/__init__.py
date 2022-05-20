from boardzorg.state import State


class RoundState(State):
    @property
    def stage(self):
        if self._stage_state is not None:
            return self._stage_state.stage
        return self._stage

    @stage.setter
    def stage(self, new_stage):
        self._stage = new_stage
        self._stage_state = None

    @property
    def stage_state(self):
        return self._stage_state

    @stage_state.setter
    def stage_state(self, new_stage_state):
        self._stage_state = new_stage_state
        self._stage = None

    def visible(self, game_state, faction):
        visible = super().visible(game_state, faction)
        visible["round"] = self.round
        return visible


class StageState(State):
    @property
    def substage(self):
        if self._substage_state is not None:
            return self._substage_state.substage
        return self._substage

    @substage.setter
    def substage(self, new_substage):
        self._substage = new_substage
        self._substage_state = None

    @property
    def substage_state(self):
        return self._substage_state

    @substage_state.setter
    def substage_state(self, new_substage_state):
        self._substage_state = new_substage_state
        self._substage = None

    def visible(self, game_state, faction):
        visible = super().visible(game_state, faction)
        visible["stage"] = self.stage
        return visible


class SubStageState(State):
    def visible(self, game_state, faction):
        visible = super().visible(game_state, faction)
        visible["substage"] = self.substage
        return visible
