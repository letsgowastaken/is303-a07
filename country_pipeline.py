"""
Country Data Analysis Pipeline

Inputs: rest countries api v5 (https://api.restcountries.com/countries/v5)
Processes: fetch country data (paginated, needs a free api key), store it in
           sqlite with peewee, query and analyze with pandas, make a bar chart
Outputs: printed analysis, population_by_region.png, countries.db
"""

from peewee import *
import requests, time
import pandas as pd
import matplotlib.pyplot as plt

# get a free key at https://restcountries.com/sign-up and paste it here
API_KEY = "rc_live_4f602a5fda994500bd7d62686b754f1e"

db = SqliteDatabase("countries.db")

class Country(Model):
    name = CharField()
    population = IntegerField()
    area = FloatField()
    region = CharField()
    subregion = CharField()
    language = CharField()
    capital = CharField()

    class Meta:
        database = db


def fetch_countries():
    """
    inputs:
        none (uses the API_KEY at the top of the file)

    process:
        fetch countries from the v5 api one page at a time (max 100 per page)
        v5 wraps results in data.objects and tells us if there is more
        sleep between pages so we are not hammering the server

    output:
        list of country dictionaries (empty list if the request fails)
    """
    if API_KEY == "" or "PASTE" in API_KEY:
        print("Add your restcountries API key to API_KEY at the top of the file.")
        return []

    base_url = "https://api.restcountries.com/countries/v5"
    fields = "names.common,population,region,subregion,area.kilometers,capitals,languages"
    headers = {"Authorization": "Bearer " + API_KEY}

    all_countries = []
    offset = 0
    limit = 100
    while True:
        url = base_url + "?limit=" + str(limit) + "&offset=" + str(offset) + "&response_fields=" + fields
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print("Request failed:", response.status_code, response.text[:200])
            break

        payload = response.json()
        data_block = payload.get("data", {})
        objects = data_block.get("objects", [])
        meta = data_block.get("meta", {})

        all_countries += objects
        print(f"Got {len(objects)} countries (offset {offset})")

        # print the first record once so we can confirm the shape
        if offset == 0 and objects:
            print("Sample record:", objects[0])

        if not meta.get("more"):
            break
        offset += limit
        time.sleep(1)

    return all_countries


def store_country(data):
    """
    inputs:
        data dictionary for one country

    process:
        skip it if the country is already in the db, otherwise add it

    output:
        none (writes to the database)
    """
    existing = Country.get_or_none(Country.name == data["name"])
    if existing:
        print(f"Skipping {data['name']}")
        return
    Country.create(**data)
    print(f"Stored {data['name']}")


def analyze():
    """
    inputs:
        none (reads from the database)

    process:
        load the country table into pandas and run a couple groupbys

    output:
        population by region (a pandas series, used for the chart)
    """
    df = pd.read_sql("select * from country", db.connection())

    print("\n===== ANALYSIS =====")
    print(f"Total countries stored: {len(df)}")
    print(f"Total world population: {df['population'].sum()}")
    print(f"Number of regions: {df['region'].nunique()}")

    # population by region (groupby with a sum)
    pop_by_region = df.groupby("region")["population"].sum().sort_values(ascending=False)
    print("\nPopulation by region:")
    print(pop_by_region)

    # how many countries are in each region
    count_by_region = df.groupby("region")["name"].count().sort_values(ascending=False)
    print("\nCountries per region:")
    print(count_by_region)

    # most populated country
    most = df.sort_values("population", ascending=False).iloc[0]
    print(f"\nMost populated country: {most['name']} ({most['population']})")

    return pop_by_region


def visualize(pop_by_region):
    """
    inputs:
        pop_by_region series from analyze()

    process:
        make a bar chart of total population by region and save it

    output:
        none (saves population_by_region.png)
    """
    plt.bar(pop_by_region.index, pop_by_region.values)
    plt.title("Total Population by Region")
    plt.xlabel("Region")
    plt.ylabel("Population")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("population_by_region.png")
    print("\nSaved chart to population_by_region.png")


def main():
    db.connect()
    db.create_tables([Country])

    countries = fetch_countries()
    for c in countries:
        # names is an object like {"common": "...", "official": "..."}
        names = c.get("names", {})
        name = names.get("common") or names.get("official") or "Unknown"

        # area is an object like {"kilometers": ..., "miles": ...}
        area_obj = c.get("area", {})
        if isinstance(area_obj, dict):
            area = area_obj.get("kilometers", 0) or 0
        else:
            area = area_obj or 0

        # capitals is a list of objects that each have a name
        caps = c.get("capitals", [])
        if caps and isinstance(caps[0], dict):
            capital = caps[0].get("name", "None")
        elif caps:
            capital = str(caps[0])
        else:
            capital = "None"

        # languages is a list of objects, grab the english name of the first one
        langs = c.get("languages", [])
        if langs and isinstance(langs[0], dict):
            first_lang = langs[0]
            language = first_lang.get("name") or first_lang.get("english") or first_lang.get("native") or "None"
        elif langs:
            language = str(langs[0])
        else:
            language = "None"

        data = {
            "name": name,
            "population": c.get("population", 0) or 0,
            "area": area,
            "region": c.get("region", "Unknown") or "Unknown",
            "subregion": c.get("subregion", "None") or "None",
            "language": language,
            "capital": capital
        }
        store_country(data)

    pop_by_region = analyze()
    visualize(pop_by_region)

    db.close()

main()
