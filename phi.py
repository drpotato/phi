#! /usr/bin/env python3

import os
import sys

__author__ = 'Chris Morgan'


class Phi:

    def __init__(self):

        if not os.path.isdir('A2dir'):
            os.mkdir('A2dir')

        os.chdir('A2dir')

        file_list = os.listdir('.')

        self.root = self.build_directory_structure(file_list)

        self.cwd = self.root

    @staticmethod
    def build_directory_structure(file_list):

        dir_levels = dict()
        root = Directory('-')

        for file in file_list:
            level = file.count('-')

            if level in dir_levels:
                dir_levels[level].add(file)
            else:
                dir_levels[level] = {file}

        for files in list(dir_levels.values())[::-1]:
            for file_path in files:
                path_list = file_path.split('-')[1:]
                file_name = path_list.pop()
                file = File(file_name)
                cwd = root
                for dir in path_list:
                    if dir in cwd:
                        cwd = cwd[dir]
                    else:
                        new_dir = Directory(dir)
                        new_dir.set_parent(cwd)
                        cwd.add_file(new_dir)
                        cwd = new_dir
                cwd.add_file(file)

        return root

    def run(self):
        """
        Starts the shell, listening until 'exit' is called.
        """

        # Infinite loop, woo!
        while True:

            # Stop pycharm complaining.
            input_string = None

            try:
                input_string = input(self.get_prompt())
            except EOFError:  # If we hit the end of a file or user types ctrl + d.
                exit()

            # For the markers.
            if not sys.stdin.isatty():
                print(self.get_prompt() + input_string)

            input_segments = input_string.split()

            command = input_segments.pop(0)
            arguments = input_segments

            # Get shell words from input
            command_strings = self.parse_line(input_string)

            if command == 'pwd':
                print(self.cwd.get_full_path())

            elif command == 'cd':
                if not arguments:
                    self.cwd = self.root
                elif arguments[0] == '..':
                    self.cwd = self.cwd.parent
                else:
                    path = arguments[0].split('-')

                    if path[0]:
                        new_cwd = self.cwd
                    else:
                        path.pop(0)
                        new_cwd = self.root

                    for directory in path:
                        new_cwd = new_cwd[directory]
                    if new_cwd is not None and not new_cwd.is_file():
                        self.cwd = new_cwd
                    else:
                        print('no such directory')

            elif command == 'ls':
                files = []
                for file in self.cwd:
                    if self.is_dir(file):
                        file_name = 'd: '
                    else:
                        file_name = 'f: '
                    file_name += str(file)
                    files.append(file_name)
                print(' '.join(files))

            elif command == 'rls':
                print(os.system('ls -l'))

            elif command == 'delete':
                if not arguments:
                    print('requires arguments')
                else:
                    self.root.search(arguments[0]).delete()



            elif command in ['exit', 'quit']:
                exit()

    def get_prompt(self):
        return '%s > ' % self.cwd

    @staticmethod
    def parse_line(line):
        """
            Breaks the line up into shell words.
            :returns: Returns a list of
            :rtype:
            """

        line_segments = line.split()

        command = line_segments.pop(0)

        return command, line_segments


class File:

    def __init__(self, name):
        self.name = name
        self.parent = None

    def set_parent(self, parent):
        self.parent = parent


    def delete(self):
        os.remove('%s-%s' % (self.get_full_path(), self.name))

    def search(self, item):
        if item == self.name:
            return self
        else:
            return None

    def __str__(self):
        return self.name

    def get_full_path(self):
        if self.parent is None:
            return self.name
        return self.parent.get_full_path() + self.name + '-'

    def is_file(self):
        return True


class Directory(File):

    def __init__(self, name):
        super().__init__(name)
        self.files = set()

    def __iter__(self):
        return iter(self.files)

    def __add__(self, other):
        self.files.update({other})

    def __contains__(self, item):

        if item.__class__.__name__ == 'str':
            for file in self.files:
                if str(file) == item:
                    return True
            return False

        return item in self.files

    def __getitem__(self, item):
        for file in self.files:
            if file.__class__.__name__ in ['File', 'Directory'] and file.name == item:
                return file
            elif file == item:
                return file

        return None

    def is_file(self):
        return False

    def delete(self):
        for file in self.files:
            file.delete()

    def search(self, item):
        if item == self.name:
            return self
        else:
            for file in self.files:
                result = file.search(item)
                if result is not None:
                    return result
            return None

    def add_file(self, file):
        self.files.add(file)
        file.set_parent(self)


if __name__ == '__main__':
    phi = Phi()
    phi.run()