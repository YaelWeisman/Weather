import requests as req
import streamlit as st
import  datetime as dt
import pandas as pd

def make_table_of_weather():
    #columns = ["city", "datetime", "temp", "humidity", "wind", "precipitation"]
    #weather_df = pd.DataFrame(columns=columns)
    end = dt.date.today() - dt.timedelta(days=1)
    start = end - dt.timedelta(days=6)
    url = (
        "https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={lat}&longitude={lon}"
        f"&start_date={start.isoformat()}&end_date={end.isoformat()}"
        "&hourly=temperature_2m,precipitation,relative_humidity_2m,"
        "shortwave_radiation,windspeed_10m,visibility"
        "&timezone=Asia/Jerusalem")
    res = req.get(url, verify=False)
    if res.status_code == 200:
        res=res.json()
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
    else:
        st.error("error !!!")
    if(data):
        st.write(df)
def make_data_set_for_features():
    url = (
        f"https://api.geoapify.com/v2/places?"
        f"categories=activity,commercial.shopping_mall,catering.restaurant,entertainment,sport,ski&"
        f"filter=circle:{lon},{lat},9000&"  
        f"bias=proximity:{lon},{lat}&" 
        f"limit=400&" 
        f"fields=properties.name,properties.brand,properties.official_name,properties.alt_name,"
        f"properties.housenumber,properties.street,properties.address_line1,"
        f"properties.address_line2,properties.categories,properties.city,properties.country,"
        f"properties.phone,properties.website,properties.distance,geometry,properties.datasource.raw&"
        f"lang=en&"
        f"apiKey=2d6acf0f3338413992829d14fa69ffdf"
    )
    response_around = req.get(url, verify=False)
    print(response_around.status_code)
    if response_around.status_code == 200:
        res1 = response_around.json()
        list_features = res1.get("features",{})
        data = []
        for feature in list_features:
            properties = feature.get("properties",{})
            raw=properties.get("datasource",{}).get("raw",{})
            geometry=feature.get("geometry",{})
            name = (
                    properties.get("name") or
                    properties.get("brand") or
                    properties.get("official_name") or
                    properties.get("alt_name") or
                    raw.get("name") or
                    raw.get("brand")
            )
            phone=(
                    properties.get("phone") or
                    properties.get("contact", {}).get("phone") or
                 raw.get("phone") or
                   raw.get("contact:phone")
            )
            address=f"{properties.get("street",'')} , {properties.get("housenumber",'')}"
            if not address:
                address=f"{properties.get('address_line1',"")} "
            city=properties.get("city") or properties.get("address_line2")
            data.append({
                "name":name,
                "address":address,
                "city":city,
                #"phone":phone,
                 "link":properties.get("website"),
                "distance":properties.get("distance"),
                 "category":properties.get("categories",[]),
                 "latitude":geometry.get("coordinates",[None, None])[1],
               "longitude":geometry.get("coordinates", [None, None])[0],
            })
        df = pd.DataFrame(data)
        df=df[df.name.notnull()]
        df=df[df.address.notnull()]
        temp_conditions=['Very Hot','Hot','Pleasant','Cold','Very Cold']
        category_dict= {'Ski':[4],
                        'Sport':[1,2,3],
                        'Shopping Mall':[0,1,2,3,4],
                        'Entertainment':[0,1,2,3,4],
                        'Restaurant':[0,1,2,3,4],
                        'parks':[1,2],
                         'activity':[1,2],}
        all_options = list(category_dict.keys())
        user_selection = st.multiselect("🎯 Choose categories you'd like to explore:", all_options)
        current_condition=None
        if currnt_temp >=32:
            current_condition='Very Hot'
        elif currnt_temp and currnt_temp >=27 and currnt_temp <=31:
            current_condition='Hot'
        elif currnt_temp and currnt_temp >=20 and currnt_temp <=26:
            current_condition='Pleasant'
        elif currnt_temp and currnt_temp >=10 and currnt_temp <=19:
            current_condition='Cold'
        elif currnt_temp and currnt_temp <10:
            current_condition='Very Cold'
        condition_index = temp_conditions.index(current_condition)
        st.dataframe(df)

lat=None
lon=None
currnt_temp=None
with st.form("location_form"):
    st.subheader("📍 write your location")
    city = st.text_input("city")
    #street = st.text_input("street")
    country = st.text_input("state", value="ישראל")
    submitted = st.form_submit_button("check weather")
    if submitted and city  and country:
        full_address = f"{city}, {country}"
        loc_url = (
            f"https://api.geoapify.com/v1/geocode/search"
            f"?text={full_address}&lang=he&format=json&apiKey=2d6acf0f3338413992829d14fa69ffdf"
        )
        res = req.get(loc_url,verify=False)
        if res.status_code == 200:
            loc_data = res.json()
            if loc_data .get("results"):
                lat = loc_data.get("results")[0].get("lat")
                lon = loc_data.get("results")[0].get("lon")
                if lat and lon:
                    weather_url = f"https://wttr.in/{lat},{lon}?format=j1"
                    weather_res = req.get(weather_url,verify=False)
                    if weather_res.status_code == 200:
                        weather_data = weather_res.json()
                        current_list =weather_data.get("current_condition", [])
                        if current_list:
                            current = current_list[0]
                            temp = current.get("temp_C", "N/A")
                            humidity = current.get("humidity", "N/A")
                            wind = current.get("windspeedKmph", "N/A")
                            #condion=current.get("weatherDesc",[])[0].get("value","N/A")
                            st.markdown(f"**📌 address:** {full_address}")
                            st.markdown("---")
                            col1, col2, col3 = st.columns(3)
                            col1.metric("🌡️ Temp", f"{temp}°C")
                            col2.metric("💧 Humidity", f"{humidity}%")
                            col3.metric("🌬️ Wind", f"{wind} km/h")
                            if temp:
                                currnt_temp=float(temp)
                                make_data_set_for_features()
                        else:
                            st.write("error could not find weather !! ")
                    else:
                        st.write("error could not find weather !! ")
        else:
            st.write("error could not find location try again !! ")
        if lat and lon :
             make_table_of_weather()