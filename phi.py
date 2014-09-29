#! /usr/bin/env python3

import os
import sys

__author__ = 'Chris Morgan - cmor149'


class Phi:

    def __init__(self):

        if not os.path.isdir('A2dir'):
            os.mkdir('A2dir')

        os.chdir('A2dir')

        self.root = Directory('-')

        for file in os.listdir('.'):
            path = file.split('-')[1:]
            file_name = path.pop()

            self.root.create(path, file_name)

        self.cwd = self.root

    def run(self):
        """
        Starts the shell, listening until 'exit' is called.
        """

        # Infinite loop, woo!
        while True:

            # Stop pycharm complaining.
            input_string = None

            try:
                input_string = input(self.get_prompt() if sys.stdin.isatty() else '')
            except EOFError:  # If we hit the end of a file or user types ctrl + d.
                exit()

            # For the markers.
            if not sys.stdin.isatty():
                print(self.get_prompt() + input_string)


            input_segments = input_string.split()

            command = input_segments.pop(0)
            arguments = input_segments

            try:
                getattr(self, 'cmd_' + command)(arguments)
            except AttributeError:
                print('Command not found: ' + command)

    def cmd_pwd(self, arguments):
        print(self.cwd.get_full_path(), '-', sep='')

    def cmd_cd(self, arguments):
        if not arguments:
            self.cwd = self.root
        elif arguments[0] == '..' and self.cwd.parent is not None:
            self.cwd = self.cwd.parent
        else:
            path = arguments[0].split('-')
            if len(path) > 1 and not path[-1]:
                path.pop()

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

    def cmd_rls(self, arguments):
        os.system('ls -l')

    def cmd_ls(self, arguments):
        path = arguments[0].split('-') if arguments else arguments

        cwd = self.root if path and not path[0] else self.cwd

        for directory in path:
            if directory in cwd:
                cwd = cwd[directory]
            else:
                print('No such directory:', path[-1])
                return
        files = []
        for file in sorted(cwd, key=str):
            if file.is_file():
                file_name = 'f: '
            else:
                file_name = 'd: '
            file_name += str(file)
            files.append(file_name)
        print('\n'.join(files)) if files else print(end='')

    def cmd_delete(self, arguments):
        if not arguments:
            print('requires arguments')
        else:

            path = arguments[0].split('-')
            if len(path) > 1 and not path[-1]:
                path.pop()

            if path[0]:
                cwd = self.cwd
            else:
                path.pop(0)
                cwd = self.root

            file = path.pop()

            cwd.traverse(path, file).delete()

    def cmd_dd(self, arguments):
        if not arguments:
            print('requires arguments')
        else:

            path = arguments[0].split('-') if arguments else arguments

            if len(path) > 1 and not path[-1]:
                path.pop()

            if path[0]:
                cwd = self.cwd

            else:
                path.pop(0)
                cwd = self.root

            item = path.pop()

            directory = cwd.traverse(path, item)

            if directory is not None:
                directory.parent.delete_directory(directory)
            else:
                print('No such directory:', path[-1])

    def cmd_tree(self, arguments):

        path = arguments[0].split('-') if arguments else arguments

        if len(path) > 1 and not path[-1]:
            path.pop()

        if not path:
            self.cwd.tree(0)
            return

        if path[0]:
            cwd = self.cwd

        else:
            path.pop(0)
            cwd = self.root

        item = path.pop()

        directory = cwd.traverse(path, item)

        if directory is not None:
            directory.tree(0)
        else:
            print('No such directory:', path[-1])

    def cmd_clear(self, arguments):
        self.cwd = self.root
        self.cwd.recursive_delete()
        self.cwd.files = set()

    def cmd_create(self, arguments):

        if not arguments:
            print('requires arguments')
        else:
            path = arguments[0].split('-')
            file_name = path.pop()
            if path and path[0]:
                self.cwd.create(path, file_name)
            else:
                self.root.create(path[1:], file_name)

    def cmd_add(self, arguments):

        if len(arguments) < 2:
            print('requires 2 arguments')
        else:
            path = arguments[0].split('-')

            if len(path) > 1 and not path[-1]:
                path.pop()

            if not path:
                self.cwd.tree(0)
                return

            if path[0]:
                cwd = self.cwd

            else:
                path.pop(0)
                cwd = self.root

            item = path.pop()

            file = cwd.traverse(path, item)

            text = ' '.join(arguments[1:])

            if file:
                file.write(text)
            else:
                print('No such file:', path[-1])

    def cmd_cat(self, arguments):
        if not arguments:
            print('requires arguments')
        else:

            path = arguments[0].split('-')

            if len(path) > 1 and not path[-1]:
                path.pop()

            if not path:
                self.cwd.tree(0)
                return

            if path[0]:
                cwd = self.cwd

            else:
                path.pop(0)
                cwd = self.root

            item = path.pop()

            file = cwd.traverse(path, item)

            if file:
                text = file.read()
                if text:
                    print(text)
            else:
                print('No such file:', path[-1])

    def cmd_quit(self, arguments):
        exit()

    cmd_exit = cmd_quit

    def get_prompt(self):
        return 'ffs> '


class File:

    def __init__(self, name):
        self.name = name
        self.parent = None

    def set_parent(self, parent):
        self.parent = parent

    def delete(self):
        os.remove(self.get_full_path())
        self.parent.files.remove(self)

    def recursive_delete(self):
        os.remove(self.get_full_path())

    def __str__(self):
        return self.name

    def get_full_path(self):
        if self.parent is None:
            return ''
        return self.parent.get_full_path() + '-' + self.name

    def is_file(self):
        return True

    def tree(self, level):
        print('    ' * (level - 1), str(self), sep='')

    def create(self, path, file_name):
        pass

    def write(self, text):
        with open(self.get_full_path(), 'a') as f:
            f.write(text)

    def read(self):
        with open(self.get_full_path(), 'r') as f:
            return f.read()


class Directory(File):

    def __init__(self, name):
        super().__init__(name)
        self.files = set()

    def __iter__(self):
        return iter(self.files)

    def __add__(self, other):
        self.files.update({other})

    def __contains__(self, item):

        if type(item) is str:
            for file in self:
                if str(file) == item:
                    return True
            return False

        return item in self.files

    def __getitem__(self, item):
        for file in self:
            if type(file) in [File, Directory] and file.name == item:
                return file
            elif file == item:
                return file

        return None

    def is_file(self):
        return False

    def recursive_delete(self):
        for file in self:
            file.recursive_delete()

    def delete_directory(self, directory):
        directory.recursive_delete()
        self.files.remove(directory)

    def traverse(self, path, item):
        if item == self.name:
            return self
        else:
            if path and path[0] in self:
                return self[path.pop(0)].traverse(path, item)
            elif item in self:
                return self[item]
        return None

    def add_file(self, file):
        self.files.add(file)
        file.set_parent(self)

    def tree(self, level):

        name = self.get_full_path() + '-' if self.parent else '-'

        print('    ' * level, name, sep='')
        print('    ' * level, '=' * len(name), sep='')

        for file in sorted(self.files, key=str):
            file.tree(level + 1)

    def create(self, path, file_name):
        if path and path[0] in self:
            self[path[0]].create(path[1:], file_name)
        else:
            if path:
                directory = Directory(path.pop(0))
                directory.parent = self
                self.add_file(directory)
                directory.create(path, file_name)
            else:
                file = File(file_name)
                self.add_file(file)
                open(self.get_full_path() + '-' + file_name, 'w')

if __name__ == '__main__':
    phi = Phi()
    phi.run()