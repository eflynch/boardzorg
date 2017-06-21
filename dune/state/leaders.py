from dune.exceptions import BadCommand

LEADERS = {
    "atreides": [
        ("Duncan-Idaho", 2),
        ("Dr-Wellington-Yueh", 1),
        ("Gurney-Halleck", 4),
        ("Lady-Jessica", 5),
        ("Thufir-Hawat", 5)
    ],
    "bene-gesserit": [
        ("Alia", 5),
        ("Margot-Lady-Fenring", 5),
        ("Princess-Irulan", 5),
        ("Reverend-Mother-Ramallo", 5),
        ("Wanna-Marcus", 5)
    ],
    "emperor": [
        ("Bashar", 2),
        ("Burseg", 3),
        ("Caid", 3),
        ("Captain-Aramsham", 5),
        ("Count-Hasimir-Fenring", 6)
    ],
    "fremen": [
        ("Chani", 6),
        ("Jamis", 2),
        ("Otheym", 6),
        ("Shadout-Mapes", 3),
        ("Stilgar", 7)
    ],
    "guild": [
        ("Esmar-Tuek", 3),
        ("Master-Bewt", 3),
        ("Representative", 1),
        ("Soo-Soo-Sook", 2),
        ("Staban-Tuek", 5)
    ],
    "harkonnen": [
        ("Captain-Iakin-Nefud", 2),
        ("Feyd-Rautha", 6),
        ("Beast-Rabban", 4),
        ("Piter-DeVries", 3),
        ("Umman-Kudu", 1)
    ]
}


def get_leader_faction(leader):
    for k in LEADERS:
        if leader in LEADERS[k]:
            return k
    return None


def parse_leader(leader):
    all_leaders = [item for sublist in LEADERS.values() for item in sublist]
    leader_list = [a for a in all_leaders if a[0] == leader]
    if not leader_list:
        raise BadCommand("Not a valid leader name")
    leader = leader_list[0]
    return leader
