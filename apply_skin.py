import os

def upper_camel(key):
    return key.replace("-", " ").title().replace(" ", "")

def camel(key):
    return key.lower()[0] + upper_camel(key)[1:]

def upper_snake(key):
    return key.replace("-", "_").upper()

def upper_spaces(key):
    return key.replace("-", " ").upper()

def snake(key):
    return key.replace("-", "_")

def spaces(key):
    return key.replace("-", " ")

def upper_train(key):
    words = key.split("-")
    return "-".join(" ".join(words).title().split(" "))

def train(key):
    return key


# If the key is a single word, we can't tell if it
# should be translated to snake, camel, train, or spaces
# so we do our best to pick the right one first and then
# manual edits will have to be made
TRANSFORMATIONS = [
    upper_camel,
    upper_snake,
    upper_spaces,
    upper_train,
    snake,
    camel,
    train,
    spaces,
]


def get_config(names_file):
    config = {}
    with open(names_file, "r") as names:
        for line in names:
            if line[0] == "#":
                continue
            if line == "\n":
                continue
            old, new = line.strip().split(":")
            if not new:
                continue
            config[old] = new
    return config


def get_file_list(directory):
    file_list = []
    for root, _, files in os.walk(directory):
        if root.find("node_modules") == -1:
            for name in files:
                file_list.append(os.path.join(root, name))
    
    return [ f for f in file_list if f.endswith( ('.js', '.py', '.css') ) ]

def get_rename_file_list(directory, repo_root):
    file_list = []
    for root, _, files in os.walk(directory):
        if root.find("node_modules") == -1:
            for name in files:
                file_list.append(os.path.relpath(os.path.join(root, name), repo_root))
    
    return [ f for f in file_list if f.endswith( ('.js', '.py', '.css', '.png', '.svg') ) ]

def modify_line(line, config):
    for old, new in reversed(sorted(config.items())):
        for transformation in TRANSFORMATIONS:
            if transformation(old) in line:
                line = line.replace(transformation(old), transformation(new))
    return line


def execute_reskin_on_file(file_path, config):
    all_lines = []
    with open(file_path, "r") as reskin_file:
        for line in reskin_file:
            all_lines.append(line)
    with open(file_path, "w") as reskin_file:
        for line in all_lines:
            reskin_file.write(modify_line(line, config))

def execute_rename_on_file(file_path, config):
    new_file_path = file_path
    for old, new in reversed(sorted(config.items())):
        for transformation in TRANSFORMATIONS:
            if transformation(old) in new_file_path:
                new_file_path = new_file_path.replace(transformation(old), transformation(new))
    if new_file_path != file_path:
        os.rename(file_path, new_file_path)


def execute_reskin(rename_dir, config):
    file_list = get_file_list(rename_dir)
    for file in file_list:
        execute_reskin_on_file(file, config)

def execute_rename(rename_dir, config, repo_root):
    rename_file_list = get_rename_file_list(rename_dir, repo_root)
    for file_path in rename_file_list:
        execute_rename_on_file(file_path, config)

def main(skin_file):
    repo_root = os.path.dirname(os.path.abspath(__file__))
    config = get_config(skin_file)
    for directory in [
        os.path.join(repo_root, "boardzorg"),
        os.path.join(repo_root, "client"),
        os.path.join(repo_root, "server"),
    ]:
        execute_reskin(directory, config)
        execute_rename(directory, config, repo_root)


if __name__ == "__main__":
    skin_file = "pooh.skin"
    main(skin_file)
