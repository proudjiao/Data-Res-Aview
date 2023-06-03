# Visualization functions
# ---------------------
# 1) plot_top_channels_viewcount(homepage_df)

# 2) plot_top_channels_subscribercount(homepage_df)

# 3) plot_top_channels_videocount(homepage_df)

# 4) plot_top_tags_wordcloud(channel_df)

# 5) plot_tag_duration(channel_df)


# from bs4 import BeautifulSoup
from googleapiclient.discovery import build
import plotly.express as px
from sam_new_func.sam_fun import *
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import math


########## scraping from https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2#AA############
# def get_country_code(country_name):
#     """
#     input a country name, output a country code
#     """
#     url = "https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2#AA"
#     page = requests.get(url)

#     soup = BeautifulSoup(page.content, "html.parser")

#     tables = soup.find_all("table", class_="wikitable")
#     dfs = []

#     for table in tables:
#         rows = table.find_all("tr")
#         data = []
#         for row in rows:
#             cells = row.find_all("td")
#             if cells:
#                 # add the contents of each cell to the data list
#                 row_data = []
#                 for cell in cells:
#                     row_data.append(cell.get_text().strip())
#                 data.append(row_data)
#         # create a pandas dataframe from the data list and add it to the dfs list
#         df = pd.DataFrame(data)
#         dfs.append(df)

#     countries = dfs[2].iloc[:, 0:2]
#     countries = countries.rename(columns={0: 'code', 1: 'country'})
#     country_index = countries[countries.country == country_name].index[0]
#     country_code = countries.code[country_index]

#     return country_code


def plot_top_channels_viewcount(homepage_df):
    """
    plot the top youtube channels based on view count

    @homepage_df: homepage_df

    """
    df_column = 'viewCount'

    legend_labels = [f'{email}' for email in homepage_df.emails]
    fig = px.bar(homepage_df, x='title', y=df_column,
                 title='Top Youtube Channels based on View Count',
                 hover_data=['title', 'country', 'viewCount',
                             'subscriberCount', 'videoCount'],
                 color=legend_labels)

    fig.update_layout(xaxis_title='Channels', yaxis_title="View Count")
    fig.update_layout(legend_title_text='Legend Title',
                      legend=dict(title='Emails', x=0, y=-1.2, orientation='h'))
    return fig


def plot_top_channels_subscribercount(homepage_df):
    """
    plot the top youtube channels based on subscriber count

    @homepage_df: a homepage_df

    """
    df_column = 'subscriberCount'

    legend_labels = [f'{email}' for email in homepage_df.emails]
    fig = px.bar(homepage_df, x='title', y=df_column,
                 title='Top Youtube Channels based on Subscriber Count',
                 hover_data=['title', 'country', 'viewCount',
                             'subscriberCount', 'videoCount'],
                 color=legend_labels)

    fig.update_layout(xaxis_title='Channels', yaxis_title="Subscriber Count")
    fig.update_layout(legend_title_text='Legend Title',
                      legend=dict(title='Emails', x=0, y=-1.2, orientation='h'))
    return fig


def plot_top_channels_videocount(homepage_df):
    """
    plot the top youtube channels based on video count

    @homepage_df: a homepage_df

    """
    df_column = 'videoCount'

    legend_labels = [f'{email}' for email in homepage_df.emails]
    fig = px.bar(homepage_df, x='title', y=df_column,
                 title='Top Youtube Channels based on Video Count',
                 hover_data=['title', 'country', 'viewCount',
                             'subscriberCount', 'videoCount'],
                 color=legend_labels)

    fig.update_layout(xaxis_title='Channels', yaxis_title="Video Count")
    fig.update_layout(legend_title_text='Legend Title',
                      legend=dict(title='Emails', x=0, y=-1.2, orientation='h'))
    return fig


###############################################################################

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


def plot_top_tags_wordcloud(channel_df):
    """
    input a channel df, plot the wordcloud of the tags of the videos in this channel

    @channel_df: a df for channel videos
    """

    tag_lists = channel_df['tags']

    text = ' '.join(str(tag) for tag in tag_lists)
    wordcloud = WordCloud(mode='RGBA', margin=0,
                          contour_width=0).generate(text)

    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    return plt

###############################################################################


def convert_duration(durations):
    """
    converts the durations column into minutes

    @durations: the duration column
    """
    minutes_list = []

    for duration in durations:
        # check if duration string is empty
        if not duration:
            minutes_list.append(0)
            continue

        # check if duration string contains 'D', the ones with 'D' considered as an outlier
        if 'D' in duration:
            minutes_list.append(math.nan)
            continue

        duration = duration.strip('PT')  # Remove 'PT'

        # check if the duration string contains valid duration information
        if 'M' not in duration and 'S' not in duration:
            minutes_list.append(0)
            continue

        total_minutes = 0
        hours_index = 0
        minutes_index = 0

        if 'H' in duration:
            hours_index = duration.index('H')
            hours = int(duration[:hours_index])
            total_minutes += hours * 60

        if 'M' in duration:
            minutes_index = duration.index('M')
            if minutes_index > hours_index:  # check if minutes exist
                try:
                    minutes = int(duration[hours_index+1:minutes_index])
                    total_minutes += minutes
                except ValueError:
                    pass

        if 'S' in duration:
            seconds_index = duration.index('S')
            if 'M' in duration and minutes_index > hours_index:
                try:
                    seconds = int(duration[minutes_index+1:seconds_index])
                    total_minutes += seconds / 60
                except ValueError:
                    pass
            elif 'H' in duration:
                try:
                    seconds = int(duration[hours_index+1:seconds_index])
                    total_minutes += seconds / 60
                except ValueError:
                    pass
            else:
                try:
                    seconds = int(duration[:seconds_index])
                    total_minutes += seconds / 60
                except ValueError:
                    pass

        minutes_list.append(round(total_minutes, 2))

    return minutes_list


def plot_tag_duration(channel_df):
    """
    input a channel title, plot the bubble plot of the video duratioin for x axis, view count for y axis, and the number of tags for the size of bubbles

    @channel_df: a df for channel videos
    """

    tag_lists = channel_df['tags']
    tag_len = []
    for tag in tag_lists:
        length = len(tag)
        tag_len.append(length)

    channel_df['tag_len'] = tag_len
    channel_df['du_min'] = convert_duration(channel_df['duration'])

    channel_df = channel_df[channel_df['du_min'] < 200]  # exclude outliers
    tag_view_du = channel_df.groupby(
        'tag_len')[['viewCount', 'du_min']].aggregate(np.median).reset_index()
    tag_view_du = tag_view_du.rename(columns={"(  'tag_len',       '')": 'tag_len',
                                              "('viewCount',   'mean')": 'view_mean',
                                              "('viewCount', 'median')": 'view_median',
                                              "(   'du_min',   'mean')": 'du_mean',
                                              "(   'du_min', 'median')": 'du_median'})

    fig = px.scatter(tag_view_du,
                     x="du_min",
                     y="viewCount",
                     size="tag_len",
                     hover_name="tag_len", size_max=30)
    fig.update_traces(
        hovertemplate='%{hovertext} tags<br>Median View Count: %{y}')
    fig.update_layout(xaxis_title="Median Duration (min)",
                      yaxis_title="Median View Count",
                      title="Duration V.S. The number of tags",
                      plot_bgcolor='black')
    return fig
