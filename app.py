
import streamlit as st
import pandas as pd

from services.air_quality import (
    get_coordinates,
    get_air_quality
)

from services.ai_assistant import ask_gemini


# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Urban Air Quality Assistant",
    page_icon="🌍",
    layout="wide"
)


# --------------------------------------------------
# 2. SESSION STATE
# --------------------------------------------------

if "air_data" not in st.session_state:
    st.session_state.air_data = None

if "location" not in st.session_state:
    st.session_state.location = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# --------------------------------------------------
# 3. AQI CLASSIFICATION
# --------------------------------------------------

def get_aqi_status(aqi):

    if aqi <= 50:
        return "Good"

    elif aqi <= 100:
        return "Moderate"

    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups"

    elif aqi <= 200:
        return "Unhealthy"

    elif aqi <= 300:
        return "Very Unhealthy"

    else:
        return "Hazardous"


def get_health_advice(aqi):

    if aqi <= 50:
        return (
            "Air quality is good. Most people can enjoy "
            "normal outdoor activities."
        )

    elif aqi <= 100:
        return (
            "Air quality is acceptable. Unusually sensitive "
            "people may consider reducing prolonged "
            "outdoor exertion."
        )

    elif aqi <= 150:
        return (
            "Sensitive groups, including children, older "
            "adults and people with respiratory conditions, "
            "should reduce prolonged outdoor exertion."
        )

    elif aqi <= 200:
        return (
            "Everyone may begin to experience health effects. "
            "Reduce prolonged outdoor exertion and consider "
            "moving exercise indoors."
        )

    elif aqi <= 300:
        return (
            "Health alert: Everyone may experience more "
            "serious health effects. Avoid outdoor exertion "
            "and reduce exposure."
        )

    else:
        return (
            "Health emergency: Avoid outdoor activities "
            "and remain in a cleaner indoor environment."
        )


# --------------------------------------------------
# 4. SIDEBAR NAVIGATION
# --------------------------------------------------

st.sidebar.title("🌍 Navigation")

page = st.sidebar.selectbox(
    "Select a section",
    [
        "Dashboard",
        "Air Quality Analysis",
        "AI Assistant",
        "Health Recommendations"
    ]
)

st.sidebar.divider()

st.sidebar.info(
    "An AI-powered platform for monitoring "
    "urban air pollution."
)

st.sidebar.caption(
    "Data source: Open-Meteo Air Quality API"
)


# --------------------------------------------------
# 5. APPLICATION HEADER
# --------------------------------------------------

st.title("🌍 Urban Air Quality Assistant")

st.subheader(
    "Monitor Air Pollution. Breathe Smarter."
)

st.write(
    "An intelligent platform for monitoring urban "
    "air quality and understanding pollution levels."
)

st.divider()


# --------------------------------------------------
# 6. DASHBOARD
# --------------------------------------------------

if page == "Dashboard":

    st.header("📊 Air Quality Dashboard")

    city = st.text_input(
        "Enter your city",
        value="Jaipur",
        placeholder="Example: Jaipur, Mumbai, Delhi"
    )

    if st.button("Check Air Quality", type="primary"):

        if not city.strip():

            st.warning("Please enter a city name.")

        else:

            try:

                with st.spinner(
                    "Fetching air quality information..."
                ):

                    location = get_coordinates(city.strip())

                    if not location:

                        st.error(
                            "City not found. Please try another city."
                        )

                    else:

                        air_data = get_air_quality(
                            location["latitude"],
                            location["longitude"]
                        )

                        if (
                            not air_data
                            or air_data.get("us_aqi") is None
                        ):

                            st.error(
                                "Air quality data is currently unavailable."
                            )

                        else:

                            st.session_state.air_data = air_data
                            st.session_state.location = location

                            st.success(
                                f"Air quality data retrieved for "
                                f"{location['name']}, "
                                f"{location['country']}!"
                            )

            except Exception as e:

                st.error(
                    f"Unable to retrieve air quality data: {e}"
                )

    # Display previously fetched data

    if st.session_state.air_data:

        data = st.session_state.air_data
        location = st.session_state.location

        aqi = float(data["us_aqi"])
        status = get_aqi_status(aqi)

        st.divider()

        st.subheader(
            f"Current Air Quality – {location['name']}"
        )

        st.caption(
            f"Measurement time: {data.get('time', 'Unavailable')} "
            "| Timezone: {data.get('timezone', 'Local API time')}"
        )

        # AQI information

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "US Air Quality Index",
                f"{aqi:.0f}"
            )

        with col2:

            st.metric(
                "Air Quality Status",
                status
            )

        st.progress(
            min(aqi / 500, 1.0)
        )

        st.info(
            get_health_advice(aqi)
        )

        st.divider()

        # Pollutant measurements

        st.subheader("🧪 Pollutant Measurements")

        pollutants = [
            ("PM2.5", "pm2_5"),
            ("PM10", "pm10"),
            ("Carbon Monoxide", "carbon_monoxide"),
            ("Nitrogen Dioxide", "nitrogen_dioxide"),
            ("Ozone", "ozone")
        ]

        for start in range(0, len(pollutants), 3):

            cols = st.columns(3)

            for col, (label, key) in zip(
                cols,
                pollutants[start:start + 3]
            ):

                value = data.get(key)

                with col:

                    if value is not None:

                        st.metric(
                            label,
                            f"{float(value):.1f} µg/m³"
                        )

                    else:

                        st.metric(
                            label,
                            "Unavailable"
                        )

        st.divider()

        # Pollution chart

        st.subheader("📈 Pollution Comparison")

        chart_data = pd.DataFrame([
            {
                "Pollutant": label,
                "Concentration (µg/m³)": float(data[key])
            }
            for label, key in pollutants
            if data.get(key) is not None
        ])

        if not chart_data.empty:

            st.bar_chart(
                chart_data.set_index("Pollutant"),
                y="Concentration (µg/m³)"
            )

            st.caption(
                "Note: Pollutants have different health thresholds. "
                "Their raw concentrations should not be interpreted "
                "as directly comparable toxicity levels."
            )

        st.caption(
            "Source: Open-Meteo Air Quality API. "
            "Values are modelled estimates, not necessarily "
            "physical monitoring station measurements."
        )

    else:

        st.info(
            "Enter a city and click Check Air Quality "
            "to retrieve its pollution information."
        )


# --------------------------------------------------
# 7. AIR QUALITY ANALYSIS
# --------------------------------------------------

elif page == "Air Quality Analysis":

    st.header("📈 Air Quality Analysis")

    if st.session_state.air_data:

        data = st.session_state.air_data

        location = st.session_state.location

        st.subheader(
            f"Pollution Analysis – {location['name']}"
        )

        aqi = float(data["us_aqi"])

        st.metric(
            "Current US AQI",
            f"{aqi:.0f}",
            get_aqi_status(aqi)
        )

        analysis_data = {
            "PM2.5": data.get("pm2_5"),
            "PM10": data.get("pm10"),
            "Carbon Monoxide": data.get("carbon_monoxide"),
            "Nitrogen Dioxide": data.get("nitrogen_dioxide"),
            "Ozone": data.get("ozone")
        }

        df = pd.DataFrame(
            list(analysis_data.items()),
            columns=["Pollutant", "Concentration"]
        )

        df = df.dropna()

        st.subheader("Pollutant Concentration")

        st.bar_chart(
            df.set_index("Pollutant")
        )

        st.subheader("Detailed Measurements")

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.warning(
            "Please fetch air quality data from the Dashboard first."
        )


# --------------------------------------------------
# 8. GEMINI AI ASSISTANT
# --------------------------------------------------

elif page == "AI Assistant":

    st.header("🤖 AI Air Quality Assistant")

    st.write(
        "Ask questions about pollution, AQI, "
        "air quality and health precautions."
    )

    if st.session_state.air_data:

        location = st.session_state.location

        st.success(
            f"Connected to air quality data for "
            f"{location['name']}, {location['country']}."
        )

    else:

        st.info(
            "You can ask general air-quality questions. "
            "For location-specific answers, fetch city data "
            "from the Dashboard first."
        )

    st.divider()

    # Clear chat button

    if st.button("🗑️ Clear Chat"):

        st.session_state.chat_history = []

        st.rerun()

    # Display chat history

    for message in st.session_state.chat_history:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

    # User question

    question = st.chat_input(
        "Ask something about air quality..."
    )

    if question:

        st.session_state.chat_history.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):

            st.markdown(question)

        # Prepare air quality context

        context = None

        if st.session_state.air_data:

            context = {
                "city": st.session_state.location["name"],
                "country": st.session_state.location["country"],
                **st.session_state.air_data
            }

        # Generate AI response

        with st.chat_message("assistant"):

            with st.spinner(
                "Gemini AI is thinking..."
            ):

                answer = ask_gemini(
                    question,
                    context
                )

                st.markdown(answer)

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": answer
        })


# --------------------------------------------------
# 9. HEALTH RECOMMENDATIONS
# --------------------------------------------------

elif page == "Health Recommendations":

    st.header("💚 Health Recommendations")

    st.write(
        "Understand how air pollution can affect "
        "your health and learn ways to reduce exposure."
    )

    if st.session_state.air_data:

        data = st.session_state.air_data

        location = st.session_state.location

        aqi = float(data["us_aqi"])

        st.subheader(
            f"Health Advisory – {location['name']}"
        )

        st.metric(
            "Current US AQI",
            f"{aqi:.0f}",
            get_aqi_status(aqi)
        )

        st.warning(
            get_health_advice(aqi)
        )

    else:

        st.info(
            "Fetch air quality data from the Dashboard "
            "to see a location-specific advisory."
        )

    st.divider()

    st.subheader("General Precautions")

    st.markdown("""
    **1. Outdoor activities**
    - Check air quality before exercising outdoors.
    - Reduce intense outdoor exercise when pollution is high.
    - Prefer indoor workouts on heavily polluted days.

    **2. Protect sensitive groups**
    - Children and older adults should take extra precautions.
    - People with asthma or heart and lung conditions should
      follow their healthcare professional's advice.

    **3. Improve indoor air quality**
    - Keep windows closed when outdoor pollution is high.
    - Use an appropriate HEPA air purifier if available.
    - Avoid indoor smoking and unnecessary burning.

    **4. Personal protection**
    - Consider a well-fitting N95 or equivalent respirator
      when exposure to fine particulate pollution is high.
    - Ordinary cloth masks offer limited protection against PM2.5.

    **5. Stay informed**
    - Monitor local air quality updates.
    - Follow official public-health advisories.
    """)

    st.caption(
        "These recommendations are general educational guidance "
        "and are not a substitute for medical advice."
    )


# --------------------------------------------------
# 10. FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "🌍 Urban Air Quality Assistant | "
    "Powered by Open-Meteo and Google Gemini AI"
)

st.caption(
    "Air quality information is modelled and may differ "
    "from local monitoring station measurements."
)
