import csv
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime
import random 
import time

header = ['ts','name','bpm','oxyzen','attempt','score','tot_att','total_socre','total_2p_score','total_3p_score']
persons= ['Ezra','Joey', 'Woochul', 'Noah', 'Dj', 'Vinay','Luke','Miguel' ]
selected_man = 'Woochul'
def simulate_performance_report():
	dict_data = { hdr : 0 for hdr in header }
	persons_tot_att = { p : 0 for p in persons}
	persons_tot_score = { p : 0 for p in persons}
	persons_tot_3p_score ={ p : 0 for p in persons}
	persons_tot_2p_score ={ p : 0 for p in persons}
	perform_data = []

	for i in range(1000):
		#cur_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		cur_time = datetime.now().strftime('%H:%M:%S')	
		for p in persons:
			dict_data['ts'] = cur_time
			dict_data['name'] = p
			dict_data['bpm'] = random.randrange(120,160) # 60 - 100
			dict_data['oxyzen'] = random.randrange(90,100)
			dict_data['attempt'] = random.randrange(0,2) # if 
			dict_data['score'] = random.randrange(2,4) if dict_data['attempt'] == 1 else 0 
			persons_tot_att[p] += dict_data['attempt']
			persons_tot_score[p] += dict_data['score']
			persons_tot_3p_score[p] += 3 if dict_data['score'] == 3 else 0 
			persons_tot_2p_score[p] += 2 if dict_data['score'] == 2 else 0
			dict_data['tot_att'] = persons_tot_att[p]
			dict_data['total_socre'] = persons_tot_score[p]
			dict_data['total_2p_score'] = persons_tot_2p_score[p] 
			dict_data['total_2p_score'] = persons_tot_3p_score[p] 
			perform_data.append(dict_data)
			dict_data = dict()
			dict_data = { hdr : 0 for hdr in header } 
		time.sleep(1)
	#print(perform_data)
	df = pd.DataFrame(perform_data,columns = header)			 
	#print(df)	
	# saving the dataframe
	df.to_csv('players_performance.csv')
	return df

def analyze_data(df):
	kpis = ['total_attemtps','mean_bpm', 'mean_oxyzen','total_two_points','total_three_points','success_rate']
	persons_kpis = { name: {kpi : 0 for kpi in kpis } for name in persons}
	for name in persons: 
		df_person_data = df.loc[df['name'] == name]
		persons_kpis[name]['total_attemtps'] = sum(df_person_data['attempt'])
		persons_kpis[name]['mean_bpm'] = df_person_data['bpm'].mean()
		persons_kpis[name]['mean_oxyzen'] = df_person_data['oxyzen'].mean()
		persons_kpis[name]['total_two_points'] = df_person_data['total_2p_score'].max()/2
		persons_kpis[name]['total_three_points'] = df_person_data['total_2p_score'].max()/3
		persons_kpis[name]['success_rate'] = (persons_kpis[name]['total_two_points'] + persons_kpis[name]['total_three_points'])/persons_kpis[name]['total_attemtps'] * 100		
		# covernting dictionary to dataframe
	return pd.DataFrame.from_dict(persons_kpis)

df = pd.read_csv("salesfunnel.csv")

mgr_options = df["Manager"].unique()

#df_perform = simulate_performance_report()
df_perform = pd.read_csv(
    "players_performance.csv"
)
df_summary =  analyze_data(df_perform)
df_players_ranks = df_summary.sort_values(by='success_rate', axis=1, ascending = False)

selected_man=[]
for i in range(5):
	selected_man.append(df_players_ranks.columns[:5][i])

player_options = df_perform["name"].unique() 

app = dash.Dash(assets_folder='./')

summary_trace =[]
axis_y = []

graph1_points=['total_two_points', 'total_three_points', 'success_rate']
graph2_points=['mean_bpm', 'mean_oxyzen']

for point in graph1_points:
	for person in persons:
		y = df_summary[person][point]
		axis_y.append(y)
	summary_trace.append(go.Bar(x=persons, y=axis_y, name=point, offsetgroup=0,))
	axis_y=[]

for point in graph2_points:
	for person in persons:
		y = df_summary[person][point]
		axis_y.append(y)
	summary_trace.append(go.Bar(x=persons, y=axis_y, name=point, offsetgroup=1,))
	axis_y=[]


app.layout = html.Div([
    html.H2("Player Peformance Report"),
    html.Img(id='player_image',alt="Select a player", style={'height':100, 'width':100}),
    html.Div(
        [
            dcc.Dropdown(
                id="Man",
                options=[{
                    'label': i,
                    'value': i
                } for i in player_options],
                value='All Players'),
        ],
        style={'width': '25%',
               'display': 'inline-block'}),
        dcc.Graph(id='performance-graph'),

	html.H2("Performance Summary"),
    html.Div(
    	style={'width': '25%',
               'display': 'inline-block'}),
        dcc.Graph(
        	id='summary-graph',
        	figure={
            	'data': summary_trace,
            	'layout':
           		 go.Layout(title='Shoot Success Rate along with BPM and Oxyzen Level', barmode='group')
        	}),
    
    html.H2("Recomend to play Top5 Best condition players"),
    html.Img(src=app.get_asset_url(selected_man[0]+'.png'), style={'height':100, 'width':100}),
	html.Div(f'{selected_man[0]}', style={'display': 'inline-block','vertical-align': 'middle'}),
    html.Img(src=app.get_asset_url(selected_man[1]+'.png'), style={'height':100, 'width':100}),
  	html.Div(f'{selected_man[1]}', style={'display': 'inline-block','vertical-align': 'middle'}),
    html.Img(src=app.get_asset_url(selected_man[2]+'.png'), style={'height':100, 'width':100}),
    html.Div(f'{selected_man[2]}', style={'display': 'inline-block','vertical-align': 'middle'}),
    html.Img(src=app.get_asset_url(selected_man[3]+'.png'), style={'height':100, 'width':100}),
    html.Div(f'{selected_man[3]}', style={'display': 'inline-block','vertical-align': 'middle'}),
    html.Img(src=app.get_asset_url(selected_man[4]+'.png'), style={'height':100, 'width':100}),
    html.Div(f'{selected_man[4]}', style={'display': 'inline-block','vertical-align': 'middle'}),

    ],

)
@app.callback(
    dash.dependencies.Output('player_image', 'src'),
    [dash.dependencies.Input('Man', 'value')])
def update_image_src(Man):
    return app.get_asset_url(Man+'.png')

@app.callback(
    dash.dependencies.Output('performance-graph', 'figure'),
    [dash.dependencies.Input('Man', 'value')])
def update_graph(Man):
	if Man == "All Players":
		df_plot = df_perform.copy()
	else:
		df_plot = df_perform[df_perform['name'] == Man]
	pv = pd.pivot_table(
	    df_plot,
	    index=['ts'],
	    columns=["name"],
	    values=['score'],
	    aggfunc=sum,
	    fill_value=0)

	trace1 = go.Scatter(x=df_plot['ts'], y=df_plot['bpm'],
		mode='lines',
		name='heart rate')
	trace2 = go.Scatter(x=df_plot['ts'], y=df_plot['oxyzen'],
		mode='lines',
		name='oxyzen level')

	trace3 = go.Bar(x=df_plot['ts'], y=df_plot['score'], name='(0) fail, (2)points, (3) points')
	trace4 = go.Bar(x=df_plot['ts'], y=df_plot['attempt'], name='attempt')

	return {
		'data': [trace1, trace2, trace3, trace4],
		'layout':
		go.Layout(
			title="Perofrmace Result(BPM,Oxyzen level,Shooting) for {}".format(Man),
			barmode='stack'
			)
	}



if __name__ == '__main__':
    app.run_server(debug=True)

