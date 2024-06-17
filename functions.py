
import random
import numpy as np


def round_number(n):
    if float(str(n)[-1]) >=8:
        return float(str(n)[:-2])+1
    elif float(str(n)[-1])<=8 and float(str(n)[-1])>=3:
        return float(str(n)[:-1]+'5')
    else:
        return float(str(n)[:-2])
def predict_games(model_home,model_away,stage,knock_out=False,useFactor=False):
    predict_col = ["total_points_home","total_points_away","rank_difference",'point_change_home','point_change_away']
    home_score = np.round(model_home.predict(stage[predict_col]),1)
    away_score = np.round(model_away.predict(stage[predict_col]),1)
    if knock_out:
        home_score = model_home.predict(stage[predict_col])
        away_score = model_away.predict(stage[predict_col])
        if useFactor:
            home_score = [random.uniform(0.0, 1.0) + i for i in home_score]
            away_score = [random.uniform(0.0, 1.0) + i for i in away_score]
    else:
        if useFactor:
            home_score = [round(random.uniform(0.0, 1.0) + i,1) for i in home_score]
            away_score = [round(random.uniform(0.0, 1.0) + i,1) for i in away_score]
        home_score = [round_number(i) for i in home_score]
        away_score = [round_number(i) for i in away_score]

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