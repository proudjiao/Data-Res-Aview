import streamlit as st
from sam_new_func import sam_fun as sf
from backend import *
from Dashboardfunctions.api_fun import *
import numpy as np
from Dashboardfunctions.viz_fun2 import *
from Dashboardfunctions.metrics_samviz import *

def update_conutry_name():
    pass

with st.sidebar:
    # region country selection dropdown
    country_names = get_country_names()
    default_index = country_names.index('United States')
    if 'country_name' in st.session_state:
        index = country_names.index(st.session_state.country_name)
    else:
        index = default_index
    selected_country_name = st.sidebar.selectbox(
        'Filter channels by countries',
        country_names, index=index, help="Some countries are not supported in YouTube API", on_change=update_conutry_name())
    # endregion

def update_conutry_name():
    st.session_state.country_name = selected_country_name

st.title("AVIEW X DataRes - Analysis of Top Youtube Channels in " + selected_country_name)
st.subheader(
    "By: Anvesha Dutta, Proud Jiao, Eric Huang, Lina Molla, Olivia Wang, Samantha Wong, Tanya Beri")


homepage_df = get_channel_stats(selected_country_name)

# display key metrics for homepage_df
col1, col2 = st.columns(2)
col1.metric(label="Average Views", value=avg_views(homepage_df))
col2.metric(label="Average Subscriber Count", value=avg_subs(homepage_df))
# col3.metric(label="Most Popular Topic", value=top_topics(topics_df(homepage_df))[0])


with st.sidebar:
    # region subscriber slider filter
    min_subs = int(homepage_df['subscriberCount'].min())
    max_subs = int(homepage_df['subscriberCount'].max())
    # st.write("Min subs: ", min_subs, " Max subs: ", max_subs)
    step = int((max_subs-min_subs)/1000)
    subscriber_count = st.slider(
        label="Filter by Subscriber Count",
        min_value=min_subs,
        max_value=max_subs,
        value=(min_subs, max_subs),
        step=step,
        help="This will filter the dataframe by selected range of subscriber count"
    )
    # st.write("You selected: ", subscriber_count)
    # endregion

homepage_df_filtered = between_subs(
    homepage_df, subscriber_count[0], subscriber_count[1])

with st.sidebar:
    options = unique_topics(homepage_df_filtered)
    selected_category = st.multiselect("Filter by category: ", options)
    if len(selected_category) > 0:
        homepage_df_filtered = categorize_channels(selected_category, homepage_df_filtered)



# st.write(homepage_df_filtered)

st.plotly_chart(plot_top_channels_subscribercount(homepage_df_filtered))
st.plotly_chart(plot_top_channels_videocount(homepage_df_filtered))
st.plotly_chart(plot_top_channels_viewcount(homepage_df_filtered))

topic_df = topics_df(homepage_df_filtered)
# st.write(topic_df)

st.session_state.titles = homepage_df["title"]


st.plotly_chart(topic_count_viz_sam(topic_df))
st.plotly_chart(topic_avg_sub_viz_sam(topic_df))
st.plotly_chart(topic_avg_view_viz_sam(topic_df))


csv = convert_df(homepage_df_filtered)

st.download_button(
   "Download Dataframe",
   csv,
   "topYoutubeChannelsIn" + selected_country_name + ".csv",
   "text/csv",
   key='download-csv'
)

st.write(homepage_df_filtered)
