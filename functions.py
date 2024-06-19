
import random
import numpy as np
import pandas as pd
latest_rank = pd.read_excel('data/RANK latest.xlsx')
rank = {}
for index, row in latest_rank.iterrows():
    rank[row['Country']] = {
        'Total Points':row['Total Points'],
        'Point Change':row['+-'],
        'Rank':int(row['Rank']),
        }
def round_number(n):
    n = np.round(n,1)
    if float(str(n)[-1]) >=8:
        return float(str(n)[:-2])+1
    elif float(str(n)[-1])<=8 and float(str(n)[-1])>=3:
        return float(str(n)[:-1]+'5')
    else:
        return float(str(n)[:-2])
    
def predict_games(model_home,model_away,stage,knock_out=False,useFactor=False):
    stage1 = stage.copy()
    stage2 = stage.rename(columns={'Home':'Away','Away':'Home'})
    stage1 = fillTeamInfo(stage1,rank)
    stage2 = fillTeamInfo(stage2,rank)
    predict_col = ["total_points_home","total_points_away","rank_difference",'point_change_home','point_change_away']
    home_score_1 = model_home.predict(stage1[predict_col])
    away_score_1 = model_away.predict(stage1[predict_col])
    home_score_2 = model_home.predict(stage2[predict_col])
    away_score_2 = model_away.predict(stage2[predict_col])
    home_score = (home_score_1 + away_score_2) / 2
    away_score = (away_score_1 + home_score_2) / 2
    if not knock_out:
        home_score = [round_number(i) for i in home_score]
        away_score = [round_number(i) for i in away_score]
    if useFactor:
        home_score = [random.uniform(-1.0, 1.0) + i for i in home_score]
        away_score = [random.uniform(-1.0, 1.0) + i for i in away_score]


    stage['Home_score'] = home_score
    stage['Away_score'] = away_score
    
    stage['Result'] = stage.apply(lambda x: 0 if x['Home_score']==x['Away_score'] else(1 if x['Home_score']>x['Away_score'] else 2),axis=1)
    
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
    return stage