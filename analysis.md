# Country Data Analysis Write-Up

## 1. Dataset Description
The data comes from the REST Countries API (v5), basically a big read-only database of country info you hit with an API key. It's paginated, so you only get 100 records at a time, which meant looping through 3 pages. Ended up with 255 records. For each country I pulled seven fields: name, population, area (km²), region, subregion, primary language, and capital. There are like 80 fields available but I only took the ones I needed.

## 2. Pipeline Description
The whole thing is five functions tied together by main(). fetch_countries() does the API calls page by page and checks the status code before touching anything. Then main() loops the raw records and flattens them, since the names and area come back as nested objects and the capital/language are buried inside lists, so I dig those out. store_country() saves each one to SQLite through Peewee and skips any country already in there so you don't double up. analyze() loads it into a pandas DataFrame and runs the groupbys, and visualize() builds the bar chart and saves it.

## 3. Findings
Population is way more lopsided than I expected. Asia alone has about 4.7 billion people, more than every other region combined. Africa, the Americas, and Europe come next, then Oceania and Antarctica are basically rounding errors. The part that actually surprised me though was that Africa has the *most* countries (60) but only the second-most people, while Asia gets the most population out of fewer countries (53). So country count and population don't line up at all. China was the single most populous at ~1.4 billion, and the total came out to roughly 8.07 billion, which matches the real world population, so that was a nice sanity check.

## 4. Ethical Considerations
This is public reference data, no personal info, just country stats from UN/ISO sources. I used a free API key, only requested the fields I needed to keep bandwidth down, and put a time.sleep(1) between each page so I wasn't hammering their server. Stayed under the free tier's monthly limit too.

## 5. Limitations
The population numbers sync on a delay so they're not perfectly live. A country that just passed another might still show lower here. It's also purely descriptive, it tells you what but not why. With more time I'd add a population density column (population ÷ area) and break down the most common languages across all the countries.
