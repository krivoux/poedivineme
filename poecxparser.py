import copy
import math
import os
import time
import networkx as nx
import matplotlib.pyplot as plt
import datetime
import requests
import csv
import re

sub= os.environ['SUB']
token=os.environ['TOKEN']
client_secret = os.environ['CLIENT_SECRET']


headers = {'User-Agent': 'OAuth poedivineapp/1.0.0 (contact: krivoux1@mail.ru)',
           'Content-Type': 'application/x-www-form-urlencoded',
           'Authorization': 'Bearer '+token}

data = {'client_id':'poedivineapp',
           'client_secret': client_secret,
           'grant_type':'client_credentials',
           'scope':'service:cxapi'}

dt = datetime.datetime.now().replace(microsecond=0,second=0,minute=0)
unix_now = int(time.mktime(time.strptime(str(dt), '%Y-%m-%d %H:%M:%S')))

hour_step = 1

next_change_id = str(unix_now-3600*hour_step)
#
API_uri = 'https://api.pathofexile.com/currency-exchange/'


# response = requests.post('https://www.pathofexile.com/oauth/token', headers=headers, data=data)
# response = requests.get(API_uri, headers=headers)
# print(response.text)


# def find_last_change_id():
#     next_change_id = '1776794400'
#     while True:
#         print(next_change_id)
#         response = requests.get(API_uri+str(next_change_id), headers=headers)
#         response.raise_for_status()
#         if response.json()["next_change_id"] != next_change_id:
#             next_change_id = response.json()["next_change_id"]
#         else: break
#     return next_change_id

current_league = 'Fate of the Vaal'
current_league = 'Mirage'


def get_league_markets(league):
    league_markets = []
    response = requests.get(API_uri+next_change_id, headers=headers)

    markets = response.json()["markets"]

    for market in markets:
        if market["league"] == league and list(market['volume_traded'].values())[0] > 0:
            league_markets.append(market)
        else: pass

    return league_markets



def savecsv(items):

    fieldnames=['league','market_id','volume_traded','lowest_stock','highest_stock','lowest_ratio','highest_ratio']
    print('Сохраняем!')

    with open('markets.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()  # writes the header row
        writer.writerows(items)  # writes all data rows

# print(get_league_markets(current_league))




def create_graph(league_markets):
    edges = []
    vertices = []
    pattern_u = r"\|(.*)"
    pattern_v = r"(.*)\|"


    for market in league_markets:
        u = re.search(pattern_u,market['market_id']).group(1)
        v = re.search(pattern_v,market['market_id']).group(1)
        w = round(math.log(market['volume_traded'][u]/market['volume_traded'][v]),2)
        r = round(math.log(market['volume_traded'][v]/market['volume_traded'][u]),2)
        edges.append([u,v,w])
        edges.append([v,u,r])
        vertices.append(u)
        vertices.append(v)

        vertices = list(set(vertices))

    return vertices,edges

def clean_deadends(g):
    cleaned_vertices = []
    cleaned_edges = []

    for vertex in g[0]:
        count = 0
        for edge in g[1]:
            if vertex == edge[0] or vertex == edge[1]:
                count += 1
            else: pass
        if count >= 3:
            cleaned_vertices.append(vertex)
        else: pass

    for edge in g[1]:
        if edge[0] in cleaned_vertices and edge[1] in cleaned_vertices:
            cleaned_edges.append(edge)
    return cleaned_vertices,cleaned_edges

graph = create_graph(get_league_markets(current_league))

cleaned_graph = clean_deadends(graph)

# print(cleaned_graph)

graph = (
    ['divine','chaos','scouring','chance'],
    [['divine','chaos', 1],['chaos','scouring',1],['scouring','chance',-0.5],['chance','chaos',-1]]
)

G = nx.DiGraph()

for edge in graph[1]:
    G.add_edge(edge[0], edge[1], weight=edge[2])

elarge = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] > 0.5]
esmall = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] <= 0.5]

pos = nx.spring_layout(G,seed=4, k=10)  # positions for all nodes - seed for reproducibility

# nodes
nx.draw_networkx_nodes(G, pos, node_size=700)

# edges
nx.draw_networkx_edges(G, pos, width=3)
# nx.draw_networkx_edges(
#     G, pos, edgelist=esmall, width=6, alpha=0.5, edge_color="b", style="dashed"
# )

# node labels
nx.draw_networkx_labels(G, pos, font_size=10, font_family="sans-serif")
# edge weight labels
edge_labels = nx.get_edge_attributes(G, "weight")
nx.draw_networkx_edge_labels(G, pos, edge_labels)

ax = plt.gca()
ax.margins(0.08)
plt.axis("off")
plt.tight_layout()
# plt.show()

def bellmanford(graph, src):
    dist = {graph[0][i]: {'dist': math.inf} for i in range(len(graph[0]))}
    dist[src]['dist'] = 0

    for i in range(len(graph[0])-1):
        i_dist = copy.deepcopy(dist) # иначе не работает

        # print(f"Прогон № {i+1} из {len(graph[0])-1}")
        for u,v,w in graph[1]:
            if i_dist[u]['dist']+w < i_dist[v]['dist'] and i_dist[u]['dist'] != math.inf:
                # print(f'Релаксировалось ребро {u, v, w}, обновляем расстояние с {i_dist[v]['dist']} до {dist[u]['dist']} + {w}')
                dist[v]['dist'] = i_dist[u]['dist']+w
                dist[v]['parent'] = u

    nc_verticies = []
    nc_paths = []

    for u,v,w in graph[1]:
        if dist[u]['dist'] + w < dist[v]['dist'] and dist[u]['dist'] != math.inf:
            dist[v]['parent'] = u
            nc_verticies.append(v)
    # print(nc_verticies)

    for vertex in nc_verticies:
        path = [vertex]
        for i in range(len(graph[0])):
            path.append(dist[path[i]]['parent'])
        nc_paths.append(path)
        # print(nc_paths)

    reverse_paths = []

    for path in nc_paths:
        reverse_path = []
        count = 0
        for i in range(len(path) - 1, -1, -1):
            if count == 2:
                break
            else:
                reverse_path.append(path[i])
                if path[i] == path[-1]:
                    count += 1
        reverse_paths.append(reverse_path)

    # print(reverse_paths)

    return reverse_paths,dist

# results=bellmanford(graph=cleaned_graph,src='divine')

removed_duplicated = []

markets = get_league_markets(current_league)
print(markets)

for result in results[0]:
    if result not in removed_duplicated:
        removed_duplicated.append(result)


pairs_with_rates = []


for i in removed_duplicated:
    for j in range(len(i)-1):
        for edge in cleaned_graph[1]:
            if edge[0]==i[j] and edge[1]==i[j+1]:
                pairs_with_rates.append([i[j],i[j+1],math.exp(edge[2])])


count = 0
for i in removed_duplicated:
    print(i)
    for j in range(len(i)-1):
        print(pairs_with_rates[j+count][2])
    count += len(i)-1


