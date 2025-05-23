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

def fetch_activations(user_id):
    url = f"https://api-db2.sota.org.uk/logs/completes/{user_id}"
    # url = f"https://api-db.sota.org.uk/admin/sota_completes_by_id?id={user_id}&desc=0"
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
            df['completed'] = pd.to_datetime(df['completed']).dt.strftime('%Y-%m-%d')
            df['Year'] = pd.to_datetime(df['completed']).dt.year
            df['Association'] = df['SummitCode'].apply(lambda x: x.split('/')[0])
            df['Region'] = df['SummitCode'].apply(lambda x: x.split('/')[1].split('-')[0])

            # Display total number of completes
            total_completes = len(df)
            st.metric(label="Total Completes", value=total_completes)

            # Bar chart for completes per year
            completes_per_year = df['Year'].value_counts().reset_index().sort_values('Year')
            completes_per_year.columns = ['Year', 'Completes']
            st.bar_chart(completes_per_year.set_index('Year'))

            # Treemap for Association and Region
            df_treemap = df.groupby(['Association', 'Region'], as_index=False)['SummitCode'].count()
            df_treemap.rename(columns={'SummitCode': 'Completes'}, inplace=True)
            fig_treemap = px.treemap(df_treemap, path=['Association', 'Region'], values='Completes',
                                     title="Completes by Association and Region",
                                     color='Completes', color_continuous_scale='blues',
                                     custom_data=['Completes'])
            fig_treemap.update_traces(hovertemplate="Completes: %{value}")
            st.plotly_chart(fig_treemap)

            # Table of summits and complete dates
            df_sorted = df[['SummitCode', 'Name', 'completed']].sort_values('completed', ascending=False)
            df_sorted.columns = ['Summit Code', 'Summit Name', 'Date Completed']

            st.subheader("Summits and Complete Dates")
            st.dataframe(df_sorted, hide_index=True)
        else:
            st.warning("No completes found for this callsign.")
    else:
        st.error("Invalid callsign or no user found.")
