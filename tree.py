import os
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern


def read_gitignore(gitignore_path):
    ignore_patterns = []

    with open(gitignore_path, 'r') as gitignore_file:
        for line in gitignore_file:
            line = line.strip()
            if not line.startswith('#') and line:
                ignore_patterns.append(line)
    return ignore_patterns


def is_ignored(relative_path, pathspec):
    if pathspec and pathspec.match_file(relative_path):
        return True
    # Check if the path is the .idea or .git folder
    if os.path.basename(relative_path) in {'.idea', '.git', '.gitignore'}:
        return True
    return False


def print_tree(start_path, project_path, pathspec, output_file, level=0):
    for item in os.listdir(start_path):
        item_path = os.path.join(start_path, item)
        relative_path = os.path.relpath(item_path, project_path)
        if not is_ignored(relative_path, pathspec):
            output_file.write(' ' * 4 * level + '+-- ' + item + '\n')
            if os.path.isdir(item_path):
                print_tree(item_path, project_path, pathspec, output_file, level + 1)


if __name__ == '__main__':
    project_path = os.getcwd()
    gitignore_path = os.path.join(project_path, '.gitignore')

    if os.path.exists(gitignore_path):
        ignore_patterns = read_gitignore(gitignore_path)
        pathspec = PathSpec.from_lines(GitWildMatchPattern, ignore_patterns)
    else:
        pathspec = None

    # Write the result to the project_structure_filtered.txt file
    with open('project_structure_filtered.txt', 'w') as output_file:
        print_tree(project_path, project_path, pathspec, output_file)
