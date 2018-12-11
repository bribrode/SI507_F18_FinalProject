import final_model
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
from secrets import *
from flask import Flask, render_template, request
import sys
import numpy as np

DBNAME = "sciDirect.db"
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        sort = request.form['sortby']
        if sort == 'country':
            catBD = final_model.country_count(DBNAME)
        else:
            catBD = final_model.category_count(DBNAME)
    else:
        catBD = final_model.category_count(DBNAME)

    labels = []
    vals = []

    for key in catBD:
        labels.append(key)
        vals.append(catBD[key])

    trace = go.Pie(labels=labels, values=vals, hoverinfo='label+percent', textinfo='value')
    # py.iplot([trace], filename='basic_pie_chart')
    div = plotly.offline.plot([trace], show_link=False, output_type="div", include_plotlyjs=True)
    sortBy = 'Category'

    return render_template('index.html', plotly = div, sortBy = sortBy)


@app.route('/category', methods=['GET', 'POST'])
def category():
    cList = []
    curr = final_model.category_count(DBNAME)
    for item in curr:
        cList.append(item)

    if request.method == 'POST':
        category = request.form['cat']
    else:
        category = "Architecture"


    thisCat = final_model.topCatCounts(DBNAME,category)
    xvals = []
    yvals = []
    for entry in thisCat.yearCounts:
        xvals.append(entry)
        yvals.append(thisCat.yearCounts[entry])

    authList = []
    numList = []
    for item in thisCat.top5Auths:
        authList.append(item)
        numList.append(thisCat.top5Auths[item])


    affList = []
    affnumList = []
    for item in thisCat.top5Affs:
        affList.append(item)
        affnumList.append(thisCat.top5Affs[item])

    trace = go.Scatter( x = xvals, y = yvals, mode = 'lines', name = 'lines')
    div = plotly.offline.plot([trace], show_link=False, output_type="div", include_plotlyjs=True)

    ###########
    journals = final_model.journalInfo(DBNAME, category)

    sizes = []
    labels = []
    for item in journals:
        sizes.append(journals[item])
        label = item
        labels.append(label)

    data = [go.Bar(
            x=sizes,
            y=labels,
            orientation = 'h'
    )]

    bubblediv = plotly.offline.plot(data, show_link=False, output_type="div", include_plotlyjs=True)

    return render_template('category.html', catList = cList, category = category, plotly = div,
    authList=authList, numList = numList,affList = affList, affnumList = affnumList, bubbleplotly = bubblediv)

if __name__ == '__main__':

    if len(sys.argv) > 1:
        if sys.argv[1] == "db":
            answer = ''
            while answer != "quit":
                answer = input('''\nEnter one of the following commands:
                'wipe' - will delete the database
                'build' - will rebuild empty tables in the database
                'populate' - will fill the database
                'all' - will do all of the above, giving you a freshly filled database
                'quit' - will allow you to exit \n\n: ''')
                if answer == "wipe":
                    final_model.wipe_db(DBNAME)
                elif answer == "build":
                    final_model.create_db(DBNAME)
                elif answer == "populate":
                    final_model.populate_db(DBNAME)
                elif answer == "all":
                    final_model.wipe_db(DBNAME)
                    final_model.create_db(DBNAME)
                    final_model.populate_db(DBNAME)
                elif answer == "quit":
                    break
                else:
                    print("please enter a valid input")
        else:
            print("Command not recognized")
    else:

        app.run(debug=True)

        # test = final_model.category_count(DBNAME)
        # test = final_model.country_count(DBNAME)
        # test = final_model.topCatCounts(DBNAME, 'ENER')
        # test = final_model.journalInfo(DBNAME, 'ARTS')
