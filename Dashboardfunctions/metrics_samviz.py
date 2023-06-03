import pandas as pd
import plotly.express as px
from Dashboardfunctions.api_fun import *
import streamlit as st

# Overall Metrics


def avg_views(df):
    '''
    Returns average views. Works for both pages of dashboard
    '''
    return round(df["viewCount"].astype(int).mean())


def avg_subs(homepage_df):
    """
    Returns aveerage subscriber count. Only works for page 1
    """
    return round(homepage_df["subscriberCount"].mean())


def top_topics(topic_df):
    '''
    Needs ** topic_df=topics_df(homepage_df) ** to run
    Returns top 10 most popular topics. Only works for page 1
    '''
    st.write(topic_df)
    return topic_df.nlargest(20, ["Number of Channels"])[0:10]["Topic"]


def avg_duration(one_channel_df):
    '''
    Returns average length of a video for a channel
    '''
    return round(one_channel_df["duration(min)"].mean())


def top_vid_avg_duration(one_channel_df):
    '''
    Average length of top 20 videos based on views
    '''
    x = one_channel_df.nlargest(20, ["viewCount"])
    return round(x["duration(min)"].mean())


# Topic visualizations
# Needs to run topic_df = top_topics(homepage_df)
# ----------------------
def topic_count_viz_sam(topic_df):
    '''
    Shows number of channels per topic
    '''
    topic_df = topic_df.nlargest(20, ["Average Subscriber Count"])
    fig = px.bar(topic_df, y="Topic", x="Number of Channels", title="Top 20 Topics based on Appearance on Youtube Trending Page",
                 color="Number of Channels", orientation="h", color_continuous_scale="Agsunset")
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    return fig


def topic_avg_sub_viz_sam(topic_df):
    '''
    Shows number of channels per topic
    '''
    topic_df = topic_df.nlargest(20, ["Average Subscriber Count"])
    fig = px.bar(topic_df, y="Topic", x="Average Subscriber Count", title="Top 20 Topics Based on Average Number of Subscribers",
                 color="Average Subscriber Count", orientation="h", color_continuous_scale="Darkmint")
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    return fig


def topic_avg_view_viz_sam(topic_df):
    '''
    Shows number of channels per topic
    '''
    topic_df = topic_df.nlargest(20, ["Average Channel View Count"])
    fig = px.bar(topic_df, y="Topic", x="Average Channel View Count", title="Top 20 Topics Based on Average Number of Views",
                 color="Average Channel View Count", orientation="h", color_continuous_scale="Viridis")
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    return fig


# Helper Functions
# ----------------------

def topics_df(homepage_df):
    '''
    returns a dataframe with "Topic","Number of Channels","Average Subscriber Count","Average Channel View Count" column. 

    '''
    index = []
    for i in homepage_df["topic"]:
        x = i is not None
        index.append(x)
    topic_counts = homepage_df["topic"][index].explode().value_counts()
    topic_df = pd.DataFrame(
        {"Topic": topic_counts.index, "Number of Channels": topic_counts.values})

    topic_df["Average Subscriber Count"] = topic_df["Topic"].map(
        topic_averages(homepage_df, "subscriberCount"))
    topic_df["Average Channel View Count"] = topic_df["Topic"].map(
        topic_averages(homepage_df, "viewCount"))
    return topic_df


def topic_averages(homepage_df, col):
    '''
    Find averages of all unique topics based on column (subscriberCount or viewCount primarily)
    '''
    avgs = []
    topics = []
    for i in unique_topics(homepage_df):
        mean = round(categorize_channels([i], homepage_df)[col].mean())
        avgs.append(mean)
        topics.append(i)
    dict1 = dict(zip(topics, avgs))
    return dict1
