import pycountry
import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from Dashboardfunctions.api_fun import *
from Dashboardfunctions.sam_fun2 import *

# region All Page Functions


@st.cache_data
def setup_and_getKey():
    """
    Loads the API key from the .env file and returns the YouTube API key
    Page used: All pages
    """
    api_key = st.secrets["YOUTUBE_API_KEY"]
    try:
        youtube = build("youtube", "v3", developerKey=api_key)
        return youtube
    except Exception as e:
        st.error("Error building youtube object: ", e)
        st.stop()


@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

# endregion

# region Home Page Functions


@st.cache_data
def get_country_code(country_name):
    """
    Returns the country code for a given country name
    For example, get_country_code('United States') returns 'US'
    Page used: Home Page
    """
    try:
        country = pycountry.countries.get(name=country_name)
        if country is not None:
            return country.alpha_2
        else:
            return None
    except LookupError:
        return None


@st.cache_data
def get_country_names():
    """
    Returns a list of country names (for pupulating dropdown menu)
    For example, get_country_names() returns ['Afghanistan', 'Albania', 'Algeria', ...]
    Page used: Home Page
    """
    country_names = []
    for country in pycountry.countries:
        country_names.append(country.name)
    return sorted(country_names)


@ st.cache_data
def get_channel_stats(country_name):
    country = get_country_code(country_name)
    youtube = setup_and_getKey()
    try:
        homepage_df = pg1_api(youtube, country)
        return homepage_df
    except HttpError as e:
        if e.resp.status == 400:
            st.write(country_name, " is not currently supported.")
        if e.resp.status == 403:
            st.write(
                "API key quota exceeded. Please wait or upgrade your API key.")
        st.stop()
    except Exception as e:
        st.error("Error: " + e)
        st.stop()


@st.cache_data
def get_video_stats(country_name):
    country = get_country_code(country_name)
    youtube = setup_and_getKey()
    try:
        videos_df = trending_videos_by_country(youtube, country)
        return videos_df
    except HttpError as e:
        if e.resp.status == 400:
            st.write(country_name, " is not currently supported.")
        if e.resp.status == 403:
            st.write(
                "API key quota exceeded. Please wait or upgrade your API key.")
        st.stop()
    except Exception as e:
        st.error("Error: " + e)
        st.stop()
    # endregion


@st.cache_data
def get_video_metrics(video_df):
    return trending_videos_metrics(video_df)

# region Page 2 Functions


@st.cache_data
def get_channel_specfic_stats(channel_name):
    """
    Returns a dataframe of channel specific stats
    """
    youtube = setup_and_getKey()
    if channel_name == "":
        st.error("Please enter a channel name")
        st.stop()
    try:
        channel_specfic_stats = pg2_api(youtube, channel_name)
        if channel_specfic_stats.empty:
            st.error("Channel " + channel_name + " not found")
            st.stop()
        return channel_specfic_stats
    except HttpError as e:
        if e.resp.status == 403:
            st.error(
                "API key quota exceeded. Please wait or upgrade your API key.")
        st.stop()
    except Exception as e:
        st.error("Error: " + e)
        st.stop()
# endregion
