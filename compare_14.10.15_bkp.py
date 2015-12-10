#!/usr/bin/env python

__author__ = "William Roberto de Paiva"
__license__ = "GPL"
__maintainer__ = "William Roberto de Paiva"
__email__ = "will.unicamp@gmail.com"
__status__ = "Production"


import networkx as nx
import os
import glob
from operator import itemgetter
import numpy as np
import matplotlib.pyplot as plt
import copy as cp

def load_graph_from_dot(path):
	G = nx.Graph(nx.read_dot(path))
	#nx.write_gexf(G,"vim.gexf")
	nx.set_node_attributes(G, 'weight', 0)
	return G

def load_call_sequence(path, as_dictionary = False):
	lines = [line.rstrip('\n').split(", ") for line in open(path,"r")]
	if as_dictionary == True:
		dictionary = dict()
		for k, v in lines[:-3]:
			dictionary[k] = v
		lines = dictionary
	return lines

def merge_sequence_graph(graph,sequence):
	g = cp.deepcopy(graph)
	for pair in sequence[:-3]:
		#print pair
		function = pair[0]
		weight = float(pair[1])
		if function in graph.nodes():
			g.node[function]['weight'] = weight
			g.node[function]['inverse_weight'] = 1.0/weight
	return g

def diff_graphs_weight(g1, g2):
	total = 0
	for node1, node2 in zip(g1.nodes(), g2.nodes()):
		total += abs(int(g1.node[node1]['weight']) - (g2.node[node2]['weight']))
	return total

def calls_compare_by_level(graph, root, path, injection_type, level=0):
	#caso o nivel seja maior que zero, pega parte do grafo
	if level != 0:	
		#pega o grafo no nivel desejado a partir da funcao raiz,
		ego = nx.ego_graph(graph,root,radius=level)
	else:
		#caso contrario, usa o grafo todo
		ego = graph
	total = 0
	for node in ego.nodes():
		total += int(ego.node[node]['weight'])
	
	totals = list()
	#le todos os arquivos definidos por injection_type	
	for filename in glob.glob(os.path.join(path, injection_type)):
		#carrega a sequencia de chamadas com injecao
		seq = load_call_sequence(filename)
		#insere a sequencia de chamadas no grafo
		call_graph = merge_sequence_graph(ego	,seq)
		#calcula a diferenca entre o numero de chamadas
		diff = diff_graphs_weight(ego,call_graph)
		totals.append(diff)

	avg = np.mean(totals)

	return avg, totals
	

#===============================================
#
#
def calls_compare(path, injection_type):
	#carrego a sequencia sem injecao de falhas
	master_seq = load_call_sequence(path+"master.out",True)
	total = 0
	for k,v in master_seq.iteritems():
		#conto as chamadas originais
		total += int(v)
	differences = dict()
	#carrego todas as sequencias de injecao por tipo
	for filename in glob.glob(os.path.join(path, injection_type)):
		#carrego uma sequencias como dicionario
		call = load_call_sequence(filename,True)
		#inicializo a diferenca em chamadas por zero
		diff = 0
		#passo em todas as chamadas feitas no master
		for k,v in master_seq.iteritems():
			total += int(v)
			#se a chamada ocorreu na injecao...
			if call.has_key(k):
				#somo a diferenca absoluta
				diff += abs(int(call[k]) - int(v))
			else:
				#somo a diferenca total
				diff += abs(int(v))
		differences[filename] = diff
	print total
	return differences

#DRAW FUNCTIONS

#===============================================
#funcao que desenha um "hub", ou seja,
#apenas um vertice e seus vizinhos, utilizando
#um ego graph
def draw_hub(G, root):
	#separa o ego graph a partir da raiz
	hub_ego=nx.ego_graph(G,root)
	#calcula as posicoes de desenho
	pos=nx.spring_layout(hub_ego)
	#desenha o grafo
	nx.draw(hub_ego,pos,node_color='b',node_size=50,with_labels=False)
	# desenha a raiz maior e em cor diferente
	nx.draw_networkx_nodes(hub_ego,pos,nodelist=[root],node_size=300,node_color='r')
	plt.show()

#===============================================
#funcao que desenha o grafico de
#distribuicao de graus
def degree_distribution(G):
	#calcula o histograma do grafo
	degree_sequence=nx.degree_histogram(G)

	# gera a lista de contagem dos graus
	x_list = []
	y_list = []
	for degree,num_of_nodes in enumerate(degree_sequence):
		if num_of_nodes > 0:
			x_list.append(degree)
			y_list.append(num_of_nodes)
	
	#plota em escala log log
	plt.loglog(x_list,y_list,'o',color='k')
	plt.title("Degree rank plot")
	plt.ylabel("number of nodes")
	plt.xlabel("degree")
	
	#salva figura no disco e exibe
	plt.savefig("degree_histogram.png")
	plt.show()

if __name__ == "__main__":

	#carrega o grafo
	g = load_graph_from_dot("/home/will/workspace/dr/analysis-24-09/vim_oct1_2015.dot")
	#insere a sequencia de chamadas original no grafo	
	seq = load_call_sequence("/home/will/PHD/results/master.out")
	h = merge_sequence_graph(g,seq)

	fault_types = ("ldeg.*", "hdeg.*")
	#calcula o diametro, que eh a maior quantidade de niveis
	#que pode ser necessario percorrer
	diameter = nx.diameter(g)

	for fault_type in fault_types:
		for i in range(diameter):
			avg, totals = calls_compare_by_level(h,"vim_free","/home/will/PHD/results/" , fault_type, i)
			avg, totals = calls_compare_by_level(h,function, faults_file_list, i)

			print avg
		print "\n"
	
	#paths = calls_by_level(g,"vim_free",1)	
	#print g.number_of_nodes()
	#print sorted(paths)
	#print paths.number_of_nodes()

	#draw_hub(g,"main")
	#degree_distribution(g)
	#print g.number_of_nodes()
	#c = calls_compare("/home/will/PHD/results/", 'ldeg.*')
	#f=open('out.txt', 'w+')
	#for k,v in c.iteritems():
	#	print k,",",v
	
	#avg = np.mean(c.values())
	#std = np.std(c.values())
	
	#print "Media: ",avg, "\nDesvio: ",std	
	'''	
	seq = load_call_sequence("/home/will/PHD/results/master.out")
	print("done call")
	g = merge_sequence_graph(g,seq)
	print g.nodes(data=True)
	'''
