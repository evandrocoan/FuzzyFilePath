###
# # FuzzyFilePath
#
# Manages autocompletions
#
# @version 0.0.3
# @author Sascha Goldhofer <post@saschagoldhofer.de>
###
import sublime
import sublime_plugin
import re
import os

from FuzzyFilePath.Cache.ProjectFiles import ProjectFiles
from FuzzyFilePath.Query import Query

Completion = {

    "active": False,
    "before": None,
    "after": None
}

query = Query()
project_files = None

def plugin_loaded():
    """load settings"""
    settings = sublime.load_settings("FuzzyFilePath.sublime-settings")
    settings.add_on_change("extensionsToSuggest", update_settings)
    update_settings()

##
# reads plugin and project settings
def update_settings():
    """update settings"""
    global project_files

    exclude_folders = []
    project_folders = sublime.active_window().project_data().get("folders", [])
    settings = sublime.load_settings("FuzzyFilePath.sublime-settings")
    query.scopes = settings.get("scopes", [])
    query.auto_trigger = (settings.get("auto_trigger", True))

    # build exclude folders
    for folder in project_folders:
        base = folder.get("path")
        exclude = folder.get("folder_exclude_patterns", [])
        for f in exclude:
            exclude_folders.append(os.path.join(base, f))

    # or use default settings
    if (len(exclude_folders) == 0):
        exclude_folders = settings.get("excludeFolders", ["node_modules"])

    project_files = ProjectFiles(settings.get("extensionsToSuggest", ["js"]), exclude_folders)


def get_path_at_cursor(view):
    word = get_word_at_cursor(view)
    line = get_line_at_cursor(view)
    path = get_path(line[0], word[0])
    path_region = sublime.Region(word[1].a, word[1].b)
    path_region.b = word[1].b
    path_region.a = word[1].a - (len(path) - len(word[0]))
    return [path, path_region]

def get_path(line, word):
    path = None
    full_words = line.split(" ")

    for full_word in full_words:
        if word in line:
            if (path is not None):
                print("multiple matches found in", line, "for", word)
            path = extract_path_from(full_word, word)

    if (path is None):
        return word

    return path


def extract_path_from(word, needle):
    result = re.search("([^\"\'\s]*)" + needle, word)

    if (result is not None):
        return result.group(0)


def get_line_at_cursor(view):
    selection = view.sel()[0]
    position = selection.begin()
    region = view.line(position)

    return [view.substr(region), region]


def get_word_at_cursor(view):
    selection = view.sel()[0]
    position = selection.begin()
    region = view.word(position)
    word = view.substr(region)

    # single line only
    if "\n" in word:
        return ["", sublime.Region(position, position)]

    if word[0] is '"':
        word = word[1:]
        region.a += 1

    if word[-1:] is '"':
        word = word[1:]
        region.a += 1

    return [word, region]


class ReplaceRegionCommand(sublime_plugin.TextCommand):

    def run(self, edit, a, b, string):
        self.view.replace(edit, sublime.Region(a, b), string)


"""triggers autocomplete"""
class InsertPathCommand(sublime_plugin.TextCommand):

    def run(self, edit, type="default"):
        query.relative = type
        self.view.run_command('auto_complete')


class FuzzyFilePath(sublime_plugin.EventListener):

    def on_text_command(self, view, command_name, args):
        if command_name == "commit_completion":

            path = get_path_at_cursor(view)
            word_replaced = re.split("[./]", path[0]).pop()
            if (path is not word_replaced):
                Completion["before"] = re.sub(word_replaced + "$", "", path[0])
                # print("before commit", path[0], word_replaced, Completion["before"])

        elif command_name == "hide_auto_complete":

            Completion["active"] = False

    def on_post_text_command(self, view, command_name, args):
        if (command_name == "commit_completion" and Completion["active"]):

            Completion["active"] = False
            if Completion["before"] is not None:

                path = get_path_at_cursor(view)
                final_path = re.sub("^" + Completion["before"], "", path[0])
                Completion["before"] = None
                # print("replace", path[0], "with", Completion["before"], final_path)
                view.run_command("replace_region", { "a": path[1].a, "b": path[1].b, "string": final_path })


    def on_post_save_async(self, view):
        if project_files is not None:
            for folder in sublime.active_window().folders():
                if folder in view.file_name():
                    project_files.update(folder, view.file_name())


    def on_query_completions(self, view, prefix, locations):
        if (query.valid is False):
            return False

        current_scope = view.scope_name(locations[0])
        needle = get_path_at_cursor(view)[0]

        if query.build(current_scope, needle, query.relative) is False:
            return

        view.run_command('_enter_insert_mode')
        Completion["active"] = True
        # print("search", query["needle"], "relative to", query["relative"], "base path:")
        # print(query.needle, query.project_folder, query.extensions, query.relative, query.extension)
        completions = project_files.search_completions(query.needle, query.project_folder, query.extensions, query.relative, query.extension)
        query.reset()
        return completions

    def on_activated(self, view):
        file_name = view.file_name()
        folders = sublime.active_window().folders()

        if (project_files is None):
            query.valid = False
            return False

        if query.update(folders, file_name):
            project_files.add(query.project_folder)