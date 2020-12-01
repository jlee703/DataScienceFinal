# -*- coding: utf-8 -*-
"""FINAL Presentation

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1zVjen6iiNvJIWC0CV7YwtPV7e1tB-8-R

**Research question: Do certain anime genres cause more polarization among MyAnimeList (online anime community and databse) users? By polarization I mean contrasts between different users' opinions.**
"""

#repeat code
import pandas as pd
import requests
import json
import time

data_anime = []

for x in range(1, 10):
  response = requests.get("https://api.jikan.moe/v3/top/anime/" + str(x))
  data_anime.append(response.json())

top500 = []

for x in range(0, len(data_anime)):
  for y in range(0, len(data_anime[x]["top"])):
    top500.append(data_anime[x]["top"][y]['mal_id'])

data_top500 = []

for x in range(len(top500)):
  response = requests.get("https://api.jikan.moe/v3/anime/" + str(top500[x]))
  data_top500.append(response.json())

from pandas.io.json import json_normalize

df_data = json_normalize(data_top500)
df_data.head()

"""The first thing I did was read in the top 450 anime. Each row is an anime, each column is a feature of the anime. (same dataframe from the data cleaning notebook)

Working with reviews

**The method I used to determine polarity was to make a dictionary of genres each with "polar votes." Polar votes are a made up unit of measurement that I gave to genres for being a:**

---

Part 1
*   Top five genres with the most helpful votes on top 4 ratings with a score of 1
*   Top five genres with the most helpful votes on top 4 ratings with a score of 2
*   Top five genres with the most helpful votes on top 4 ratings with a score of 3
*   Top five genres with the most helpful votes on top 4 ratings with a score of 4
*   Top five genres with the most helpful votes on top 4 ratings with a score of 5

---

Part 2
*   Top five genres with the highest percentage of users giving a score of 1
*   Top five genres with the highest percentage of users giving a score of 2
*   Top five genres with the highest percentage of users giving a score of 3
*   Top five genres with the highest percentage of users giving a score of 4
*   Top five genres with the highest percentage of users giving a score of 5

---

Part 3
*   Top five genres with the highest percentage of top 4 reviews giving scores 1-5 

---

Part 4
*   Top five genres with the highest percentage of users giving scores that deviate from the mean scores

**Part 1**
"""

# get the top 20 reviews for each of the top 500 anime
data_top500 = []

for x in range(len(top500)):
  response = requests.get("https://api.jikan.moe/v3/anime/" + str(top500[x]) + '/reviews')
  data_top500.append(response.json())

df_reviews = json_normalize(data_top500)

"""**Each top anime has user written reviews, which include a score, date, content, and more. Each review has a "helpful count" which is the number of users that have essentially voted for the review.**

Higher voted reviews are moved to the top of the review board. This feature was my main inspiration for the research question, because you will often find very low reviews with a high number of helpful votes. I mostly think it is because of people trying to be different from the norm or hate on something popular, but I don't think there is one direct cause, rather a number of different factors. I read in the top 20 (or as many reviews as there was if less than 20) for each of the top 450 anime.
"""

import numpy as np

df_reviews_genres = pd.DataFrame()

for x in range(0, len(df_data)):
  for y in range(0, len(df_data['genres'][x])):
    df_reviews_genres.insert(x, str(df_data['genres'][x][y]['name']), df_reviews.loc[x], allow_duplicates=True)

df_reviews_genres = df_reviews_genres.transpose()

"""Each row is a genre with a corresponding show, the column "reviews" is the list of corresponding reviews for that show. """

for x in range(1, 11):
  df_reviews_genres['helpful' + str(x)]  = np.nan

# insert a column "helpful"
for x in range(len(df_reviews_genres)):
  for y in range(min(4, len(df_reviews_genres['reviews'][x]))):
    mean = (df_reviews_genres['reviews'][x][y]['reviewer']['scores']['overall'])
    if df_reviews_genres['helpful' + str(round(mean))][x] > 0:
      df_reviews_genres['helpful' + str(round(mean))][x] = round(df_reviews_genres['reviews'][x][y]['helpful_count'] + df_reviews_genres['helpful' + str(round(mean))][x])
    else:
      df_reviews_genres['helpful' + str(round(mean))][x] = df_reviews_genres['reviews'][x][y]['helpful_count']

"""Each column is a movies' genre(s). Each column "helpfulx" is the number of helpful votes the review for that show recieved.

For every movies' genre(s), I grabbed the top 4 reviews for the movie and added a column corresponding to the reviews' score with the value being the total number of helpful votes it recieved. **I chose the top 4 reviews, because for every anime on the page, the top 4 reviews are the ones shown unless you click "More reviews."** The top 4 reviews are the most significant because many people use those reviews to judge the anime because they are seen as the most credible.
"""

df_reviews_genres.reset_index(inplace=True)
df_reviews_genres_grouped = df_reviews_genres.groupby('index').mean()

polar_votes = {}

def get_polar_votes(genre):
    for x in range(5):
      if genre[x] in polar_votes:
        polar_votes[str(genre[x])] += 1
      else:
        polar_votes[str(genre[x])] = 1

df_reviews_genres_grouped['helpful1'].sort_values(ascending=False).plot.bar(figsize = (25, 10)).set_xlabel("x label")
get_polar_votes(df_reviews_genres_grouped['helpful1'].sort_values(ascending=False).index[:5])

"""**I graphed the number of helpful votes for each score by genre. Ie Out of all "music" anime in the top 450, the top 4 reviews with a "1" rating recieved a total of about 2500 helpful votes. Music, Sci-Fi, Mecha, Military, and Drama all get one polar vote.**

I then added one polar vote to the top 5 genres with the most "helpful" votes on reviews with a 1 rating, because a rating of 1 is the lowest and it is very contraversial to give any anime in the top 450 a rating of 1, but a number of people voted "helpful" on the review.
"""

df_reviews_genres_grouped['helpful2'].sort_values(ascending=False).plot.bar(figsize = (25, 10))
get_polar_votes(df_reviews_genres_grouped['helpful2'].sort_values(ascending=False).index[:5])

df_reviews_genres_grouped['helpful3'].sort_values(ascending=False).plot.bar(figsize = (25, 10))
get_polar_votes(df_reviews_genres_grouped['helpful3'].sort_values(ascending=False).index[:5])

df_reviews_genres_grouped['helpful4'].sort_values(ascending=False).plot.bar(figsize = (25, 10))
get_polar_votes(df_reviews_genres_grouped['helpful4'].sort_values(ascending=False).index[:5])

df_reviews_genres_grouped['helpful5'].sort_values(ascending=False).plot.bar(figsize = (25, 10))
get_polar_votes(df_reviews_genres_grouped['helpful5'].sort_values(ascending=False).index[:5])

"""**For the genres with the top 5 most "helpful" votes on reviews with a 1-5 rating, they recieve 1 "polar vote." These Genre recieve a polar vote because a rating of 1-5 is contraversial to give any anime in the top 450, but a number of people voted "helpful" on the review, which indicates polarity.**

I repeated the process for every possible score (1-10). I gave polar points to every genre having the top 5 most helpful votes for reviews with score 1, 2, 3, 4, or 5. I did not give polar points to any genres with score 6, 7, 8, 9, 10, because these are not really contraversial scores.
"""

polar_votes

"""**This is what the polar votes dictionary looks like now.**

**Part 2**

This is the breakdown of each genres polar votes. Some of the genres are not shown because they have polar scores of 0. It seems dementia, kids, mecha, music, parody, and space are the most polar genres. However, just using the frequency helpful votes appeared on low rating reviews is not the only factor that displays polarization.

Working with stats
"""

# get the stats for each of the top 500 anime
data_top500 = []

for x in range(len(top500)):
  response = requests.get("https://api.jikan.moe/v3/anime/" + str(top500[x]) + '/stats')
  data_top500.append(response.json()['scores'])

df_stats = json_normalize(data_top500)

"""Each row is an anime, each column is a feature of the anime.

I read in the number and percentage of each score (1-10) for every anime in the top 450. These scores represent all scores given to each anime, ie the first anime had 7124 users who gave the anime a 1, which makes up .7% of all scores given. The mean of all scores in a row is the overall score of the anime.
"""

df_stats_genres = pd.DataFrame()

for x in range(0, len(df_data)):
  for y in range(0, len(df_data['genres'][x])):
    df_stats_genres.insert(x, str(df_data['genres'][x][y]['name']), df_stats.loc[x], allow_duplicates=True)

df_stats_genres = df_stats_genres.transpose()

"""Each row is a genre with a corresponding movie, columns are the same as above."""

df_stats_genres.reset_index(inplace=True)
df_stats_genres_grouped = df_stats_genres.groupby('index').mean()

# make a dataframe vote percentage only
df_stats_genres_percent = df_stats_genres_grouped.drop(['1.votes', '2.votes', '3.votes', '4.votes', '5.votes',
                              '6.votes', '7.votes', '8.votes', '9.votes', '10.votes'], axis = 1)
df_stats_genres_percent

"""Each row is a genre, each column is the percentage of users that gave the anime the corresponding score. Ie on average, 0.603468% of the top 450 anime recieved a user given score of 1. This dataframe is too complex to draw conclusions from, so I analyzed each genre by score. """

df_stats_genres_percent['1.percentage'].sort_values(ascending=False).plot.bar(figsize = (25, 10))
get_polar_votes(df_stats_genres_percent['1.percentage'].sort_values(ascending=False).index[:5])

"""**I graphed the percentage of votes for each score by genre. Ie Out of all "josei" anime in the top 450, about 1.5% of users who rated the anime gave the anime a score of 1.**

**I used the same process as above but with different criteria. The top 5 genres with the highest percentage of users giving a score 1-5 were given a polar vote**

I used the same "polar_votes" dictionary that was keeping track of if a genre seems polar. For the genres with the top 5 highest percetnage of users giving a 1 rating, they recieve 1 "polar point." Genres with the top 5 highest percentage of users giving a 1 rating recieve a polar vote because a rating of 1 is the lowest and it is very contraversial to give any anime in the top 450 a rating of 1.
"""

df_stats_genres_percent['2.percentage'].sort_values(ascending=False).plot.bar(figsize = (25, 10))
get_polar_votes(df_stats_genres_percent['2.percentage'].sort_values(ascending=False).index[:5])

df_stats_genres_percent['3.percentage'].sort_values(ascending=False).plot.bar(figsize = (25, 10))
get_polar_votes(df_stats_genres_percent['3.percentage'].sort_values(ascending=False).index[:5])

df_stats_genres_percent['4.percentage'].sort_values(ascending=False).plot.bar(figsize = (25, 10))
get_polar_votes(df_stats_genres_percent['4.percentage'].sort_values(ascending=False).index[:5])

df_stats_genres_percent['5.percentage'].sort_values(ascending=False).plot.bar(figsize = (25, 10))
get_polar_votes(df_stats_genres_percent['5.percentage'].sort_values(ascending=False).index[:5])

"""I repeated the process for every possible score (1-10). I gave polar points to every genre having the top 5 highest percentage of users giving scores of 1, 2, 3, 4, or 5. I did not give polar points to any genres with users giving scores of 6, 7, 8, 9, 10, because these are not really contraversial scores. """

pd.Series(polar_votes).sort_values(ascending=False)

"""**The updated polar_votes dictionary. Genres with polar votes 2 or higher I deemed were suspicious of being polar. This was: 'Dementia', 'Game', 'Kids', 'Mecha',
          'Music', 'Parody', 'Space', 'Horror',
          'Magic', 'Martial Arts', 'Military',
          'Psychological', 'Samurai', 'School',
          'Shounen Ai', 'Thriller'.**

**Part 3**
"""

genres = ['Dementia', 'Game', 'Kids', 'Mecha',
          'Music', 'Parody', 'Space', 'Horror',
          'Magic', 'Martial Arts', 'Military',
          'Psychological', 'Samurai', 'School',
          'Shounen Ai', 'Thriller', 'Other']
values = [4, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0]
df_polar = pd.DataFrame(values, index = genres, columns = ['count'])

for x in range(1, 11):
  df_polar[str(x)]  = np.nan

for x in range(len(df_reviews_genres)):
  for y in range(min(4, len(df_reviews_genres['reviews'][x]))):
    mean = (df_reviews_genres['reviews'][x][y]['reviewer']['scores']['overall'])
    if df_reviews_genres['index'][x] == 'Dementia':
      if df_polar[str(round(mean))][0] > 0:
        df_polar[str(round(mean))][0] += 1
      else:
        df_polar[str(round(mean))][0] = 1
    elif df_reviews_genres['index'][x] == 'Game':
      if df_polar[str(round(mean))][1] > 0:
        df_polar[str(round(mean))][1] += 1
      else:
        df_polar[str(round(mean))][1] = 1    
    elif df_reviews_genres['index'][x] == 'Kids':
      if df_polar[str(round(mean))][2] > 0:
        df_polar[str(round(mean))][2] += 1
      else:
        df_polar[str(round(mean))][2] = 1
    elif df_reviews_genres['index'][x] == 'Mecha':
      if df_polar[str(round(mean))][3] > 0:
        df_polar[str(round(mean))][3] += 1
      else:
        df_polar[str(round(mean))][3] = 1
    elif df_reviews_genres['index'][x] == 'Music':
      if df_polar[str(round(mean))][4] > 0:
        df_polar[str(round(mean))][4] += 1
      else:
        df_polar[str(round(mean))][4] = 1
    elif df_reviews_genres['index'][x] == 'Parody':
      if df_polar[str(round(mean))][5] > 0:
        df_polar[str(round(mean))][5] += 1
      else:
        df_polar[str(round(mean))][5] = 1
    elif df_reviews_genres['index'][x] == 'Space':
      if df_polar[str(round(mean))][6] > 0:
        df_polar[str(round(mean))][6] += 1
      else:
        df_polar[str(round(mean))][6] = 1
    elif df_reviews_genres['index'][x] == 'Horror':
      if df_polar[str(round(mean))][7] > 0:
        df_polar[str(round(mean))][7] += 1
      else:
        df_polar[str(round(mean))][7] = 1
    elif df_reviews_genres['index'][x] == 'Magic':
      if df_polar[str(round(mean))][8] > 0:
        df_polar[str(round(mean))][8] += 1
      else:
        df_polar[str(round(mean))][8] = 1
    elif df_reviews_genres['index'][x] == 'Martial Arts':
      if df_polar[str(round(mean))][9] > 0:
        df_polar[str(round(mean))][9] += 1
      else:
        df_polar[str(round(mean))][9] = 1
    elif df_reviews_genres['index'][x] == 'Military':
      if df_polar[str(round(mean))][10] > 0:
        df_polar[str(round(mean))][10] += 1
      else:
        df_polar[str(round(mean))][10] = 1
    elif df_reviews_genres['index'][x] == 'Psychological':
      if df_polar[str(round(mean))][11] > 0:
        df_polar[str(round(mean))][11] += 1
      else:
        df_polar[str(round(mean))][11] = 1
    elif df_reviews_genres['index'][x] == 'Samurai':
      if df_polar[str(round(mean))][12] > 0:
        df_polar[str(round(mean))][12] += 1
      else:
        df_polar[str(round(mean))][12] = 1
    elif df_reviews_genres['index'][x] == 'School':
      if df_polar[str(round(mean))][13] > 0:
        df_polar[str(round(mean))][13] += 1
      else:
        df_polar[str(round(mean))][13] = 1
    elif df_reviews_genres['index'][x] == 'Shounen Ai':
      if df_polar[str(round(mean))][14] > 0:
        df_polar[str(round(mean))][14] += 1
      else:
        df_polar[str(round(mean))][14] = 1
    elif df_reviews_genres['index'][x] == 'Thriller':
      if df_polar[str(round(mean))][15] > 0:
        df_polar[str(round(mean))][15] += 1
      else:
        df_polar[str(round(mean))][15] = 1
    if df_polar[str(round(mean))][16] > 0:
      df_polar[str(round(mean))][16] += 1
    else:
      df_polar[str(round(mean))][16] = 1

"""Each row is a genre, each column is the number of top 4 reviews given by users with a corresponding score. Ie for dementia anime, there were 2 reviews with a score of "5", 1 review with a score of "8", 2 reviews with a score of "9", and 7 reviews with a score of "10" in the top 4 for all dementia anime in the top 450.

I created this dataframe to compare the number of scores of top 4 reviews for each genre that I marked as having a polar vote 2 or higher. The row "other" represents the total number of reviews with corresponding scores for genres not having a polar vote of 2 of higher.
"""

df_polar['count'] = 0
df_polar = df_polar.div(df_polar.sum(axis=1), axis=0) * 100
df_polar.fillna(0, inplace= True)
df_polar

"""**Each row is a genre, each column is the percentage of reviews with corresponding scores for all top 4 reviews of that genre. Ie for dementia 16.6% of top 4 reviews were given a score of 5, 8.3% of top 4 reviews were given a score of 8, 16.6% of top 4 reviews were given a score of 9, and 58.3% of scores were given a score of 10. The "other" row is the mean of all genres not listed explicitly.**

The DatFrame above is the same as the DataFrame before it but in percentage view. From comparing each row with the other row, the genres with high polarization seem to be dementia, game, music, parody, samurai, school.
"""

dict_polar = {}

for x in range(len(df_polar)):
  bottom = 0
  for y in range(1, 6):
    bottom += df_polar[str(y)][x]
  dict_polar[df_polar.index[x]] = (round(bottom, 1))

dict_polar

"""**I added the percentage of the top 4 reviews that were 5 and below, so that it was easier to compare to the "other" percentage of values 5 and below. This makes sense, because if I was comparing every score (1-10) for each genre, I would be comparing "0" to the percentage of "other" alot.**"""

for x in dict_polar:
  dict_polar[x] = round(dict_polar[x] - 11.7, 1)

pd.Series(dict_polar).sort_values(ascending=False)

"""**I subtracted "other" from every value in the dictionary to determine the values that had the greatest deviation of percentage of values 5 and below from other. It seems dementia, mecha, parody, school, and thriller deviate the most.**"""

polar_votes['Dementia'] += 1
polar_votes['Mecha'] += 1
polar_votes['School'] += 1
polar_votes['Psychological'] += 1
polar_votes['Space'] += 1

"""**I gave the five listed genres above 1 more polar vote, because a high percentage of the top 4 scores being 5 or below is contraversial.**

**Part 4**
"""

df_stats_genres_percent

"""I made this dataframe earlier, I need to use it again."""

other = pd.Series()

for x in df_stats_genres_percent.columns:
  other[x] = df_stats_genres_percent[x].mean()

other

"""I added a row "other" representing all the genres, thus the column values are the mean of all the other column values."""

pd.Series(polar_votes).sort_values(ascending=False)

dif = pd.DataFrame()

for x in ['Dementia', 'Game', 'Music', 'Kids', 'Parody', 'Space', 'School', 'Mecha', 'Thriller']:
  dif[x] = abs(df_stats_genres_percent.loc[x] - other)

dif.transpose()

"""**Each row is a genre, each column is the difference of the percentage of users who gave the corresponding score for each genre and the average of the percentage of users who gave the corresponding score. Ie for dementia .09% of users give more or less 1s than the average genre.**"""

pd.Series(dif.sum()).sort_values(ascending=False)

polar_votes['Dementia'] += 1
polar_votes['Kids'] += 1
polar_votes['Parody'] += 1
polar_votes['Game'] += 1
polar_votes['Thriller'] += 1

"""**I gave each of these genres polar votes, because it is contraversial to have a high percentage of users giving scores different from the mean.**"""

pd.Series(polar_votes).sort_values(ascending=False)

"""**Using my polar_votes dictionary, some genres do seem to cause or at least correlate with polarity. The fact that some genres consistently had patterns in voting and scores by users implies some sort of causation between genre and polarization. I would make the assumption given my observations that anime of the dementia genre cause the most polarity. It is important to understand that my "polar votes" is a measurement that I made up. The reality is that some features may have more indication of polarity than others, but there is no numeric or objective measure of polarity.**"""

from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score

linear_model = pipeline = make_pipeline(
    StandardScaler(),
    LinearRegression()
)

knn_model = pipeline = make_pipeline(
    StandardScaler(),
    KNeighborsRegressor(n_neighbors=3)
)

from sklearn.ensemble import StackingRegressor

X_train = df_data[["popularity", "score", "favorites", "scored_by"]]

stacking_model = StackingRegressor([
    ("linear", linear_model), 
    ("knn", knn_model)],
    final_estimator=LinearRegression()
)
-cross_val_score(stacking_model, X=X_train, y=df_data['members'], cv=10,
                 scoring="neg_root_mean_squared_error").mean()

"""**Small portion of ML part.**

To recap, the measures of polarity I used are:


*   Top five genres with the most helpful votes on top 4 ratings with a score of 1
*   Top five genres with the most helpful votes on top 4 ratings with a score of 2
*   Top five genres with the most helpful votes on top 4 ratings with a score of 3
*   Top five genres with the most helpful votes on top 4 ratings with a score of 4
*   Top five genres with the most helpful votes on top 4 ratings with a score of 5

*   Top five genres with the highest percentage of users giving a score of 1
*   Top five genres with the highest percentage of users giving a score of 2
*   Top five genres with the highest percentage of users giving a score of 3
*   Top five genres with the highest percentage of users giving a score of 4
*   Top five genres with the highest percentage of users giving a score of 5

*   Top five genres with the highest percentage of top 4 reviews giving scores 1-5 
*   Top five genres with the highest percentage of users giving scores that deviate from the mean scores
"""