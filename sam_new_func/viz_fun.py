import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
import pandas as pd
import plotly.express as px
import re
from sam_fun import *
import matplotlib.pyplot as plt
from wordcloud import WordCloud

api_key = "AIzaSyBqgqP0nQ-qP4LJc4_kytQTERSq-pXOff0" # you can change it to your own api 

########## scraping from https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2#AA############
def get_country_code(country_name):
    
    """
    input a country name, output a country code
    """
    url = "https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2#AA"
    page = requests.get(url)

    soup = BeautifulSoup(page.content, "html.parser")

    tables = soup.find_all("table", class_="wikitable")
    dfs = []

    for table in tables:
        rows = table.find_all("tr")
        data = []
        for row in rows:
            cells = row.find_all("td")
            if cells:
                # add the contents of each cell to the data list
                row_data = []
                for cell in cells:
                    row_data.append(cell.get_text().strip())
                data.append(row_data)
        # create a pandas dataframe from the data list and add it to the dfs list
        df = pd.DataFrame(data)
        dfs.append(df)


    countries = dfs[2].iloc[:, 0:2]
    countries = countries.rename(columns={0: 'code', 1: 'country'})
    country_index = countries[countries.country == country_name].index[0]
    country_code = countries.code[country_index]
    
    return country_code
    
###############################################################################
def plot_top_channels(country, column, top_percentile):
    """
    returns a df with top percentile Youtube channels in a specific country:
    
    @country: a string for the name of the country
    @column: a string for the column to define "top"; 
            3 options: 'Subscriber Count', 'View Count', 'Video Count'
    @top_percentile: a double or integer indicating what percentile of creators, 
                    ex 5 is top 5% of creators
    """
    country_code = get_country_code(country) # switch the country name into country code
    if column == 'Subscriber Count':
        df_column = 'subscriberCount'
    elif column == 'View Count':
        df_column = 'viewCount'
    elif column == 'Video Count':
        df_column = 'videoCount'
        
    youtube = build("youtube","v3", developerKey=api_key)
    creator_ids= trending_creators_by_country(youtube, country_code)
    stats_df = channels_stats(youtube, creator_ids)
    stats_df = add_emails(stats_df)
    #top5 = in_stats_df.sort_values(df_column, ascending = False).head(5)
    top_channels_df = top_channels(stats_df, df_column, (100 - top_percentile))
     
    #text_labels = [f'{value}' for value in top5[df_column]] 
    legend_labels = [f'{email}' for email in top_channels_df.emails]
    fig = px.bar(top_channels_df, x = 'title', y = df_column,
            title = 'Top ' + str(top_percentile) + ' Percentile Youtube Channels in\n' + ' ' + 
                 country + ' ' + 'Based on' + ' ' + column,
            hover_data = ['title', 'country', 'viewCount', 'subscriberCount', 'videoCount'],
            color = legend_labels) # text_labels?
    
    fig.update_layout(xaxis_title = 'Channels', yaxis_title= column)
    fig.update_layout(legend_title_text='Legend Title', 
                      legend=dict(title='Emails', x=0, y=-1.2, orientation='h'))
    fig.show()
    
###############################################################################    
    
def get_channel_id(channel_title):
    """
    input channel title, output its channel id
    
    @channel_title: a string for the title of a Youtube channel
    """
    youtube = build('youtube', 'v3', developerKey = api_key)
    search_response = youtube.search().list(
        q=channel_title,
        part='id',
        type='channel',
        maxResults=1
    ).execute()

    channel_id = search_response['items'][0]['id']['channelId']
    
    return channel_id

###############################################################################     
    
def plot_tags_wordcloud(channel_title):
    """
    input a channel title, plot the wordcloud of the tags of the videos in this channel
    
    @channel_title: a string for the title of a Youtube channel
    """
    
    youtube = build('youtube', 'v3', developerKey = api_key)
    channel_id = get_channel_id(channel_title)
    video_id = get_videoID_list(youtube, channel_id)
    df = get_video_details(youtube,video_id)

    tag_lists = df['tags']
    combined_tag_lists = [item for sublist in tag_lists for item in sublist]

    text = ' '.join(combined_tag_lists)

    wordcloud = WordCloud(background_color="white").generate(text)

    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.show()
