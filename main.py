import requests as req
import streamlit as st
import  datetime as dt
import pandas as pd


st.title("🌍 Personalized Weather")
res = req.get("https://ipinfo.io/json", headers={"User-Agent": "my-app"})
data = res.json()
lat, lon = map(float, data["loc"].split(","))
city = data.get("city", "Unknown")
region = data.get("region", "Unknown")
country = data.get("country", "Unknown")
weather_url = (
    f"https://api.open-meteo.com/v1/forecast"
    f"?latitude={lat}&longitude={lon}"
    "&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weathercode"
    "&timezone=auto"
)
weather_res = req.get(weather_url, verify=False)
weather_data = weather_res.json()
current = weather_data["current"]
st.subheader(f"📍 Location: {city}, {region}, {country}")
st.markdown("---")
col1, col2, col3 = st.columns(3)
col1.metric("🌡️ Temp", f"{current['temperature_2m']}°C")
col2.metric("💧 Humidity", f"{current['relative_humidity_2m']}%")
col3.metric("🌬️ Wind", f"{current['wind_speed_10m']} km/h")
st.caption(f"Weather Code: {current['weathercode']}")
#הערה להוסיף תנאים במקרה והמידע לא הגיע שלא יוצג בקובץ הסופי השגיאות
def make_table_of_weather():
    locations = {
        "tel_aviv": [32.109333, 34.855499],
        "haifa": [32.794044, 34.989571],
        "safed": [32.964650, 35.496000],
        "eilat": [29.560000, 34.950000],
        "beer_sheva": [31.250000, 34.800000],
    }
    columns = ["city", "datetime", "temp", "humidity", "wind", "precipitation"]
    weather_df = pd.DataFrame(columns=columns)
    for location, value in locations.items():
        end = dt.date.today() - dt.timedelta(days=1)
        start = end - dt.timedelta(days=6)
        lat=value[0]
        lon=value[1]
        url = (
        "https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={lat}&longitude={lon}"
        f"&start_date={start.isoformat()}&end_date={end.isoformat()}"
        "&hourly=temperature_2m,precipitation,relative_humidity_2m,"
        "shortwave_radiation,windspeed_10m,visibility"
        "&timezone=Asia/Jerusalem")
        res = req.get(url, verify=False)
        res.raise_for_status()
        res=res.json()
        city= location
        datetime=res.get("hourly",{}).get("time",[])
        temp=res.get("hourly",{}).get("temperature_2m",[])
        humidity=res.get("hourly",{}).get("relative_humidity_2m",[])
        wind=res.get("hourly", {}).get("windspeed_10m", [])
        precipitation=res.get("hourly",{}).get("precipitation",[])
        data=[]
        for i in range(len(datetime)):
           data.append({
               "city": city,
               "temp": temp[i],
               "humidity": humidity[i],
               "wind": wind[i],
               "precipitation": precipitation[i],
                "datetime": datetime[i],
           })
        df=pd.DataFrame(data)
        weather_df=pd.concat([weather_df,df], ignore_index=True)
    st.write(weather_df)

def make_data_set_for_features():
    url = (f"https://api.geoapify.com/v2/places?categories=activity,commercial.shopping_mall,catering.restaurant,entertainment,sport,ski&filter=circle:{lon},{lat},5000&bias=proximity:{lon},{lat}&limit=400&fields=properties.name,properties.housenumber,properties.street,properties.address_line1,properties.address_line2,properties.categories,properties.city,properties.country,properties.phone,properties.website,properties.distance,geometry,properties.datasource.raw&lang=en&apiKey=2d6acf0f3338413992829d14fa69ffdf")
    response_around = req.get(url, verify=False)
    res1 = response_around.json()
    list_features = res1.get("features",{})
    data = []
    for feature in list_features:
        data.append({
            "name":feature.get("properties",{}).get("name") or feature.get("properties",{}).get("datasource",{}).get("raw",{}).get("name",None),
            "address":f"{feature.get("properties",{}).get("street","")} , {feature.get("properties",{}).get("housenumber","")}",
            "city":feature.get("properties",{}).get("city") or feature.get("properties",{}).get("address_line2",None),
            "phone":feature.get("properties",{}).get("phone", ""),
             "link":feature.get("properties",{}).get("website", None),
            "distance":feature.get("properties",{}).get("distance", None),
             "category":feature.get("properties",{}).get("categories ",[]),
             "latitude":feature.get("properties",{}).get("geometry", {}).get("coordinates",[None, None])[0],
           "longitude":feature.get("geometry", {}).get("coordinates", [None, None])[1],
        })
    df = pd.DataFrame(data)
    st.dataframe(df)

make_data_set_for_features()
make_table_of_weather()