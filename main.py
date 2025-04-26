import streamlit as st
import io
from requests import get
from requests.exceptions import RequestException
from time import sleep
import re
import pandas as pd 

lines=['#EXTM3U\n']
XTREAM_HOST=st.text_input('Enter the host (ex: http://provider.co:80): ').strip()
XTREAM_USERNAME=st.text_input('Enter your username: ')
XTREAM_PASSWORD=st.text_input('Enter your password: ')
choice=st.selectbox('Select the type of channels you want to download:', ('Bein Sports , SSC , AD', 'All Channels', 'Sport Channels','custom'))
custom=''
df={
    'Channel Name':[],
    'Channel ID':[],
}
if choice == 'Bein Sports , SSC , AD':
    choice = 1
elif choice == 'All Channels':
    choice = 2
elif choice == 'Sport Channels':
    choice = 3
elif choice == 'custom':
    choice = 4
    custom = st.text_input('Enter the keyword to search for in channel names: ')
file_name = 'Sports' if choice == 1 or choice == 3 else 'Channels'
if st.toggle('change file name'):
    file_name = st.text_input('Enter the file name: ')

def run():
    def get_xtream_channels():
        api_url = f"{XTREAM_HOST}/player_api.php?username={XTREAM_USERNAME}&password={XTREAM_PASSWORD}&action=get_live_streams"
        
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        
        for attempt in range(3):
            try:
                response = get(api_url, headers=headers, timeout=10)
                response.raise_for_status()
                return response.json()
            except RequestException as e:
                print(f"Attempt {attempt + 1}/3 : Connection failed - {e} \n make sure you are not using VPN ")
                sleep(5)
        return None

    def condition(choice , channel):
        if choice == 1:
            return re.search(r'bein|ssc|AD |ADSport', channel['name'],re.IGNORECASE)
        elif choice==2:
            return True
        elif choice==3:
            return re.search(r'sport', channel['name'], re.IGNORECASE)
        elif choice==4:
            return re.search(custom, channel['name'], re.IGNORECASE)

    channels = get_xtream_channels()
    global df
    if channels:
        for channel in channels:
            if condition(choice,channel):
                lines.append(f"#EXTINF:0,{channel['name']}\n{XTREAM_HOST}/live/{XTREAM_USERNAME}/{XTREAM_PASSWORD}/{channel['stream_id']}.ts\n")
                df['Channel Name'].append(channel['name'])
                df['Channel ID'].append(channel['stream_id'])

        buffer = io.BytesIO()
        for line in lines:
            buffer.write(line.encode("utf-8"))

        buffer.seek(0)
        st.success(f'File created successfully with {len(lines)-1} channels')
        st.download_button(
        label=f"Download {file_name}.m3u",
        data=buffer,
        file_name=f"{file_name}.m3u",
        mime="audio/x-mpegurl"
        )
        df=pd.DataFrame(df)
        st.dataframe(df)
    else:
        st.error("Failed to retrieve channels. Please check your credentials and try again.")

if st.button('save'):
    run()