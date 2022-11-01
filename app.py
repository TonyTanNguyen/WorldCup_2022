import streamlit as st
import pandas as pd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
import random
import pickle
import networkx as nx

import random
from collections import Counter
import json
import pandas as pd
import numpy as np
import time
#import simulation
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb

# pd.options.st.table.float_format = "{:,.3f}".format
filename_rf = 'RF_WC_Predictor.sav'
filename_lr = 'Logic_WC_Predictor.sav'
filename_svc = 'SVC_WC_Predictor.sav'
filename_svc_proba = 'SVC_WC_Predictor_proba.sav'

rf_model = pickle.load(open(filename_rf, 'rb'))
lr_model = pickle.load(open(filename_lr, 'rb'))
svc_model = pickle.load(open(filename_svc, 'rb'))
svc_model_proba = pickle.load(open(filename_svc_proba, 'rb'))




flags = {
    "Uruguay":'🇺🇾',
    "Netherlands": '🇳🇱',
    "Belgium": '🇧🇪',
    "France": '🇫🇷',
    "England":'🏴󠁧󠁢󠁥󠁮󠁧󠁿',
    "Brazil":'🇧🇷',
    "Germany": '🇩🇪',
    "Argentina":'🇦🇷',
    "Switzerland": '🇨🇭',
    "Croatia": '🇭🇷',
    "Denmark":'🇩🇰',
    "Spain":'🇪🇸',
    "Mexico":'🇲🇽',
    "USA":'🇺🇸',
    "Portugal":'🇵🇹',
    "Senegal":'🇸🇳',
    "South Korea":'🇰🇷',
    "Morocco":'🇲🇦',
    "Serbia":'🇷🇸',
    "Japan":'🇯🇵',
    "Ecuador":'🇪🇨',
    "Tunisia":'🇹🇳',
    "Poland":'🇵🇱',
    "Iran":'🇮🇷',
    "Costa Rica":'🇨🇷',
    "Canada":'🇨🇦',
    "Cameroon":'🇨🇲',
    "Australia":'🇦🇺',
    "Saudi Arabia":'🇸🇦',
    "Wales":'🏴󠁧󠁢󠁷󠁬󠁳󠁿',
    "Ghana":'🇬🇭',
    "Qatar":'🇶🇦',
}


f = open("winrate_by_year")
# returns JSON object as 
# a dictionary
winrate = json.load(f)
f.close()

wc_participants = pd.read_excel('team_participate_wc_2022.xlsx',index_col=0)
wc_participants.fillna("")
wc_participants = wc_participants.replace("USA","United States")

df_ranking = pd.read_excel('ranking_over_time.xlsx',index_col=0)
df_ranking.rename(columns=({'IR Iran':"Iran","Korea Republic":
                            "South Korea","Côte d'Ivoire":"Ivory Coast","USA":"United States"}),inplace=True)



#Prepare input:
curent_ranking = pd.read_excel('FIFA RANK.xlsx')
current_ranking_dict = curent_ranking.set_index(keys='Country')['Rank'].to_dict()
wc_22_matches = pd.read_csv('matchs-schudule.csv',sep=';')
group_order = pd.read_csv('Qatar2022-teams.csv',sep=';')
group_order.columns = ['Team','Group']
teams = group_order['Team'].sort_values(ascending=True).to_list()

groupA = group_order[group_order['Group'] == 'A']['Team'].to_list()
groupB = group_order[group_order['Group'] == 'B']['Team'].to_list()
groupC = group_order[group_order['Group'] == 'C']['Team'].to_list()
groupD = group_order[group_order['Group'] == 'D']['Team'].to_list()
groupE = group_order[group_order['Group'] == 'E']['Team'].to_list()
groupF = group_order[group_order['Group'] == 'F']['Team'].to_list()
groupG = group_order[group_order['Group'] == 'G']['Team'].to_list()
groupH = group_order[group_order['Group'] == 'H']['Team'].to_list()

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

def simulation(df,year,times):
    if year in wc_participants.columns:
        
        teams = [t for t in wc_participants[year].values if t not in ["",np.nan]]
        #for participants only
        #cols = df[teams].columns.to_list()
        
        #for all countries
        cols = df.columns.to_list()[1:]

        #weights = df[df['year']==year][teams].iloc[0].to_list()
        weights = df[df['year']==year].iloc[0,1:].to_list()
        weights_with_winrate = []
        for i in range(len(weights)):
            if cols[i] in winrate[str(year)]:
                weights_with_winrate.append(weights[i] + (winrate[str(year)][cols[i]])*weights[i])
            else:
                weights_with_winrate.append(weights[i])
        
        
        result = {}

        item = random.choices(cols, weights=weights_with_winrate, k=times)

        count_dict = Counter(item)
        result_df = pd.DataFrame.from_dict(count_dict,orient='index')
        result_df.columns=['result']

        result_df = result_df.loc[teams]
        
        total_count = result_df['result'].sum()
        result_df['percent'] = result_df['result'].map(lambda x: (x/total_count)*100)
        result_df = result_df.sort_values(by='percent',ascending = False)

        return result_df
    else:
        print(f'{year} is not a World Cup event')

def predict_func(home_team,away_team):
    input_team = [filter_country(home_team),filter_country(away_team),True]
    home_rank = current_ranking_dict[input_team[0]]
    away_rank = current_ranking_dict[input_team[1]]

    average_rank = (home_rank + away_rank)/2
    rank_diff = home_rank - away_rank 
    rank_diff2 = away_rank - home_rank
    is_stake = input_team[2]

    input_for_predict = np.asarray([[average_rank,rank_diff,is_stake]])
    input_for_predict2 = np.asarray([[average_rank,rank_diff2,is_stake]])

    class_result = loaded_model.predict(input_for_predict)[0]
    class_result2 = loaded_model.predict(input_for_predict2)[0]

    probality = loaded_model_proba.predict_proba(input_for_predict)[0]
    probality2 = loaded_model_proba.predict_proba(input_for_predict2)[0]

    if class_result == class_result2:
        if probality[0] > probality2[0]:
            probality = probality2
            home_team,away_team = away_team,home_team



    probality_output = probality[0] if probality[0] > probality[1] else probality[1]


    probality_output_text = str(round(probality_output*100,3)) + '%'
    team_win = home_team if class_result else away_team
    result = [3,0,probality_output] if class_result else [0,3,probality_output]
    
#     st.markdown(f"Group {group_name}:")
    st.write(f"<b style='color:red'> {flags[home_team]}{home_team}</b> :soccer: <b style='color:red'>{flags[away_team]}{away_team}</b>: <b style='color:blue'>{flags[team_win]}{team_win}</b> wins with probability <b>{probality_output_text}</b>",unsafe_allow_html=True)
#     st.markdown("========================================================\n")
#     time.sleep(0.1)
    return result
def main():
    currentgroup = ''
    group_stage_result = {}
#     st.markdown('\n##### ***************** GROUP STAGE PREDICTING *****************')
    st.markdown("<h2 style='text-align: center';> &#x1F50E; GROUP STAGE PREDICTING &#x1F50D; </h2>",unsafe_allow_html=True)
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
    round_of_16_pairs_a = []
    
    st.markdown("\n\n\n##### ======= SCORE AFTER GROUP STAGE =======")
    
    for gr in group_stage_result_df['Group'].unique():
        current_group = group_stage_result_df[group_stage_result_df['Group']==gr]
        round_of_16_pairs_a.append([current_group['Country'][:2].values])
        current_group['Country'] = current_group['Country'].map(lambda x: flags[x] + x)
        st.table(current_group.reset_index(drop=True))
    
    st.markdown("""---""")
    # quater_final pairs
    
    
#     st.markdown("\n\n\n#### =================== ROUND OF 16 ===================")
    st.markdown("<h2 style='text-align: center';> &#x1F50E; ROUND OF 16 &#x1F50D; </h2>",unsafe_allow_html=True)
   
    predict_top_16(round_of_16_pairs_a)
def predict_top_16(round_of_16_pairs):
    round_of_16_matches = []
    node = []
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
    
    # st.markdown("\n\n\n======= ROUND OF 16 IN TABLE =======")
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
    st.markdown("<h2 style='text-align: center';>&#x1F50E; QUATER-FINALS &#x1F50D;</h2>",unsafe_allow_html=True)
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
    st.markdown("<h2 style='text-align: center';>&#x1F50E; SEMI-FINALS &#x1F50D;</h2>",unsafe_allow_html=True)
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
    

    st.markdown('\n#### ========== Third place ==========')




#     st.markdown('\n#### ========== GRAND-FINALS ==========')
    st.markdown("<h2 style='text-align: center';>&#x1F50E; GRAND-FINAL &#x1F50D;</h2>",unsafe_allow_html=True)
    st.table(grand_final_df)

    champion = ''
    runners_up = ''
    grand_final_df['Team wins'] = ''
    grand_final_df['Proba_win'] = pd.Series().astype(float)

    for index, row in grand_final_df.iterrows():

        output_result = predict_func(row['Team 1'], row['Team 2'])
        champion = row['Team 1'] if output_result[0]==3 else row['Team 2']
        runners_up = row['Team 1'] if output_result[0]!=3 else row['Team 2']
    #     dump_semi.append(win_team)
    #     if len(dump_semi)==2:
    #          grand_final_list.append(dump_semi)
    #         dump_semi = []
        grand_final_df.loc[index,'Team wins'] = champion
        grand_final_df.loc[index,'Proba_win'] = round(output_result[2],3)
        node.append(champion)
    st.markdown('\n\n\n\n======= GRAND-FINALS RESULT IN TABLE ========')
    st.table(grand_final_df.reset_index(drop=True))

#     st.markdown('\n\n\n\n****======= FIFA WORLD CUP 2022 RESULT=======****')
    st.markdown("<h2 style='text-align: center; color:red'>FIFA WORLD CUP 2022 CHAMPION</h2>",unsafe_allow_html=True)
    st.markdown(f"### :trophy: {flags[champion]}{champion}")
    st.markdown(f"### 🥈 {flags[runners_up]}{runners_up}")

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
        node_dict[i] =  node[30-i]
    

    

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

st.markdown("<h2 style='text-align: center; color:#bd0042'>FIFA WORLD CUP 2022 PREDICTOR</h2>",unsafe_allow_html=True)

img_link = 'https://tgmresearch.com/images/Artboard_4.png'

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
tab1, tab2, tab3 , tab4 = st.tabs(["Full FIFA World Cup 2022 Predicting", "Predict between 2 teams", "Pick your top 16","Simulating Probability"])

def show_flag(selected_country):
    return flags[selected_country] + selected_country


with tab1:
	st.write("Start predicting with selected algorithm from the group stage until final match")
	bt = st.button('Start Predicting!')
	if bt:
		main()

with tab2:
    st.session_state.projects=teams
    def submit_delete_project():
        if st.session_state['selected1'] == st.session_state['selected2']:
            st.session_state['selected1'] = st.session_state.projects[random.choice(range(len(st.session_state.projects)))]
    team1 = st.selectbox("Select Team 1",st.session_state.projects,key='selected1',on_change = submit_delete_project,index=1, format_func = show_flag)
    team2 = st.selectbox("Select Team 2",st.session_state.projects,key='selected2',on_change = submit_delete_project,index=2, format_func = show_flag)
    bt_2_team = st.button("Predict!")
    if bt_2_team:
        predict_func(team1,team2)
        st.balloons()
		
with tab3:
    with st.container():
        col1,col2,col3,col4 = st.columns(4)
        with col1:
            groupA_sel = st.multiselect('Group A',groupA,max_selections = 2 , format_func = show_flag)
            # groupE_sel = st.multiselect('Group E',groupE,max_selections = 2, format_func = show_flag)
        with col2:
            groupB_sel = st.multiselect('Group B',groupB,max_selections = 2, format_func = show_flag)
            # groupF_sel = st.multiselect('Group F',groupF,max_selections = 2, format_func = show_flag)
        with col3:
            groupC_sel = st.multiselect('Group C',groupC,max_selections = 2, format_func = show_flag)
            # groupG_sel = st.multiselect('Group G',groupG,max_selections = 2, format_func = show_flag)
        with col4:
            groupD_sel = st.multiselect('Group D',groupD,max_selections = 2, format_func = show_flag)
            # groupH_sel = st.multiselect('Group H',groupH,max_selections = 2, format_func = show_flag)

    with st.container():
        col5,col6,col7,col8 = st.columns(4)
        with col5:
            # groupA_sel = st.multiselect('Group A',groupA,max_selections = 2 , format_func = show_flag)
            groupE_sel = st.multiselect('Group E',groupE,max_selections = 2, format_func = show_flag)
        with col6:
            # groupB_sel = st.multiselect('Group B',groupB,max_selections = 2, format_func = show_flag)
            groupF_sel = st.multiselect('Group F',groupF,max_selections = 2, format_func = show_flag)
        with col7:
            # groupC_sel = st.multiselect('Group C',groupC,max_selections = 2, format_func = show_flag)
            groupG_sel = st.multiselect('Group G',groupG,max_selections = 2, format_func = show_flag)
        with col8:
            # groupD_sel = st.multiselect('Group D',groupD,max_selections = 2, format_func = show_flag)
            groupH_sel = st.multiselect('Group H',groupH,max_selections = 2, format_func = show_flag)


    tab3_button  = st.button('Start Predicting!',key = 'dsfjksdkf')
    check_bt = st.button('Check Line up')
    if check_bt:
        check_if_ok = len(groupA_sel+groupB_sel+groupC_sel+groupD_sel+groupE_sel+groupF_sel+groupG_sel+groupH_sel)
        if check_if_ok == 16:
            teams_input = [[groupA_sel[0],groupB_sel[1]],[groupB_sel[0],groupA_sel[1]],[groupC_sel[0],groupD_sel[1]],[groupD_sel[0],groupC_sel[1]],[groupE_sel[0],groupF_sel[1]],[groupF_sel[0],groupE_sel[1]],[groupG_sel[0],groupH_sel[1]],[groupH_sel[0],groupG_sel[1]]]
            round_of_16_matches_df = pd.DataFrame(teams_input, columns=['Team 1','Team 2']).reset_index()
            round_of_16_matches_df['Team 1'] = round_of_16_matches_df['Team 1'].map(lambda x: flags[x] + x)
            round_of_16_matches_df['Team 2'] = round_of_16_matches_df['Team 2'].map(lambda x: flags[x] + x)
            round_of_16_matches_df['Match'] = round_of_16_matches_df.pop('index')+1
            st.table(round_of_16_matches_df)
        else:
            st.warning('Need 16 teams in total!')
    if tab3_button:
        check_if_ok = len(groupA_sel+groupB_sel+groupC_sel+groupD_sel+groupE_sel+groupF_sel+groupG_sel+groupH_sel)
        if check_if_ok == 16:
            # round_of_16_pairs_b = [[[groupA_sel[0],groupB_sel[1]]],[[groupA_sel[1],groupB_sel[0]]],[[groupC_sel[0],groupD_sel[1]]],[[groupC_sel[1],groupD_sel[0]]],[[groupE_sel[0],groupF_sel[1]]],[[groupE_sel[1],groupF_sel[0]]],[[groupG_sel[0],groupH_sel[1]]],[[groupG_sel[1],groupH_sel[0]]]]
            round_of_16_pairs_b = [[[groupA_sel[0],groupA_sel[1]]],[[groupB_sel[0],groupB_sel[1]]],[[groupC_sel[0],groupC_sel[1]]],[[groupD_sel[0],groupD_sel[1]]],[[groupE_sel[0],groupE_sel[1]]],[[groupF_sel[0],groupF_sel[1]]],[[groupG_sel[0],groupG_sel[1]]],[[groupH_sel[0],groupH_sel[1]]]]

        # round_of_16_matches_df = pd.DataFrame(teams_input, columns=['Team 1','Team 2']).reset_index()
        # round_of_16_matches_df['Match'] = round_of_16_matches_df.pop('index')+1
            predict_top_16(round_of_16_pairs_b)
        
            st.balloons()
        else:
            st.warning('Cannot Predict, need 16 teams in total!')
    # Using "with" notation

with tab4:
	st.write('We generate opportunity of being World Cup champion for each participants by using probability simulating events. Choose the year of World Cup and how many times you would like to simulate!')
	simu_button = st.button('Start simulating!')
	select_simu = st.selectbox('Select year:',[1994,1998,2002,2006,2010,2014,2018,2022])
	simulating_time = st.selectbox('How many times would you like to simulate?',[5000,10000,20000,50000,100000,1000000])
	if simu_button:
        
		simu_df = simulation(df_ranking,select_simu,simulating_time)
		for index,col in enumerate(simu_df.iloc):
			st.write(f"{index+1} {col.name} with probability: {col.percent}")
		st.table(simu_df)
		@st.cache
		def to_excel(df):
			output = BytesIO()
			writer = pd.ExcelWriter(output, engine='xlsxwriter')
			df.to_excel(writer, index=False, sheet_name='Sheet1')
			workbook = writer.book
			worksheet = writer.sheets['Sheet1']
			format1 = workbook.add_format({'num_format': '0.00'}) 
			worksheet.set_column('A:A', None, format1)  
			writer.save()
			processed_data = output.getvalue()
			return processed_data

		simu_df = simu_df.reset_index()
		simu_df.columns=['Team','result','percent']
		df_xlsx = to_excel(simu_df)
		st.download_button(label='📥 Download Current Result',data=df_xlsx,file_name= f'{select_simu}_{simulating_time}_simulation_times_output.xlsx')
