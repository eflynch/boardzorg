import os

NAMES_FILE = "names.txt"

RENAME_DIR = "."


def title(key):
    return key.title()


def upper(key):
    return key.upper()


def snake(key):
    return key.replace("-", "_")


def spaces(key):
    return key.replace("-", " ")

def title_hyphens(key):
    words = key.split("-")
    return "-".join(" ".join(words).title().split(" "))

TRANSFORMATIONS = [
    lambda key: key,
    title,
    upper,
    snake,
    spaces,
    title_hyphens
]


def get_config(names_file):
    config = {}
    with open(NAMES_FILE, "r") as names:
        for line in names:
            old, new = line.strip().split(":")
            config[old] = new
    return config


def get_file_list(directory):
    file_list = []
    for root, _, files in os.walk(directory):
        for name in files:
            file_list.append(os.path.join(root, name))


def modify_line(line, config):
    for old, new in config.items():
        for transformation in TRANSFORMATIONS:
            if transformation(old) in line:
                line = line.replace(transformation(old), transformation(new))
    return line


def execute_reskin(file_path, config):
    all_lines = []
    with open(file_path, "r") as reskin_file:
        for line in reskin_file:
            all_lines.append(line)
    with open(file_path, "w") as reskin_file:
        for line in all_lines:
            reskin_file.write(modify_line(line, config))



def main():
    # file_list = get_file_list(RENAME_DIR)
    # for file_path in file_list:
    config = get_config(NAMES_FILE)
    execute_reskin("test.txt", config)


if __name__ == "__main__":
    main()
