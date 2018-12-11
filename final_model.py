import requests
import json
import csv
import sqlite3
from secrets import *

###############MODE
##Define a unique ID for each cache entry using base url and params
def params_unique_combination(baseurl, params):
    alphabetized_keys = sorted(params.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}-{}".format(k, params[k]))
    return baseurl + "_".join(res)

#####Cache handling


##Make new request only if info isn't already in cache
def make_request_using_cache(baseurl, params):

    uniqueID = params_unique_combination(baseurl, params)

    if uniqueID in CACHE_DICTION:
        print("Getting cached data...")
        return CACHE_DICTION[uniqueID]
    else:
        print("Making a request for new data...")
        resp = requests.get(baseurl, params)
        CACHE_DICTION[uniqueID] = json.loads(resp.text)
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME, "w")
        fw.write(dumped_json_cache)
        fw.close()
        return CACHE_DICTION[uniqueID]


##Delete all tables from the database
def wipe_db(database):
    conn = sqlite3.connect(database)
    cur = conn.cursor()

    statement = "DROP TABLE IF EXISTS 'Categories'"
    cur.execute(statement)
    statement = "DROP TABLE IF EXISTS 'Affiliations'"
    cur.execute(statement)
    statement = "DROP TABLE IF EXISTS 'Cities'"
    cur.execute(statement)
    statement = "DROP TABLE IF EXISTS 'Countries'"
    cur.execute(statement)
    statement = "DROP TABLE IF EXISTS 'Journals'"
    cur.execute(statement)
    statement = "DROP TABLE IF EXISTS 'Articles'"
    cur.execute(statement)
    statement = "DROP TABLE IF EXISTS 'FirstAuthors'"
    cur.execute(statement)
    statement = "DROP TABLE IF EXISTS 'Years'"
    cur.execute(statement)

    conn.commit()
    conn.close()


#Create all necessary tables (unpopulated)
def create_db(database):
    conn = sqlite3.connect(database)
    cur = conn.cursor()

    statement = '''
        CREATE TABLE 'Categories' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Code' INT NOT NULL,
            'Category' TEXT,
            'Abbrev' TEXT )
    '''
    cur.execute(statement)

    statement = '''
        CREATE TABLE 'Affiliations' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'AffiliatedOrg' TEXT NOT NULL UNIQUE,
            'City' INT,
            'Country' INT )
    '''
    cur.execute(statement)

    statement = '''
        CREATE TABLE 'Cities' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'City' TEXT UNIQUE,
            'Country' TEXT )
    '''
    cur.execute(statement)

    statement = '''
        CREATE TABLE 'Countries' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Country' TEXT UNIQUE )
    '''
    cur.execute(statement)

    statement = '''
        CREATE TABLE 'Journals' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'JournalName' TEXT UNIQUE,
            'SubjectArea' INT)
    '''
    cur.execute(statement)

    statement = '''
        CREATE TABLE 'FirstAuthors' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Name' TEXT UNIQUE)
    '''
    cur.execute(statement)

    statement = '''
        CREATE TABLE 'Years' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'YEAR' INT UNIQUE
        )
        '''
    cur.execute(statement)

    statement = '''
        CREATE TABLE 'Articles' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Title' TEXT UNIQUE,
            'Date' TEXT,
            'Creator' INT,
            'Journal' INT,
            'Affiliation' INT,
            'Subject' TEXT,
            'Cited-by' INT)
    '''
    cur.execute(statement)

    conn.commit()
    conn.close()


###POPULATE THE Database
def populate_db(database):
    conn = sqlite3.connect(database)
    cur = conn.cursor()

    ##Set up for request
    base_url = 'https://api.elsevier.com'
    params = {}

    ##Retrieve a list of all of the subjects available using the SCOPUS Subject Classification API
    subjectURL = base_url + '/content/subject/scopus'
    cats = make_request_using_cache(subjectURL, params)

    ##Populate the Category table
    allCategories = []
    for category in cats['subject-classifications']['subject-classification']:
        code = category["code"]
        catDesc = category["detail"]
        abbrev = category["abbrev"]
        if abbrev not in allCategories:
            allCategories.append(abbrev)
        vals = (None, code, catDesc, abbrev)


        statement = "INSERT INTO 'Categories' VALUES (?,?,?,?)"
        cur.execute(statement, vals)


    ##Use SCOPUS API to get article information
    scopusURL = base_url + '/content/search/scopus'
    sortOpts = ['citedby-count', 'relevancy', '-pagecount', '+pagecount']
    # subj = 'SUBJAREA(AGRI)'
    # params = {'apiKey': sd_key, 'sort': sortOpts[0], 'query': subj}
    # scopus = make_request_using_cache(scopusURL, params)

    for category in allCategories:
        subj = 'SUBJAREA(' + category + ')'
        for opt in sortOpts:
            params = {'apiKey': sd_key, 'sort': opt, 'query': subj}
            scopus = make_request_using_cache(scopusURL, params)

            ##POPULATE THE TABLES RELATED TO THIS SEARCH
            for article in scopus['search-results']['entry']:
                title = article['dc:title']
                date = None
                creator = None
                journal = None
                country = None
                city = None
                affil = None
                subject = None
                citedBy = article['citedby-count']

                if 'prism:publicationName' in article:
                    journal = article['prism:publicationName']

                if 'dc:creator' in article:
                    creator = article['dc:creator']

                if 'prism:coverDate' in article:
                    date = article['prism:coverDate']
                    date = date[:4]

                ##Populate into years table
                if date != None:
                    vals = (None, date)
                    statement = "INSERT OR IGNORE INTO 'YEARS' VALUES(?,?)"
                    cur.execute(statement, vals)

                ##Pull foreign key from  years table for later
                statement = "SELECT Id FROM 'Years' WHERE Year = ?"
                vals = (date,)
                cur.execute(statement, vals)
                for row in cur:
                    date = row[0]

                ##Populate into creator table
                if creator != None:
                    vals = (None, creator)
                    statement = "INSERT OR IGNORE INTO 'FirstAuthors' VALUES (?,?)"
                    cur.execute(statement, vals)

                ##Only execute if there is an affiliation listed with the article
                if 'affiliation' in article:
                    country = article['affiliation'][0]['affiliation-country']
                    city = article['affiliation'][0]['affiliation-city']
                    affil = article['affiliation'][0]['affilname']

                    ##Populate into Countries table
                    if country != None:
                        statement = "INSERT OR IGNORE INTO 'Countries' VALUES(?,?)"
                        vals = (None, country)
                        cur.execute(statement, vals)

                    ##Pull foreign key for Country to use in City and Affil Tables
                    statement ="SELECT Id FROM 'Countries' WHERE Country = ?"
                    vals = (country,)
                    cur.execute(statement, vals)
                    for row in cur:
                        country = row[0]

                    ##Populate into Cities Table
                    if city != None:
                        vals = (None, city, country)
                        statement = "INSERT OR IGNORE INTO 'Cities' VALUES(?,?,?)"
                        cur.execute(statement, vals)

                    ##Pull foreign key for City to use in Affil Table
                    statement = "SELECT Id FROM 'Cities' WHERE City = ?"
                    vals = (city,)
                    cur.execute(statement, vals)
                    for row in cur:
                        city = row[0]

                    ##Populate into Affil Table
                    statement = "INSERT OR IGNORE INTO 'Affiliations' Values(?,?,?,?)"
                    vals = (None, affil, city, country)
                    cur.execute(statement, vals)

                ##Popluate into Journals Table
                statement = "INSERT OR IGNORE INTO 'Journals' VALUES(?,?,?) "
                vals = (None, journal,None )
                cur.execute(statement, vals)

                ##Pull foreign key from creator to use in
                statement = "SELECT Id FROM 'FirstAuthors' WHERE Name = ?"
                vals = (creator,)
                cur.execute(statement, vals)
                for row in cur:
                    creator = row[0]

                ##Pull foreign key from Journal
                statement = "SELECT Id FROM 'Journals' WHERE JournalName = ?"
                vals = (journal,)
                cur.execute(statement, vals)
                for row in cur:
                    journal = row[0]

                ##Pull foreign key from affil
                statement = "SELECT Id FROM 'Affiliations' WHERE AffiliatedOrg = ?"
                vals = (affil,)
                cur.execute(statement, vals)
                for row in cur:
                    affil = row[0]

                ##Pull foreign key for subjects to use in articles table
                statement = "SELECT Id FROM 'Categories' WHERE Abbrev = ?"
                vals = (category,)
                cur.execute(statement, vals)
                for row in cur:
                    subject = row[0]

                ##Populate into Articles
                statement = "INSERT OR IGNORE INTO 'Articles' VALUES(?,?,?,?,?,?,?,?)"
                vals = (None, title, date, creator, journal, affil, subject, citedBy )
                cur.execute(statement, vals)

    #Get Journal information using the Science Direct Serial Title Search API
    #Collect all journal names from DB
    allJournals = []
    statement = "SELECT JournalName FROM 'Journals'"
    cur.execute(statement)
    for row in cur:
        allJournals.append(row[0])
    print(len(allJournals))

    serialURL = base_url + '/content/serial/title'
    for journal in allJournals:
        if journal != None:
            params = {'apiKey': sd_key,
                    'title': journal,
                    'count': '1'}
            serialInfo = make_request_using_cache(serialURL, params)

            if 'error' not in serialInfo['serial-metadata-response']:
                if serialInfo['serial-metadata-response']['entry'][0]['dc:title'] == journal:
                    curr = serialInfo['serial-metadata-response']['entry'][0]
                    subject = None

                    if 'subject-area' in curr:
                        subject = curr['subject-area'][0]['@code']


                    statement = 'UPDATE Journals '
                    statement += 'SET SubjectArea = ' + str(subject) + ' WHERE JournalName = "' + journal + '"'
                    cur.execute(statement)


    conn.commit()
    conn.close()

CACHE_FNAME = 'sciDirect.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICTION = {}


######Processing the database

##Return a dictionary where each key is a category and each value is the number of articles of that category
def category_count(database):
    conn = sqlite3.connect(database)
    cur = conn.cursor()

    counts = {}

    statement = 'SELECT Categories.Category, COUNT(*) FROM Categories '
    statement += 'JOIN Articles ON Categories.Id = Articles.Subject '
    statement += 'GROUP BY Categories.Id'
    cur.execute(statement)

    for row in cur:
        counts[row[0]] = row[1]

    conn.close()
    return counts

##return a dictionary where each key is a country and each value is the number of articles from that country
def country_count(database):
    conn = sqlite3.connect(database)
    cur = conn.cursor()

    counts = {}
    other = 0

    statement = 'SELECT Countries.Country, Count(*) FROM Countries '
    statement += 'JOIN Affiliations ON Countries.Id = Affiliations.Country '
    statement += 'JOIN Articles ON Articles.Affiliation = Affiliations.Id '
    statement += 'GROUP BY Countries.Country '
    cur.execute(statement)

    for row in cur:
        if row[1] > 4:
            counts[row[0]] = row[1]
        else:
            other += row[1]
    counts["other"] = other


    conn.close()
    return counts

##class for categories to hold all the information
class Category():
    def __init__(self, abbrev):
        self.abbrev = abbrev
        self.yearCounts = {}
        self.top5Auths = {}
        self.top5Affs = {}

    def addYear(year, count):
        self.yearCounts[year] = count

    def addAuth(auth, count):
        self.top5Auths[auth] = count

    def addAff(aff, count):
        self.top5Affs[aff] = count

##HANDLE ALL DATA FOR CATEGORY PAGES - returns an instance of the category class
def topCatCounts(database, category):

    currCat = Category(category)

    conn = sqlite3.connect(database)
    cur = conn.cursor()

    ##ADD TOP AFFILIATIONS
    statement = 'Select Affiliations.AffiliatedOrg, COUNT(*) FROM Affiliations '
    statement += 'JOIN Articles ON Articles.Affiliation = Affiliations.Id '
    statement += 'JOIN Categories ON Categories.Id = Articles.Subject '
    statement += 'GROUP BY Affiliations.AffiliatedOrg '
    statement += 'HAVING Categories.Category = ? '
    statement += 'ORDER BY COUNT(*) DESC '
    statement += 'LIMIT 5'
    vals = (category,)
    cur.execute(statement, vals)

    for row in cur:
        currCat.top5Affs[row[0]] = row[1]

    ##Add top FirstAuthors
    statement = 'Select FirstAuthors.Name, COUNT(*) FROM FirstAuthors '
    statement += 'JOIN Articles ON Articles.Creator = FirstAuthors.Id '
    statement += 'JOIN Categories ON Categories.Id = Articles.Subject '
    statement += 'GROUP BY FirstAuthors.Id '
    statement += 'HAVING Categories.Category = ? '
    statement += 'ORDER BY COUNT(*) DESC '
    statement += 'LIMIT 5'
    vals = (category,)
    cur.execute(statement, vals)

    for row in cur:
        currCat.top5Auths[row[0]] = row[1]


    ##YEARS
    statement = 'Select Years.Year, COUNT(*) FROM Years '
    statement += 'JOIN Articles ON Articles.Date = Years.Id '
    statement += 'JOIN Categories ON Categories.Id = Articles.Subject '
    statement += 'WHERE Categories.Category = ?'
    statement += 'GROUP BY Years.Year '
    statement += 'ORDER BY Years.Year ASC'
    vals = (category,)
    cur.execute(statement, vals)

    for row in cur:
        currCat.yearCounts[row[0]] = row[1]

    conn.close()
    return currCat


def journalInfo(database, category):
    conn = sqlite3.connect(database)
    cur = conn.cursor()

    counts = {}

    statement = 'Select c.Category, COUNT(*) FROM Articles '
    statement += 'JOIN Journals ON Journals.Id = Articles.Journal '
    statement += 'JOIN Categories as c ON c.Code = Journals.SubjectArea '
    statement += 'JOIN Categories as a ON a.Id = Articles.Subject '
    statement += 'WHERE a.Category = ? '
    statement += 'GROUP BY c.Id '
    statement += 'ORDER BY COUNT(*) desc '
    statement += 'LIMIT 10 '
    vals = (category,)
    cur.execute(statement, vals)

    for row in cur:
        counts[row[0]] = row[1]

    conn.close()
    return counts

def getAbbrev(database, category):
    conn = sqlite3.connect(database)
    cur = conn.cursor()

###articles of this kind often get published in journals of this sort
