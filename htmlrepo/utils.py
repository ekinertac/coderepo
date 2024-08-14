import os


def create_default_ignore_file():
    config_path = os.path.expanduser('~/.htmlrepoignore')

    # read example config file
    with open(os.path.join(os.path.dirname(__file__), '.htmlrepoignore-example'), 'r') as file:
        example_content = file.read()

    if not os.path.exists(config_path):
        with open(config_path, 'w') as file:
            file.write(example_content)
        print(f"Created default .htmlrepoignore file at {config_path}")
