import pandas as pd
from textblob import TextBlob
import matplotlib.pyplot as plt
import time

def classify_feedback(comment):
    blob = TextBlob(comment)
    sentiment_score = blob.sentiment.polarity
    if sentiment_score > 0:
        return 'Positive'
    elif sentiment_score < 0:
        return 'Negative'
    else:
        return 'Neutral'


file_path = "../data/scrapped_data.json"
df = pd.read_json(file_path)
df.drop(columns=["postlink", "link", "date"], inplace=True)

# Group by city name and keyword, and concatenate comments for each group
merged_df = df.groupby(['cityname', 'keyword','source'])['comments'].apply(lambda x: sum(x, [])).reset_index()


df_1 = merged_df
df_1['processed_comments'] = merged_df['comments']

#remove unnecessary characters
for i in range(len(df_1['processed_comments'])):
    for j in range(len(df_1['processed_comments'][i])):
        df_1['processed_comments'][i][j] = df_1['processed_comments'][i][j].replace("&amp;", '').replace("'", '').replace("\n", '')
        

#removes deleted comments and comments tags that starts with #
for i in range(len(df_1['processed_comments'])):
    df_1['processed_comments'][i] = [word for word in df_1['processed_comments'][i] if not word.startswith('#') and word != '[deleted]']



merged_df['positive_sentiment'] = ''
merged_df['negative_sentiment'] = ''
merged_df['neutral_sentiment'] = ''

for index, row in merged_df.iterrows():
    positive_count = 0
    negative_count = 0
    neutral_count = 0
    
    for comment in row['processed_comments']:
        sentiment = classify_feedback(comment)
        if sentiment == 'Positive':
            positive_count += 1
        elif sentiment == 'Negative':
            negative_count += 1
        else:
            neutral_count += 1
    
    merged_df.at[index, 'positive_sentiment'] = positive_count
    merged_df.at[index, 'negative_sentiment'] = negative_count
    merged_df.at[index, 'neutral_sentiment'] = neutral_count

for index, row in merged_df.iterrows():
    keyword = row['keyword']
    positive_count = row['positive_sentiment']
    negative_count = row['negative_sentiment']
    neutral_count = row['neutral_sentiment']
    
    text = f"For the keyword '{keyword}', there are {positive_count} positive, {negative_count} negative, and {neutral_count} neutral sentiments."
    print(text)

df.to_csv("../data/scrapped_data.csv", index=False, mode='w')


# Group by keyword and calculate sentiment counts
keyword_sentiment_counts = merged_df.groupby('keyword')[['positive_sentiment', 'negative_sentiment', 'neutral_sentiment']].sum()
plt.figure(figsize=(12, 6))
bar_width = 0.2
bar_positions = range(len(keyword_sentiment_counts))
for i, sentiment in enumerate(['positive_sentiment', 'negative_sentiment', 'neutral_sentiment']):
    plt.bar(
        [pos + i * bar_width for pos in bar_positions],
        keyword_sentiment_counts[sentiment],
        bar_width,
        label=sentiment.split('_')[0].capitalize(),  # Extract sentiment class (positive, negative, neutral) from column name
        color=['#FF5733', '#33FF57', '#3333FF'][i]  # Choose color for each sentiment class
    )
keywords = keyword_sentiment_counts.index
x_positions = [pos + bar_width for pos in range(len(keyword_sentiment_counts))]
plt.xticks(x_positions, keywords, rotation=45)

plt.xlabel('Keyword')
plt.ylabel('Count')
plt.title('Sentiment Distribution for Each Keyword')
plt.legend(title='Sentiment Class', loc='upper right')
plt.tight_layout()
plt.show()

time.sleep(30)
plt.close()