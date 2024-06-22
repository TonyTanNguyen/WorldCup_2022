import pandas as pd
from functions import *
from flags import flags

def get_result(x):
    if x['Result']==0:
        return 'Draw'
    elif x['Result']==1:
        return x['Home'] + ' win'
    elif x['Result']==2:
        return x['Away'] + ' win'
    else:
        return 'TBD'
    
def result_bin(x):
    if x['Home_score_actual']=='':
        return 'TBD'
    elif x['Home_score_actual']==x['Away_score_actual']:
        return 0
    elif x['Home_score_actual']>x['Away_score_actual']:
        return 1
    else:
        return 2
    
real_result = pd.read_excel('FIFA groupstage Real results.xlsx')
real_result = real_result.fillna('')
real_result['Result'] = real_result.apply(lambda x: result_bin(x),axis=1)
real_result['Actual result'] = real_result.apply(lambda x: get_result(x),axis=1)
def simulator(group_stage,best_3rds_table,round_of_16,quarter_final,semi_final,grand_final,rank,all_team,stats,predictor_select1,predictor_select2,simu=False):
    #######GROUP STAGE#########
    group_stage = predict_games(predictor_select1,predictor_select2,group_stage,simu=simu)
    group_stage['Actual Result'] = real_result['Actual result']
    group_stage_table = group_stage[['Home','Away','Result','Actual Result','Group']]
    group_stage_table['Result'] = group_stage_table.apply(lambda x: get_result(x),axis=1) #return
    groups = group_stage['Group'].sort_values().unique()
    group_stage_result = {}
    template_dict = {
                    'Points': 0,
                    'GF': 0,
                    'GA' : 0,
                    'GD' : 0,
                }
    for group in groups:
        group_stage_result[group] = {} 
        currentGroup_df = group_stage[group_stage['Group']==group]
        for index,row in currentGroup_df.iterrows():
            if row['Home'] not in group_stage_result[group]:
                group_stage_result[group][row['Home']]= template_dict.copy()
            if row['Away'] not in group_stage_result[group]:
                group_stage_result[group][row['Away']]=template_dict.copy()
                
            #Calculate for Home team
            group_stage_result[group][row['Home']]['Points']+=row['Home_win_points']
            group_stage_result[group][row['Home']]['GF']+=row['Result_proba'][1]
            group_stage_result[group][row['Home']]['GA']+=row['Result_proba'][2]
            group_stage_result[group][row['Home']]['GD']+=row['Result_proba'][1]-row['Result_proba'][2]
            #Calculate for Away team
            group_stage_result[group][row['Away']]['Points']+=row['Away_win_points']
            group_stage_result[group][row['Away']]['GF']+=row['Result_proba'][2]
            group_stage_result[group][row['Away']]['GA']+=row['Result_proba'][1]
            group_stage_result[group][row['Away']]['GD']+=row['Result_proba'][2]-row['Result_proba'][1]
    
    
    best_4_3rd = {}
    top1_2 = {}
    group_result_dfs = {} ### return
    for group in group_stage_result.keys():
        currentGroup = pd.DataFrame(group_stage_result[group]).T
        currentGroup = currentGroup.sort_values(by=list(currentGroup.columns),ascending=False)
        
        #get top 1 and 2
        top1_2['1'+ group] = currentGroup.index[0]
        top1_2['2'+ group] = currentGroup.index[1]
        top1_2['3'+ group] = currentGroup.index[2]
    
        #get 3rds
        best_4_3rd[currentGroup.index[2]] = currentGroup.iloc[2,:]
        best_4_3rd[currentGroup.index[2]]['Group'] = group
        group_result_dfs[group] = currentGroup
        
    best_4_3rd_df = pd.DataFrame(best_4_3rd).T #return
    best_4_3rd_df = best_4_3rd_df.sort_values(by=list(best_4_3rd_df.columns),ascending=False)
    combination_3rd = ''.join(sorted(best_4_3rd_df['Group'][:4].values.tolist()))
    pairs = best_3rds_table.loc[combination_3rd]




    ####### ROUND OF 16 #######
    #fill 3rds first
    for idx in pairs.index:
        round_of_16.loc[round_of_16['Home_code']==idx,'Away_code'] = pairs[idx]
    
    #then fill the rest
    round_of_16['Home'] = round_of_16.apply(lambda x: top1_2[x['Home_code']],axis=1)
    round_of_16['Away'] = round_of_16.apply(lambda x: top1_2[x['Away_code']],axis=1)
    round_of_16_result = predict_games(predictor_select1,predictor_select2,round_of_16,simu=simu)
    round_of_16_table = round_of_16[['Home','Away','Match No.','Type']]
    round_of_16_result_table = round_of_16_result[['Home','Away','Match No.','Type','Result']] #return
    round_of_16_result_table['Result'] = round_of_16_result_table.apply(lambda x: get_result(x),axis=1) #return
    ##Get stats for group of 16##
    for i in top1_2:
        if i[0]!='3':
            stats[top1_2[i]]['Round of 16']+=1
        
    ######### QUARTER FINAL #############
    win_round_of_16 = {}
    for idx,row in round_of_16_result.iterrows():
        win_round_of_16['W'+ str(row['Match No.'])] = row['Home'] if row['Result']==1 else row['Away']
        
    quarter_final['Home'] = quarter_final['Home_code'].map(lambda x: win_round_of_16[x])
    quarter_final['Away'] = quarter_final['Away_code'].map(lambda x: win_round_of_16[x])
    quarter_final_result = predict_games(predictor_select1,predictor_select2,quarter_final,knock_out=True,simu=simu)

    quarter_final_table = quarter_final[['Home','Away','Match No.','Type']]#return
    quarter_final_result_table = quarter_final_result[['Home','Away','Match No.','Type','Result']] #return
    quarter_final_result_table['Result'] = quarter_final_result_table.apply(lambda x: get_result(x),axis=1) #return
    #Get stats
    for i in win_round_of_16:
        stats[win_round_of_16[i]]['Quarter Final']+=1
    ######### SEMI FINAL ##########
    win_quarter_final = {}
    for idx,row in quarter_final_result.iterrows():
        win_quarter_final['W'+ str(row['Match No.'])] = row['Home'] if row['Result']==1 else row['Away']
    
    semi_final['Home'] = semi_final['Home_code'].map(lambda x: win_quarter_final[x])
    semi_final['Away'] = semi_final['Away_code'].map(lambda x: win_quarter_final[x])
    semi_final = fillTeamInfo(semi_final,rank)
    semi_final_result = predict_games(predictor_select1,predictor_select2,semi_final,knock_out=True,simu=simu)

    semi_final_table = semi_final[['Home','Away','Match No.','Type']] #return
    semi_final_result_table = semi_final_result[['Home','Away','Match No.','Type','Result']] #return
    semi_final_result_table['Result'] = semi_final_result_table.apply(lambda x: get_result(x),axis=1) #return
    #get stats
    for i in win_quarter_final:
        stats[win_quarter_final[i]]['Semi Final']+=1
    ######### GRAND FINAL
    win_semi_final = {}
    for idx,row in semi_final_result.iterrows():
        win_semi_final['W'+ str(row['Match No.'])] = row['Home'] if row['Result']==1 else row['Away']
    
    grand_final['Home'] = grand_final['Home_code'].map(lambda x: win_semi_final[x])
    grand_final['Away'] = grand_final['Away_code'].map(lambda x: win_semi_final[x])
    grand_final = fillTeamInfo(grand_final,rank)
    grand_final_result = predict_games(predictor_select1,predictor_select2,grand_final,knock_out=True,simu=simu)

    grand_final_table = grand_final[['Home','Away','Match No.','Type']]
    grand_final_result_table = grand_final_result[['Home','Away','Match No.','Type','Result']] #return
    grand_final_result_table['Result'] = grand_final_result_table.apply(lambda x: get_result(x),axis=1) #return
    #get stats
    for i in win_semi_final:
        stats[win_semi_final[i]]['Grand Final']+=1
    #Champion
    champion = grand_final_result['Home'].values[0] if grand_final_result['Result'].values[0] == 1 else grand_final_result['Away'].values[0]
    stats[champion]['Champion']+=1

    #Add flags
    group_stage_table['Home'] = group_stage_table['Home'].map(lambda x: flags[x] + x if x in flags else x)
    group_stage_table['Away'] = group_stage_table['Away'].map(lambda x: flags[x] + x if x in flags else x)
    round_of_16_table['Home'] = round_of_16_table['Home'].map(lambda x: flags[x] + x if x in flags else x)
    round_of_16_table['Away'] = round_of_16_table['Away'].map(lambda x: flags[x] + x if x in flags else x)
    round_of_16_result_table['Home'] = round_of_16_result_table['Home'].map(lambda x: flags[x] + x if x in flags else x)
    round_of_16_result_table['Away'] = round_of_16_result_table['Away'].map(lambda x: flags[x] + x if x in flags else x)
    quarter_final_table['Home'] = quarter_final_table['Home'].map(lambda x: flags[x] + x if x in flags else x)
    quarter_final_table['Away'] = quarter_final_table['Away'].map(lambda x: flags[x] + x if x in flags else x)
    quarter_final_result_table['Home'] = quarter_final_result_table['Home'].map(lambda x: flags[x] + x if x in flags else x)
    quarter_final_result_table['Away'] = quarter_final_result_table['Away'].map(lambda x: flags[x] + x if x in flags else x)
    semi_final_table['Home'] = semi_final_table['Home'].map(lambda x: flags[x] + x if x in flags else x)
    semi_final_table['Away'] = semi_final_table['Away'].map(lambda x: flags[x] + x if x in flags else x)
    semi_final_result_table['Home'] = semi_final_result_table['Home'].map(lambda x: flags[x] + x if x in flags else x)
    semi_final_result_table['Away'] = semi_final_result_table['Away'].map(lambda x: flags[x] + x if x in flags else x)
    grand_final_table['Home'] = grand_final_table['Home'].map(lambda x: flags[x] + x if x in flags else x)
    grand_final_table['Away'] = grand_final_table['Away'].map(lambda x: flags[x] + x if x in flags else x)
    grand_final_result_table['Home'] = grand_final_result_table['Home'].map(lambda x: flags[x] + x if x in flags else x)
    grand_final_result_table['Away'] = grand_final_result_table['Away'].map(lambda x: flags[x] + x if x in flags else x)
    champion = flags[champion] + ' ' + champion
    if not simu:
        return group_stage_table,group_result_dfs,best_4_3rd_df,round_of_16_table,round_of_16_result_table,quarter_final_table,quarter_final_result_table,semi_final_table,semi_final_result_table,grand_final_table,grand_final_result_table,champion,stats
    else:
        return stats