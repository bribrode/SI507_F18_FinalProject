import unittest
import final_model
import final
import sqlite3

class TestDBInit(unittest.TestCase):

    ##Ensures that tables were properly created
    def testTableCreate(self):
        db = 'sciDirect.db'
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        final_model.wipe_db(db)
        final_model.create_db(db)

        statement = 'INSERT INTO "YEARS" VALUES (?,?)'
        vals = (None, 1772)
        try:
            cur.execute(statement, vals)
        except:
            self.fail()

        statement = 'INSERT INTO "FirstAuthors" VALUES (?,?)'
        vals = (None, 'Broderick, B')
        try:
            cur.execute(statement, vals)
        except:
            self.fail()

        conn.close()

class TestPopulation(unittest.TestCase):
    def testPop(self):
        db = 'sciDirect.db'
        conn=sqlite3.connect(db)
        cur=conn.cursor()
        final_model.populate_db('sciDirect.db')

        statement1 = 'SELECT * FROM "Articles"'
        cur.execute(statement1)
        test1 = 0
        for row in cur:
            test1 = row[0]

        statement2 = 'SELECT * FROM "FirstAuthors"'
        cur.execute(statement2)
        test2 = 0
        for row in cur:
            test2 = row[0]

        statement3 = 'SELECT * FROM "Journals"'
        cur.execute(statement3)
        test3 = 0
        for row in cur:
            test3 = row[0]

        statement4 = 'SELECT * FROM "Categories"'
        cur.execute(statement4)
        test4 = 0
        for row in cur:
            test4 = row[0]

        statement5 = 'SELECT * FROM "Countries"'
        cur.execute(statement5)
        test5 = 0
        for row in cur:
            test5 = row[0]

        self.assertGreater(test1, 2000)
        self.assertGreater(test2, 1500)
        self.assertGreater(test3, 1200)
        self.assertGreater(test4, 300)
        self.assertGreater(test5, 50)



    #
    # def testWipe(self):
    #     db = 'sciDirect.db'
    #     conn=sqlite3.connect(db)
    #     final_model.wipe_db(db)
    #     conn.close()
    #     pass

class TestProcessing(unittest.TestCase):

    def testCategoryCounts(self):
        category = 'ENGI'
        db = 'sciDirect.db'
        testCat = final_model.Category('ARTS')
        category = final_model.topCatCounts(db, category)
        self.assertEqual(type(category), type(testCat))

        ##Make sure a bogus category doesn't return results
        bogus = final_model.topCatCounts(db, 'ZZZZ')
        self.assertEqual(len(bogus.yearCounts),0)


    def testJournals(self):
        category = 'Architecture'
        db = 'sciDirect.db'
        testDict = {}
        testJournal = final_model.journalInfo(db, category)
        self.assertEqual(type(testDict), type(testJournal))
        self.assertGreater(len(testJournal), 0)

        ##Make sure a bogus category doesn't return results
        bogus = final_model.journalInfo(db, 'YYYY')
        self.assertEqual(len(bogus),0)


    def testcounts(self):
        db = 'sciDirect.db'
        testDict = {}
        testcats = final_model.category_count(db)
        # print(len)
        testcntry = final_model.country_count(db)
        self.assertEqual(type(testDict), type(testcats))
        ##we know there are 27 parent categories
        self.assertEqual(len(testcats), 27)
        self.assertEqual(type(testcntry), type(testDict))




# our tests should show that you are able to access data from all of your sources, that your database is correctly constructed and can satisfy queries that are necessary for your program, and that your data processing produces the results and data structures you need for presentation.
unittest.main()
