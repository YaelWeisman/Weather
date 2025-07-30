# WeatherX – Smart Weather Dashboard

WeatherX is a web application that analyzes historical weather data, shows current conditions, and recommends nearby places and activities that match the current weather.

 ##What it does
- Analyzes the **last 30 days** of weather using the [Open-Meteo API](https://open-meteo.com/)
- Displays **current weather**: temperature, humidity, wind – via [wttr.in](https://wttr.in).
- Visualizes data:
-Temperature distribution
-Temp ↔ Humidity correlation
-Hourly patterns (average & max)
- Suggests places to go nearby, **tailored to current weather** (restaurants, parks, malls, etc.).
- Integrates with  [Geoapify Places API](https://www.geoapify.com/places-api).


 ##How it works:
The user inputs a **city + country**__
The app geocodes the location using **Geoapify**.__
It fetches weather data and processes it using **pandas**.__
Charts are built using **Seaborn** and **Plotly**.__
Based on current temp, it filters relevant places and displays them as cards__


##Development Highlights:
State management handled with **Streamlit logic** (no heavy backend).
Designed for **clarity and responsiveness** with minimal UI elements
Used **API chaining** and **weather-based filtering** for personalized recommendations.

##[link](https://yaelweisman-weather-main-klvytg.streamlit.app/)

ךןדצך'lli

 ךךן
##ך





