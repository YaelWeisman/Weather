from sys import flags

import requests as req
import streamlit as st
import  datetime as dt
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: "Segoe UI", sans-serif;
    direction: ltr;
}
hr {
    border: none;
    border-top: 1px solid #eee;
    margin: 1rem 0;
}
.site-title {
    text-align: center;
    font-size: 36px;
    font-weight: bold;
    color: #FF7043;
    margin-bottom: 10px;
    padding-bottom: 5px;
    border-bottom: 3px solid #42A5F5;
}
.metric-container {
    text-align: center;
    padding: 10px;
    background-color: #f2f9ff;
    border-radius: 12px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    margin-bottom: 10px;
}
.metric-label {
    font-size: 16px;
    color: #333;
}
.metric-value {
    font-size: 24px;
    font-weight: bold;
    color: #FF7043;
}
.section-title {
    font-size: 20px;
    font-weight: bold;
    color: #42A5F5;
    text-align: center;
    margin-top: 20px;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='site-title'>WeatherX</div>", unsafe_allow_html=True)

def find_category(cat_list1,cat_list2):
    for c in cat_list1:
        if c in cat_list2:
            return c
    return None

def display_filtered_places(df):
    if df.empty:
        st.warning("😕 No matching places found.")
    else:
        for _, row in df.iterrows():
            st.markdown(f"""
                <div style='border:1px solid #ccc; border-radius:10px; padding:15px; margin:10px 0; background-color:#e6f7ff;'>
                    <h4 style='margin:0;'>📍 {row['name']}</h4>
                    <p style='margin:0;'><strong>📌 Address:</strong> {row['address']} | {row['city']}</p>
                    <p style='margin:0;'><strong>🔗 Distance:</strong> {int(row['distance'])} meters</p>
                    <p style='margin:0;'><strong>🏷️ Category:</strong> {row['category']}</p>
                    {f'<p style="margin:0;"><a href="{row["link"]}" target="_blank">🌐 Website</a></p>' if pd.notnull(row["link"]) else ''}
                </div>
                """, unsafe_allow_html=True)


def make_table_of_weather(lon ,lat):
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
    if res.status_code != 200:
        st.error("⚠️ Failed to fetch weather history data.")
        return
    res=res.json()
    datetime = res.get("hourly", {}).get("time", [])
    temp = res.get("hourly", {}).get("temperature_2m", [])
    humidity = res.get("hourly", {}).get("relative_humidity_2m", [])
    wind = res.get("hourly", {}).get("windspeed_10m", [])
    precipitation = res.get("hourly", {}).get("precipitation", [])
    data = []
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
    if(data):
        df=df[df.temp.notnull()]
        df=df[["temp","humidity","wind","datetime"]]
        df=df.set_index("datetime")
        df.index = pd.to_datetime(df.index).tz_localize("UTC").tz_convert("Asia/Jerusalem")
        df["hour"] = df.index.hour
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("<div class='section-title'>Temperature Distribution</div>", unsafe_allow_html=True)
            # הגדלנו את height כדי לתת לגרף יותר מקום בעמודה
            fig = sns.displot(x='temp', data=df, kde=True, color="#FF7043", height=4, aspect=1.2)
            st.pyplot(fig.figure)
            plt.close(fig.figure)

        with col2:
            st.markdown("<div class='section-title'>Temp vs Humidity</div>", unsafe_allow_html=True)
            fig2 = sns.lmplot(x="temp", y="humidity", data=df, height=4, aspect=1.2,
                              line_kws={"color": "#42A5F5"})  # שיניתי צבע ל-line_kws
            st.pyplot(fig2.figure)
            plt.close(fig2.figure)

        with col3:
            st.markdown("<div class='section-title'>Hourly Temp</div>", unsafe_allow_html=True)
            fig3, ax3 = plt.subplots(figsize=(6, 4))
            sns.scatterplot(x="hour", y="temp", data=df, color="#FF7043", alpha=0.3, ax=ax3)
            sns.lineplot(x="hour", y="temp", data=df, estimator='mean', color="black", ax=ax3)
            sns.lineplot(x='hour', y='temp', data=df, estimator='max', color="blue", ax=ax3)
            ax3.set_xticks(range(0, 24, 2))
            ax3.set_xlabel("Hour")
            ax3.set_ylabel("Temp (°C)")
            st.pyplot(fig3)
            plt.close(fig3)

        st.markdown("---")
        st.markdown("<div class='section-title'>🌡️ Temperature & Humidity Over Time</div>",
                    unsafe_allow_html=True)

        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(x=df.index, y=df["temp"], mode='lines', name='Temp (°C)', line=dict(color='#FF7043')))
        fig4.add_trace(
            go.Scatter(x=df.index, y=df["humidity"], mode='lines', name='Humidity (%)', line=dict(color='#42A5F5'),
                       yaxis="y2"))
        fig4.update_layout(
            title_text="",
            xaxis=dict(title="Date & Time"),
            yaxis=dict(title="Temp (°C)", side='left'),
            yaxis2=dict(title="Humidity (%)", overlaying='y', side='right'),
            legend=dict(x=0.01, y=0.99),
            hovermode="x unified",
            height=500,
            margin=dict(l=40, r=40, t=40, b=40)
        )
        st.plotly_chart(fig4, use_container_width=True)  #

def make_data_set_for_features(lon,lat,currnt_temp):
    currnt_temp=float(currnt_temp)
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
    if response_around.status_code != 200:
        st.error("⚠️ Failed to fetch location data.")
        return
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
            address=f"{properties.get('address_line1','')} "
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
    st.info(f"🌤️ Today is {current_condition}")
    df["category"] = df["category"].apply(lambda row: find_category(row, list(categories.keys())))
    df = df[df["category"].notnull()]
    df["category"] = df["category"].astype(str)
    df["category"] = df["category"].str.strip()
    df = df[df["category"].apply(lambda c: condition_index in categories.get(c, []))]
    display_filtered_places(df)


lat = lon = currnt_temp = None
#form_submitted = False

with st.form("location_form"):
    city = st.text_input("City")
    country = st.text_input("Country", value="Israel")
    submitted = st.form_submit_button("Check Weather")
    if submitted and city and country:
            #form_submitted = True
            full_address = f"{city}, {country}"
            loc_url = f"https://api.geoapify.com/v1/geocode/search?text={full_address}&lang=en&format=json&apiKey=2d6acf0f3338413992829d14fa69ffdf"
            res = req.get(loc_url, verify=False)
            if res.status_code == 200 and res.json().get("results"):
                result = res.json()["results"][0]
                lat, lon = result.get("lat"), result.get("lon")
                if lat and lon:
                    weather_url = f"http://wttr.in/{lat},{lon}?format=j1"
                    weather_res = req.get(weather_url, verify=False)
                    if weather_res.status_code ==200:
                        current = weather_res.json().get("current_condition", [{}])[0]
                        temp = current.get("temp_C", "N/A")
                        humidity = current.get("humidity", "N/A")
                        wind = current.get("windspeedKmph", "N/A")
                        now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
                        st.markdown(f"""
                        <div style='text-align:center; font-size:16px;'>
                            📌 <strong>Address:</strong> {full_address}<br>
                            🕒 <strong>As of:</strong> {now}
                        </div><hr>
                        """, unsafe_allow_html=True)
                        col1, col2, col3 = st.columns(3)
                        col1.markdown(f"""<div class='metric-container'><div class='metric-label'>🌡️ Temp</div><div class='metric-value'>{temp}°C</div></div>""", unsafe_allow_html=True)
                        col2.markdown(f"""<div class='metric-container'><div class='metric-label'>💧 Humidity</div><div class='metric-value'>{humidity}%</div></div>""", unsafe_allow_html=True)
                        col3.markdown(f"""<div class='metric-container'><div class='metric-label'>🌬️ Wind</div><div class='metric-value'>{wind} km/h</div></div>""", unsafe_allow_html=True)
                        st.session_state.lat = lat
                        st.session_state.lon = lon
                        st.session_state.currnt_temp = temp
                        st.session_state.weather_ready = True


if st.session_state.get("weather_ready") and all([st.session_state.lat,st.session_state.lon,st.session_state.currnt_temp]):
    with st.form("recommend_form"):
        make_table_of_weather(st.session_state.lon, st.session_state.lat)
        click = st.form_submit_button("🌤️ Show recommended places based on current weather")
        if click:
            make_data_set_for_features(st.session_state.lon, st.session_state.lat,st.session_state.currnt_temp)