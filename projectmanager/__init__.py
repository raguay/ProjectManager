#
# Load the libraries that are used in these commands.
#
from core.quicksearch_matchers import contains_chars
from fman import DirectoryPaneCommand, DirectoryPaneListener, show_alert
from fman import load_json, DATA_DIRECTORY, show_prompt, YES, NO, show_quicksearch
from fman import QuicksearchItem, show_status_message, clear_status_message
from core.commands import _get_thirdparty_plugins, _THIRDPARTY_PLUGINS_DIR
import os
import stat
from fman.url import as_human_readable, as_url, join
from fman.fs import iterdir, exists, mkdir

#
# I'm using two globals because it is faster for checking
# the directories. I also have an Alfred workflow that makes
# use of this information.
#
PROJECTDIR = os.path.expanduser("~") + "/.currentprojectdir"
PROJECTSLIST = os.path.expanduser("~") + "/.projects"


class SearchProjects(DirectoryPaneCommand):
    #
    # This directory command is for selecting a project
    # and going to that directory.
    #
    def __call__(self):
        show_status_message('Project Selection')
        result = show_quicksearch(self._suggest_projects)
        if result:
            query, projectName = result
            if os.path.isfile(PROJECTSLIST):
                with open(PROJECTSLIST, "r") as f:
                    projects = f.readlines()
            for projectTuple in projects:
                parts = projectTuple.split('|')
                if parts[0].strip() == projectName:
                    self.pane.set_path(as_url(parts[1].strip()))
        clear_status_message()

    def _suggest_projects(self, query):
        projects = ["No Projects are setup."]
        if os.path.isfile(PROJECTSLIST):
            with open(PROJECTSLIST, "r") as f:
                projects = f.readlines()
        for projectTuple in projects:
            if projectTuple.strip() != "":
                project = projectTuple.split('|')[0].strip()
                match = contains_chars(project.lower(), query.lower())
                if match or not query:
                    yield QuicksearchItem(project, highlight=match)

class RemoveProject(DirectoryPaneCommand):
    #
    # This directory command is for selecting a project
    # and going to that directory.
    #
    def __call__(self):
        show_status_message('Remove Project Selection')
        result = show_quicksearch(self._suggest_projects)
        if result:
            query, projectName = result
            if os.path.isfile(PROJECTSLIST):
                with open(PROJECTSLIST, "r") as f:
                    projects = f.readlines()
                with open(PROJECTSLIST, "w") as f:
                    for projectTuple in projects:
                        parts = projectTuple.split('|')
                        if parts[0].strip() != projectName:
                            f.write(projectTuple)
        clear_status_message()

    def _suggest_projects(self, query):
        projects = ["No Projects are setup."]
        if os.path.isfile(PROJECTSLIST):
            with open(PROJECTSLIST, "r") as f:
                projects = f.readlines()
        for projectTuple in projects:
            if projectTuple.strip() != "":
                project = projectTuple.split('|')[0].strip()
                match = contains_chars(project.lower(), query.lower())
                if match or not query:
                    yield QuicksearchItem(project, highlight=match)

class SetProjectDirectory(DirectoryPaneCommand):
    #
    # This dirctory command is for setting up a new project
    # directory. It will add to the list of project directories
    # and set the current project directory to the directory.     #
    def __call__(self):
        #
        # Get the directory path.
        #
        selected_files = self.pane.get_selected_files()
        if len(selected_files) >= 1 or (len(selected_files) == 0 and self.get_chosen_files()):
            if len(selected_files) == 0 and self.get_chosen_files():
                selected_files.append(self.get_chosen_files()[0])
            dirName = as_human_readable(selected_files[0])
            if os.path.isfile(dirName):
                #
                # It's a file, not a directory. Get the directory
                # name for this file's parent directory.
                #
                dirName = os.path.dirname(dirName)
            #
            # Set the directory obtained as a project directory.
            #
            with open(PROJECTDIR, "w") as f:
                f.write(dirName)
            #
            # Add to the list of projects. Get a name
            # from the user.
            #
            projName, checked = show_prompt("Name this Project:")
            projEntry = projName + "|" + dirName
            writeappend = 'w'
            if os.path.isfile(PROJECTSLIST):
                writeappend = 'a'
            with open(PROJECTSLIST, writeappend) as f:
                f.write(projEntry+"\n")
            #
            # Create the launch script file and open in the
            # editor.
            #
            scriptFile = dirName + "/.startproject"
            with open(scriptFile, 'w') as f:
                f.write("#!/bin/sh\n\n")
            os.chmod(scriptFile, stat.S_IEXEC|stat.S_IRUSR|stat.S_IWUSR)
            if (_THIRDPARTY_PLUGINS_DIR + "/OpenWithEditor") in _get_thirdparty_plugins():
                self.pane.run_command("my_open_with_editor", args={'url': as_url(scriptFile)})
            else:
                self.pane.run_command("open_with_editor", args={'url': as_url(scriptFile)})
        else:
            #
            # Technically, this will never be reached. Just here
            # for completeness.
            #
            show_alert("No directory selected")

class ClearProjectDirectory(DirectoryPaneCommand):
    #
    # This dirctory command is clearing out the current project.
    # This is good to do before exiting fman.
    #
    def __call__(self):
        with open(PROJECTDIR,'w') as f:
            f.write("")

class EditProjectStartScript(DirectoryPaneCommand):
    #
    # This dirctory command is clearing out the current project.
    # This is good to do before exiting fman.
    #
    def __call__(self):
        #
        # Get the current project directory.
        #
        dirName = ""
        with open(PROJECTDIR, 'r') as f:
            dirName = f.read()
        if dirName != "":
            #
            # A project directory is set. Edit it's start file.
            #
            scriptFile = dirName + "/.startproject"
            if (_THIRDPARTY_PLUGINS_DIR + "/OpenWithEditor") in _get_thirdparty_plugins():
                self.pane.run_command("my_open_with_editor", args={'url': as_url(scriptFile)})
            else:
                self.pane.run_command("open_with_editor", args={'url': as_url(scriptFile)})

class EnteringProjectDirectory(DirectoryPaneListener):
    #
    # This is called everytime a directory is changed
    # in fman. Do a quick check to see if it's a project
    # directory. If so, if it's not the current project,
    # set to the current project and run the setup script
    # for the project.
    #
    def on_path_changed(self):
        #
        # See if the new directory is a project directory.
        #
        newDir = as_human_readable(self.pane.get_path())
        scriptFile = newDir + "/.startproject"
        if os.path.isfile(scriptFile):
            #
            # Get the current project name and see if they
            # are the same.
            #
            projDir = ""
            with open(PROJECTDIR) as f:
                projDir = f.read()
            if projDir != newDir:
                #
                # They are different! Set the new project directory
                # and run the .startproject script. Pass the new project 
                # directory to the script file.
                #
                with open(PROJECTDIR, "w") as f:
                    f.write(newDir)
                os.system("'" + scriptFile + "' '" + newDir + "'")

class SearchProjects(DirectoryPaneCommand):
    #
    # This directory command is for selecting a project
    # and going to that directory.
    #
    def __call__(self):
        show_status_message('Project Selection')
        result = show_quicksearch(self._suggest_projects)
        if result:
            query, projectName = result
            if os.path.isfile(PROJECTSLIST):
                with open(PROJECTSLIST, "r") as f:
                    projects = f.readlines()
            for projectTuple in projects:
                parts = projectTuple.split('|')
                if parts[0].strip() == projectName:
                    self.pane.set_path(as_url(parts[1].strip()))
        clear_status_message()

    def _suggest_projects(self, query):
        projects = ["No Projects are setup."]
        if os.path.isfile(PROJECTSLIST):
            with open(PROJECTSLIST, "r") as f:
                projects = f.readlines()
        for projectTuple in projects:
            if projectTuple.strip() != "":
                project = projectTuple.split('|')[0].strip()
                match = contains_chars(project.lower(), query.lower())
                if match or not query:
                    yield QuicksearchItem(project, highlight=match)



