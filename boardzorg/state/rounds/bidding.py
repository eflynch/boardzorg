from boardzorg.state.rounds import RoundState, StageState, SubStageState


class SetupStage(StageState):
    stage = "setup"


class AuctionStage(StageState):
    stage = "auction"

    def __init__(self):
        self.substage_state = BiddingSubStage()
        self.bids = {}
        self.winner = None
        self.winning_bid = None

    def visible(self, game_state, faction):
        bids = {f: self.bids[f] for f in self.bids if self.bids[f] != float("inf")}
        for f in self.bids:
            if self.bids[f] == float("inf"):
                bids[f] = "inf"
        visible = super().visible(game_state, faction)
        visible["bids"] = bids
        visible["winner"] = self.winner
        visible["winning_bid"] = self.winning_bid if self.winning_bid != float("inf") else "inf"
        visible["substage_state"] = self.substage_state.visible(game_state, faction)
        return visible


class BiddingSubStage(SubStageState):
    substage = "bidding"

    def __init__(self):
        self.faction_turn = None

    def visible(self, game_state, faction):
        visible = super().visible(game_state, faction)
        visible["faction_turn"] = self.faction_turn
        return visible


class PaymentSubStage(SubStageState):
    substage = "payment"


class CollectSubStage(SubStageState):
    substage = "collect"

    def __init__(self):
        self.author_passes = []

    def visible(self, game_state, faction):
        visible = super().visible(game_state, faction)
        visible["author_passes"] = self.author_passes
        return visible


class BiddingRound(RoundState):
    def __init__(self):
        self.round = "bidding"
        self.total_for_auction = 0
        self.stage_state = SetupStage()
        self.up_for_auction = []
        self.choam_claimers = dict()

    def visible(self, game_state, faction):
        visible = super().visible(game_state, faction)
        visible["total_for_auction"] = self.total_for_auction
        visible["stage_state"] = self.stage_state.visible(game_state, faction)
        visible["up_for_auction"] = {"length": len(self.up_for_auction)}
        if faction == "owl" and self.up_for_auction:
            visible["up_for_auction"]["next"] = self.up_for_auction[0]

        return visible
