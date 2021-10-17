# -*- coding: utf-8 -*-
"""Hunger Games.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1IXkwXa-XD2O0B0Z6CiYf20YNGSN0EV9U

- Create a BA graph with 300 nodes
- Assign each player(node) a marksmanship, “which can take on one of the three possible values: [0.5, 0.8, 1]. Marksmanship levels are randomly distributed in the network with equal initial proportions.”
- “At each step in the game: one node is chosen randomly. 
	- This chosen player, in turn, randomly selects two opponents among his neighbour nodes, and the three players play a sequential truel with a fixed shooting order. 
	- However, if the initially chosen player has only one neighbour, a duel occurs. 
	- Moreover, players are assumed to be rational (i.e., they strictly follow the strongest opponent strategy but never aim at a player of the same type). 
	- Finally, the losers of either a truel or a duel are removed from the network, and if a node has no neighbours left, it will be reattached to the network along the lines of the preferential-attachment algorithm that was used to create the scale-free network.
	- In the unlikely event that no strongest player exists because all players chosen have the same level of marksmanship, no duel or truel will be played. In this case, a new node and its neighbours will be randomly selected to continue the game.”
- The program will iterate until no more duels or truels can be played under these rules
"""

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import seaborn as sns

# modified version of the NetworkX implementation from
# https://github.com/networkx/networkx/blob/master/networkx/generators/random_graphs.py
# by Allen Downey
import random
from random import choices

def flip(p):
    return np.random.random() < p


def _random_subset(repeated_nodes, k):
    """Select a random subset of nodes without repeating.
    
    repeated_nodes: list of nodes
    k: size of set
    
    returns: set of nodes
    """
    targets = set()
    while len(targets) < k:
        x = random.choice(repeated_nodes)
        targets.add(x)
    return targets

def barabasi_albert_graph(n, k, seed=None):
    """Constructs a BA graph.
    
    n: number of nodes
    k: number of edges for each new node
    seed: random seen
    """
    if seed is not None:
        random.seed(seed)
    
    G = nx.empty_graph(k)
    targets = set(range(k))
    repeated_nodes = []

    for source in range(k, n):

        G.add_edges_from(zip([source]*k, targets))

        repeated_nodes.extend(targets)
        repeated_nodes.extend([source] * k)

        targets = _random_subset(repeated_nodes, k)

    return G

class HungerGames:
  def __init__(self, n, k, seed=None):
    self.k = k
    self.G = barabasi_albert_graph(n=300, k=10, seed = seed)
    self.assign_marksmanships()
    self.marksmanships = dict(list(self.G.nodes(data='marksmanship')))


  """Code below assigns marksmanships to each player and show that it works."""
  def assign_marksmanships(self):
    list_of_marksmanships = [0.5, 0.8, 1]
    for node in self.G.nodes():
      self.G.nodes[node]["marksmanship"] = random.choice(list_of_marksmanships)


  def random_duel(self, players):

    if self.marksmanships[players[0]] == self.marksmanships[players[1]]:
      return players
      
    self.duel_count += 1
    while len(players) == 2 :
      random.shuffle(players)
      starting_player = players[0]
      if flip(self.marksmanships[starting_player]):
        other_player = players[1]
        players.remove(other_player)
        self.G.remove_node(other_player)

    return players


  def sequential_duel(self, players, starting_player = None):
    players.sort(key=lambda player: self.marksmanships[player], reverse=False)

    if starting_player == None:
      [starting_player, other_player] = players
    else:
      if starting_player == players[0]:
        other_player = players[1]
      else:
        other_player = players[0]

    players = [starting_player, other_player]

    # If marksmanships between players are equal, considered a tie
    if self.marksmanships[starting_player] == self.marksmanships[other_player]:
      #print("Tie in duel!")
      return players

    shot_count = 0
    while len(players) == 2 :
      player = players[shot_count%2]
      opponent = players[(shot_count+1)%2]
      if flip(self.marksmanships[player]):
        players.remove(opponent)
        self.G.remove_node(opponent)
    return players

  def sequential_truel(self, players):
    players.sort(key=lambda player: self.marksmanships[player], reverse=False)
    [c, b, a] = players

    #If marksmanships between players are same, considered a tie
    if self.marksmanships[c] == self.marksmanships[b] and self.marksmanships[c] == self.marksmanships[a]:
      #print("Tie!")
      return players

    self.truel_count += 1
    #Formated x attack y (or z if x and y have same marksmanship)
    strongest_opponent_strategy = {c: [a,b], b: [a,c], a : [b, c]}

    shot_count = 0
    while len(players) == 3:
      player = players[shot_count%3]
      #if player hits
      if flip(self.marksmanships[player]):
        opponent_strong = strongest_opponent_strategy[player][0]
        opponent_weak = strongest_opponent_strategy[player][1]
        if self.marksmanships[player] != self.marksmanships[opponent_strong]:
          players.remove(opponent_strong)
          self.G.remove_node(opponent_strong)
        elif self.marksmanships[player] != self.marksmanships[opponent_weak]:
          players.remove(opponent_weak)
          self.G.remove_node(opponent_weak)
      shot_count += 1
      
    #Goes into a seqeuntial duel after one player is eliminated
    return self.sequential_duel(players, starting_player = players[shot_count%2])



  """Make this into a stand alone function that can be repeated. That way, we can establish an end-case before it is called. """

  # Choose a random player and put them in a duel/truel

  def step(self):
    """
    Make a random player in G compete in either a duel or truel
    depending on how many neighbors it has.
    """
    #Get random player
    players = [random.choice(list(self.G.nodes()))]
    # if this player has at least two neighbors, go into a truel; otherwise, go into a duel
    if len(self.G[players[0]]) > 1:
      players.extend(_random_subset(list(self.G[players[0]]), 2))
      #print("Battle " + str(counter) + ": ", players)
      players = self.sequential_truel(players)

    elif len(self.G[players[0]]) == 1:
      players.extend(_random_subset(list(self.G[players[0]]), 1))
      players = self.random_duel(players)
      
    #Clear list after done
    players = []

  """Reattachment function."""

  def reattachment_check(self):
    """
    G : graph
    """     
    degrees = list(self.G.degree())
    nodes, degs = map(list,zip(*degrees))

    k = min([self.k, len(nodes) - 1])

    if k != 0:
      for node in self.G.nodes:
        if len(self.G[node]) == 0:
          start_node = node
          start_node_index = nodes.index(start_node) 
          # print(start_node_index)

          del nodes[start_node_index]
          del degs[start_node_index]

          end_nodes = choices(nodes, degs, k = k)
          edges = [(start_node, end_nodes[i]) for i in range(k)]

          self.G.add_edges_from(edges)

  """Now this next function defines the end case. The end-case holds to be true if, for every node in the graph:
  - The node has either no neighbors, or
  - The neighbors of the node have the same marksmanship as the original node.
  """

  def check_for_end_case(self):
    """
    Returns True if end case as defined above is achieved. Returns False if not.
    """
    for n in self.G:
      #Check if the node has at least one neighbor
      neighbors = list(self.G[n])
      if len(set(self.marksmanships[neighbor] for neighbor in neighbors)) > 1:
        return False
    return True

  def loop(self):
    self.truel_count =  0
    self.duel_count = 0
    finished = False
    battle_count = 0
    # While there are less than 100,000 battles or the end case is not reached
    while (battle_count < 100000) and (finished != True):
      battle_count += 1
      self.reattachment_check()
      self.step()
      self.check_for_end_case()
    
    #Return the number of red, blue, and black players
    reds = []
    blues = []
    blacks = []
    for n in self.G:
      if self.marksmanships[n] == 1:
        reds.append(n)
      elif self.marksmanships[n] == 0.8:
        blues.append(n)
      else:
        blacks.append(n)
    
    return [len(reds), len(blues), len(blacks)]



"""Now, we can use Monte-Carlo experimentation to figure out the average number of red, blue, and black players, respectively, that will survive at the end of random conditions. We will loop through 10 random seeds, and for each starting condition, each one is run 10 times.
(NOTE: Currently, this program runs through 10 million duels/truels and can take approximately a half-hour to run.)
"""
def monte_carlo(n, k, seed, runs):
  """
  Runs the simulation k times for a random seed.
  """
  res = np.array([0.0,0.0,0.0])
  for run in range(runs):
    print("run:" +str(run))
    simulation = HungerGames(n, k, seed)
    winners = np.array(simulation.loop())
    res += winners
  return res/k

# #########
# res = np.array([0.0,0.0,0.0])
# for seed in range(10):
#   winners = monte_carlo(300, 10, seed, 10)
#   res += winners
# res = (res/10).tolist()
# #print(res)

# """Create a bar graph of the results, by percentage."""

# reds, blues, blacks = res
# sum = reds + blues + blacks
# percent_reds = reds/sum * 100
# percent_blues = blues/sum * 100
# percent_blacks = blacks/sum * 100

# x = ['reds', 'blues', 'blacks']
# y = [percent_reds, percent_blues, percent_blacks]

# plt.bar(x,y)
# plt.ylabel('Percentage of Winners (%)')
# plt.title('Average Percentages of Each Player Remaining')
# plt.show()
n, k = 300, 2
seed = 3
simulation = HungerGames(n, k, seed)
winners = np.array(simulation.loop())
print("truel_count:" + str(simulation.truel_count))
print("duel_count:" + str(simulation.duel_count))