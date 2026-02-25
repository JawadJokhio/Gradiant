import json
import os

p = r'c:\Users\KIET\OneDrive\Desktop\Geography\data\geography_data.json'
try:
    with open(p, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    data['glaciers'] = [
        {'id':'siachen','name':'Siachen Glacier','coordinate':[35.4212,77.1095],'facts':'World\'s second longest glacier (76km), Karakoram Range.'},
        {'id':'baltoro','name':'Baltoro Glacier','coordinate':[35.7364,76.3811],'facts':'63km long, source of the Shigar River.'},
        {'id':'biafo','name':'Biafo Glacier','coordinate':[35.9167,75.8333],'facts':'67km long, meets the Hispar glacier at Hispar La.'}
    ]
    data['canals'] = [
        {'id':'nara','name':'Nara Canal','path':[[26.8,68.9],[26.0,69.0],[25.0,69.2]],'color':'#3b82f6','facts':'Longest canal in Pakistan.'},
        {'id':'rohri','name':'Rohri Canal','path':[[27.7,68.9],[26.5,68.5],[25.5,68.3]],'color':'#3b82f6','facts':'Major perennial canal from Sukkur Barrage.'},
        {'id':'thal','name':'Thal Canal','path':[[32.5,71.5],[31.5,71.2],[30.5,71.0]],'color':'#3b82f6','facts':'Irrigates the Thal desert.'}
    ]
    if 'energy_resources' in data:
        data['energy_resources'].extend([
            {'id':'parco','name':'PARCO Mid-Country Refinery','coordinate':[30.0,71.0],'type':'refinery','facts':'Largest oil refinery in Pakistan, near Mahmood Kot.'},
            {'id':'nrp','name':'National Refinery','coordinate':[24.8,67.0],'type':'refinery','facts':'Refinery near Karachi.'}
        ])
    
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print("Successfully updated geography_data.json")
except Exception as e:
    print(f"Error: {e}")
