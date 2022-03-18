import os
import re
import datetime

import requests
from bs4 import BeautifulSoup
import pandas as pd


def fetch_timetable(planner_url):
    '''Creates a csv file with a timetable, given a proper url

    Parameters
    ----------
    planner_url : str
        The url of the desired university campus. It is in the form
        "https://planner.uniud.it/EasyRoom//index.php?page=4&content=view_prenotazioni&vista=day&area=XX&_lang=it"
        where "XX" is the code of the campus (e.g.: 13 -> Rizzi)

    Returns
    -------
    Saves a csv file containing a DataFrame with the entire timetable
    of the specified campus for the current day
    '''

    print ("Fetching timetable....")

    r = requests.get(planner_url,
                     headers={'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'},
                     timeout=15)

    # for each room, find all seats and put them in the `seats` list
    get_text = r.text
    soup = BeautifulSoup(get_text, "html.parser")
    seats = soup.findAll("span", {"class": "subheader"})
    seats = seats[1::2]
    seats = [re.search('<span class="subheader">(.*)</span>', str(i)).group(1) for i in seats]
    seats = [i.replace("<br/>", "") for i in seats]

    # read the timetable and create a DataFrame
    df = pd.read_html(r.content)[0]
    # delete rows with all NaN
    df.dropna(how='all', inplace=True)
    # delete rows for which the last column ('Unnamed: 23') is empty
    df = df[pd.notnull(df['Unnamed: 23'])]
    # reindex the DataFrame: it now contains only all rooms and classes
    df.reset_index(drop=True, inplace=True)
    # drop the last column
    df.drop(df.columns[len(df.columns)-1], axis=1, inplace=True)
    # rename the first column 'Aula'
    df.rename(columns={'Unnamed: 0':'Aula'}, inplace=True)

    #fix classrooms names' removing the seats
    j = 0
    new_aule = []
    for i in df['Aula']:
        new_aule.append(i.replace(seats[j], ""))
        j += 1

    fixed_aule = pd.Series(new_aule)
    df['Aula'] = fixed_aule
    
    # change the column names from str to datetime.time
    # NOTE: the column name refers to the END time of the half-hour timeslot
    df.set_index('Aula', inplace=True)

    for col in df.columns:
        df.rename(columns={col : col[6:]}, inplace=True)

    df.columns = pd.to_timedelta(df.columns+':00')
    df.reset_index()

    # export the DataFrame to csv
    df.to_csv("rizzi.csv")

    print("Done.")


def empty_rooms(df, time, span=0):
    '''Given a time and a time span, returns a list of empty classrooms
    
    Parameters
    ----------
    df : DataFrame
        Pandas DataFrame with a daily timetable of a campus
    time : datetime.time
        A datetime time (hh mm ss mmmm)
    span : int, optional
        A time span in hours. It is needed to compute the empty rooms from
        the time `time` to (at least) `span` hours from `time` (default is 0).
        Examples:
        * `time`=now, `span`=0 -> empty rooms in this moment
        * `time`=now, `span`=N -> empty rooms from now to (at least) N hours

    Returns
    -------
    available_classrooms : list
        A list of empty rooms
    '''

    df2 = df.copy()  # deep copy of the dataframe
    available_classrooms = []
    day = datetime.datetime.now().weekday()

    if day == 5 or day == 6:  # sat or sun
        return available_classrooms

    time_frame = False
    # find the correct time slot
    for col in df2.columns:
        if col != 'Aula':
            table_time = datetime.datetime.strptime(col[-8:], '%H:%M:%S').time()
            if time < table_time:
                time_frame = col  # name of the correct column / time slot
                break

    if time_frame == False:  # time is during closing hours
        return available_classrooms
    else:
        # drop not null rows, e.g.: not available classrooms
        df2.set_index('Aula', inplace=True)
        starting_index = df2.columns.get_loc(time_frame)
        ending_index = starting_index+(2*span)+1
        sub_df = df2.iloc[:, starting_index:ending_index]
        # delete all rows that aren't all NaN (e.g.: keep rows that are all NaN)
        sub_df = sub_df[sub_df.isnull().all(1)]
        available_classrooms = list(sub_df.index)
        
        return available_classrooms


if __name__ == "__main__":
    #rizzi url
    planner_url = "https://planner.uniud.it/EasyRoom//index.php?page=4&content=view_prenotazioni&vista=day&area=13&_lang=it"

    if not os.path.exists("rizzi.csv"):
        fetch_timetable(planner_url)
        
    df = pd.read_csv("rizzi.csv")
    time = datetime.datetime.now().time() #current time
    available_classrooms = empty_rooms(df,time) #empty classrooms now

    for i in available_classrooms:
        print(i)
