import os

example_file = """
# Extensions to include
# .py
# .js
# .jsx

# Extensions to exclude
!*.min.js
!*.min.css


# Files to ignore
!package-lock.json

# Folders to ignore
/.git
/node_modules
/dist
/venv
/.venv
/.expo
/migrations
/public-api
/htmlcov
/docs
/.devcontainer
/static
/.idea

"""

def create_default_ignore_file():
    config_path = os.path.expanduser('~/.coderepoignore')

    if not os.path.exists(config_path):
        with open(config_path, 'w') as file:
            file.write(example_file)
        print(f"Created default .coderepoignore file at {config_path}")
