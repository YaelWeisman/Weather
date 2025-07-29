import requests as req
import streamlit as st
import  datetime as dt
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

def find_category(cat_list1,cat_list2):
    for c in cat_list1:
        if c in cat_list2:
            return c
    return None

def display_filtered_places(df):
    if 'show_places' not in st.session_state:
        st.session_state.show_places = False

    toggle_label = "🔽 Hide recommended places" if st.session_state.show_places else "✨ Show places based on the weather"
    if st.button(toggle_label):
        st.session_state.show_places = not st.session_state.show_places

    if st.session_state.show_places:
        df = df[df["category"].notnull()]
        df["category"] = df["category"].astype(str).str.strip().str.lower()
        if df.empty:
            st.warning("😕 No matching locations found.")
        else:
            for _, row in df.iterrows():
                text_dir = "rtl"
                st.markdown(f"""
                <div style='border:1px solid #ccc; border-radius:10px; padding:15px; margin:10px 0; background-color: #e6f7ff; direction:{text_dir}; text-align:{'right' if text_dir=='rtl' else 'left'};'>
                    <h4 style='margin:0;'>📍 {row['name']}</h4>
                    <p style='margin:0;'><strong>📌 Address:</strong> {row['address']} | {row['city']}</p>
                    <p style='margin:0;'><strong>🔗 Distance:</strong> {int(row['distance'])} meters</p>
                    <p style='margin:0;'><strong>🏷️ Category:</strong> {row['category']}</p>
                    {f'<p style="margin:0;"><a href="{row["link"]}" target="_blank">🌐 Website</a></p>' if pd.notnull(row["link"]) else ''}
                </div>
                """, unsafe_allow_html=True)

def make_table_of_weather():
    end = dt.date.today() - dt.timedelta(days=1)
    start = end - dt.timedelta(days=30)
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
        df=df[df.temp.notnull()]
        df=df[["temp","humidity","wind","datetime"]]
        #st.markdown("**lets research the weather in your city for the last month**:")
        df=df.set_index("datetime")
        #st.dataframe(df)
        #selected_date = st.date_input("📅 Choose a date to filter:", value=end, min_value=start, max_value=end)
        #if selected_date:
            #selected_date=selected_date.strftime("%Y-%m-%d")
            #filter_df=df[df.index.str.startswith(selected_date)]
            #st.dataframe(filter_df)
        df.index = pd.to_datetime(df.index).tz_localize("UTC").tz_convert("Asia/Jerusalem")
        df["hour"] = df.index.hour
        with col1:
            st.subheader("התפלגות טמפרטורה")
            fig = sns.displot(x='temp', data=df, kde=True, color="#FF7043", height=3, aspect=1)
            st.pyplot(fig.figure)
            plt.close(fig.figure)

        with col2:
            st.subheader("טמפרטורה מול לחות")
            fig2 = sns.lmplot(x="temp", y="humidity", data=df, height=3, aspect=1, line_kws={"color": "#FF7043"})
            st.pyplot(fig2.figure)
            plt.close(fig2.figure)

        with col3:
            st.subheader("average tempe for hour:")
            fig3, ax3 = plt.subplots(figsize=(8, 6))
            sns.scatterplot(x="hour", y="temp", data=df, color="#FF7043", alpha=0.3, ax=ax3)
            sns.lineplot(x="hour", y="temp", data=df, estimator='mean', color="black", ax=ax3)
            ax3.set_xticks(range(24))
            ax3.set_xlabel("hour")
            ax3.set_ylabel("temp (°C)")
            st.pyplot(fig3)
            plt.close(fig3)
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(
        x=df.index,
        y=df["temp"],
        mode='lines',
        name='טמפרטורה (°C)',
        line=dict(color='tomato')
    ))

    # קו לחות
    fig4.add_trace(go.Scatter(
        x=df.index,
        y=df["humidity"],
        mode='lines',
        name='לחות (%)',
        line=dict(color='royalblue'),
        yaxis="y2"
    ))

    fig4.update_layout(
        title="🌡️ טמפרטורה ולחות לאורך זמן",
        xaxis=dict(title="תאריך ושעה"),
        yaxis=dict(title="טמפרטורה (°C)", side='left'),
        yaxis2=dict(title="לחות (%)", overlaying='y', side='right'),
        legend=dict(x=0.01, y=0.99),
        hovermode="x unified",
        height=500
    )

    st.plotly_chart(fig4, use_container_width=True)

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
            address=f"{properties.get("street",'')} , {properties.get("housenumber",'')}"
            if not address:
                address=f"{properties.get('address_line1',"")} "
            city=properties.get("city") or properties.get("address_line2")
            data.append({
                "name":name,
                "address":address,
                "city":city,
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
        categories={'activity':[1,2],
                       'commercial.shopping_mall':[0,1,2,3,4],
                       'catering.restaurant':[0,1,2,3,4],
                       'entertainment':[0,1,2,3,4],
                       'sport':[1,2,3],
                       'ski':[4],
                       'activity.hiking':[1,2],
                       "entertainment.theme_park":[1,2,3]}
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
        st.write("🌤️ Today is", current_condition)
        df["category"] = df["category"].apply(lambda row: find_category(row, list(categories.keys())))
        df = df[df["category"].notnull()]
        df["category"] = df["category"].astype(str)
        df["category"] = df["category"].str.strip()
        df = df[df["category"].apply(lambda c: condition_index in categories.get(c, []))]
        display_filtered_places(df)

lat=None
lon=None
currnt_temp=None
st.subheader("WeatherX ")
with st.form("location_form"):
    st.subheader("📍 Write your location")
    city = st.text_input("city")
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
                    weather_url = f"http://wttr.in/{lat},{lon}?format=j1"
                    weather_res = req.get(weather_url,verify=False)
                    if weather_res.status_code == 200:
                        weather_data = weather_res.json()
                        current_list =weather_data.get("current_condition", [])
                        if current_list:
                            current = current_list[0]
                            temp = current.get("temp_C", "N/A")
                            humidity = current.get("humidity", "N/A")
                            wind = current.get("windspeedKmph", "N/A")
                            st.markdown(f"**📌 address:** {full_address}")
                            st.markdown("---")
                            col1, col2, col3 = st.columns(3)
                            col1.metric("🌡️ Temp", f"{temp}°C")
                            col2.metric("💧 Humidity", f"{humidity}%")
                            col3.metric("🌬️ Wind", f"{wind} km/h")
                            if temp:
                                currnt_temp = float(temp)
                                st.session_state.lat = lat
                                st.session_state.lon = lon
                                st.session_state.currnt_temp = currnt_temp
                                st.session_state.city = city
lat = st.session_state.get("lat")
lon = st.session_state.get("lon")
currnt_temp = st.session_state.get("currnt_temp")
city = st.session_state.get("city")
if all([lat, lon, currnt_temp]):
    make_data_set_for_features()
    make_table_of_weather()