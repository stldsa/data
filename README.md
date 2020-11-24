# STL DSA Data Dashboard

### To get started:

1. Install Python 3.8+ (I use [pyenv](https://realpython.com/intro-to-pyenv/) to manage my python versions, but use whatever works for you and your machine)
2. Install [Poetry](https://python-poetry.org/docs/) for dependency management (if you're used to pip or another Python dependency management system feel free to use it but your mileage may vary)
3. Clone the repo with `git clone https://github.com/schlich/stldsa-data.git` and `cd` into the directory
4. Install your dependencies with `poetry install`
5. Activate your virtual environment with `poetry shell` (you will need to do this every time you work on the project)

Best practices dictate that we don't commit our data to version control. Thus, to start with, we will be storing all data in the top-level "data" directory, which will be ignored by git. You will have to manually add all_donations.csv and any other data you want to work with to this directory, including geographic/shapefile data.

Run the app with `python app.py`

That should get things up and running, reach out if you have any questions
