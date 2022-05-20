from boardzorg.state.rounds import RoundState

class StormRound(RoundState):
    round = "storm"

    def __init__(self):
        self.weather_control_passes = []
