# SCiPnet
For my final project, I have chosen to create a command line access terminal for the SCiPnet, using Python.

## So what is the SCiPnet?
The SCP Foundation is a fictional international organisation that specialises in the control of anomalous entities, and objects. Things that don’t follow the normal laws of reality. Those things have files. Lots of files. The job of the SCiPnet, is to provide a way for Foundation agents wrought the globe to access the deepwell, the Foundation’s central server.

## Ok, how do I use this?
All you need to connect, are client.py and utils. As long as the central server is running, `python client.py` will initialise the access terminal. After connecting to the server, the startup sequence will initialise, and after you log in or register an account, you’re good to go!

## What can I do?
Before explaining commands, here are some clarification points:
- command are formatted as uppercase, but are not case sensitive
- valid file types are: SCP, SITE, MTF or USER

`Access`: used to access a file. Format: `ACCESS [filetype] [file id]`
While the use of file ID can make files hard to access, I plan to make a search command, where you can search for files based on type and name.

`Create`: used to create a file. Format: `CREATE [filetype]`
After the server validates your clearance, you will be prompted to provide information for your chosen file. I may add the option to read files at some point.

`Logout`: terminate your connection to the deepwell

`Clear`/`Cls`: clears the screen

`Help`: displays a simple guide to using available commands