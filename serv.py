from flask import Flask, render_template, request, redirect, url_for
from jinja2 import Template
import numpy as np
import pandas as pd

app = Flask(__name__)

@app.route('/')
@app.route('/index/')
def index():
    return render_template('index.html')  # in templates folder
    
#get from form and pass to results page
@app.route('/handle_data/', methods=['POST'])
def handle_data():
    return redirect(url_for('result', anime=request.form['anime_name']))

#call get_corr_list method with params from url and pass its result to template
@app.route('/result/<string:anime>')
def result(anime):
    return render_template('result.html', anime_name=anime, my_list=get_corr_list(anime))

score_mean_count = []
user_anime_rating = []

#process data from csv files (should only call once)
def proc_data():
    global score_mean_count; global user_anime_rating   
    ratings_data, anime_names = pd.read_csv("ratings_clean.csv"), pd.read_csv("anime_clean.csv")
    anime_data = pd.merge(ratings_data, anime_names, on='mal_id')
    score_mean_count = pd.DataFrame(anime_data.groupby('title')['score'].mean())
    score_mean_count['score_counts'] = pd.DataFrame(anime_data.groupby('title')['score'].count())
    user_anime_rating = anime_data.pivot_table(index='username', columns='title', values='score')

def get_corr_list(name):
    if not type(user_anime_rating)=='pandas.core.frame.DataFrame' or not type(score_mean_count)=='pandas.core.frame.DataFrame':
        proc_data() #if these variables are not dataframes that means they have not been processed yet.
    get_new_ratings = user_anime_rating[name]
    anime_like = user_anime_rating.corrwith(get_new_ratings)
    corr_with_new = pd.DataFrame(anime_like, columns=['Correlation'])
    corr_with_new.dropna(inplace=True)
    corr_with_new = corr_with_new.join(score_mean_count['score_counts'])
    corr_list = corr_with_new[corr_with_new ['score_counts'] > 50].sort_values('Correlation', ascending=False).head(6)[1:]
    return corr_list # ['Correlation'].keys().tolist()

if __name__ == '__main__':
    app.run()
