#! /usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import sublime
import sublime_plugin
from .proto_formatter import ProtoParser, ProtoFormatter

class PrettyProtoCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        region = sublime.Region(0, self.view.size())
        lines = self.view.substr(region)

        command = ['clang-format']
        if self.view.file_name():
            command += ['-assume-filename', self.view.file_name()]
        proc = subprocess.Popen(command, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        stdout, stderr = proc.communicate(input=lines.encode())
        if stderr:
          print(f'{stderr = }')
        if not stdout:
          print('No output from clang-format, maybe crashed...\n'
                'Please report to https://github.com/hanfezh/pretty-proto/issues')
          return

        # Replace with formatted content
        self.view.replace(edit, region, stdout.decode())

class PrettyDebugStringCommand(sublime_plugin.TextCommand):
    parser = ProtoParser()

    def pretty_proto(self, s):
        obj = self.parser.parse(s)
        return ProtoFormatter(obj).format()

    def run(self, edit):
        if len(self.view.sel()) < 1:
            return
        first_reg = self.view.sel()[0]
        if first_reg.empty():
            first_reg = sublime.Region(0, self.view.size())
        lines = self.view.substr(first_reg)
        if not lines:
            return
        try:
            lines = self.pretty_proto(lines)
            if lines:
                self.view.replace(edit, first_reg, lines)
        except lex.LexError as err:
            print(f'{lines = }\n{err = }')
