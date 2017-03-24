#
# Load the libraries that are used in these commands.
#
from fman import DirectoryPaneCommand, DirectoryPaneListener, show_alert, load_json, DATA_DIRECTORY, show_prompt
import os, stat

#
# I'm using two globals because it is faster for checking
# the directories. I also have an Alfred workflow that makes
# use of this information.
#
PROJECTDIR = os.path.expanduser("~") + "/.currentprojectdir"
PROJECTSLIST = os.path.expanduser("~") + "/.projects"

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
            dirName = selected_files[0]
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
            with open(PROJECTSLIST,writeappend) as f:
                f.write(projEntry+"\n")
            #
            # Create the launch script file and open in the
            # editor.
            #
            scriptFile = dirName + "/.startproject"
            with open(scriptFile, 'w') as f:
                f.write("#!/bin/sh\n\n")
            os.chmod(scriptFile, stat.S_IEXEC|stat.S_IRUSR|stat.S_IWUSR)
            scriptLoc = load_json("OpenWithEditor.json")["scriptLoc"]
            if scriptLoc is None:
                #
                # Open the file with the TextEdit that is on every Mac.
                #
                os.system("/usr/bin/open -a TextEdit '" + scriptFile + "'")
            else:
                #
                # They have the OpenWithEditor extension. Use it.
                #
                os.system("'" + scriptLoc + "' 'file' '" + scriptFile + "' &")
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
        with open(PROJECTDIR,'r') as f:
            dirName = f.read()
        if dirName != "":
            #
            # A project directory is set. Edit it's start file.
            #
            scriptFile = dirName + "/.startproject"
            scriptLoc = load_json("OpenWithEditor.json")["scriptLoc"]
            if scriptLoc is None:
                #
                # Open the file with the TextEdit that is on every Mac.
                #
                os.system("/usr/bin/open -a TextEdit '" + scriptFile + "'")
            else:
                #
                # They have the OpenWithEditor extension. Use it.
                #
                os.system("'" + scriptLoc + "' 'file' '" + scriptFile + "' &")

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
        newDir = self.pane.get_path()
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
                # and run the .startproject script.
                #
                with open(PROJECTDIR, "w") as f:
                    f.write(newDir)
                os.system("'" + scriptFile + "'")