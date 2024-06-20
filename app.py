import streamlit as st
import pandas as pd
import numpy as np
import random
import pickle
from functions import *
from simulator import simulator
from flags import flags
import altair as alt

st.set_page_config(
    page_title = "EURO 2024 Predictor",
    page_icon="🧊",
    layout="wide")

# pd.options.st.table.float_format = "{:,.3f}".format
home_predictor_path = 'home_predictor.sav'
away_predictor_path = 'away_predictor.sav'


home_predictor = pickle.load(open(home_predictor_path, 'rb'))
away_predictor = pickle.load(open(away_predictor_path, 'rb'))

title = 'Test'
text_teamplate = """<title>{title}</title><style>
        .title {
            color: white;
            background-color: red;
            padding: 10px;
            font-size: 2em;
            text-align: center;
        }
    </style>
    """

#Prepare input:
euro_2024_matches = pd.read_excel('data/EURO_2024_all_matches.xlsx')
euro_2024_matches['Group'] = euro_2024_matches.apply(lambda x: x['Home_code'][0] if x['Type']=='Group Stage' else np.nan,axis=1)
group_stage = euro_2024_matches[~euro_2024_matches['Group'].isna()]
best_3rds_table  = pd.read_excel('data/EURO_2024_all_matches.xlsx',sheet_name=1,index_col=0)
round_of_16 = euro_2024_matches[euro_2024_matches['Type']=='Round of 16']
quarter_final = euro_2024_matches[euro_2024_matches['Type']=='Quarter Final']
semi_final = euro_2024_matches[euro_2024_matches['Type']=='Semi Final']
grand_final = euro_2024_matches[euro_2024_matches['Type']=='Grand Final']
all_team = list(set(group_stage['Home'].to_list() + group_stage['Away'].to_list()))
latest_rank = pd.read_excel('data/RANK latest.xlsx')
currentRank = {}
for index, row in latest_rank.iterrows():
    currentRank[row['Country']] = int(row['Rank'])
        
    
stats = {i:{'Round of 16': 0,
            'Quarter Final':0,
            'Semi Final': 0,
            'Grand Final': 0,
            'Champion':0,
        } for i in all_team}



def show_flag(selected_country):
        return flags[selected_country] + selected_country



#================================== UI =========================================

streamlit_style = """
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap');

            html, body, [class*="css"]  {
            font-family: 'Poppins', sans-serif;
            }
            </style>
            """
st.markdown(streamlit_style, unsafe_allow_html=True)

hide_streamlit_style = """
            <style>
            footer {visibility: hidden;}
            body {background-color: #EAFBFF;}
            #MainMenu {visibility: hidden;}
        .block-container.css-12oz5g7.egzxvld2 {background-color: #fff;border-radius:20px;box-shadow: 0 2px 2px 0 rgba(0, 0, 0, 0.1), 0 3px 15px 0 rgba(0, 0, 0, 0.19)}
            
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

st.markdown("<h2 style='text-align: center; color:#bd0042'>EURO 2024 PREDICTOR</h2>",unsafe_allow_html=True)

# img_link = 'https://tgmresearch.com/images/Artboard_4.png'

# st.image(img_link)


tab1,tab2,tab3 = st.tabs(['Predict full competition (Standard)','Run simulation (Using unknown factors)','Predict 1vs1'])
with tab1:
    st.write('We only use historical data (FIFA rank of each team, FIFA points changed overtime, goals made,...) to predict the result of a match between two teams.')
    start_predict_1 = st.button('Start Predicting',key='A')
    if start_predict_1:
        group_stage_table,group_result_dfs,best_4_3rd_df,round_of_16_table,round_of_16_result_table,quarter_final_table,quarter_final_result_table,semi_final_table,semi_final_result_table,grand_final_table,grand_final_result_table,champion,stats = simulator(group_stage,best_3rds_table,round_of_16,quarter_final,semi_final,grand_final,rank,all_team,stats,home_predictor,away_predictor,False)
        
        group_stage_con = tab1.container(border=True)
        round_16_con = tab1.container(border=True)
        quarter_con = tab1.container(border=True)
        semi_con = tab1.container(border=True)
        grand_con = tab1.container(border=True)
        
        #Title for each container
        group_stage_con.header('GROUP STAGE')
        group_stage_con.table(group_stage_table.style.format(precision=1, thousands=''))
        group_stage_con.write('<h3 style="color: white; background-color: #1750ad; padding: 10px; text-align: center;">Result Group Stage</h3>',unsafe_allow_html=True)
        for group in group_result_dfs:
            group_stage_con.write(f'Group {group}')
            group_stage_con.table(group_result_dfs[group].style.format(precision=1, thousands=''))
        
        group_stage_con.write('Best of 3rd')
        group_stage_con.table(best_4_3rd_df.style.format(precision=1, thousands=''))
        round_16_con.header('ROUND OF 16')
        round_16_con.table(round_of_16_table.style.format(precision=1, thousands=''))
        round_16_con.write('<h3 style="color: white; background-color: #1750ad; padding: 10px; text-align: center;">Result Round of 16</h3>',unsafe_allow_html=True)
        round_16_con.table(round_of_16_result_table)
        quarter_con.header('QUARTER FINAL')
        quarter_con.table(quarter_final_table)
        quarter_con.write('<h3 style="color: white; background-color: #1750ad; padding: 10px; text-align: center;">Result Quarter Final</h3>',unsafe_allow_html=True)
        quarter_con.table(quarter_final_result_table)
        semi_con.header('SEMI FINAL')
        semi_con.table(semi_final_table)
        semi_con.write('<h3 style="color: white; background-color: #1750ad; padding: 10px; text-align: center;">Result Semi Final</h3>',unsafe_allow_html=True)
        semi_con.table(semi_final_result_table)
        grand_con.header('GRAND FINAL')
        grand_con.table(grand_final_table)
        grand_con.write('<h3 style="color: white; background-color: #1750ad; padding: 10px; text-align: center;">Result Grand Final</h3>',unsafe_allow_html=True)
        grand_con.table(grand_final_result_table)
        
        st.write('<h3 style="color: white; background-color: #1750ad; padding: 10px; text-align: center;">Champion</h3>',unsafe_allow_html=True)

        st.header(f'{champion}')
        st.balloons()


with tab2:
    st.write('In real world, especially in high level competition games, small things can change the result of a match. We use an "unknown" factor, stands for unpredicted condition that might effect the result of each match, and run the simulation n times to get probability for each team to be qualified from round of 16 to become champion.')
    simulating_time = tab2.selectbox('Select times to simulate',[100,1000,2000,5000])
    start_predict_2 = tab2.button('Start simulating',key='B')
    view_result = tab2.button('View pre-run result from our simulating 10,000 times')
    if view_result:
        t16,t8,t4,t2,t1 = tab2.tabs(['Round of 16','Quarter Final','Semi Final','Grand Final','Champion'])
        with t16:
            drawChart(output,x='Round of 16',y='Team')
        with t8:
            drawChart(output,x='Quarter Final',y='Team')
        with t4:
            drawChart(output,x='Semi Final',y='Team')
        with t2:
            drawChart(output,x='Grand Final',y='Team')
        with t1:
            drawChart(output,x='Champion',y='Team')
    if start_predict_2:
        my_bar = tab2.progress(0)
        n = simulating_time
        for time in range(n):
            my_bar.progress(time/n + 1/n)
            stats= simulator(group_stage,best_3rds_table,round_of_16,quarter_final,semi_final,grand_final,rank,all_team,stats,home_predictor,away_predictor,useFactor=True,simu=True)
        output = pd.DataFrame(stats).T
        
        
        for col in output.columns:
            output[col] = output[col]/n
        output = output.reset_index()
        output = output.rename(columns={'index':'Team'})
        t16,t8,t4,t2,t1 = tab2.tabs(['Round of 16','Quarter Final','Semi Final','Grand Final','Champion'])
        with t16:
            drawChart(output,x='Round of 16',y='Team')
        with t8:
            drawChart(output,x='Quarter Final',y='Team')
        with t4:
            drawChart(output,x='Semi Final',y='Team')
        with t2:
            drawChart(output,x='Grand Final',y='Team')
        with t1:

            drawChart(output,x='Champion',y='Team')
with tab3:
    #Use for simulation

    tab3.write('Start predicting by selecting competition of two teams.')
    
    st.session_state.projects = all_team
    def submit_delete_project():
        if st.session_state['selected1'] == st.session_state['selected2']:
            st.session_state['selected1'] = st.session_state.projects[random.choice(range(len(st.session_state.projects)))]
    team1 = tab3.selectbox('Select Team 1',st.session_state.projects,key='selected1',on_change = submit_delete_project,index=1, format_func = show_flag)
    team2 = tab3.selectbox('Select Team 2',st.session_state.projects,key='selected2',on_change = submit_delete_project,index=2, format_func = show_flag)
    bt_2_team = tab3.button('Predict',key = 'dsfsdddddd')
    if bt_2_team:
        dump_df = pd.DataFrame({'Home':[team1],
                   'Away':[team2],})
        dump_df = predict_games(home_predictor,away_predictor,dump_df,knock_out=True,useFactor=False)
        team_win = dump_df['Home'].values[0] if dump_df['Result'].values[0]==1 else dump_df['Away'].values[0]
        goals_proba = str(dump_df['Home_score'].values[0]) +' vs ' + str(dump_df['Away_score'].values[0])
        con = tab3.container(border=True)
        con.write(f"<b style='color:red'> {flags[team1]}{team1} (Rank {currentRank[team1]})</b> :soccer: <b style='color:red'>{flags[team2]}{team2} (Rank {currentRank[team2]})</b>: <b style='color:blue'>{flags[team_win]}{team_win}</b> wins with goals probability: <b>{goals_proba}</b>",unsafe_allow_html=True)
        st.balloons()