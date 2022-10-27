import streamlit as st
import pandas as pd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
import random
import pickle
import networkx as nx

# pd.options.st.table.float_format = "{:,.3f}".format
filename_rf = 'RF_WC_Predictor.sav'
filename_lr = 'Logic_WC_Predictor.sav'
filename_svc = 'SVC_WC_Predictor.sav'
filename_svc_proba = 'SVC_WC_Predictor_proba.sav'

rf_model = pickle.load(open(filename_rf, 'rb'))
lr_model = pickle.load(open(filename_lr, 'rb'))
svc_model = pickle.load(open(filename_svc, 'rb'))
svc_model_proba = pickle.load(open(filename_svc_proba, 'rb'))





#Prepare input:
curent_ranking = pd.read_excel('FIFA RANK.xlsx')
current_ranking_dict = curent_ranking.set_index(keys='Country')['Rank'].to_dict()
wc_22_matches = pd.read_csv('matchs-schudule.csv',sep=';')
group_order = pd.read_csv('Qatar2022-teams.csv',sep=';')
group_order.columns = ['Team','Group']
teams = group_order['Team'].sort_values(ascending=True).to_list()


wc_22_matches_groupstage = wc_22_matches[wc_22_matches['phase']=='group matches']

#add group name
wc_22_matches_groupstage = pd.merge(wc_22_matches_groupstage,group_order,left_on = 'country1',right_on = 'Team')

#Sort by A-Z on Group
wc_22_matches_groupstage = wc_22_matches_groupstage.sort_values(by='Group')

#rename
wc_22_matches_groupstage.rename(columns=({'country1': 'Country_1','coutry2':'Country_2'}),inplace=True)




#=============== Functions ================
def filter_country(name):
    if name =='South Korea':
        return "Korea Republic"
    return name



def predict_func(home_team,away_team):
    input_team = [filter_country(home_team),filter_country(away_team),True]
    home_rank = current_ranking_dict[input_team[0]]
    away_rank = current_ranking_dict[input_team[1]]
    
    average_rank = (home_rank + away_rank)/2
    rank_diff = home_rank - away_rank
    is_stake = input_team[2]
    input_for_predict = np.asarray([[average_rank,rank_diff,is_stake]])
    class_result = loaded_model.predict(input_for_predict)[0]
    probality = loaded_model_proba.predict_proba(input_for_predict)[0]
    probality_output = probality[0] if probality[0] > probality[1] else probality[1]
    probality_output_text = str(round(probality_output*100,3)) + '%'
    team_win = home_team if class_result else away_team
    result = [3,0,probality_output] if class_result else [0,3,probality_output]
    
#     st.markdown(f"Group {group_name}:")
    st.write(f"<b style='color:red'>{home_team}</b> vs. <b style='color:red'>{away_team}</b>: <b style='color:blue'>{team_win}</b> wins with probability <b>{probality_output_text}</b>",unsafe_allow_html=True)
#     st.markdown("========================================================\n")
#     time.sleep(0.1)
    return result
def main():
    currentgroup = ''
    group_stage_result = {}
#     st.markdown('\n##### ***************** GROUP STAGE PREDICTING *****************')
    st.markdown("<h2 style='text-align: center';> GROUP STAGE PREDICTING </h2>",unsafe_allow_html=True)
    for index, row in wc_22_matches_groupstage.iterrows():
        newgroup = row['Group']
        if newgroup != currentgroup:
            currentgroup = newgroup
            st.markdown(f'\n\n\n=========== GROUP {currentgroup} ===========')

        output_result = predict_func(row['Country_1'], row['Country_2'])
        if row['Country_1'] in group_stage_result:
            group_stage_result[row['Country_1']] += output_result[0]
        else:
            group_stage_result[row['Country_1']] = output_result[0]
        if row['Country_2'] in group_stage_result:
            group_stage_result[row['Country_2']] += output_result[1]
        else:
            group_stage_result[row['Country_2']] = output_result[1]

    #Score for each team after Group Stage
    group_stage_result_df = pd.DataFrame({'Country':group_stage_result.keys(),'Score':group_stage_result.values()}).sort_values('Score',ascending=False)
    # group_stage_result_df.to_excel('after_group_stage.xlsx') #Export to excel
    group_stage_result_df = pd.merge(group_stage_result_df,group_order,left_on = 'Country',right_on = 'Team')[['Country','Score','Group']].sort_values(by=['Group','Score'],ascending=[True,False])
    round_of_16_pairs = []
    node = []
    st.markdown("\n\n\n##### ======= SCORE AFTER GROUP STAGE =======")
    
    for gr in group_stage_result_df['Group'].unique():
        current_group = group_stage_result_df[group_stage_result_df['Group']==gr]
        round_of_16_pairs.append([current_group['Country'][:2].values])
        st.table(current_group.reset_index(drop=True))
    
    st.markdown("""---""")
    # quater_final pairs
    round_of_16_matches = []
#     st.markdown("\n\n\n#### =================== ROUND OF 16 ===================")
    st.markdown("<h2 style='text-align: center';>ROUND OF 16</h2>",unsafe_allow_html=True)
    for i in range(0,len(round_of_16_pairs),2):
        winner_group_1 = round_of_16_pairs[i][0][0]
        runners_up_group_2 = round_of_16_pairs[i+1][0][1]
        winner_group_2 = round_of_16_pairs[i+1][0][0]
        runners_up_group_1 = round_of_16_pairs[i][0][1]
        #for visualize nodes
        node.append(winner_group_1)
        node.append(runners_up_group_2)
        node.append(winner_group_2)
        node.append(runners_up_group_1)
        
        # st.markdown(f"{winner_group_1} vs. {runners_up_group_2}")
        # st.markdown(f"{winner_group_2} vs. {runners_up_group_1}")
        round_of_16_matches.append([winner_group_1,runners_up_group_2])
        round_of_16_matches.append([winner_group_2,runners_up_group_1])
        
    st.markdown("\n\n\n======= ROUND OF 16 IN TABLE =======")
    round_of_16_matches_df = pd.DataFrame(round_of_16_matches,columns=['Team 1','Team 2']).reset_index()
    round_of_16_matches_df['Match'] = round_of_16_matches_df.pop('index')+1
    st.table(round_of_16_matches_df.reset_index(drop=True))


    

    quater_final_list = []

    round_of_16_matches_df['Team wins'] = ''
    round_of_16_matches_df['Proba_win'] = pd.Series().astype(float)

    dump_semi = []

    for index, row in round_of_16_matches_df.iterrows():

        st.markdown(f"\n======= Match {row['Match']} =======")
        output_result = predict_func(row['Team 1'], row['Team 2'])
        win_team = row['Team 1'] if output_result[0]==3 else row['Team 2']
        dump_semi.append(win_team)
        if len(dump_semi)==2:
            quater_final_list.append(dump_semi)
            dump_semi = []
        round_of_16_matches_df.loc[index,'Team wins'] = win_team
        round_of_16_matches_df.loc[index,'Proba_win'] = round(output_result[2],3)
        node.append(win_team)
    st.markdown('\n\n\n\n======= ROUND 16 RESULT IN TABLE ========')
    st.table(round_of_16_matches_df)

    quarter_final_df = pd.DataFrame(quater_final_list,columns=['Team 1','Team 2'])
    
    
    st.markdown("""---""")
#     st.markdown('\n#### ========== QUATER-FINALS ==========')
    st.markdown("<h2 style='text-align: center';>QUATER-FINALS</h2>",unsafe_allow_html=True)
    st.table(quarter_final_df.reset_index(drop=True))


    #Predicting Quarter-finals
    semi_final_list = []

    quarter_final_df['Team wins'] = ''
    quarter_final_df['Proba_win'] = pd.Series().astype(float)

    for index, row in quarter_final_df.iterrows():

        st.markdown(f"\n======= Quater-final {index+1} =======")
        output_result = predict_func(row['Team 1'], row['Team 2'])
        win_team = row['Team 1'] if output_result[0]==3 else row['Team 2']
        dump_semi.append(win_team)
        if len(dump_semi)==2:
            semi_final_list.append(dump_semi)
            dump_semi = []
        quarter_final_df.loc[index,'Team wins'] = win_team
        quarter_final_df.loc[index,'Proba_win'] = round(output_result[2],3)
        node.append(win_team)
    st.markdown('\n\n\n\n======= QUATER-FINALS RESULT IN TABLE ========')
    st.table(quarter_final_df.reset_index(drop=True))

    st.markdown("""---""")
    #Predict Semi-Finals
    semi_final_df = pd.DataFrame(semi_final_list,columns=['Team 1','Team 2'])
    
#     st.markdown('\n#### ========== SEMI-FINALS ==========')
    st.markdown("<h2 style='text-align: center';>SEMI-FINALS</h2>",unsafe_allow_html=True)
    st.table(semi_final_df)

    grand_final_list = []

    semi_final_result = {}
    semi_final_df['Team wins'] = ''
    semi_final_df['Proba_win'] = pd.Series().astype(float)

    for index, row in semi_final_df.iterrows():

        st.markdown(f"\n======= SEMI-FINALS {index+1} =======")
        output_result = predict_func(row['Team 1'], row['Team 2'])
        win_team = row['Team 1'] if output_result[0]==3 else row['Team 2']
        dump_semi.append(win_team)
        if len(dump_semi)==2:
            grand_final_list.append(dump_semi)
            dump_semi = []
        semi_final_df.loc[index,'Team wins'] = win_team
        semi_final_df.loc[index,'Proba_win'] = round(output_result[2],3)
        node.append(win_team)
    st.markdown('\n\n\n\n======= SEMI-FINALS RESULT IN TABLE ========')
    st.table(semi_final_df)

    st.markdown("""---""")
    #Grand Final
    grand_final_df = pd.DataFrame(grand_final_list,columns=['Team 1','Team 2'])
    
#     st.markdown('\n#### ========== GRAND-FINALS ==========')
    st.markdown("<h2 style='text-align: center';>GRAND-FINALS</h2>",unsafe_allow_html=True)
    st.table(grand_final_df)

    champion = ''

    grand_final_df['Team wins'] = ''
    grand_final_df['Proba_win'] = pd.Series().astype(float)

    for index, row in grand_final_df.iterrows():

        output_result = predict_func(row['Team 1'], row['Team 2'])
        champion = row['Team 1'] if output_result[0]==3 else row['Team 2']
    #     dump_semi.append(win_team)
    #     if len(dump_semi)==2:
    #          grand_final_list.append(dump_semi)
    #         dump_semi = []
        grand_final_df.loc[index,'Team wins'] = win_team
        grand_final_df.loc[index,'Proba_win'] = round(output_result[2],3)
        node.append(win_team)
    st.markdown('\n\n\n\n======= GRAND-FINALS RESULT IN TABLE ========')
    st.table(grand_final_df.reset_index(drop=True))

#     st.markdown('\n\n\n\n****======= FIFA WOURLD CUP 2022 CHAMPIONS=======****')
    st.markdown("<h2 style='text-align: center'; color:'red'>FIFA WOURLD CUP 2022 CHAMPIONS</h2>",unsafe_allow_html=True)
    st.markdown(f"## {champion}")


    st.markdown("""---""")
    #Visualize

    st.markdown("### Visualization")
    country_unique = list(set(node))
    number_of_colors = len(country_unique)

    colors = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
                for i in range(number_of_colors)]
    colors_dict = {country_unique[i]:colors[i] for i in range(len(country_unique))}

    colors_node_list = [colors_dict[i] for i in node]
    colors_node_list = list(reversed(colors_node_list))
    node_dict = dict()
    for i in range(31):
        node_dict[i] = node[30-i]
    

    

    plt.figure(figsize=(12,12))
    fig, ax = plt.subplots()
    H = nx.balanced_tree(2, 4)
    # pos = graphviz_layout(H, prog='twopi')
    threshold = 0.5

    #positions of nodes
    pos = {
        0:(0,0),
        1:(0,1),
        2:(0,-1),
        3:(-1,1),
        4:(1,1),
        5:(1,-1),
        6:(-1,-1),
        7:(-2,2),
        8:(-1,2),
        9:(1,2),
        10:(2,2),
        11:(2,-2),
        12:(1,-2),
        13:(-1,-2),
        14:(-2,-2),
        15:(-4,3),
        16:(-3,3),
        17:(-2,3),
        18:(-1,3),
        19:(1,3),
        20:(2,3),
        21:(3,3),
        22:(4,3),
        23:(4,-3),
        24:(3,-3),
        25:(2,-3),
        26:(1,-3),
        27:(-1,-3),
        28:(-2,-3),
        29:(-3,-3),
        30:(-4,-3)
        
    }
    #Draw labels based on node positions
    nx.draw_networkx(H,pos= pos,with_labels=False,node_size=700,node_color = colors_node_list,width = 0.5)
    nx.draw_networkx_labels(H,pos, node_dict,font_size = 5,bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="black", lw=.5, alpha=1))
    st.pyplot(fig)
    st.balloons()







#================================== UI =========================================
# st.markdown("<h1 style='text-align: center; color: red;'>Predicting FIFA World Cup 2022 using Machine Learning</h1>", unsafe_allow_html=True)

# slide1 =  st.sidebar.radio('',['About the model','Go Predicting!'])
# slide2 =  st.sidebar.button('Go Predicting!')




# st.write('&nbsp;')
# st.write('&nbsp;')
# st.write('&nbsp;')
# st.write('&nbsp;')



# if slide1 == 'About the model':
    
#     st.write('&nbsp;')
#     st.image('https://i.ibb.co/GpVPmZx/1-Km-E-AC5-P0-HJlz-WFmbyjg.png')
#     st.write('&nbsp;')
#     st.markdown("#### Introduction")
#     st.write('With the 2022 FIFA World Cup incoming: We are curious to know which team will win using Machine Learning?')

#     st.markdown("#### Goal")
#     st.write('Using Machine Learning to predict who is going to win the FIFA World Cup 2022.')
#     st.write('Predicting the outcome of individual matches for the entire competition.')
#     st.write('Running simulation of the next matches i.e quarter finals, semi finals and finals. These goals present a unique real-world Machine Learning prediction problem and involve solving various Machine Learning tasks: data integration, feature modelling and outcome prediction.')

#     st.markdown("#### Data")
#     st.write('We used data from Kaggle, International football result fro 1870 to 2022. We will use results of historical matches since the beginning of the championship (1930) for all participating teams. We also used data ranking from 1992 to 2022 for building models')
#     st.markdown("#### How we build models?")
#     st.write('By using ML algorithms. For this one, we used Logistic Regresion, Random Forest and SVM. Ranking is the main input.')
#     st.write('We will base on the results of competitive matches only (not Friendly), and use rankings of the two teams from a match at that specific time. For example:')
#     st.write('Rankings of Brazil and Argentina in 1990 will be different with rankings of Brazil and Argentina in 2022, the same as others.')
#     st.markdown("#### How many algorithms that we built?")
#     st.write('3 algorithms in total. Random Forest, SVM and Logistic Regresion ')

# elif slide1 == 'Go Predicting!':

streamlit_style = """
			<style>
			@import url('https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;700;800;900&display=swap');

			html, body, [class*="css"]  {
			font-family: 'Inter', sans-serif;
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

st.markdown("<h2 style='text-align: center; color:red'>FIFA WOURLD CUP 2022 PREDICTOR</h2>",unsafe_allow_html=True)

img_link = 'https://lh3.googleusercontent.com/Rxtieadih8m8ZfaGrKFYWLvkmJtDiGb5-R_fGWHDnq-IJmCd0-XjP3V-Zj6dwlfLH0n7ImXO6rBLZVlr3RKAkdtsg6_llDO8UZJaNMDH2aK32jKLF5vEKlh7-whuy8iHUtN9qJJGBkZZlQFsA2a5UVXJ46JgDV_4u80dnSCZXP34C64d2OG7qWW8F0k9OuqFp1SK4b-XjHXVFLzHV0-jb7V2tMRna_jMrIwX8wrALXmk3wtWiOd7klUzD9gLm8k7_rqjrwd_2oig0hKLGpjdh2BGzHZtczQXbcz_Cw784fA95sUo1bA87PnjIsXjD3xvpqtw88CHdPIsWc4dw69sgc8rg13g5yopSqw3EqtpeczWeWyIO2JaaZlV8Gb0eWmff7F-B3BCGBr_ty6g9dyYsHOmxJZrSbtqb6HDC-_-edTuLUM378LesYlbNFA3TgBK6Q7lAPsG2BDmG5olWK4fgMHy_hc2MSVv_Qfsx089kAUCZlv3KgnICwwk7DCFatrfNGnuEhhz-2g2hZDI8NlyhZSXTaJRZlGW3AATgXqVE1DvTF3Ja59ZdgJGLbGuapQDiMM8DASLo_riqd1RnsYmqbqBYnv-DmG3fYYZgBNugpXiSMiMDwJSfz373CivutWVWd6gJxeZTsy41cigTkZjr_B8NeChmNYDODG7qRlKdXjjzGRrIxPmX4neqD9d2BHe_nXl2iYWDgWeXgJZJMokn8EkmNtXBP50WJfvNTgcPzbBHAKVflbi5e4JDnoM6kw_103608ZIRJ2YXUkc98Vf9luAvDvWmf7ET70tO1E4eESTxxkRtBwF3omh9w915FbD8klr2AHTMZPnlXv6heiYAIinA7-YvpiZMUBRDsmEWsrQQvJAzq-QgKQBj1VoV1fisRAGe8bf8m5agRfDps1tuCGvKfEqGnZUQbaodNi8pMFDCAvE=w3840-h848-no?authuser=0'

st.image(img_link)


model_selection = st.radio('Please select algorithm',['Logistic Regrestion','Random Forest','SVC'])
if model_selection == 'Logistic Regrestion':
    loaded_model = lr_model
    loaded_model_proba = loaded_model
elif model_selection == 'Random Forest':
    loaded_model = rf_model
    loaded_model_proba = rf_model 

elif model_selection == 'SVC':
    loaded_model = svc_model
    loaded_model_proba = svc_model_proba

st.markdown("""---""")
tab1, tab2 = st.tabs(["Full FiFa World Cup 2022 Predicting", "Predict between 2 teams"])

with tab1:



    bt = st.button('Start Predicting!')


    if bt:
        main()

with tab2:
    st.session_state.projects=teams
    def submit_delete_project():
        if st.session_state['selected1'] == st.session_state['selected2']:
            st.session_state['selected1'] = st.session_state.projects[random.choice(range(len(st.session_state.projects)))]
    team1 = st.selectbox("Select Team 1",st.session_state.projects,key='selected1',on_change = submit_delete_project,index=1)
    team2 = st.selectbox("Select Team 2",st.session_state.projects,key='selected2',on_change = submit_delete_project,index=2)
    bt_2_team = st.button("Predict!")
    if bt_2_team:
        predict_func(team1,team2)
        st.balloons()


    # Using "with" notation


