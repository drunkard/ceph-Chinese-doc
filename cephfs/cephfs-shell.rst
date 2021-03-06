.. CephFS Shell

=============
CephFS Shell
=============

CephFS Shell 包含各种类似 shell 的命令，可以直接与
:term:`Ceph 文件系统`\ 交互。

This tool can be used in interactive mode as well as in non-interactive mode.
In former mode, cephfs-shell opens a shell session and after the given command
is finished, it prints the prompt string and waits indefinitely. When the
shell session is finished, cephfs-shell quits with the return value of last
executed command. In non-interactive mode, cephfs-shell issues a command and
exits right after the command's execution is complete with the command's return
value.

Behaviour of CephFS Shell can be tweaked using cephfs-shell.conf. CephFS Shell
looks for it by default at the path provided in environment variable
`CEPHFS_SHELL_CONF` and then in user's home directory
(`~/.cephfs-shell.conf`).

用法：

    cephfs-shell [options] [command]
    cephfs-shell [options] -- [command, command,...]

选项：

    -c, --config FILE     配置文件 cephfs-shell.conf 的路径
    -b, --batch FILE      批处理文件的路径
    -t, --test FILE       Path to transcript(s) in FILE for testing


.. note::

    Latest version of the cmd2 module is required for running cephfs-shell.
    If CephFS is installed through source, execute cephfs-shell in the build
    directory. It can also be executed as following using virtualenv:

.. code:: bash

    [build]$ virtualenv -p python3 venv && source venv/bin/activate && pip3 install cmd2
    [build]$ source vstart_environment.sh && source venv/bin/activate && python3 ../src/tools/cephfs/cephfs-shell


.. Commands

命令
====

mkdir
-----

Create the directory(ies), if they do not already exist.

用法：
        
    mkdir [-option] <directory>... 

* directory - name of the directory to be created.

选项：
  -m MODE    Sets the access mode for the new directory.
  -p, --parent         Create parent directories as necessary. When this option is specified, no error is reported if a directory already exists.
 
put
---

Copy a file/directory to Ceph File System from Local File System.

用法：
    
        put [options] <source_path> [target_path]

* source_path - local file/directory path to be copied to cephfs.
    * if `.` copies all the file/directories in the local working directory.
    * if `-`  Reads the input from stdin. 

* target_path - remote directory path where the files/directories are to be copied to.
    * if `.` files/directories are copied to the remote working directory.

选项：
   -f, --force        Overwrites the destination if it already exists.


get
---
 
Copy a file from Ceph File System to Local File System.

用法： :: 

    get [options] <source_path> [target_path]

* source_path - remote file/directory path which is to be copied to local file system.
    * if `.` copies all the file/directories in the remote working directory.
                    
* target_path - local directory path where the files/directories are to be copied to.
    * if `.` files/directories are copied to the local working directory. 
    * if `-` Writes output to stdout.

选项：
  -f, --force        Overwrites the destination if it already exists.

ls
--

List all the files and directories in the current working directory.

用法： :: 
    
    ls [option] [directory]...

* directory - name of directory whose files/directories are to be listed. 
    * By default current working directory's files/directories are listed.

选项：
  -l, --long	    list with long format - show permissions
  -r, --reverse     reverse sort     
  -H                human readable
  -a, -all          ignore entries starting with .
  -S                Sort by file_size


cat
---

Concatenate files and print on the standard output

用法： :: 

    cat  <file>....

* file - name of the file

cd
--

Change current working directory.

用法： :: 
    
    cd [directory]
        
* directory - path/directory name. If no directory is mentioned it is changed to the root directory.
    * If '.' moves to the parent directory of the current directory.

cwd
---

Get current working directory.
 
用法： :: 
    
    cwd


quit/Ctrl + D
-------------

Close the shell.

chmod
-----

Change the permissions of file/directory.
 
用法： :: 
    
    chmod <mode> <file/directory>

mv
--

Moves files/Directory from source to destination.

用法： :: 
    
    mv <source_path> <destination_path>

rmdir
-----

Delete a directory(ies).

用法： :: 
    
    rmdir <directory_name>.....

rm
--

Remove a file(es).

用法： :: 
    
    rm <file_name/pattern>...


write
-----

Create and Write a file.

用法： :: 
        
        write <file_name>
        <Enter Data>
        Ctrl+D Exit.

lls
---

Lists all files and directories in the specified directory.Current local directory files and directories are listed if no     path is mentioned

Usage: 
    
    lls <path>.....

lcd
---

Moves into the given local directory.

用法： :: 
    
    lcd <path>

lpwd
----

Prints the absolute path of the current local directory.

用法： :: 
    
    lpwd


umask
-----

Set and get the file mode creation mask 

用法： :: 
    
    umask [mode]

alias
-----

Define or display aliases

Usage: 

    alias [name] | [<name> <value>]

* name - name of the alias being looked up, added, or replaced
* value - what the alias will be resolved to (if adding or replacing) this can contain spaces and does not need to be quoted

run_pyscript
------------

Runs a python script file inside the console

Usage: 
    
    run_pyscript <script_path> [script_arguments]

* Console commands can be executed inside this script with cmd ("your command")
  However, you cannot run nested "py" or "pyscript" commands from within this
  script. Paths or arguments that contain spaces must be enclosed in quotes

.. note:: This command is available as ``pyscript`` for cmd2 versions 0.9.13
   or less.

py
--

Invoke python command, shell, or script

用法： :: 

        py <command>: Executes a Python command.
        py: Enters interactive Python mode.

shortcuts
---------

Lists shortcuts (aliases) available

用法： ::

    shortcuts

history
-------

View, run, edit, and save previously entered commands.

用法： :: 
    
    history [-h] [-r | -e | -s | -o FILE | -t TRANSCRIPT] [arg]

选项：
   -h             show this help message and exit
   -r             run selected history items
   -e             edit and then run selected history items
   -s             script format; no separation lines
   -o FILE        output commands to a script file
   -t TRANSCRIPT  output commands and results to a transcript file

unalias
-------

Unsets aliases
 
用法： :: 
    
    unalias [-a] name [name ...]

* name - name of the alias being unset

选项：
   -a     remove all alias definitions

set
---

Sets a settable parameter or shows current settings of parameters.

用法： :: 

    set [-h] [-a] [-l] [settable [settable ...]]

* Call without arguments for a list of settable parameters with their values.

选项：
  -h     show this help message and exit
  -a     display read-only settings as well
  -l     describe function of parameter

edit
----

Edit a file in a text editor.

Usage:  

    edit [file_path]

* file_path - path to a file to open in editor

run_script
----------

Runs commands in script file that is encoded as either ASCII or UTF-8 text.
Each command in the script should be separated by a newline.

Usage:  
    
    run_script <file_path>


* file_path - a file path pointing to a script

.. note:: This command is available as ``load`` for cmd2 versions 0.9.13
   or less.

shell
-----

Execute a command as if at the OS prompt.

Usage:  
    
    shell <command> [arguments]

locate
------

Find an item in File System

Usage:

     locate [options] <name>

选项：
  -c       Count number of items found
  -i       Ignore case 

stat
------

Display file status.

用法： ::

     stat [-h] <file_name> [file_name ...]

选项：
  -h     Shows the help message

snap
----

Create or Delete Snapshot

Usage:

     snap {create|delete} <snap_name> <dir_name>

* snap_name - Snapshot name to be created or deleted

* dir_name - directory under which snapshot should be created or deleted

setxattr
--------

Set extended attribute for a file

用法： ::

     setxattr [-h] <path> <name> <value>

*  path - Path to the file

*  name - Extended attribute name to get or set

*  value - Extended attribute value to be set

选项：
  -h, --help   Shows the help message

getxattr
--------

Get extended attribute value for the name associated with the path

用法： ::

     getxattr [-h] <path> <name>

*  path - Path to the file

*  name - Extended attribute name to get or set

选项：
  -h, --help   Shows the help message

listxattr
---------

List extended attribute names associated with the path

用法：

     listxattr [-h] <path>

*  path - Path to the file

选项：
  -h, --help   Shows the help message

df
--

Display amount of available disk space

Usage :

    df [-h] [file [file ...]]

* file - name of the file

Options:
  -h, --help   Shows the help message

du
--

Show disk usage of a directory

Usage :

    du [-h] [-r] [paths [paths ...]]

* paths - name of the directory

Options:
  -h, --help   Shows the help message

  -r     Recursive Disk usage of all directories


quota
-----

Quota management for a Directory

Usage :

    quota [-h] [--max_bytes [MAX_BYTES]] [--max_files [MAX_FILES]] {get,set} path

* {get,set} - quota operation type.

* path - name of the directory.

Options :
  -h, --help   Shows the help message

  --max_bytes MAX_BYTES    Set max cumulative size of the data under this directory

  --max_files MAX_FILES    Set total number of files under this directory tree


Exit Code
=========

Following exit codes are returned by cephfs shell

+-----------------------------------------------+-----------+
| Error Type                                    | Exit Code |
+===============================================+===========+
| Miscellaneous                                 |     1     |
+-----------------------------------------------+-----------+
| Keyboard Interrupt                            |     2     |
+-----------------------------------------------+-----------+
| Operation not permitted                       |     3     |
+-----------------------------------------------+-----------+
| Permission denied                             |     4     |
+-----------------------------------------------+-----------+
| No such file or directory                     |     5     |
+-----------------------------------------------+-----------+
| I/O error                                     |     6     |
+-----------------------------------------------+-----------+
| No space left on device                       |     7     |
+-----------------------------------------------+-----------+
| File exists                                   |     8     |
+-----------------------------------------------+-----------+
| No data available                             |     9     |
+-----------------------------------------------+-----------+
| Invalid argument                              |     10    |
+-----------------------------------------------+-----------+
| Operation not supported on transport endpoint |     11    |
+-----------------------------------------------+-----------+
| Range error                                   |     12    |
+-----------------------------------------------+-----------+
| Operation would block                         |     13    |
+-----------------------------------------------+-----------+
| Directory not empty                           |     14    |
+-----------------------------------------------+-----------+
| Not a directory                               |     15    |
+-----------------------------------------------+-----------+
| Disk quota exceeded                           |     16    |
+-----------------------------------------------+-----------+
| Broken pipe                                   |     17    |
+-----------------------------------------------+-----------+
| Cannot send after transport endpoint shutdown |     18    |
+-----------------------------------------------+-----------+
| Connection aborted                            |     19    |
+-----------------------------------------------+-----------+
| Connection refused                            |     20    |
+-----------------------------------------------+-----------+
| Connection reset                              |     21    |
+-----------------------------------------------+-----------+
| Interrupted function call                     |     22    |
+-----------------------------------------------+-----------+
