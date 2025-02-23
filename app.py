import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Completely", page_icon=":100:")
st.title("Completely 💯")

@st.cache_data
def fetch_user_id(callsign):
    url = f"https://sotl.as/api/activators/{callsign}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('userId')
    return None

@st.cache_data
def fetch_activations(user_id):
    url = f"https://api-db.sota.org.uk/admin/sota_completes_by_id?id={user_id}&desc=0"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return []

callsign = st.text_input("Enter your callsign:").upper()

if callsign:
    user_id = fetch_user_id(callsign)
    if user_id:
        data = fetch_activations(user_id)
        if data:
            df = pd.DataFrame(data)

            # Convert date column to datetime
            df['completed'] = pd.to_datetime(df['completed'])
            df['Year'] = df['completed'].dt.year
            df['Association'] = df['SummitCode'].apply(lambda x: x.split('/')[0])
            df['Region'] = df['SummitCode'].apply(lambda x: x.split('/')[1].split('-')[0])

            # Display total number of completes
            total_completes = len(df)
            st.metric(label="Total Completes", value=total_completes)

            # Bar chart for completes per year
            completes_per_year = df['Year'].value_counts().reset_index()
            completes_per_year.columns = ['Year', 'Completes']
            fig_year = px.bar(completes_per_year, x='Year', y='Completes',
                              text='Completes', labels={'Completes': 'Number of Completes'},
                              title="Completes Per Year")
            fig_year.update_traces(textposition='outside')
            st.plotly_chart(fig_year)

            # Treemap for Association and Region
            df_treemap = df.groupby(['Association', 'Region']).size().reset_index(name='Completes')
            fig_treemap = px.treemap(df_treemap, path=['Association', 'Region'], values='Completes',
                                     title="Completes by Association and Region",
                                     color='Completes', color_continuous_scale='blues')
            st.plotly_chart(fig_treemap)
        else:
            st.warning("No completes found for this callsign.")
    else:
        st.error("Invalid callsign or no user found.")
