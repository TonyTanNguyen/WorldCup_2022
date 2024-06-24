
import random
import numpy as np
import pandas as pd
import altair as alt
import streamlit as st
import json
latest_rank = pd.read_excel('data/RANK latest.xlsx')
rank = {}
cols = ["total_points_home","total_points_away","rank_difference","home_team_last_5_wins","away_team_last_5_wins","home_team_last_10_wins","away_team_last_10_wins"]
for index, row in latest_rank.iterrows():
    rank[row['Country']] = {
        'Total Points':row['Total Points'],
        'Point Change':row['+-'],
        'Rank':int(row['Rank']),
        }
last5_home = 'last5_home.json'
last5_away = 'last5_away.json'
last10_home = 'last10_home.json'
last10_away = 'last10_away.json'

with open(last5_home, 'r') as file:
    last_5_home_wins = json.load(file)
with open(last5_away, 'r') as file:
    last_5_away_wins = json.load(file)
with open(last10_home, 'r') as file:
    last_10_home_wins = json.load(file)
with open(last10_away, 'r') as file:
    last_10_away_wins = json.load(file)

def count_wins(results):
    return sum(1 for result in results if result == 1)
def round_number(n):
    n = np.round(n,1)
    if float(str(n)[-1]) >=8:
        return float(str(n)[:-2])+1
    elif float(str(n)[-1])<=8 and float(str(n)[-1])>=3:
        return float(str(n)[:-1]+'5')
    else:
        return float(str(n)[:-2])
def proba_to_class(my_list):
    max_value = max(my_list)
    return my_list.index(max_value)
def predict_games(model1,model2,stage_input,knock_out=False,simu=False):
    stage = stage_input.copy()
    stage = fillTeamInfo(stage,rank)
    predict_col = cols
    stage['Result_proba1'] = [i for i in model1.predict_proba(stage[predict_col])]
    
    stage['Result_proba2'] = [i for i in model2.predict_proba(stage[predict_col])]
    stage['Result_proba'] = stage.apply(lambda x: [(d + y)/2 for d, y in zip(x['Result_proba1'], x['Result_proba2'])],axis=1)
    sampleList = [0,1,2]
    stage['Result'] = stage['Result_proba'].map(lambda x: proba_to_class(x))
    
    if simu:
        stage['Result'] = stage.apply(lambda x: random.choices(sampleList, weights=x['Result_proba'], k=1)[0],axis=1)
    if knock_out:
        if simu:
            stage['Result'] = stage.apply(lambda x: random.choices(sampleList[1:], weights=x['Result_proba'][1:], k=1)[0],axis=1)
        else:
            stage['Result'] = stage['Result_proba'].map(lambda x: 1 if x[1]>x[2] else 2)
    stage['Home_win_points'] = stage['Result'].map(lambda x: 3 if x==1 else(1 if x==0 else 0))
    stage['Away_win_points'] = stage['Result'].map(lambda x: 3 if x==2 else(1 if x==0 else 0))
    return stage

def fillTeamInfo(stage,infor_dict):
    stage['total_points_home'] = stage['Home'].map(lambda x: float(infor_dict[x]['Total Points'])).astype(float)
    stage['total_points_away'] = stage['Away'].map(lambda x: float(infor_dict[x]['Total Points'])).astype(float)
    stage['home rank'] = stage['Home'].map(lambda x: int(infor_dict[x]['Rank'])).astype(int)
    stage['away rank'] = stage['Away'].map(lambda x: int(infor_dict[x]['Rank'])).astype(int)
    stage['rank_difference'] = stage['home rank'] - stage['away rank']
    stage['point_change_home'] = stage['Home'].map(lambda x: float(infor_dict[x]['Point Change'])).astype(float)
    stage['point_change_away'] = stage['Away'].map(lambda x: float(infor_dict[x]['Point Change'])).astype(float)
    stage['home_team_last_5_wins'] = stage['Home'].map(lambda x: count_wins(last_5_home_wins[x]))
    stage['away_team_last_5_wins'] = stage['Away'].map(lambda x: count_wins(last_5_away_wins[x]))
    stage['home_team_last_10_wins'] = stage['Home'].map(lambda x: count_wins(last_10_home_wins[x]))
    stage['away_team_last_10_wins'] = stage['Away'].map(lambda x: count_wins(last_10_away_wins[x]))
    return stage



def drawChart(df,x,y):
    df=df.sort_values(by=x,ascending = False)
    bars = alt.Chart(df).mark_bar().encode(
        x= alt.X(f'{x}:Q',sort=None,stack='zero',axis=alt.Axis(labels=False)),
        y= alt.Y(f"{y}:O",sort=None)
    ).properties(height=600)

    text = alt.Chart(df).mark_text(dx=15, dy=3, color='black').encode(
            x=alt.X(f'{x}:Q', stack='zero',sort=None,axis=alt.Axis(labels=False)),
            y=alt.Y(f'{y}:N',sort=None),
            # detail='site:N',
            text=alt.Text(f'{x}:Q', format='.2%')
        )
    chart = bars + text
    chart = chart.configure_axis(grid=False)
    return st.altair_chart(chart, theme = "streamlit", use_container_width=True)