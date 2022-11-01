




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
        result_df.columns=['time']

        result_df = result_df.loc[teams]
        
        total_count = result_df['time'].sum()
        result_df['percent'] = result_df['time'].map(lambda x: (x/total_count)*100)
        result_df = result_df.sort_values(by='percent',ascending = False)

        return result_df
    else:
        print(f'{year} is not a World Cup event')