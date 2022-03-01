# Running Streamlit
import streamlit as st

# Extracting Transcript from YouTube
import pafy
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse
from textwrap import dedent



# Input Video Link
url = st.sidebar.text_input('Video URL', 'https://www.youtube.com/watch?v=T-JVpKku5SI')

# Display Video and Title
video = pafy.new(url)
value = video.title
st.info("### " + value)
st.video(url)

# If Summarize button is clicked
if st.sidebar.button('Summarize'):
    st.success(dedent("""### \U0001F4D6 Summary
> Success!
    """))

    # Generate Transcript by slicing YouTube link to id 
    url_data = urlparse(url)
    id = url_data.query[2::]
    
    def generate_transcript(id):
            transcript = YouTubeTranscriptApi.get_transcript(id)
            script = ""

            for text in transcript:
                    t = text["text"]
                    if t != '[Music]':
                            script += t + " "
                    
            return script, len(script.split())
    transcript, no_of_words = generate_transcript(id)
    

    # Priting Transcript in "JUSTIFY" alignment
    html_str = f"""
<style>
p.a {{
text-align: justify;
}}
</style>
<p class="a">{transcript}</p>
"""
    st.markdown(html_str, unsafe_allow_html=True)
    
st.sidebar.info(
        dedent(
            """
        This web [app][#streamlit-app] is made by
        [Soman Yadav][#linkedin2] and [Diksha Dutt][#linkedin1].
        
        [#linkedin1]: https://www.linkedin.com/in/dikshadutt08/
        [#linkedin2]: https://www.linkedin.com/in/somanyadav/
        [#streamlit-app]: {Defaults.APP_URL}
        
        """
        )
    )
    
