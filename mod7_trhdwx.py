# imports
import json
import pygal
import requests
import datetime
import unittest



def get_stock_symbol():
    return input("Enter the stock symbol you are looking for: ")
    
class SymbolTest(unittest.TestCase):

    def test_symbolfunc_1(self):
        result = get_stock_symbol
        self.assertTrue(result.isupper())
        
# Noah's chart function
def get_chart_type(var):
    if var == 1 or var == 2:
        return True
    else:
        print("Error: Please choose from one of the provided options")
        return False
        
class ChartTest(unittest.TestCase):
    
    def test_chartfunc_1(self):
        self.assertEqual(get_chart_type(1),True)
        self.assertEqual(get_chart_type(7),False)

def get_time_series(var):
    choice = var
    if choice == 1 or choice == 2 or choice == 3 or choice == 4:
        return True
    else:
        print("Error: Please choose from one of the provided options.")
        return False

class TimeTest(unittest.TestCase):

    def test_timefunc_1(self):
        self.assertEqual(get_time_series(3),True)
        self.assertEqual(get_time_series(5),False)

def get_beginning_date(var):
    beginning_date = var
    try:
        beginning_date = datetime.datetime.strptime(beginning_date, "%Y-%m-%d").date()
    except (ValueError, Exception):
        print("Error: Invalid date. Please try again.")
        return False
    return True

class BeginTest(unittest.TestCase):

    def test_beginfunc_1(self):
         self.assertEqual(get_beginning_date("2020-02-02"),True)
         self.assertEqual(get_beginning_date("2022340-02-02"),False)

def get_end_date(var):
    input_end_date = var
    try:
        ending_date = datetime.datetime.strptime(input_end_date, "%Y-%m-%d").date()
    except (ValueError, Exception):
        print("Invalid date. Please try again.")
        return False
    return True

class EndTest(unittest.TestCase):
    
    def test_endfunc_1(self):
         self.assertEqual(get_end_date("2020-02-02"),True)
         self.assertEqual(get_end_date("2022340-02-02"),False)

# json_to_dataframe()
# Description:
#   transforms the json object returned from the api call into a pandas dataframe
# inputs:
#   date: data from api call in a pandas dataframe
#   record_path: defined record path to be used for locating the data in the json object. this changes depending
#                on the time series used for the api call.
# outputs:
#   data_df: API data in a pandas dataframe
# Author:
#   Zac Lipperd - ZMLMCB
def json_to_dataframe(data, record_path):
    # json object to a flattened json string, begins dumping to string at the nested json for 'record_path'
    json_str = json.dumps(data[record_path])
    # json to pandas df
    data_df = pd.read_json(json_str)
    # data is rotated 90 degrees, perform pandas transform
    data_df = data_df.T
    # after transform index is incorrect order, sort to return to ascending
    data_df.sort_index(inplace=True, ascending=True)
    return data_df


# retrieve_date_range()
# Description:
#   parses the dataframe retrieved from the api call for the desired date range into a new dataframe
#   returns the newly created frame
# inputs:
#   date: data from api call in a pandas dataframe
#   bd: beginning date of user requested for date range
#   ed: end date of user requested for date range
# outputs:
#   data: returns the original data frame if data is for an intraday api call
#   data_ranged: new data frame containing only the data in range bd - ed
# Author:
#   Zac Lipperd - ZMLMCB
def retrieve_date_range(data, bd, ed):
    # if bd and ed are integer value 0, the api data is for intraday trading, no range is needed return data unchanged
    if bd == 0 and ed == 0:
        return data
    else:
        # pandas loc function using bd and ed will return a data frame containing values in this range
        data_ranged = data.loc[bd: ed]
        return data_ranged


# graph_date()
# Description:
#   graphs the data retrieved from the api call using pygal and displays it in user browser using lxml
# inputs:
#   date: data from api call in a pandas dataframe
#   ss: stock symbol used for creating chart title
#   ts: time series used for chart title
#   ct: chart type user wants
#   bd: beginning date of user requested for date range
#   ed: end date of user requested for date range
# outputs:
#   void
# Author:
#   Zac Lipperd - ZMLMCB
def graph_data(data, ss, ts, ct, bd, ed):
    # get needed range from dataframe
    data = retrieve_date_range(data, bd, ed)
    # define chart type
    if ct == "1":
        chart = pygal.Line(x_label_rotation=20, show_minor_x_labels=False)
    else:
        chart = pygal.Bar(x_label_rotation=20, show_minor_x_labels=False, logarithmic=True)
    # set title, will be different from intraday as there is no date range
    if ts == "1":
        chart.title = "Stock Data for " + ss + ": Intraday values for last 100 hours"
    else:
        chart.title = "Stock Data for " + ss + ": " + str(bd) + " to " + str(ed)
    # get x axis label from dataframe
    data_list = data.index.tolist()
    chart.x_labels = data_list
    # if too many x data, chart is unreadable, if over 25 skip every 5
    if len(data_list) > 25:
        n = 5
    else:
        n = 1
    # add data to chart
    chart.x_labels_major = data_list[::n]
    chart.add('Open', data.loc[:, "1. open"].values)
    chart.add('High', data.loc[:, "2. high"].values)
    chart.add('Low', data.loc[:, "3. low"].values)
    chart.add('Close', data.loc[:, "4. close"].values)
    # render the chart in user browser
    chart.render_in_browser()


# api_call()
# Description:
#   preforms api call from user inputs using requests. data is then processed and presented
#   as a graph to the user in browser using pygal
#   Alpha Vantage Stock API https://www.alphavantage.co/
# inputs:
#   ss: stock symbol used for creating chart title
#   ct: chart type user wants
#   ts: time series used for chart title
#   bd: beginning date of user requested for date range
#   ed: end date of user requested for date range
# outputs:
#   void
# Author:
#   Zac Lipperd - ZMLMCB
def api_call(ss, ct, ts, bd, ed):
    # api call differs for each time series, if else and set the needed parameters to make api call, and date processing
    # url is passed to request to make the call
    # record_path is used in data processing in json_to_dataframe()
    if ts == "1":
        url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=' + ss + \
              '&interval=60min&outputsize=compact&apikey=2C4AFL520Q27QCZ9'
        record_path = "Time Series (60min)"
    elif ts == "2":
        url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=' + ss + \
              '&outputsize=full&apikey=2C4AFL520Q27QCZ9'
        record_path = "Time Series (Daily)"
    elif ts == "3":
        url = 'https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol=' + ss + '&apikey=2C4AFL520Q27QCZ9'
        record_path = "Weekly Time Series"
    else:
        url = 'https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol=' + ss + '&apikey=2C4AFL520Q27QCZ9'
        record_path = "Monthly Time Series"
    # make api request and store returned data in a json object
    r = requests.get(url)
    data_json = r.json()
    # if api response contains an error message, notify the user and return to main.
    if 'Error Message' in data_json:
        print("\nThere was an error in your request. Stock symbol '" + ss + "' does not exist.")
        return
    # transform json object to dataframe for easier processing into pygal
    data = json_to_dataframe(data_json, record_path)
    # graph the data
    graph_data(data, ss, ts, ct, bd, ed)
    return


# exit_prompt()
# Description:
#   prompt user if the want to run api call for another stock
# inputs:
#   void
# outputs:
#   return 0 if user wants to close the program,
#   return 1 if the wish to run another api call
# Author:
#   Zac Lipperd - ZMLMCB
def exit_prompt():
    # prompt user for y or n
    x = input("Would you like to view more stock data? Enter 'y' to continue, or 'n' to exit:   ")
    if x == 'n':
        print("Thank you and Goodbye!")
        return 0
    elif x == 'y':
        return 1
    else:
        # if anything other then a 'n' or 'y', call exit_prompt() again until a valid input is received
        print("\nError: Error: Please choose from one of the provided options")
        return exit_prompt()


# Main
# Author:
#   Scrum Team 3
if __name__ == "__main__":
    unittest.main()
    