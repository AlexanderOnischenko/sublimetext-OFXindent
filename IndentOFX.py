import sublime
import sublime_plugin
import re
import xml.dom.minidom
from os.path import basename, splitext


class BaseIndentCommand(sublime_plugin.TextCommand):
    def __init__(self, view):
        self.view = view
        self.language = self.get_language()

    def get_language(self):
        syntax = self.view.settings().get('syntax')
        language = splitext(basename(syntax))[0].lower() if syntax is not None else "plain text"
        return language

    def check_enabled(self, lang):
        return True

    def is_enabled(self):
        """
        Enables or disables the 'indent' command. Command will be disabled if
        there are currently no text selections and current file is not 'XML' or
        'Plain Text'. This helps clarify to the user about when the command can
        be executed, especially useful for UI controls.
        """
        if self.view is None:
            return False

        return self.check_enabled(self.get_language())

    def run(self, edit):
        """
        Main plugin logic for the 'indent' command.
        """
        view = self.view
        regions = view.sel()
        # if there are more than 1 region or region one and it's not empty
        if len(regions) > 1 or not regions[0].empty():
            for region in view.sel():
                if not region.empty():
                    s = view.substr(region).strip()
                    s = self.indent(s)
                    view.replace(edit, region, s)
        else:  # format all text
            alltextreg = sublime.Region(0, view.size())
            s = view.substr(alltextreg).strip()
            s = self.indent(s)
            if s:
                view.replace(edit, alltextreg, s)

    def indent(self, s):
        return s


class AutoIndentCommand(BaseIndentCommand):
    def get_text_type(self, s):
        language = self.language
        if language == 'xml':
            return 'xml'
        if language == 'json':
            return 'json'
        if language == 'ofx':
            return 'OFX'
        if language == 'plain text' and s:
            if s[0] == '<':
                return 'xml'
            if s[0] == '{' or s[0] == '[':
                return 'json'

        return 'notsupported'

    def indent(self, s):
        text_type = self.get_text_type(s)
        if text_type == 'xml':
            command = IndentXmlCommand(self.view)
        if text_type == 'json':
            command = IndentJsonCommand(self.view)
        if text_type == 'OFX':
            command = IndentOFXCommand(self.view)
        if text_type == 'notsupported':
            return s

        return command.indent(s)

    def check_enabled(self, lang):
        return True

class IndentOFXCommand(BaseIndentCommand):
    def indent(self, s):
        matches = re.findall(r'<\?OFX.*?><\/OFX>', s, re.DOTALL)
        incindent = 3
        for match in matches:
            new_match = match
            #detect and indent OFX header
            headers = re.findall(r'\n*<\?OFX[^>]*?>', match, re.DOTALL)
            for header in headers:
                new_match = new_match.replace(header, "\n" + header.lstrip('\n') )
            #start with the first opening tag <OFX>
            position = new_match.find('<OFX>')
            if position < 0:
                #if there is no <OFX> tag - exit
                return s
            indent = 0
            secondclose = False
            while position < len(new_match)-5:
                #skip for already indented tags
                searchstr = re.search(r'\n[\s]*<[^>]*>', new_match[position:])
                if searchstr != None:
                    position = position + searchstr.end()
                    continue
                searchstr = re.search(r'<.*>', new_match[position:])
                if searchstr != None:
                    any_tag_position = position + searchstr.start()
                else:
                    any_tag_position = -1
                searchstr = re.search(r'<\/[^>]*>', new_match[position:])
                if searchstr != None:
                    close_tag_position = position + searchstr.start()
                    close_tag_position_end = position + searchstr.end()
                else:
                    close_tag_position = -1
                    close_tag_position_end = 0
              #  print(any_tag_position, close_tag_position, secondclose)
                if any_tag_position != close_tag_position:
                    #мы нашли открытый тэг
                  #  print(new_match[any_tag_position:any_tag_position+30]+"\n")
                    new_match = new_match[:any_tag_position] + "\n" + ' ' * indent + new_match[any_tag_position:].lstrip()
                    indent = indent + incindent
                    position = any_tag_position + 2 + indent
                  #  print(new_match[any_tag_position:any_tag_position+30]+"\n")
                    secondclose = False
                else:
                    #мы нашли закрытый тэг
                    indent = indent - incindent if indent > incindent else 0
                  #  print(new_match[any_tag_position:any_tag_position+30]+"\n")
                    if secondclose:
                        new_match = new_match[:any_tag_position] + "\n" + ' ' * indent + new_match[any_tag_position:].lstrip()
                    #   print(new_match[any_tag_position:any_tag_position+30]+"\n")
                        position = any_tag_position + 2+ indent
                    else:
                        position = close_tag_position_end
                    secondclose = True
                # print(new_match[position:position+30]+"\n")
            s = s.replace(match, new_match)
        return s

    def check_enabled(self, language):
        return (language == "xml") or (language == "plain text")