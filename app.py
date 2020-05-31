'''
Project files to the university lecture "Marktforschung & KI".
Please see the README.md for installation infos.

IMPORTANT! You have to insert your specific path to your database in two locations of this
script:
1) app.config["SQLALCHEMY_DATABASE_URI"]
2) def get_data

If you do not enter your path here, the app will not startup!

If you have further questions, dont hasitate to contact me under my linkedin contacts:
https://de.linkedin.com/in/daniel-kiermeier



----------------------------------------------------------------------------------------
 <universityJobDay is a software who shows young students a small example of ki-alike software in the context of market research.>
    Copyright (C) <2020>  <Daniel Kiermeier>

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
-----------------------------------------------------------------------------------------



author: Daniel Kiermeier
e-mail: d.kiermeier(at)el-amara.net
linkedin: https://de.linkedin.com/in/daniel-kiermeier
'''

from flask import Flask
from flask import request, render_template, redirect, url_for, session, jsonify
from flask import Markup

import json as js

from flask_login import LoginManager
from flask_login import current_user, login_user, logout_user, login_required, UserMixin

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sqlite3 as sq 

from werkzeug.security import generate_password_hash, check_password_hash

from functools import wraps

from pathlib import Path

from datetime import datetime

import logging
from logging.handlers import RotatingFileHandler

import numpy as np
import pandas as pd

import spacy
import de_core_news_sm
from spacy.lang.de.stop_words import STOP_WORDS
from spacy.lemmatizer import Lemmatizer

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.manifold import TSNE

import pyLDAvis
import pyLDAvis.sklearn

import random
import string

from py_files import labels as lb




# create app and config ----------------------------
app = Flask(__name__)
app.config["SECRET_KEY"] = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))

# path
currentPath = Path().cwd()
dbPath = currentPath/ "database"
dbName = "answers.db"

# create database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:/// ADD PATH TO YOUR DB HERE!"     # add here the path to your database! in my case it was "/var/www/universityJobDay/universityJobDay/database/answers.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False # not necessary due to flask-migrate
db = SQLAlchemy(app) # create db object and assign it to db

# set up migration engine
migrate = Migrate(app, db) # create object and bind it to our app

# set up login manager
login = LoginManager(app)
login.login_view = "user_login"

# classes ------------------------------------------
# db table for the questionnaire answers
class Answers(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    sessionID = db.Column(db.Integer, index = True, nullable = False, unique=True)
    f1 = db.Column(db.String, index = True, nullable = True)
    f2 = db.Column(db.String, index = True, nullable = True)
    f3 = db.Column(db.String, index = True, nullable = True)
    f4 = db.Column(db.String, index = True, nullable = True)
    f5 = db.Column(db.String, index = True, nullable = True)
    f6 = db.Column(db.String, index = True, nullable = True)
    date = db.Column(db.DateTime, index = True, default=datetime.utcnow)

# db pw for admin
class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(120), index = True, unique = True, nullable = False)
    pwHash = db.Column(db.String(120), index = True, unique = True, nullable = True)

    def set_password(self, password):
        self.pwHash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pwHash, password)


# global variables ---------------------------------
clear_permission = False # used to set the option to clear the session for a new questionnaire run.
dashboard_access = False # used to give normal user permission to see the results

# functions ----------------------------------------
def get_data(uri = ' ADD YOUR PATH TO DB HERE '): # add here your path to your db too! for example: '/var/www/universityJobDay/universityJobDay/database/answers.db'
    # open connection to sql
    conn = sq.connect(uri)
    # query data
    df = pd.read_sql_query('SELECT * from answers', conn)
    # close connection
    conn.close()

    return df

@login.user_loader # for custom loader functions, to track the "current_user.is_authenticated"
def load_user(id):
    return Admin.query.get(int(id)) # Flask-Login returns strings. One has to convert it manually to ints!

def standard_size():
    return ["col-xl-2 col-lg-2 col-md-1 col-sm-1","col-xl-6 col-lg-6 col-md-10 col-sm-10", "col-xl-4 col-lg-4 col-md-1 col-sm-1"]

def open_question(comment = "Textbox", answerIdent = "", counterIdent=""):
    '''
    function to produce a open answer question
    
    arguments --
    - comment: text displayed right above input box
    - answerIdent: class name for jquery search the answers
    
    returns --
    - HTML code for the question
    '''
    answer = [
        '<div class="form-group">',
        '<label for="comment">' + comment + '</label>',
        '<textarea class="form-control ' + answerIdent + '" rows="5" id="comment"></textarea>',
        '</div>',
        '<div id=' + counterIdent + '></div>'
    ]

    answer = ''.join(answer)

    return answer

def radio_question(answerOptions, answerIdent = "", randomized = False):
    '''
    function to produce a open answer question
    
    arguments --
    - answerOptions: text for the answer options
    - answerIdent: class name for jquery search the answers
    - randomized: randomizes the answers
    
    returns --
    - HTML code for the question
    '''
    
    # create radio html --> answers!
    answer = []
    
    for i, option in enumerate(answerOptions):
        tempBase = [
            '<div class="form-check">',
            '<label class="form-check-label">',
            '<input type="radio" class="form-check-input ' + answerIdent + '" name="optradio" value="' + str(i) + '">' + option,
            '</label>',
            '</div>'
        ]
        answer.append(''.join(tempBase))

    if randomized:
        random.shuffle(answer)
        
    answer = ''.join(answer) # join to one string; spaces between strings dont needed!

    return answer

def checkbox_question(answerOptions, answerIdent = "", randomized = False):
    '''
    function to produce a open answer question
    
    arguments --
    - answerOptions: text for the answer options
    - answerIdent: class name for jquery search the answers
    - randomized: randomizes answers
    
    returns --
    - HTML code for the question
    '''
    
    # create radio html --> answers!
    answer = []
    
    for i, option in enumerate(answerOptions):
        tempBase = [

            '<div class="form-check">',
            '<label class="form-check-label">',
            '<input type="checkbox" class="form-check-input" value="' + str(i) + '">' + option,
            '</label>',
            '</div>'
        ]

        answer.append(''.join(tempBase))
    
    if randomized:
        random.shuffle(answer)

    answer = ''.join(answer) # join to one string; spaces between strings dont needed!
    
    return answer

def standard_question(questionHead, questionText, answerFunction, divIdent= [""], formIdent = [""], buttonText = "Next Question", onclick = "", bootstrap = standard_size()):
    '''
    function to produce a open answer question
    
    arguments --
    - questionHead: title of question
    - questionText: text of question
    - answerFunction: list-like which creates the answer format. first entry equals answertype, other entries equals arguments.
        * available options:
            + for open Answer Box: ["open", "comment", "answerIdent", "countIdent]
                open: answertype
                comment: string; text right abov the input field
                answerIdent: string; class for jquery search
            + for checkbox answer type: ["checkbox", "answerOptions", "answerIdent", randomization]
                checkbox: answertype
                answerOptions: list-like with the answer options
                answerIdent: string; class for jquery search
                randomization: true for randomized answers
            + for radio type: ["radio", "answerOptions", "answerIdent", randomization]
                radio: answertype
                answerOptions: see checkbox
                answerIdent: see checkbox
                randomization: see checkbox
    - divIdent: list-like to add new classes to the main div container (e.g. ["answer1", "spaceTop"] adds 'answer1 spaceTop' to the class property)
    - formIdent: list-like to add ne classes to the form container.
    - buttonText: display text for the button
    - onclick: define onclick-functions
    - bootstrap: change the bootstrap col size. List-like with 3 entries
    
    returns --
    - HTML code for the question
    '''

    notListLike = Markup("<div><p>Your answer options are not list-like!</p></div>")
    notStringLike = Markup("<div><p>String Error: argument in 'answerFunction' should be a string, but isnt!</p></div>")

    # check for answer type & also check if requirements are met
    if answerFunction[0] == "open":
        try:
            temp = answerFunction[1]
            if isinstance(temp, str):
                com = temp
            else:
                return notStringLike
        except Exception as e:
            com = ""
        
        try:
            temp = answerFunction[2]
            if isinstance(temp, str):
                aswIdent = temp
            else:
                return notStringLike
        except Exception as e:
            aswIdent = ""

        try:
            temp = answerFunction[3]
            if isinstance(temp,str):
                countId = temp
            else:
                return notStringLike
        except Exception as e:
            countId = ""

        answerType = open_question(comment = com, answerIdent = aswIdent, counterIdent=countId)

    elif answerFunction[0] == "checkbox":
        try:
            temp = answerFunction[1]
            if isinstance(temp, list):
                com = temp
            else:
                return notListLike
        except Exception as e:
            return notListlike
        
        try:
            temp = answerFunction[2]
            if isinstance(temp, str):
                aswIdent = temp
            else:
                return notStringLike
        except Exception as e:
            aswIdent = ""

        try:
            temp = answerFunction[3]
            if isinstance(temp, bool):
                ran = temp
            else: ran = False
        except:
            ran = False

        answerType = checkbox_question(answerOptions = com, answerIdent = aswIdent, randomized=ran)
        
    elif answerFunction[0] == "radio":
        notListlike = Markup("<div><p>Your answer options are not list-like!</p></div>")
        try:
            temp = answerFunction[1]
            if isinstance(temp, list):
                com = temp
            else:
                return notListLike
        except Exception as e:
            return notListlike
        
        try:
            temp = answerFunction[2]
            if isinstance(temp, str):
                aswIdent = temp
            else:
                return notStringLike
        except Exception as e:
            aswIdent = ""

        try:
            temp = answerFunction[3]
            if isinstance(temp, bool):
                ran = temp
            else: ran = False
        except:
            ran = False

        answerType = radio_question(answerOptions = com, answerIdent = aswIdent, randomized=ran)
        
    else:
        return Markup("<div><p>No valid answertype defined! only 'open', 'checkbox' or 'radio' allowed.</p></div>")

    # prevent app from crashing if divIdent is not assigned correctly.
    try:
        addClasses = " ".join(divIdent)
    except Exception as e:
        addClasses = ""

    try:
        addForm = " ".join(formIdent)
    except Exception as e:
        addForm = ""


    # create html
    htmlBase = [
        '<div class="container progressbarSpace ' + addClasses + '">',
        
        '<!-- question Number -->',
        '<div class="row">',
        '<div class="' + bootstrap[0] + '"></div>',
        '<div class="' + bootstrap[1] + '">',
        '<h2>' + questionHead + '</h2>',
        '</div>',
        '<div class="' + bootstrap[2] + '"></div>',
        '</div>',

        '<!-- question text -->',
        '<div class="row">',
        '<div class="' + bootstrap[0] + '"></div>',
        '<div class="' + bootstrap[1] + '">',
        '<p>' + questionText + '</p>',
        '</div>',
        '<div class="' + bootstrap[2] + '"></div>',
        '</div>',

        '<!-- answer -->',
        '<div class="row">',
        '<div class="' + bootstrap[0] + '"></div>',
        '<div class="' + bootstrap[1] + '">',
        
        '<!-- answer options -->',
        '<form class="' + addForm + '">',
        answerType,
        '</form>'

        '</div>',
        '<div class="' + bootstrap[2] + '"></div>',
        '</div>',

        '<!-- next button -->',
        '<div class="row buttonSpace">',
        '<div class="' + bootstrap[0] + '"></div>',
        '<div class="' + bootstrap[1] + '">',
        '<button onclick="' + onclick + '" type="button" class="btn btn-danger">' + buttonText + '</button></a>',
        '</div>',
        '<div class="' + bootstrap[2] + '"></div>',
        '</div>',
        '</div>'
    ]

    html = Markup(''.join(htmlBase)) # join it
    
    return html

def unzip(data):
    names = []
    dataSet = []

    # caution: javascript returns arrays in arrays --> sometimes you have to double index!
    for element in data:
        names.append(element[0][0])

        _type = element[1][0]

        if _type == -1:
            pass
        elif _type == 2:
            if len(element[_type]) > 1:
                select = "~".join(element[_type]) # parse list into one string
            else:
                select = str(element[_type][0])

            dataSet.append(select)

        elif _type == 3:
            dataSet.append(element[_type][0])
    
    return names, dataSet

def shutdown_server():
    func = request.environ.get("werkzeug.server.shutdown")
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server")
    func()

def create_id(length):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(length))

def cookie_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs): # wrapper function, takes all arguments of base function (--> *args, **kwargs)
        if "cookie_accepted" not in session: 
            app.logger.warning('Function: cookie_required || cookie_accepted not in session!')
            return redirect(url_for('cookie_content'))

        elif session["cookie_accepted"] != True:
            app.logger.warning('Function: cookie_required || cookie_accepted not True!')
            return redirect(url_for('go_back'))

        else:
            return f(*args, **kwargs) # --> return base function without adjustments (incl. old *args, **kwargs)

    return decorated_function # return all

def viewpermission_required(f):
    @wraps(f)
    def viewpermission(*args, **kwargs):
        if (current_user.is_authenticated) | (dashboard_access):
            return f(*args, **kwargs)
        else:
            return redirect(url_for('index'))
    return viewpermission 
        
def col_percent_single(data, label_dict):
    """
    Function to calculate column percentage of a single-answer-type question

    args -
    data: pandas series
    label_dict: dictionary with value labels

    returns: list-like [groupnames, percent, groupsize, total_n]
    """

    prep = data.replace(label_dict).value_counts().dropna()
    calculation = prep.apply(lambda x: int(x/data.shape[0]*100))
    
    return [calculation.index.to_list(), [int(value) for value in calculation.values], ['group n = ' + str(value) for value in prep.values], data.shape[0]]

def col_percent_multi(data, label_dict):
    """
    function to calculate colum percentage of a multi-answer-type-question.

    args -
    data: pandas df
    label_dict: dictionary with value labels

    returns: list-like [groupnames, percent, total_answers_per_option, total_n (of participants)]
    """

    n = data.shape[0]
    prep = data.replace(label_dict).melt().value.dropna().value_counts()
    calculation = prep.apply(lambda x: int(x/n*100))
    
    return [calculation.index.to_list(), [int(value) for value in calculation.values], ['group n = ' + str(value) for value in prep.values], n]

def prepare_df(df):
    """
    function to clean and prepare the pulled db data

    args-
    data: pandas dataframe of 'answers'

    returns: pandas dataframe (cleaned)
    """

    # split f3 into single columns; -99 is a substitution and will be replaced with np.nan
    f3 = df["f3"].apply(lambda x: x.split("~"))
    f3 = pd.DataFrame([entry + ["-99"] * (3-len(entry)) for entry in f3], columns = ["f3_1", "f3_2", "f3_3"]).astype(int)
    f3.replace(-99, np.nan, inplace = True)

    # prepare the date
    date = pd.DataFrame([[entry.split(" ")[0], entry.split(" ")[1]] for entry in df["date"]], columns = ["date", "time"])

    # concatenate old and new data
    df = pd.concat([df.loc[:, [col for col in df.columns if col not in  ["f3", "date"]]], f3, date], axis = 1)

    # convert remaining columns to ints (if possible)
    for col in ["f1", "f2", "f4", "f6"]:
        df[col] = df[col].astype(int)

    return df

def calculate_splits(question, split):
    """
    function to calculate market research column percentages for filtered groups.

    args - 
    - question: list-like --> [question, label dictionairy]
    - filter: list-like --> [question, label_dictionairy]

    returns -
    list-like --> [labels of items, values, group n, total n, labels of splits]
    """
    prep = pd.crosstab(split[0].replace(split[1]), question[0].replace(question[1]))
    calculation = prep.apply(lambda r: (r/r.sum()*100), axis = 1).astype(int)

    int_converted = []
    for _, row in calculation.iterrows():
        int_converted.append([int(entry) for entry in row])

    int_group_n = ["group n = " + str(entry) for entry in prep.sum(axis = 1)]

    return [calculation.columns.to_list(), int_converted, int_group_n, question[0].shape[0], calculation.index.to_list()]
    
def calculate_split_multi(question, split):
    """
    function to calculate market research column percentages for filtered groups of multi answer questions.

    args - 
    - question: list-like --> [question Dataframe (e.g. all columns for question), label dictionairy]
    - filter: list-like --> [question, label_dictionairy]

    returns -
    list-like --> [labels of items, values, group n, total n, labels of splits]
    """
    merged = pd.concat([question[0].replace(question[1]), split[0].replace(split[1])], axis = 1)
    splitCol = merged.columns[-1]

    melt = merged.melt(id_vars = splitCol)

    prep = pd.crosstab(melt[splitCol], melt["value"])
    calculation = prep.apply(lambda r: (r/r.sum()*100), axis = 1).astype(int)

    int_converted = []
    for _, row in calculation.iterrows():
        int_converted.append([int(entry) for entry in row])

    int_group_n = ["group n = " + str(entry) for entry in prep.sum(axis = 1)]

    return [calculation.columns.to_list(), int_converted, int_group_n, question[0].shape[0], calculation.index.to_list()]

def dash_access_state():
    return dashboard_access

def dummy(doc):
    """
    dummy function for the sklearn vectorizer
    """
    return doc

def text_analysis(numberOfTopics, numberOfTopWords, textData, perplexity):
    """
    preprocesses text + calculates the LDA with specific number of topics.

    args-
    -numberOfTopics: the number of topics over all documents
    -numberOfTopWords: the number of top words to be displayed
    -textData: DataFrame of text documents

    returns [pyLDAvis.thml, pd.DataFrame all results, DataFrame for wordPerTopic]
    """

    # text preprocessing
    # initialize nlp
    nlp = de_core_news_sm.load()

    # feed the document into the object
    document_list = [nlp(answer) for answer in textData]

    # delete stop words
    without_stop_words = []
    for doc in document_list:
        without_stop_words.append([token for token in doc if token.is_stop != True])

    # lemmatize
    lemma_list = []
    for doc in without_stop_words:
        lemma_list.append([token.lemma_ for token in doc])

    # clean expressions
    expressions = [":", "-", "(", ")", "\n", "\n\n", "?", ":","\'", '\"', ".", ",", "'s", "...", "&", "+", "1", "2", "3", "4", "5", "6", "7", "8", "9", ";-)", " ", ";", "/", "z.", "b."]

    # acutal cleaning
    cleaned_lemma = []
    for doc in lemma_list:
        cleaned_lemma.append([token for token in doc if token not in expressions])

    # convert text to lowercase
    low = []
    for doc in cleaned_lemma:
        low.append([token.lower() for token in doc])

    # terminate empty cells or 1-word cells
    final = []
    text_list = []
    for doc, t in zip(low, textData):
        if len(doc)>1:
            final.append(doc)
            text_list.append(t)

    # cleane non informative words
    final2 = []
    for doc in final:
        final2.append([token for token in doc if token not in ["risiko", "chance", "ki"]])

    # text mining!
    # call vectorizer
    cV = CountVectorizer(tokenizer=dummy, preprocessor=dummy)

    # fit vecotrizer
    cV.fit(final2)

    # create bow corpus
    bow_corpus_sk = cV.transform(final2)

    # LDA
    alpha = 0.5 # the higher the more topics in one document
    beta = 0.1 # the higher the more words of the corpus are in the topic

    #call the lda object
    lda_sk = LatentDirichletAllocation(n_components=numberOfTopics, doc_topic_prior=beta, topic_word_prior=alpha, random_state=1)
    #fitting
    lda_sk.fit(bow_corpus_sk)

    """
    # currently killed
    # pyLDAvis
    vis_sk = pyLDAvis.sklearn.prepare(lda_sk, bow_corpus_sk, cV)
    vis_html = pyLDAvis.prepared_data_to_html(vis_sk, template_type="simple")
    """

    #prepare the pd.DataFrame!
    # probability of each word in a topic
    wordPerTopic_sk = pd.DataFrame(lda_sk.components_, index=["topic"+str(num) for num in range(lda_sk.n_components)], columns = cV.get_feature_names())

    # top words for each topic
    top = numberOfTopWords
    topWordPerTopic_sk = pd.DataFrame([[name, rows.sort_values(ascending = False).index.tolist()[:top]] for name, rows in wordPerTopic_sk.iterrows()])

    # probability of each topic per document
    topicPerDoc_sk = pd.DataFrame(lda_sk.transform(bow_corpus_sk), index = ["commentary" + str(i) for i in range(len(final2))], columns = ["topic" + str(i) for i in range(lda_sk.n_components)])

    topTopicPerDoc_sk = topicPerDoc_sk.T.apply(lambda x: x.idxmax())

    # merge different parts
    merged = pd.DataFrame(topTopicPerDoc_sk).merge(topWordPerTopic_sk, how="left")
    merged = pd.concat([merged, pd.Series(text_list)], axis = 1)

    # rename
    merged.columns = ["topic", "words", "text"]

    #split words in seperate cols
    merged[["word" + str(n) for n in range(top)]] = pd.DataFrame(merged["words"].tolist())
    newSorting = ["topic"] + ["word"+str(i) for i in range(top)] + ["text"]
    merged = merged.loc[:, newSorting]

    topWords = topWordPerTopic_sk.iloc[:, 0]
    topWords = pd.concat([topWords, pd.DataFrame(topWordPerTopic_sk.iloc[:,1].tolist(), columns = ["word " + str(n+1) for n in range(top)])], axis = 1)
    topWords.rename(columns={0:"Topic"}, inplace=True)

    # tsne for visualization --> probability of each word in 
    bow_embedded = pd.DataFrame(TSNE(n_components=2, random_state=5, perplexity=perplexity).fit_transform(lda_sk.transform(bow_corpus_sk)))
    bow_embedded.topic = ["value1", "value2"]
    bow_embedded["topic"] = merged["topic"]
    bow_embedded["text"] = merged["text"]


    return [bow_embedded, merged, topWords]

def pandas_to_table(df, name = 'database entries'):
    """
    function to turn a pandas dataframe to a fixed table

    args-
    df: pandas Dataframe

    returns Markup(htmlCode)
    """

    tableColumns = df.columns.to_list()

    tableRows = []
    for idx, rows in df.iterrows():
        tableRows.extend([
            '<tr>',
            '<th scope="row">',
            str(idx),
            '</th>'])

        for entry in rows:
            tableRows.extend([
                '<td>',
                str(entry),
                '</td>'])

        tableRows.extend(['</tr>'])

    tableRows = ''.join(tableRows)

    head = []
    for cols in df.columns:
        head.extend([
            '<th scope="col">',
            str(cols),
            '</th>'])

    head = ''.join(head)

    completeTable = [
        '<div class="container">',
        '<div class= "table-responsive">',
        '<table class="table table-hover">',
        '<caption>' + name + '</caption>',
        '<thead>',
        '<tr>',
        '<th scope="col">#</th>',
        head,
        '</tr>',
        '</thead>',
        '<tbody>',
        tableRows,
        '</tbody>',
        '</table>',
        '</div>',
        '</div>',
    ]

    return Markup(''.join(completeTable))




# add some functions to jinja
app.jinja_env.globals.update(standard_size=standard_size, standard_question=standard_question, dash_access_state=dash_access_state)


# viewport functions aka. routings -----------------
@app.route("/")
@app.route("/index")
@cookie_required
def index():
    app.logger.warning('Requested /index')
    
    # check if application did already set up an admin
    if Admin.query.filter_by(name="admin").first() is None:
        app.logger.warning('app.route(/) || admin not found. >>> redirecting to set_admin')
        return redirect(url_for('set_admin'))

    # check if user already has session id
    if "ID" not in session:
        app.logger.warning('app.route(/) || id not in session found >>> creating one')
        session["ID"] = create_id(15)

        # if the id already exists in the database, create new one
        if Answers.query.filter_by(sessionID=session["ID"]).scalar() is not None:
            session["ID"] = create_id(15)

    else:
        pass
    
    # create permission variable
    if "permission" not in session:
        session["permission"] = False # answer to checkbox "allowed to collect data"
    
    return render_template("index.html")

@app.route("/_permission_check", methods = ["POST"])
def _permission_check(): #--> function to check and change the "permission to collect data" status
    try:
        session["permission"] = request.form["permission"]

        if session["permission"]:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False})
    except Exception as e:
        return jsonify({"success": False})

@app.route("/shutdown")
@login_required
def _shutdown():
    shutdown_server()
    return "Server shutting down..."

@app.route("/clear_database")
@login_required
def _clear_database():
    meta = db.metadata
    for table, tableName in zip(reversed(meta.sorted_tables), meta.sorted_tables) :
        db.session.execute(table.delete())
    db.session.commit()

    return redirect(url_for('index'))

@app.route("/login", methods = ["GET", "POST"])
@cookie_required
def user_login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    admin = Admin.query.filter_by(name="admin").first()
    if admin is None:
        return redirect(url_for('set_admin'))
    
    if request.method == "POST":
        if admin.check_password(request.form["pw"]):
            login_user(admin)
            return jsonify({"success": True, "redirect": "{{ url_for('index') }}" })

        else:
            return jsonify({"error": "wrong Password"})

    return render_template("login.html")

@app.route("/logout")
def user_logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/set_admin", methods = ["POST", "GET"])
def set_admin():
    app.logger.warning('app.route(/set_admin) || request site')

    if current_user.is_authenticated:
        app.logger.warning('app.route(/set_admin) || user already logged in as admin! >>> redirect to index')
        return redirect(url_for('index'))

    admin = Admin.query.filter_by(name="admin").first()

    if admin is not None:
        app.logger.warning('app.route(/set_admin) || admin already registered in DB. >>> redirecting to index')
        return redirect(url_for('index'))
    
    if request.method == "POST":
        app.logger.warning('app.route(/set_admin) || Ajax: pw post received.')

        newAdmin = Admin(name="admin")
        newAdmin.set_password(request.form["pw"])

        try:
            app.logger.warning('app.route(/set_admin) || trying to add pw to db')
            db.session.add(newAdmin)
            db.session.commit()

            return jsonify({"success": True, "redirect": "{{ url_for('index') }}"})

        except Exception as e:
            app.logger.warning('app.route(/set_admin) || failure during commit, jsonify error')
            db.session.rollback()
            db.session.flush()

            return jsonify({"error": True, "msg": "Failure during admin creation. Please try again!"})
    
    return render_template('set_admin.html')

@app.route("/_clear_session")
def _clear_session():
    session.clear()
    return redirect(url_for('index'))

@app.route("/_toggle_clear", methods = ["POST"])
def _toggle_clear(): # set the permission to clear the session
    global clear_permission # global needs to be set to change the global variables value!

    if eval(request.form["toggle"]):
        if current_user.is_authenticated:
            if clear_permission:
                clear_permission = False
                return jsonify({"now": False})
            else:
                clear_permission = True
                return jsonify({"now": True})
        else:
            return jsonify({"now": "Permission denied!"})

@app.route("/_toggle_viewpermission", methods = ["POST"])
def _toggle_viewpermission():
    global dashboard_access

    if eval(request.form["toggle"]):
        if current_user.is_authenticated:
            if dashboard_access:
                dashboard_access = False
                return jsonify({"now": False})

            else:
                dashboard_access = True
                return jsonify({"now": True})
        else:
            return jsonify({"now": "Permission denied!"})

@app.route("/questions")
@cookie_required
def questions():
    if "permission" not in session:
        return redirect(url_for('index'))
    else:
        if session["permission"]: # checks permission to collect data.
            pass
        else:
            return redirect(url_for('index'))

    # check for session-id
    if "ID" not in session:
        return redirect(url_for('index'))
    else:
        # check if the id is already in the database
        var = Answers.query.filter_by(sessionID=session["ID"]).first()

        if var is not None:
            return redirect(url_for('time_paradox'))
        else:
            return render_template("questions.html")

@app.route("/_submit", methods = ["POST"])
def _submit():

    answers = request.json

    # unzip list
    name, data = unzip(answers)

    # create new entry:
    answer = Answers(f1=data[0] , f2=data[1] , f3=data[2], f4=data[3], f5=data[4], f6=data[5] ,sessionID=session["ID"])
    db.session.add(answer)
    db.session.commit()

    # set session cookie ["submit" = True] --> datenschutz anzeige
    session["submit"] = True

    """
    TBD: Irgendwie geht das so nicht.
    # add each answer
    listOfCols = [col.key for col in Answers.__table__.columns]  # col 0 == id!

    for col, data in zip(listOfCols[1:], data):
        entry = "answer." + col + "=" + "\'" + str(data) + "\'"
        print(entry)
        eval(entry)

    db.session.add(answer)
    db.session.commit()
    """

    return jsonify({"success": True})

@app.route("/end_of_questionnaire")
@cookie_required
def end_of_questionnaire():
    return render_template('end.html')

@app.route("/time_paradox")
@cookie_required
def time_paradox():
    return render_template('time_paradox.html')

@app.route("/impressum")
def impressum():
    return render_template("impressum.html")

@app.route("/datenschutz")
def datenschutz():
    return render_template("datenschutz.html", clear_permission=clear_permission)

@app.route("/cookie_content", methods = ["POST", "GET"])
def cookie_content():
    app.logger.warning('app.route(/cookie_content) || Requested the page')

    session["cookie_accepted"] = None

    if request.method == "POST":
        app.logger.warning('app.route(/cookie_content) || Ajax Request:')
        
        temp = request.form["cookie"]

        if temp == "accepted":
            app.logger.warning('app.route(/cookie_content) || Ajax == accept')

            session["cookie_accepted"] = True

            return jsonify({"success": True})
        else:
            app.logger.warning('app.route(/cookie_content) || Ajax != accept')

            session["cookie_accepted"] = False

            return jsonify({"success": False})

    return render_template('cookie_content.html')

@app.route("/go_back", methods = ["POST", "GET"])
def go_back():
    if "cookie_accepted" not in session:
        return redirect(url_for('cookie_content'))
    elif session["cookie_accepted"]:
        return redirect(url_for('index'))
        
    return render_template("go_back.html")

@app.route("/results", methods = ["GET", "POST"])
@viewpermission_required
def results():
    """
    textAnalysis is currently not filterble! See function _text_analysis()
    """

    if request.method == "POST":
        socio = request.form["socio"]
        occasion = request.form["occasion"]
        
        # get complete data from db
        df = get_data()

        df = prepare_df(df)

        print(socio, " &" , occasion)
        print(socio != "no", "&", occasion != "no")

        # filter by occasion:
        if occasion != "no":
            filtered = df.loc[df["f4"] == int(occasion)]
            
            singles_filtered = [
                col_percent_single(filtered["f1"].astype(int), lb.labels()[0]),
                col_percent_single(filtered["f2"].astype(int), lb.labels()[1]),
                col_percent_single(filtered["f4"].astype(int), lb.labels()[3]),
                col_percent_single(filtered["f6"].astype(int), lb.labels()[4])
                ]

            multies_filtered = [col_percent_multi(filtered.loc[:, [col for col in filtered.columns if "f3" in col]],lb.labels()[2])]


        # calculating by splits:
        if socio != "no":
            # get command
            split = lb.splits().get(socio)

            # values for dataset if filtered
            if occasion != "no":
                singles_splits_filtered = [
                    calculate_splits([filtered["f1"].astype(int), lb.labels()[0]], [filtered[split[0]], split[1]]),
                    calculate_splits([filtered["f2"].astype(int), lb.labels()[1]], [filtered[split[0]], split[1]]),
                    calculate_splits([filtered["f4"].astype(int), lb.labels()[3]], [filtered[split[0]], split[1]]),
                    calculate_splits([filtered["f6"].astype(int), lb.labels()[4]], [filtered[split[0]], split[1]])
                    ]
                
                multies_splits_filtered = [calculate_split_multi([filtered.loc[:, [col for col in filtered.columns if "f3" in col]], lb.labels()[2]], [filtered[split[0]], split[1]])]

            # values for splits without filtered dataset            
            singles_splits = [
                calculate_splits([df["f1"].astype(int), lb.labels()[0]], [df[split[0]], split[1]]),
                calculate_splits([df["f2"].astype(int), lb.labels()[1]], [df[split[0]], split[1]]),
                calculate_splits([df["f4"].astype(int), lb.labels()[3]], [df[split[0]], split[1]]),
                calculate_splits([df["f6"].astype(int), lb.labels()[4]], [df[split[0]], split[1]])
                ]
            
            multies_splits = [calculate_split_multi([df.loc[:, [col for col in df.columns if "f3" in col]], lb.labels()[2]], [df[split[0]], split[1]])]
            

        # calculate total value
        singles = [
                col_percent_single(df["f1"].astype(int), lb.labels()[0]),
                col_percent_single(df["f2"].astype(int), lb.labels()[1]),
                col_percent_single(df["f4"].astype(int), lb.labels()[3]),
                col_percent_single(df["f6"].astype(int), lb.labels()[4])
                ]

        multies = [col_percent_multi(df.loc[:, [col for col in df.columns if "f3" in col]],lb.labels()[2])]

        # text Analysis (TBD)
        textAnalysis = []

        

        # create return lists depending on filters
        if (socio == "no") & (occasion == "no"):
            # no splits, no filters; returning mega array for total
            # --> [0] = total values, [1] = filtered values, [2] is splitted? --> no
            megaArray = [
                [singles[0], singles[1], multies[0], singles[2], textAnalysis, singles[3]],
                [],
                False
                ]
            return js.dumps(megaArray)

        elif (socio == "no") & (occasion != "no"):
            # no splits, but occasion filters
            # --> [0] = total values, [1] = filtered values, [2] is splitted? --> no
            megaArray = [
                [singles[0], singles[1], multies[0], singles[2], textAnalysis, singles[3]],
                [singles_filtered[0], singles_filtered[1], multies_filtered[0], singles_filtered[2], textAnalysis, singles_filtered[3]],
                False
                ]

        elif (socio != "no") & (occasion == "no"):
            # splits, but no occasion filters
            # --> [0] total values, [1] = splits, [2] is splitted? --> yes
            megaArray = [
                [singles[0], singles[1], multies[0], singles[2], textAnalysis, singles[3]],
                [singles_splits[0], singles_splits[1], multies_splits[0], singles_splits[2], textAnalysis, singles_splits[3]],
                True
                ]

        else:
            # splits & filters!
            # --> [0] total values, [1] filtered_splits, [2] is splitted? --> yes!
            megaArray = [
                [singles[0], singles[1], multies[0], singles[2], textAnalysis, singles[3]],
                [singles_splits_filtered[0], singles_splits_filtered[1], multies_splits_filtered[0], singles_splits_filtered[2], textAnalysis, singles_splits_filtered[3]],
                True
                ]


        return js.dumps(megaArray)

    return render_template("results.html")

@app.route("/display")
@login_required
def display():
    #all_entries = [[data.id, data.f1, data.f2, data.f3, data.f4, data.sessionID] for data in Answers.query.all()]
    df = get_data()
    
    completeTable = pandas_to_table(df)

    return render_template('status.html', table = completeTable)

@app.route("/_text", methods=["POST"])
def _text_analysis():

    if request.method=="POST":
        numberOfTopics = int(request.form["numberOfTopics"])
        numberOfTopWords = int(request.form["numberOfTopWords"])
        perplexity = int(request.form["perplexity"])

        # get complete data from db
        df = get_data()
        text = df["f5"]

        app.logger.warning('app.route(/_text) || hand over text')

        result = text_analysis(numberOfTopics, numberOfTopWords, text, perplexity)

        app.logger.warning('app.route(/_text) || calculating completeTable')

        # create word counts
        wordCounts = result[1]["topic"].value_counts()
        countIndex = wordCounts.index.tolist()
        countValues = wordCounts.values.tolist()

        # create Html table
        completeTable = pandas_to_table(result[2], name='Wörter mit höchster Wahrscheinlichkeit pro Topic')

        # create lookup for text
        textTable = result[1].loc[:, ["topic", "text"]].values.tolist()

        app.logger.warning('app.route(/_text) || sending result to js.dumps')

        # split tsne result
        tsne = result[0]
        perTopic = []
        topic_list = tsne.loc[:, "topic"].unique()
        for topic in topic_list:
            perTopic.append(tsne.loc[tsne["topic"] == topic].T.values.tolist())

        # dump
        dump = js.dumps([perTopic, completeTable, textTable, [countIndex, countValues]])

        return dump


# if you want to deploy it with gunicorn, delete the following start app code.
# start app ----------------------------------------
if __name__ == "__main__":
    handlerName = 'app.log'
    handlerPath = Path().cwd() / 'logs' / handlerName
    
    handler = RotatingFileHandler('app.log', maxBytes = 10000, backupCount=1)
    handler.setLevel(logging.ERROR)
    app.logger.addHandler(handler)

    app.run(debug=True)

