## Project Manager

Plugin for [fman.io](https://fman.io) that gives you the ability to run startup scripts when entering a project directory.

Install by uploading "ProjectManager" to your [data directory](https://fman.io/docs/customizing-fman)`/Plugins`. This extension is designed to work with the "OpenWithEditor" extension as well. If the "OpenWithEditor" extension is loaded, it will open the script files using the editor selected in **BitBar**. Otherwise, it will use **TextEdit**.

After restarting **fman**, you will have the ability to set a new project directory, start processes, etc.

### Usage

<Shift+s>  - Runs the set_project_directory function in the current directory (or the directory under the cursor).

<Shift+c> - Clear the current project setting.

<Shift+e> - Edit the current project's startup script.

Search Projects - This allows you to pick a project to go to from a list. By typing letters in the name, it will fuzzy match and trim down the selection list.

### Features

 - The ability to set a current project directory.
 - Run a startup script when entering a project directory from another one.
 - Go to the project by picking it from a list of projects.
