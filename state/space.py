SPACES = [
    ('Arsunt', 'sand', None, None, (10, 11)),
    ('Basin', 'sand', None, None, (8,)),
    ('Bright-of-the-Cliff', 'sand', None, None, (13, 14)),
    ('Broken-Land', 'sand', 11, 8, (10, 11)),
    ('Cielago-Depression', 'sand', None, None, (0, 1, 2)),
    ('Cielago-East', 'sand', None, None, (2, 3)),
    ('Cielago-North', 'sand', 2, 8, (0, 1, 2)),
    ('Cielago-South', 'sand', 1, 12, (1, 2)),
    ('Cielago-West', 'sand', None, None, (0, 17)),
    ('Funeral-Plain', 'sand', 14, 6, (14,)),
    ('Gara-Kulon', 'sand', None, None, (7,)),
    ('Habbanya-Erg', 'sand', 15, 8, (15, 16)),
    ('Habbanya-Ridge-Flat', 'sand', 17, 10, (16, 17)),
    ('Hagga-Basin', 'sand', 12, 6, (11, 12)),
    ('Harg-Pass', 'sand', None, None, (3, 4)),
    ('Hole-in-the-Rock', 'sand', None, None, (8,)),
    ('Meridian', 'sand', None, None, (0, 1)),
    ('Old-Gap', 'sand', 9, 6, (8, 9, 10)),
    ('Red-Chasm', 'sand', 6, 8, (6,)),
    ('Rock-Outcroppings', 'sand', 13, 6, (12, 13)),
    ('Sihaya-Ridge', 'sand', 8, 6, (8,)),
    ('South-Mesa', 'sand', 4, 10, (3, 4, 5)),
    ('Great-Flat', 'sand', 14, 10, (14,)),
    ('Greater-Flat', 'sand', None, None, (15,)),
    ('Minor-Erg', 'sand', 7, 8, (4, 5, 6, 7)),
    ('Tsimpo', 'sand', None, None, (10, 11, 12)),
    ('Wind-Pass', 'sand', None, None, (13, 14, 15, 16)),
    ('Wind-Pass-North', 'sand', 16, 6, (16, 17)),
    ('Polar-Sink', 'sink', None, None, (-1,)),
    ('False-Wall-East', 'rock', None, None, (4, 5, 6, 7, 8)),
    ('False-Wall-South', 'rock', None, None, (3, 4)),
    ('False-Wall-West', 'rock', None, None, (15, 16, 17)),
    ('Pasty-Mesa', 'rock', None, None, (4, 5, 6, 7)),
    ('Plastic-Basin', 'rock', None, None, (11, 12, 13)),
    ('Rim-Wall-West', 'rock', None, None, (8,)),
    ('Shield-Wall', 'rock', None, None, (7, 8)),
    ('Habbanya-Sietch', 'stronghold', None, None, (16,)),
    ('Sietch-Tabr', 'stronghold', None, None, (13,)),
    ('Tueks-Sietch', 'stronghold', None, None, (4,)),
    ('Arrakeen', 'shielded-stronghold', None, None, (9,)),
    ('Carthag', 'shielded-stronghold', None, None, (10,)),
    ('Imperial-Basin', 'shielded-sand', None, None, (8, 9, 10))
]


class SpaceState:
    def __init__(self, name, kind, spice_sector, spice_amount, sectors):
        # Properties
        self.name = name
        self.type = kind
        self.spice_sector = spice_sector
        self.spice_amount = spice_amount
        self.sectors = sectors

        # State
        self.spice = 0
        self.forces = {}
