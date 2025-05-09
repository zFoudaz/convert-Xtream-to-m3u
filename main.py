import requests
import pandas as pd 
import streamlit as st
import re

XTREAM_HOST=st.text_input('Enter the host (ex: http://provider.co:80): ').strip()
XTREAM_USERNAME=st.text_input('Enter your username: ').strip()
XTREAM_PASSWORD=st.text_input('Enter your password: ')
choice = ''
target = st.selectbox('Select what you want to download:', ('Live TV', 'Movies'))

if target == 'Live TV':
    choice = st.selectbox('Select the type of channels you want to download:', ( 'All Channels','Bein Sports , SSC , AD', 'Sport Channels','custom'))
elif target == 'Movies':
    choice= 1

if choice == 'All Channels': choice = 1
elif choice == 'Bein Sports , SSC , AD': choice = 2
elif choice == 'Sport Channels': choice = 3
elif choice == 'custom': 
    choice = 4
    custom_search = st.text_input('Enter the keyword to search for in channel names: ').strip()

file_name = st.text_input('Enter the file name: ', value='Movies' if target == 'Movies' else 'Channels') 
file_name = file_name if file_name else 'File'
file_data=['#EXTM3u\n']
filterd_channels = {
    'Channel Name':[],
    'Channel ID':[],
}
def condition(channel , choice):
    if choice == 1:
        return True
    elif choice == 2:
        return re.search(r'beinsport|bein sport|ssc|ADsport|AD sport',channel['name'],re.IGNORECASE)
    elif choice == 3:
        return re.search(r'sport',channel['name'],re.IGNORECASE)
    elif choice == 4:
        return re.search(custom_search,channel['name'],re.IGNORECASE)

def get_channels():
    url = f"{XTREAM_HOST}/player_api.php?username={XTREAM_USERNAME}&password={XTREAM_PASSWORD}&action={'get_vod_streams' if target == 'Movies' else 'get_live_streams'}"
    try: 
        response = requests.get(url)
        return response.json()
    except :
        return None


if st.button('save'):
    all_channels = get_channels()
    if all_channels:
        for channel in all_channels:
            if condition(channel,choice):
                file_data.append(f"#EXTINF:0,{channel['name']}\n{XTREAM_HOST}/movie/{XTREAM_USERNAME}/{XTREAM_PASSWORD}/{channel['stream_id']}.{channel['container_extension'] if target =='Movies' else 'ts'}\n")
                filterd_channels['Channel Name'].append(channel['name'])
                filterd_channels['Channel ID'].append(channel['stream_id'])
        st.success(f"File created successfully with {len(file_data)-1} channels.")
        st.download_button(
            label='Download file',
            data=''.join(file_data),
            file_name=f"{file_name}.m3u")
        st.dataframe(pd.DataFrame(filterd_channels,index=range(1,len(filterd_channels['Channel Name'])+1)))
    else:
        st.error("Failed to fetch channels. Please check your credentials and try again.")
        st.text('the error can be due to your provider not supporting using the account outside your region')
