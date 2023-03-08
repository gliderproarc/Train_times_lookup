# CSV-to-train-times
A python script that takes in a csv of data and looks up train times from Yahoo.com.

You may not find this particularly useful if you don't live in Japan or ride the trains here, but looking up how long it takes to get from one train station is actually quite a common task. And Yahoo's train times are wonderfully current, but the website it's self can be a little cumbersome. The goal of this script was to go beyond simply getting transit time and make a table from a CSV file.

If you would like to re-purpose this for something else, you may want to swap out the names "Teacher" and location from both the script and the way the CSV file is structured, but you could use this as is if you just pretend these two labels mean something else.

# Intended use
The intended use is passing a path to a CSV file, and writing out a CSV file to the root of the project with table of the travel times from each of the "Teachers" in or original data to each of the "locations" in the data.

# Special thanks
Also, I want to give a shout out to Mr. Kou who posted some very helpful code on his blog about using Python to scrape train times from Yahoo with Python.
https://atooshi-note.com/python-yahoo-trans-scraping/
I took lots of inspiration from this gentleman's work on how the yahoo url request scheme works to pull data out of the HTMl that gets returned, as well as how to build URL requests from a departure and destination pair of station names.
