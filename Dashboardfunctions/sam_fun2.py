# Important functions
# ---------------------
# 1) trending_creators_by_country(youtube, country): Gets list of creator IDs of creators who had a video on selected country's trending page

# 2) channels_stats(youtube,channel_ids): gets ["title","country","viewCount","subscriberCount","videoCount"], for all channels given in a list of channel_ids

# 3) top_channels(df,column,percentile): indexes top percent of creators. percentile = 95 means top 5% of creators. column is what metric you base percentile off of

# 4) get_videoID_list(youtube, channel_id): gets all unique video ids from a single channel, aka all their videos

# 5) get_video_details(youtube,video_list): takes in video ids and returns a dataframe with video stats["title", "published", "description", "tags", "viewCount", "dislikeCount", "commentCount"]


import pandas as pd
import numpy as np
import re


def trending_creators_by_country(youtube, country):
    '''
    Gets list of creator IDs of creators who had a video on selected country's trending page
    Returns more than 50 entries

    country: country of the trending page you want to access
        - To find code:
        - https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2 

    returns: list of channel IDs 

    '''
    channel_list = []
    request = youtube.videos().list(
        part="snippet,contentDetails",
        chart="mostPopular",
        regionCode=country,
        maxResults=50
    )
    next_page = True
    pages = 0
    while next_page:
        response = request.execute()
        data = response["items"]

        for video in data:
            channel_id = video["snippet"]["channelId"]
            if channel_id not in channel_list:
                channel_list.append(channel_id)
        if "nextPageToken" in response.keys():
            next_page = True
            request = youtube.videos().list(
                part="snippet, contentDetails",
                chart="mostPopular",
                regionCode=country,
                maxResults=50,
                pageToken=response['nextPageToken']
            )
        else:
            next_page = False
    return channel_list


def channel_items(youtube, channel_id):
    '''
    Gets "items" from channel_id

    Contains playlist id, so you can access all a creator's video id with
    get_videoID_list
    '''
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics,topicDetails,status",
        id=channel_id
    )
    response = request.execute()

    # get only stats from"items" key
    return response['items']


def stats_loc_name(response_items):
    '''
    Uses response['items'] for a channel to pull out view count, subscriber count, video count, user name of channel, and location of creator

    channel_stats: return object from get_channel_stats
    '''

    viewCount = pd.to_numeric(
        response_items[0]["statistics"].get("viewCount", 0))
    subscriberCount = pd.to_numeric(
        response_items[0]["statistics"].get("subscriberCount", 0))
    videoCount = pd.to_numeric(
        response_items[0]["statistics"].get("videoCount", 0))
    country = response_items[0]["snippet"].get("country", None)
    title = response_items[0]["snippet"].get("title", None)

    try:
        topic = response_items[0]['topicDetails'].get('topicCategories', 0)
    except:
        topic = 0
    return title, country, viewCount, subscriberCount, videoCount, topic


def get_1_channel_stats(youtube, channel_id):
    '''
    Gets list of items from youtube api for 1 channel
    '''
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics,topicDetails,status",
        id=channel_id
    )
    response = request.execute()

    # get only stats from"items" key
    return stats_loc_name(response['items'])


def get_1_channel_description(youtube, channel_id):
    '''
    Gets description from youtube api for 1 channel
    '''
    request = youtube.channels().list(
        part="snippet,brandingSettings",
        id=channel_id
    )
    response = request.execute()

    # get only stats from"items" key

    # x = response['items'][0]
    x = response['items'][0]["snippet"].get("description", 0)
    return x


def channels_stats(youtube, channel_ids):
    '''
    loops through list of channel ids to get channel stats and append to dataframe
    '''
    des = []
    all_data = []
    for channel_id in channel_ids:
        z = stats_loc_name(channel_items(youtube, channel_id))
        all_data.append(z)
        des.append(get_1_channel_description(youtube, channel_id))
    df = pd.DataFrame(all_data, columns=[
                      "title", "country", "viewCount", "subscriberCount", "videoCount", "topic"])
    df["description"] = des
    df["channel_id"] = channel_ids
    df["topic"] = df["topic"].apply(rid_url)
    return df


def rid_url(urls):
    prefix = 'https://en.wikipedia.org/wiki/'
    new_urls = []
    if urls == 0:
        return None
    else:
        for url in urls:
            # check if the URL is NaN, and skip it if it is
            new_urls.append(url.replace(prefix, ''))
    return new_urls


def top_channels(df, column, percentile):
    '''
    filters dataframe of channel_stats to get top percentile based off a 
    column (viewCount,subscriberCount, or videoCount)

    df: channel_stats dataframe
    column: which column / stat you want to base percentile off of
    percentile: what percentile of creators, ex 95 is top 5% of creators
    '''
    num = np.percentile(pd.to_numeric(df[column]), percentile)
    return df[df[column] >= num].reset_index(drop=True)


def get_videoID_list(youtube, channel_id):
    '''
    Grabs unique ID for every video on a channel

    youtube: youtube API build()
   channel_id: unique ID for playlist of every video on channel

    Returns:list of unique ID of
    '''
    upload_id = channel_items(youtube, channel_id)[
        0]["contentDetails"]["relatedPlaylists"]["uploads"]

    video_list = []
    request = youtube.playlistItems().list(
        part="snippet,contentDetails",
        playlistId=upload_id,
        maxResults=50  # most results you can get on one page from API is 50
    )
    next_page = True  # when False means no more pages

    while next_page:  # as long as next_page is true, it will keep searching for results
        response = request.execute()
        data = response['items']

        for video in data:
            # for each video result, look into content details then in that get video ID
            video_id = video["contentDetails"]["videoId"]
            if video_id not in video_list:
                video_list.append(video_id)
        if "nextPageToken" in response.keys():  # if in JSON theres a nextPageToken, it means there are more responses
            next_page = True
            request = youtube.playlistItems().list(
                part="snippet,contentDetails",
                playlistId=upload_id,
                maxResults=50,
                # gets next page of results
                pageToken=response['nextPageToken']
            )
        else:
            next_page = False  # exits the while loop
    return video_list


def get_video_details(youtube, video_list):
    '''
    Grabs data for all videos in a channel

    youtube: youtube API build()
    video_list: list containing all unique video IDs of data you want to grab

    returns: a list of dictionaries, each dictionary contains stats for a unique video

    '''
    stats_list = []
    all_stats = []
    # because YT only lets you grab 50 videos at a time
    # need to jump 0-49, 50-99 etc (count by 50)

    for i in range(0, len(video_list), 50):
        request = youtube.videos().list(
            part="snippet,contentDetails,status,statistics",
            id=video_list[i:i+50]  # non inclusive, will grab 0-49
        )

        data = request.execute()

        for video in data["items"]:

            title = video["snippet"]['title']
            published = video['snippet']['publishedAt']
            description = video['snippet']['description']
            # how many tags video has bc 'tags' is a list
            tags = video["snippet"].get('tags', [])
            postingDate = video['snippet'].get('publishedAt', None)
            description = video['snippet'].get('description', None)

            # .get ensures that if the info is unavailable (private etc), it won't throw an error, but put 0
            viewCount = video["statistics"].get("viewCount", 0)
            likeCount = video["statistics"].get("likeCount", 0)
            # dislike count is always private to public I think
            dislikeCount = video["statistics"].get("dislikeCount", "private")
            commentCount = video["statistics"].get("commentCount", 0)

            duration = video["contentDetails"].get("duration", 0)

            made_for_kids = video['status'].get('madeForKids', None)

            # makes dictionary for each video with stas
            stats_dictionary = dict(title=title,
                                    published=published,
                                    description=description,
                                    tags=tags,
                                    viewCount=viewCount,
                                    likeCount=likeCount,
                                    dislikeCount=dislikeCount,
                                    commentCount=commentCount,
                                    duration=duration,
                                    postingDate=postingDate,


                                    )
            stats_list.append(stats_dictionary)
            return_df = pd.DataFrame(stats_list)
            return_df.insert(9, "duration(min)",
                             duration_min(return_df["duration"]))
            return_df["viewCount"] = return_df["viewCount"].astype(int)
    return return_df


def add_emails(df):
    """
    Inputs a df(e.g. in_stats_df), Returns a new data frame with one more column 'email', 
    which contains email address for the corresponding channel from 'description'; 
    returns NaN if no email address detected.

    Parameter:
    @df: a data frame, such as 'in_stats_df'
    """
    email_list = []
    des = df['description']
    length = df.shape[0]

    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    for i in range(length):
        emails = re.findall(email_regex, des[i])

        if len(emails) == 0:
            email_list.append(np.nan)
        else:
            delimiter = ', '
            result = delimiter.join(emails)
            email_list.append(result)

    df['emails'] = email_list

    return df


def get_channel_id(channel_title):
    """
    input channel title, output its channel id

    @channel_title: a string for the title of a Youtube channel
    """
    youtube = build('youtube', 'v3', developerKey=api_key)
    search_response = youtube.search().list(
        q=channel_title,
        part='id',
        type='channel',
        maxResults=1
    ).execute()

    channel_id = search_response['items'][0]['id']['channelId']

    return channel_id


def duration_min(duration_list):
    durations = []
    for duration_string in duration_list:
        minutes_match = re.search(r"(\d+)M", duration_string)
        seconds_match = re.search(r"(\d+)S", duration_string)

        minutes = int(minutes_match.group(1)) if minutes_match else 0
        seconds = int(seconds_match.group(1)) if seconds_match else 0
        # Convert minutes and seconds to total minutes
        total_minutes = minutes + seconds / 60

        durations.append(total_minutes)

    return durations
