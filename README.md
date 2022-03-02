# available-classrooms
Tool that shows the empty classrooms at uniud at a given time

## minimal-working-example usage
* Clone the repo
* Install from Pipfile:
    ```
    pipenv install
    ```
* Activate the Pipenv shell:
    ```
    pipenv shell
    ```
* run the script
    ```
    python minimal-working-example.py
    ```

The script prints to terminal the empty classrooms at the time you run it. 

To change the starting time (e.g. the time you want to see empty classes) change
```
time = datetime.datetime.now().time()
```
to the preferred time (it must be of `datetime.time` type).

To show available classrooms starting from `time` and empty for (at least) `N` hours, add an integer number as third argument when calling the `empty_rooms()` function. Example:
```
available_classrooms = empty_rooms(df, time, 2)
```

To change the campus (default: Rizzi), change the `planner_url` string (see the `fetch_timetable()` docstring for more details).
