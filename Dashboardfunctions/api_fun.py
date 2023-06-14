import numpy as np
import pandas as pd
from Dashboardfunctions.sam_fun2 import *


# Main Functions
# ______________________________


def build_api(api_key):
    """
    Need to run this first and save return as youtube
    """
    api_key = api_key
    from googleapiclient.discovery import build
    youtube = build("youtube", "v3", developerKey=api_key)

    return youtube

# Page 1 Functions
# --------------------------------------------
# Pulling data


def pg1_api(youtube, country):
    '''
    Pulls channel data from a country's homepage. Used for PG1 of streamlit dashboard

    '''
    # returns list of channel IDs from country's homepage
    creators = trending_creators_by_country(youtube, country)

    homepage_df = channels_stats(youtube, creators)
    homepage_df = add_emails(homepage_df)

    return homepage_df

# Filtering


def between_subs(df, lower_limit, upper_limit):
    '''
    Takes a lower and upper limit, to finds channels between the two. It is inclusive of both boundaries.

    lower_limit: A number
    upper_limit: A number
    df: channel stats df

    returns filtered version of df
    '''
    filtered_df = df[df['subscriberCount'].between(lower_limit, upper_limit)]
    return filtered_df.reset_index(drop=True)


def categorize_channels(chosen_topics, df):  # TODO: look into this function
    '''
    Takes a list of topics, returns channels that include at least one of specified topics

    chosen_topic: a list of one or more topics
    df: channel stats df

    returns: filtered version of df
    '''
    filtered_df = df[df['topic'].apply(
        lambda x: x is not None and any(word in x for word in chosen_topics))]
    return filtered_df.reset_index(drop=True)


# --------------------------------


# Page 2 functions
def add_emails_sam(youtube, channel_id):
    """
    Inputs a df(e.g. in_stats_df), Returns a new data frame with one more column 'email', 
    which contains email address for the corresponding channel from 'description'; 
    returns NaN if no email address detected.

    Parameter:
    @df: a data frame, such as 'in_stats_df'
    """
    email_list = []
    des = get_1_channel_description(youtube, channel_id)

    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    emails = re.findall(email_regex, des)

    if len(emails) == 0:
        email_list.append(np.nan)
    else:
        delimiter = ', '
        result = delimiter.join(emails)
        email_list.append(result)

    return email_list


def pg2_api(youtube, username):
    '''
    returns data frame of one channel's stats for pg2 of dashboard
    '''
    channel_id = get_channel_id2(youtube, username)
    # all video ids for entire channel
    video_ids = get_videoID_list(youtube, channel_id)
    one_channel_stats = get_video_details(youtube, video_ids)
    one_channel_stats["emails"] = add_emails_sam(
        youtube, channel_id) * len(one_channel_stats)
    one_channel_stats.insert(0, "username", username)
    return one_channel_stats


# ------------------------------------------------

# Helper functions
def get_channel_id2(youtube, channel_title):
    """
    input channel title, output its channel id

    @channel_title: a string for the title of a Youtube channel
   """
    search_response = youtube.search().list(
        q=channel_title,
        part='id',
        type='channel',
        maxResults=1
    ).execute()

    channel_id = search_response['items'][0]['id']['channelId']

    return channel_id


def unique_topics(df):
    """
    Gets all unique (individual) topics from entire data frame (not unique lists of topics)
    """
    lists = list(df["topic"])
    combined_list = [
        item for sublist in lists if sublist is not None for item in sublist]
    unique_topics = list(set(combined_list))
    return unique_topics
