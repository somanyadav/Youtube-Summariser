#-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x
# Importing Libraries

# Running Streamlit
import streamlit as st
st.set_page_config( # Added favicon and title to the web app
     page_title="Youtube Summariser",
     page_icon='favicon.ico',
     layout="wide",
     initial_sidebar_state="expanded",
 )
import base64

# Extracting Transcript from YouTube
import pafy
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse
from textwrap import dedent

#-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x
# All Funtions

# Gensim Summarization
from gensim.summarization.summarizer import summarize

def gensim_summarize(text_content, percent):
    summary = summarize(text_content, ratio=(int(percent) / 100), split=False).replace("\n", " ")
    return summary

# NLTK Summarization
import nltk
from string import punctuation
from heapq import nlargest
nltk.download('punkt')
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

def nltk_summarize(text_content, percent):
    tokens = word_tokenize(text_content)
    stop_words = stopwords.words('english')
    punctuation_items = punctuation + '\n'

    word_frequencies = {}
    for word in tokens:
        if word.lower() not in stop_words:
            if word.lower() not in punctuation_items:
                if word not in word_frequencies.keys():
                    word_frequencies[word] = 1
                else:
                    word_frequencies[word] += 1
    max_frequency = max(word_frequencies.values())

    for word in word_frequencies.keys():
        word_frequencies[word] = word_frequencies[word] / max_frequency
    sentence_token = sent_tokenize(text_content)
    sentence_scores = {}
    for sent in sentence_token:
        sentence = sent.split(" ")
        for word in sentence:
            if word.lower() in word_frequencies.keys():
                if sent not in sentence_scores.keys():
                    sentence_scores[sent] = word_frequencies[word.lower()]
                else:
                    sentence_scores[sent] += word_frequencies[word.lower()]

    select_length = int(len(sentence_token) * (int(percent) / 100))
    summary = nlargest(select_length, sentence_scores, key=sentence_scores.get)
    final_summary = [word for word in summary]
    summary = ' '.join(final_summary)
    return summary

# Spacy Summarization
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
import en_core_web_sm
nlp = en_core_web_sm.load()
def spacy_summarize(text_content, percent):
    stop_words = list(STOP_WORDS)
    punctuation_items = punctuation + '\n'
    nlp = spacy.load('en_core_web_sm')

    nlp_object = nlp(text_content)
    word_frequencies = {}
    for word in nlp_object:
        if word.text.lower() not in stop_words:
            if word.text.lower() not in punctuation_items:
                if word.text not in word_frequencies.keys():
                    word_frequencies[word.text] = 1
                else:
                    word_frequencies[word.text] += 1
                    
    max_frequency = max(word_frequencies.values())
    for word in word_frequencies.keys():
        word_frequencies[word] = word_frequencies[word] / max_frequency
    sentence_token = [sentence for sentence in nlp_object.sents]
    sentence_scores = {}
    for sent in sentence_token:
        sentence = sent.text.split(" ")
        for word in sentence:
            if word.lower() in word_frequencies.keys():
                if sent not in sentence_scores.keys():
                    sentence_scores[sent] = word_frequencies[word.lower()]
                else:
                    sentence_scores[sent] += word_frequencies[word.lower()]

    select_length = int(len(sentence_token) * (int(percent) / 100))
    summary = nlargest(select_length, sentence_scores, key=sentence_scores.get)
    final_summary = [word.text for word in summary]
    summary = ' '.join(final_summary)
    return summary

#-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x

# Hide Streamlit Footer and buttons
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

# Adding logo for the App
file_ = open("app_logo.gif", "rb")
contents = file_.read()
data_url = base64.b64encode(contents).decode("utf-8")
file_.close()

st.sidebar.markdown(
    f'<img src="data:image/gif;base64,{data_url}" alt="" style="height:300px; width:400px;">',
    unsafe_allow_html=True,
)

# Input Video Link
url = st.sidebar.text_input('Video URL', 'https://www.youtube.com/watch?v=T-JVpKku5SI')

# Display Video and Title
video = pafy.new(url)
value = video.title
st.info("### " + value)
st.video(url)

# Specify the summarization algorithm
sumalgo = st.sidebar.selectbox(
     'Select a Summarisation Algorithm',
     options=['Gensim', 'NLTK', 'Spacy'])

# Specify the summary length
length = st.sidebar.select_slider(
     'Specify length of Summary',
     options=['10%', '20%', '30%', '40%', '50%'])


#-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x
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

    # Transcript Summarization is done here
    if sumalgo == 'Gensim':
        summ = gensim_summarize(transcript, int(length[:2]))
        # Priting Summary (summ) in "JUSTIFY" alignment
        html_str = f"""
<style>
p.a {{
text-align: justify;
}}
</style>
<p class="a">{summ}</p>
"""
        st.markdown(html_str, unsafe_allow_html=True)

    if sumalgo == 'NLTK':
        summ1 = nltk_summarize(transcript, int(length[:2]))
        # Priting Summary (summ) in "JUSTIFY" alignment
        html_str1 = f"""
<style>
p.a {{
text-align: justify;
}}
</style>
<p class="a">{summ1}</p>
"""
        st.markdown(html_str1, unsafe_allow_html=True)

    if sumalgo == 'Spacy':
        summ2 = spacy_summarize(transcript, int(length[:2]))
        # Priting Summary (summ) in "JUSTIFY" alignment
        html_str2 = f"""
<style>
p.a {{
text-align: justify;
}}
</style>
<p class="a">{summ2}</p>
"""
        st.markdown(html_str2, unsafe_allow_html=True)

    


#-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x


# Add Sidebar Info
st.sidebar.info(
        dedent(
            """
        This web [app][#streamlit-app] is made by\n
        [Diksha Dutt][#linkedin1] and [Soman Yadav][#linkedin2].
        
        [#linkedin1]: https://www.linkedin.com/in/dikshadutt08/
        [#linkedin2]: https://www.linkedin.com/in/somanyadav/
        [#streamlit-app]: https://github.com/somanyadav/Youtube-Summariser/
        
        """
        )
    )
