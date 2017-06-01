from dune.state.rounds import RoundState


class BiddingRound(RoundState):
    def __init__(self):
        self.round = "bidding"
        self.bene_gesserit_charity_claimed = False
        self.faction_turn = None
        self.total_for_auction = 0
        self.up_for_auction = []
        self.bids = {}
        self.payment_done = False
        self.payment_cancel_passed = False
        self.winner = None
        self.prescience_cancel_karama = False
        self.extra_card_karama_used = False
        self.karama_pass = []
