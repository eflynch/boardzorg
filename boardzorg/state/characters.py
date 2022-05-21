from boardzorg.exceptions import BadCommand

CHARACTERS = {
    "owl": [
        ("Wol", 2),
        ("Incorrect-Owl", 1),
        ("Boastful-Owl", 4),
        ("Serious-Owl", 5),
        ("Wise-Owl", 5)
    ],
    "rabbit": [
        ("Small", 5),
        ("Alexander-Beetle", 5),
        ("Smallest-Of-All", 5),
        ("Late", 5),
        ("Early", 5)
    ],
    "eeyore": [
        ("EeyoreWithoutTail", 2),
        ("EeyoreWithTail", 3),
        ("DejectedEeyore", 3),
        ("Sad-Eeyore", 5),
        ("Soggy-Eeyore", 6)
    ],
    "christopher_robbin": [
        ("PoohBear", 6),
        ("SpottedBackson", 2),
        ("HerbaceousBackson", 5),
        ("Jagular", 3),
        ("ChristopherRobbin", 7)
    ],
    "kanga": [
        ("Kanga-Knows-Best", 3),
        ("Sympathetic-Roo", 3),
        ("ExtractOfMalt", 1),
        ("Curious-Roo", 2),
        ("Kanga-With-Pouch", 5)
    ],
    "piglet": [
        ("Piglet", 2),
        ("Henry-Pootel", 6),
        ("Trespassers-W", 4),
        ("Trespassers-Will", 3),
        ("Trespassers-William", 1)
    ]
}


def get_character_faction(character):
    for k in CHARACTERS:
        if character in CHARACTERS[k]:
            return k
    return None


def parse_character(character):
    all_characters = [item for sublist in CHARACTERS.values() for item in sublist]
    character_list = [a for a in all_characters if a[0] == character]
    if not character_list:
        raise BadCommand("Not a valid character name")
    character = character_list[0]
    return character
