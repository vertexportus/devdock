import re
from tempfile import mkstemp
from shutil import move, copymode
from os import fdopen, remove
from .gitprogress import GitProgress
from .colorargparse import ColoredArgumentParser


def file_regex_replace(file_path, pattern, subst):
    regex = re.compile(pattern)
    # Create temp file
    fh, abs_path = mkstemp()
    with fdopen(fh, 'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                if regex.match(line):
                    value = regex.sub(line, subst)
                else:
                    value = line
                new_file.write(value)
    # Copy the file permissions from the old file to the new file
    copymode(file_path, abs_path)
    # Remove original file
    remove(file_path)
    # Move new file
    move(abs_path, file_path)
