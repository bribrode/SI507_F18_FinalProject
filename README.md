#SI507 Fall 2018 Final Project: Visualizing Research with Science Direct

##Data sources
3 APIs from Elsevier and Science Direct were used - users can visit the developer portal at https://dev.elsevier.com/ to request an API key

**The APIs used in this project were:**
- Subject Classification API (https://dev.elsevier.com/documentation/SubjectClassificationsAPI.wadl)
  This API does not require authorization to use
  This allowed access to all of the official subject categories on Science direct

- SCOPUS Search API (https://dev.elsevier.com/documentation/ScopusSearchAPI.wadl)
  This API requires api key authorization
  This API facilitated searching the SCOPUS database of Science Direct to gather information of articles from specified Categories

- Serial Search API (https://dev.elsevier.com/documentation/SerialTitleAPI.wadl)
  This API requires api key authorization
  This API was used to fetch detailed information for each article identified by the SCOPUS Search API

##Tools
**Plotly** is used to facilitate the display of graphs on this application, users should set up a plotly account and get an API key. https://plot.ly/python/getting-started/ is a great resource to assist with this process.

**Flask** acts as a local server to host the wep pages displayed by this application

##secrets.py
Users should create a secrets.py file with the following information:
  `sd_key = <science direct api key>
  PLOTLY_USERNAME = <plotly username>
  PLOTLY_API_KEY = <plotly api key>``
**Users should also make sure their plotly certifications file includes the  proper username and api key**

##Code Structure
Data is gathered using the above mentioned API's - this information is cached in **sciDirect.json** and made available for later access.

This data is used to populate the **sciDirect.db** database. This database includes tables for Articles, Subject Categories, First Authors, Affiliated Organizations, Cities, Countries, Journals and Publication Years.

Information in this database is processed through the following data structures:
  - **Category Class** this class holds information about a specified category - it requires a category abbreviation be passed to its constructor. The class holds that abbreviation name, as well as dictionaries that include:
    **top5Auths** - a dictionary that holds top 5 authors associated with the specified category where the key is an author's name and the value is the number of publications they have in that category
    **top5Affs** - a dictionary that holds top 5 affiliated organizations associated with the specified category where the key is an organization name and the value is the number of publications they have in that category
    **yearCounts** - a dictionary where each key is a year and each value is the number of publications from the specified category that were published that year
  (Each category class instance is created and returned with the topCatCounts() function)

  - **Count Dictionaries** two dictionaries hold the breakdown information for all of the articles in the database - in one of these dictionaries, each key is a caategory and each value is the number of publications from that category, in the other each key is a country and the value is the number of publications from that country
  (These dictionaries are created and returned with the country_count() and category_count() functions)

  - **Journal Info Dictionary** this dictionary shows subjects of articles that are often included by journals of a specified subject. The dictionary has up to 10 entries, each with a key of a related subject and a value of the number of articles of the key category published by journals of the previously requested category.
  (This dictionary is created and returned with the journalInfo() function)

##Unit tests


##User Guide
**To delete or rebuild the database:**
Users can delete, rebuild and populate the database by running the program as
`python final.py db`
Here, users will be prompted with information regarding what commands are available: these include:
  `wipe` - this will delete everything from the database
  `build` - this will rebuild the empty tables into the database
  `populate` - this will populate all information into the database
  `all` - this will wipe, build and populate the database
  `quit` - allows the user to exit

**To run the program**
Users just simply have to enter `python final.py` into the command line, once the program is running, the user should open their preferred browser and type in `localhost:5000` to the address bar. This will pull up the main page of the application.

**Home Page - Article breakdown**
On the main page, users can switch the view of the pie chart between:
  **category view** - will show a breakdown of all of the articles in the database by category. The label of each section is the number of articles in the database from that category. Hovering over a section will provide the name of the category as well as the percentage of the total articles it makes up.  

  **country view** -  will show a breakdown of all of the articles in the database by country. The label of each section is the number of articles in the database from that country. Hovering over a section will provide the name of the country as well as the percentage of the total articles it makes up.
  **To aid display - if a country has less than 5 articles in this database, it will be included in the "other" category**

**Category Patterns Page**
Here, users can select a specific category from the available drop down menu
When a user clicks **update**, information for the specified category will load including:
  **Top published authors**
  This is a table of the 5 most published authors in this field along with the number of publications they have in the category

  **Top published affiliated organizations**
  This is a table of the 5 most published organizations in this field along with the number of publications each organization has in this category

  **Publications over time**
  This is a line chart that shows all how many publications were released in this category each year

  **Journals also publish...**
  This is a horizontal bar graph that shows the top 10 categories of articles that are publishe din Journals of this subject

**To exit the application**
Users can simply quit their web browser and hit control+c on their keyboard to end the Flask hosting session. 
