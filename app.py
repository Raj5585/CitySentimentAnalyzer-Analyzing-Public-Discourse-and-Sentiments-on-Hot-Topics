import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import asyncio

import scrapping.timesofindia as newssite
import publicforums
from DataPreprocessing import sentimentanalysis


async def async_function(user_input):
    headlines = await newssite.timesofindia(user_input)
    # await asyncio.sleep(3)
    return headlines

def loading_spinner(text):
    spinner = st.empty()
    spinner.markdown(f"""
    <div style="display: flex; justify-content: center; align-items: center;">
        <div class="spinner" role="status"></div>
        <div style="margin-top: 10px;">{text}</div>
    </div>
    <style>
    .spinner {{
        width: 40px;
        height: 40px;
        border: 4px solid #007bff;
        border-top-color: transparent;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }}
    @keyframes spin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}
    </style>
    """, unsafe_allow_html=True)
    return spinner


@st.cache
def load_data(file_path):
    return pd.read_csv(file_path)

def plot_sentiment_bar(data):
    keyword_sentiment_counts = data.groupby('keyword')[['positive_sentiment', 'negative_sentiment', 'neutral_sentiment']].sum()

    # Plot grouped bar plot for a specific keyword
    fig, ax = plt.subplots(figsize=(12, 6))  # Set facecolor to 'w' for white background
    bar_width = 0.2


    bar_positions = range(len(keyword_sentiment_counts))

    # Bars for each sentiment class
    for i, sentiment in enumerate(['positive_sentiment', 'negative_sentiment', 'neutral_sentiment']):
        ax.bar(
            [pos + i * bar_width for pos in bar_positions],
            keyword_sentiment_counts[sentiment],
            bar_width,
            label=sentiment.split('_')[0].capitalize(),  # Extract sentiment class (positive, negative, neutral) from column name
            color=['#FF5733', '#33FF57', '#3333FF'][i]  # Choose color for each sentiment class
        )

    # Set the x-axis labels
    keywords = keyword_sentiment_counts.index
    x_positions = [pos + bar_width for pos in range(len(keyword_sentiment_counts))]
    
    ax.set_xticks(x_positions)
    ax.set_xticklabels([f'{i}' for i, keyword in enumerate(keywords)])  # Updated line to add index and keyword

    # Labels and title
    ax.set_xlabel('Keyword', fontweight='bold')
    ax.set_ylabel('Count', fontweight='bold')
    ax.set_title('Sentiment Distribution for Each Keyword',  fontweight='bold',loc='center')
    ax.legend(title='Sentiment Class',loc='upper right')

    ax.text(0.5, -0.23, ''.join([f'{i} = {keyword}\n' for i, keyword in enumerate(keywords)]), 
        horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,
        fontweight='bold')
    ax.set_facecolor((0,0,0,0.1))  # Set background color with transparency
    fig.set_facecolor('#F0F0F0')  # Change the color to light gray

    # fig.patch.set_alpha(0.0)



    st.pyplot(fig)




async def main():

    # st.title("Dashboard")
    news_sources = st.sidebar.selectbox("Select News Source", ["News Portal", "Social Media", "Google Trends"])

    user_input = st.sidebar.text_input("Enter City's Name:")
    button_clicked = st.sidebar.button("Search")
    if button_clicked:
        spinner = loading_spinner("Scraping data") 
        headlines = await async_function(user_input)

        spinner.empty()
        if(len(headlines) == 0):
            st.write(f"No Hottopic for {user_input} Today:")
        else:
            st.title(f" Hot-Topics on {user_input} are:")
        # st.write(headlines)
        # for my_list in headlines:
        html_list = "<ul style='color:orange;list-style-type: none;text-decoration: none; font-size:45px;'>"
        for item in headlines:
            html_list += "<li>&#9658; {}</li>".format(item)
        html_list += "</ul>"
        st.markdown(html_list, unsafe_allow_html=True)
        spinner = loading_spinner("Generating Data") 
        await publicforums.PublicForum().main(headlines,user_input)
        spinner.empty()

        sentimentanalysis.sentimentanalysis()
        print("done")


        file_path = "./data/model.csv"
        st.title("Sentiment Analysis based on public Forum Discussion")
        if file_path is not None:
            data = pd.read_csv(file_path)
            print("here")
            plot_sentiment_bar(data)
            sentimentanalysis.summary(data)


asyncio.run(main())

# if __name__ == "__main__":
#     main()
