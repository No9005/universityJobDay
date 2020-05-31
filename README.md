# universityJobDay
Showcase project for the Job-Day at University Kiel

by Daniel Kiermeier
mail: d.kiermeier(at)el-amara.net
linkedin: https://de.linkedin.com/in/daniel-kiermeier


--------------------------------------------------------------------
universityJobDay is a software who shows young students a
small example of AI-alike software in
the context of market research.
    
    Copyright (C) 2020  Daniel Kiermeier

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
---------------------------------------------------------------------


IMPORTANT:
This software needs in the current version flask-session cookies to run properly.
Therefore chrome and safari are not supportet as browsers!




<<<<<<>>>>>>
Needed:
<<<<<<>>>>>>

Python 3.7, pip & pipenv.



<<<<<<>>>>>>
Installation guide for
Windows and Unix-Systems:
<<<<<<>>>>>>

Prerequisite:
Download and install for your system python 3.7 from
https://www.python.org/downloads/release/python-377/


For Windows user -------------
1* open new terminal
2* type: 'pip3 install pipenv' (without '')
NOTE: if the 'command' 'pip3' or 'pipenv' is not found after installing python, pip and pipenv, you have to
make sure your PATH variables are set correctly.
Most of the time, a complete deinstallation and reinstallation of python and all packages is sufficent to fix the problem.
If you decide to deinstall python, make sure to deinstall every python-software-package you have installed in your system.
This includes python 2.x, python 3.x, python launchers, anaconda, etc.
If you do not want to reinstall all the packages, please check the internet for appropriate information on this subject! 

For Unix-like system user -------------
open new terminal and type: 
1* 'sudo apt-get update'
2* 'sudo apt-get install python3-pip'
3* 'pip3 install pipenv



<<<<<<>>>>>>
app startup:
<<<<<<>>>>>>

NOTE: every shell/terminal command has to be written without quotes ('')

1* after downloading the git folder open a new terminal and change the directory (hint: command should look something like "cd '.../universityJobDay'", while '.../' is the path to the folder universityJobDay!)
2* create a folder called '.venv' ('mkdir .venv')
3* open up a pipenv shell the first time to create the virutal environment (pipenv should tell
   you something like: 'creating virtual environment'). After creation, exit the shell with 'exit'.
   PRO TIP: check if pipenv created the virtual environment under .venv with: 'pipenv --venv'. The path should be something
   like '/yourfolder/.venv'
4* type: 'pipenv install --three' to install all necessary packages
5* check if "answer.db" is already in the subfolder "database". If not, follow Steps 5A, else continue with step 6

5A* check if the folder 'migration' exists under your main project rood ('.../universityJobDay'). If it does, delete it. else type: 'pipenv shell' to open a virtual environment
5B* type: 'flask db init' to startup the database (if pipenv prints something like: could not find "app", check if your app's name is 'app.py'. Else rename it to 'app.py', repeat 'flask db init')
5C* type: 'flask db migrate -m "somecomment"' to log your first change
5D* type: 'flask db upgrade' to run the change
5E* type: 'exit' to leave the virtual shell
5F* optional: run 5&6 everytime you change the database in the 'app.py' script.

6* type: 'pipenv run python3 app.py' to startup the testenvironment

7* open a new browser and go to: 'localhost:5000'. (if it is your first time using the app after you resetted the database, you have to insert a master passwort first)
8* Answer the Questionnaire multiple times
9* go to: 'localhost:5000/restults'

you can always repeat the calculation or add new answers by running the questionnaire

<<<<<<>>>>>>
shutdown the server:
<<<<<<>>>>>>

go to your shell, running flask. Click on it and press 'STRG+C' to abort the process.
To startup the server a second time just follow the steps 1 & 9 from "app startup".

<<<<<<>>>>>>
clean the database:
<<<<<<>>>>>>

go to: you can find a reset button after you logged in under 'system'.

<<<<<<>>>>>>
disable/enable session-clear
<<<<<<>>>>>>

if you want to allow your users to answer the questionnaire multiple times, you can toggle the 'clear-permission' option under 'system'.
If done, each user can trick the system to be a new user by clicking on "clear-session" under "datenschutz".

NOTE. you have to be logged in as administrator to find the 'system' option on the right top side.

<<<<<<>>>>>>
disable/enable results screen for users
<<<<<<>>>>>>

if you want to allow your users to to check the results for themself, you can toggle the 'dash-permission' option under 'system'.
If done, each user can see a 'results' button in the navbar on the right side after page reload.

NOTE. you have to be logged in as administrator to find the 'system' option on the right top side.
