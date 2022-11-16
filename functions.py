


def predict_func_to_df(home_team,away_team):
    input_team = [filter_country(home_team),filter_country(away_team),True]
    home_rank = current_ranking_dict[input_team[0]]
    away_rank = current_ranking_dict[input_team[1]]
    
    average_rank = (home_rank + away_rank)/2
    rank_diff = home_rank - away_rank
    is_stake = input_team[2]
    input_for_predict = np.asarray([[average_rank,rank_diff,is_stake]])
    class_result = loaded_model.predict(input_for_predict)[0]
    probality = loaded_model.predict_proba(input_for_predict)[0]
    
    team1_win_proba = probality[1]
    team2_win_proba = probality[0]

    probality = [round(n,4) for n in probality]
#     probality_output = probality[0] if probality[0] > probality[1] else probality[1]
    team_win = home_team if class_result else away_team
    result = ",".join([str(team1_win_proba),str(team2_win_proba),team_win])

    return result

def predict_func_knock_out(home_team,away_team):
    input_team = [filter_country(home_team),filter_country(away_team),True]
    home_rank = current_ranking_dict[input_team[0]]
    away_rank = current_ranking_dict[input_team[1]]
    
    average_rank = (home_rank + away_rank)/2
    rank_diff = home_rank - away_rank
    is_stake = input_team[2]
    input_for_predict = np.asarray([[average_rank,rank_diff,is_stake]])
    
    probality = loaded_model.predict_proba(input_for_predict)[0]
    
    team1_win_proba = probality[1]
    team2_win_proba = probality[0]

    probality = [round(n,4) for n in probality]
#     probality_output = probality[0] if probality[0] > probality[1] else probality[1]
    ran_num = random.random()
    
    check_result = sim_teamwin(team1_win_proba,team2_win_proba,ran_num)
    
    team_win = ''
    if check_result:
        team_win = home_team
    else:
        team_win = away_team
    
    
    return team_win

def sim_teamwin(t1_proba,t2_proba,random_num):
    if t1_proba > random_num:
        return True
    return False

def result_score(my_df):
    score_dict = dict()
    for index, row in my_df.iterrows():
        team1 = row['Country_1']
        team2 = row['Country_2']
        if team1 not in score_dict:
            score_dict[team1] = 0
        if team2 not in score_dict:
            score_dict[team2] = 0
        result = row['Team1_win']
        if result:
            score_dict[team1] += 3
        else:
            score_dict[team2] += 3
    return score_dict

def cal_percent_quater(col,time_to_simulate):
    try:
#         return (quater_dict[col['Team']]/country_proba[col['Team']]) * col['Percent_to_group_16']
        return (quater_dict[col['Team']]*100/time_to_simulate)
    except:
        return 0
    
def cal_percent_semi(col,time_to_simulate):
    try:
#         return (semi_dict[col['Team']]/quater_dict[col['Team']]) * col['Percent_to_quater']
        return (semi_dict[col['Team']]*100/time_to_simulate)
    except:
        return 0 
    
def cal_percent_final(col,time_to_simulate):
    try:
#         return (final_dict[col['Team']]/semi_dict[col['Team']]) * col['Percent_to_semi']
        return (final_dict[col['Team']]*100/time_to_simulate)
    except:
        return 0  
    
def cal_percent_cham(col,time_to_simulate):
    try:
        return (champion_dict[col['Team']]*100/time_to_simulate)
#         return (champion_dict[col['Team']]/final_dict[col['Team']]) * col['Percent_to_final']
    except:
        return 0  