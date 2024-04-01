# Task 1 - Gather data
To gather data about the top five hot topics in a city, I found news portals to be the most relevant source. Therefore, I scraped Times of India to search for any news related to the city and extracted the titles. Although I attempted to gather data from other sources, including Google Trends, I found that they didn't provide relevant data. Hence, I decided to stick to the news portal for now.

# Task 2 - Gather relevant discussions
After obtaining the news titles, I searched for these topics on Twitter and extracted all the posts and their comments. To ensure comprehensive coverage and a substantial dataset, I scraped data from all available sources on Twitter. Finally, I stored the collected data in a JSON file.

Similarly, I used PRAW(Python Reddit API Wrapper) to search for the extracted data from news portals on the Reddit platform and extract the top 3 posts and their comments using Reddit API pp. Finally, I stored all the collected data, including both the Twitter and Reddit data, in the same JSON file.

# Task 3 - Analyze gathered information
After collecting the data and public discussions on these topics, I perform data preprocessing, which includes Exploratory Data Analysis (EDA) and other data processing methods. This involves removing tags and comment strings, as well as unnecessary strings like '/n' and skip sequences.

To analyze the sentiment in the comments for the given posts, I use the TextBlob library. TextBlob is a Python library for processing textual data. It provides simple API methods for common natural language processing (NLP) tasks, including sentiment analysis. By leveraging TextBlob, I performed the sentiment analysis (positive, negative, or neutral) of the comments in the dataset.
