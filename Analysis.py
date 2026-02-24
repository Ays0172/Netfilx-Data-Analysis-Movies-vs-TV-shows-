# %%
# Import the libraries

import pandas as pd
import matplotlib.pyplot as plt

# Load the data
df = pd.read_csv('netflix_titles.csv')
print("Column Headings:")       # To verify if the data is loading correctly
print(df.head())

print('\n, Headings: ', "\t", df.columns)

# %%
# Data Cleaning

df = df.dropna(subset = ['type', 'release_year', 'rating', 'country', 'duration'])

type_counts = df['type'].value_counts()
plt.figure(figsize=(8,6))
plt.pie(type_counts.values, labels = type_counts.index, autopct = '%1.1f%%', startangle = 90)     
plt.title("Comparing the quantity of Movies to TV Series")
plt.tight_layout()
plt.legend()
plt.savefig('movies_vs_tvshows.png')
plt.show()

# %%
# Bar Chart for Rating

rating_counts = df['rating'].value_counts()
plt.figure(figsize=(6,4))
plt.barh(rating_counts.index, rating_counts.values)
plt.title("Content Ratings")
plt.tight_layout()
plt.xlabel('Rating Type')
plt.ylabel('Count')
plt.legend()
plt.savefig('content_ratings.png')
plt.show()

# %%
#Histograms for movie duration distribution

movie_df = df[df['type'] == 'Movie'].copy()
movie_df['duration_int'] = movie_df['duration'].str.replace(' min', '').astype(int)

plt.figure(figsize=(8,6))
plt.hist(movie_df['duration_int'], bins =30, color = 'purple', edgecolor = 'black')
plt.title("Distribution of Movie Duration")
plt.tight_layout()
plt.xlabel('Duration(minutes)')
plt.ylabel('Number of Movies')
plt.legend()
plt.savefig('movies_duration.png')
plt.show()

# %%
#Scatter Plot
release_counts = df['release_year'].value_counts().sort_index()
plt.figure(figsize=(10,6))
plt.scatter(release_counts.index, release_counts.values, color = 'red')
plt.title("Release Year VS Number of Shows")
plt.tight_layout()
plt.xlabel('Release Year')
plt.ylabel('Number of Shows')
plt.legend()
plt.savefig('release_year.png')
plt.show()

# %%
# Top 10 COuntries for producing movies

country_counts = df['country'].value_counts().head(10)
plt.figure(figsize = (8,6))
plt.barh(country_counts.index, country_counts.values)
plt.title("Top 10 Countries by Number of Shows")
plt.tight_layout()
plt.xlabel('Country')
plt.ylabel('Number of Shows')
plt.legend()
plt.savefig('top10_coiuntries.png')
plt.show()

# %%
#Content by Year

cy = df.groupby(['release_year', 'type']).size().unstack().fillna(0)
fig, ax = plt.subplots(1,2, figsize=(12,5))

# first subplot: Movies
ax[0].plot(cy.index, cy['Movie'], color = 'blue')
ax[0].set_title('Movies release per Year')
ax[0].set_xlabel('Year')
ax[0].set_ylabel('Number of Movies')

# second subplot: TV Shows
ax[1].plot(cy.index, cy['TV Show'], color = 'orange')
ax[1].set_title('TV Shows release per Year')
ax[1].set_xlabel('Year')
ax[1].set_ylabel('Number of TV Shows')

fig.suptitle('Comparison of Movies and TV Titles over Years')

plt.tight_layout()
plt.savefig('movies_tvshows_comparison.png')

# %%
# Better comparison of movies & TV Shows Release per year

cy = df.groupby(['release_year', 'type']).size().unstack().fillna(0)
fig, ax = plt.subplots(figsize=(8,5))

ax.plot(cy.index, cy['Movie'], color='blue', label='Movies')
ax.plot(cy.index, cy['TV Show'], color='orange', label='TV Shows')

ax.set_xlabel('Year')
ax.set_ylabel('Count')
ax.legend()

fig.suptitle('Comparison of Movies and TV Titles over Years')
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig('movies_tvshows_contrast.png')
plt.show()



