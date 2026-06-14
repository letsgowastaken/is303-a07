# Country Data Pipeline (IS 303 A07)

This is my capstone pipeline for IS 303. It pulls country data from the REST Countries API, stores it in a SQLite database, analyzes it with pandas, and saves a chart. Basically the whole fetch to store to analyze to visualize flow in one program.

Context B: Country Data.

## Files
- `country_pipeline.py` is the main program. It does the API calls, stores everything, runs the analysis, and builds the chart.
- `countries.db` is the SQLite database the program creates. Holds all 255 countries with population, area, region, language, and capital.
- `population_by_region.png` is the bar chart it spits out. Shows total population by region, and Asia is way out in front.
- `analysis.md` is my write-up (dataset, pipeline, findings, ethics, limitations).
- `README.md` is this file.

## Setup
You need a free API key since the old free version of this API got deprecated.
1. Grab a key at https://restcountries.com/sign-up (free tier, no card).
2. Paste it into the `API_KEY` line near the top of `country_pipeline.py`.

## How to run
```bash
pip install requests peewee pandas matplotlib
python country_pipeline.py
```
Running it creates `countries.db` and `population_by_region.png` and prints the analysis. If you run it again it skips countries already in the database so you don't get duplicates.

## Notes
The v5 API is paginated and only gives 100 records per request, so the program loops with limit/offset until it runs out of pages (about 3 requests for all the countries). The free tier allows 500 requests a month and one full run uses around 3.
