import streamlit as st
from backend import *
from Dashboardfunctions.api_fun import *
from Dashboardfunctions.lina_viz2 import *
from Dashboardfunctions.viz_fun2 import *
from Dashboardfunctions.metrics_samviz import *
# from Dashboardfunctions.sam_fun2 import *

# st.set_page_config(layout="wide")
youtube = setup_and_getKey()


def update_session_state():
    pass


# Create an input box on the sidebar for YouTube channel name
with st.sidebar:
    if 'channel_name' in st.session_state:
        default_channel_name = st.session_state.channel_name
    else:
        default_channel_name = 'MrBeast'
    channel_name = st.text_input(
        "Enter YouTube Channel Name", value=default_channel_name, on_change=update_session_state())


def update_session_state():
    st.session_state.channel_name = channel_name


st.title("AVIEW X DataRes - Channel Specific Statistics")

channel = get_channel_specfic_stats(channel_name)

col1, col2, col3 = st.columns(3)
col1.metric(label="Channel", value=channel_name)
col2.metric(label="Average duration for top videos (min)",
            value=top_vid_avg_duration(channel))
col3.metric(label="Average duration (min)", value=avg_duration(channel))


@st.cache_data
def visualize_channel_lina1(channel):
    columns = ['Like Count', 'View Count', 'Comment Count', "Duration"]
    for column in columns:
        if column == 'Duration':
            title = 'Duration in Minutes for 10 Most Recent Videos'
        else:
            title = 'Number of ' + column + ' on 10 Most Recent Videos'
        st.plotly_chart(plot_most_recent(channel, column))


visualize_channel_lina1(channel)


@st.cache_data
def get_plot_lina2(channel):
    return plot_top_tags(channel)


st.plotly_chart(get_plot_lina2(channel))


st.markdown('#### Top tags of popular videos')
st.pyplot(plot_top_tags_wordcloud(channel))

st.plotly_chart(plot_tag_duration(channel))


csv = convert_df(channel)

st.download_button(
    "Download Dataframe",
    csv,
    channel_name+"TopVids.csv",
    "text/csv",
    key='download-csv'
)

st.write(channel)
