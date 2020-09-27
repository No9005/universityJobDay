# universityJobDay
Showcase project for the Job-Day at University Kiel

by Daniel Kiermeier
mail: d.kiermeier(at)el-amara.net
linkedin: https://de.linkedin.com/in/daniel-kiermeier

This software was developed for the universityJobDay. 
Its purpose is to give young students an idea of online questionnairs, dashboards and AI-alike applications for market research.
For the sake of simplicity, the project was shortened to a single file (app.py), which completely manages the backend.


--------------------------------------------------------------------
    
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


_IMPORTANT:_
This software needs in the current version flask-session cookies to run properly.
Therefore chrome and safari are not supportet as browsers!


# Needed:
Python 3.7, pip & pipenv.


# Installation guide for Windows and Unix-Systems:
Prerequisite:
Download and install python 3.7 for your system from either
https://www.python.org/downloads/release/python-377/
or use your packagemanager to install it.


## For Windows user
- open up a new terminal
- type: 'pip3 install pipenv' (without '')
_NOTE: if the 'command' 'pip3' or 'pipenv' is not found after installing python, you have to ensure that the PATH variables are set correctly._


## For Unix-like system user
- open up a new terminal and type (without quotes): 
- 'sudo apt-get update'
- 'sudo apt-get install python3-pip'
- 'pip3 install pipenv


# app startup:
_NOTE: every shell/terminal command has to be written without quotes ('')_

- after downloading the git folder open a new terminal and change the directory (hint: command should look something like "cd '.../universityJobDay'", while '.../' is the path to the folder universityJobDay!)
- create a folder called '.venv' (on linux: 'mkdir .venv')
- open up a pipenv shell the first time to create the virutal environment (pipenv should tell you something like: 'creating virtual environment'). After creation, exit the shell with 'exit'. PRO TIP: check if pipenv created the virtual environment under .venv with: 'pipenv --venv'. The path should be something like '/yourfolder/.venv'
- type: 'pipenv install --three' to install all necessary packages
- check if "answer.db" is already in the subfolder "database". If not, follow Steps a) - f), else continue with the next step.

    - a) check if the folder 'migration' exists under your main project root ('.../universityJobDay'). If it does, delete it. Next type: 'pipenv shell' to open a virtual environment
    - b)type: 'flask db init' to startup the database (if pipenv prints something like: could not find "app", check if your app's name is 'app.py'. Else rename it to 'app.py', repeat 'flask db init')
    - c) type: 'flask db migrate -m "somecomment"' to log your first change
    - d) type: 'flask db upgrade' to run the change
    - e) type: 'exit' to leave the virtual shell
    - f) optional: run these steps everytime after changeing the database in the 'app.py' script.

- type: 'pipenv run python3 app.py' to startup the testenvironment
- open a new browser and go to: 'localhost:5000'. (if it is your first time using the app after you resetted the database, you have to insert a master passwort first)
- Answer the Questionnaire multiple times
- go to: 'localhost:5000/restults'

You can always repeat the calculation or add new answers by running the questionnaire.
Please note that text analysis usually only works well with a large number of data points (or text answers in this case).


# shutdown the server:
Go to your shell which runs flask. Click on it and press 'STRG+C' to abort the process.
To startup the server a second time just follow the steps from __app startup__.


# clean the database:
You can find a reset button on the homepage after logging in under 'system'.

NOTE. you have to be logged in as administrator to find the 'system' option on the right top side.


# disable/enable session-clear
If you want to allow your users to answer the questionnaire multiple times, you can toggle the 'clear-permission' option under 'system'.
If done, each user can trick the system to be a new user by clicking on "clear-session" under "Datenschutz".

NOTE. you have to be logged in as administrator to find the 'system' option on the right top side.


# disable/enable results screen for users
If you want to allow your users to to check the results for themself, you can toggle the 'dash-permission' option under 'system'.
If done, each user can see a 'results' button in the navbar on the right side after page reload.

NOTE. you have to be logged in as administrator to find the 'system' option on the right top side.
