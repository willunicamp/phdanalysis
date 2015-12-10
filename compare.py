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
import math

#===============================================
#le o arquivo contendo
#funcao versao1 versao2 ...
def read_fault_file(filename):
	lines = [line.rstrip('\n').split(" ") for line in open(filename,"r")]
	dictionary = dict()
	for line in lines:
		dictionary[line[0]] = line[1:]
	return dictionary
		

#===============================================
#carrega um grafo de um arquivo DOT
#
def load_graph_from_dot(path):
	G = nx.Graph(nx.read_dot(path))
	#nx.write_gexf(G,"vim.gexf")
	nx.set_node_attributes(G, 'weight', 0)
	return G

#===============================================
#le arquivo de sequencia de chamadas criado pelo PIN
#
def load_call_sequence(path, as_dictionary = False):
	lines = [line.rstrip('\n').split(", ") for line in open(path,"r")]
	if as_dictionary == True:
		dictionary = dict()
		for k, v in lines[:-3]:
			dictionary[k] = v
		lines = dictionary
	return lines

#===============================================
#Une o grafo com uma sequencia de chamadas
#
def merge_sequence_graph(graph,sequence,golden=False):
	#zera a quantidade de chamadas
	g = cp.deepcopy(graph)
	if golden == True:
		nx.set_node_attributes(g, 'weight_golden', 0)
	else:
		nx.set_node_attributes(g, 'weight', 0)
		nx.set_node_attributes(g, 'inverse_weight', 0)
	for pair in sequence[:-3]:
		#print pair
		function = pair[0]
		weight = float(pair[1])
		if function in g.nodes():
			if golden == True:
				g.node[function]['weight_golden'] = weight
			else:
				g.node[function]['weight'] = weight
				g.node[function]['inverse_weight'] = 1.0/weight
	return g

#===============================================
#Calcula o total absoluto (modulo) da diferenca de 
#chamadas entre dois grafos
def diff_golden_and_faults(graph):
	total = 0
	for node in graph.nodes():
		total += abs(int(graph.node[node]['weight_golden']) - int(graph.node[node]['weight']))
	return total

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
	#print total
	return differences

#===============================================
#avalia o numero de chamadas da funcao por nivel
#partindo da funcao root
def calls_compare_by_level(graph, root, faults, level=0):
	#pega o grafo no nivel desejado a partir da funcao raiz,
	ego = nx.ego_graph(graph,root,radius=level)

	totals = list()
	#le todos os arquivos definidos por faults
	for filename in faults:
		#carrega a sequencia de chamadas com injecao
		file_path = "/home/will/PHD/results/"+filename+".out"
		if os.path.exists(file_path):
			seq = load_call_sequence(file_path)
			#insere a sequencia de chamadas de falhas no grafo
			call_graph = merge_sequence_graph(ego ,seq)
			#calcula a diferenca entre o numero de chamadas
			diff = diff_golden_and_faults(ego)
			totals.append(diff)

	avg = np.mean(totals)

	return avg, totals

#===============================================
#Creates a graph of the difference betweeen golden
#run and fault graph
def calls_difference_graph(graph, root, faults):
	#carrego todas as sequencias de injecao por tipo
	pos=nx.spring_layout(graph)
	for filename in faults:
		#carrega a sequencia de chamadas com injecao
		file_path = "/home/will/PHD/results/"+filename+".out"
		if os.path.exists(file_path):
			seq = load_call_sequence(file_path)
			#insere a sequencia de chamadas de falhas no grafo
			call_graph = merge_sequence_graph(graph ,seq)
			

			total = 0
			removing_nodes = list()
			sizes = list()
			colors = list()
			print call_graph.number_of_nodes()
			for node in call_graph.nodes():
				if abs(int(call_graph.node[node]['weight_golden']) - int(call_graph.node[node]['weight'])) < 100:
					removing_nodes.append(node)
				else:
					call_graph.node[node]['size'] = int(call_graph.node[node]['weight']) - int(call_graph.node[node]['weight_golden'])

			call_graph.remove_nodes_from(removing_nodes)
			if call_graph.number_of_nodes() > 0:
				for node in call_graph.nodes(data=True):
					sizes.append(int(math.sqrt(abs(int(node[1]['size'])+10))))
					colors.append(int(node[1]['size']))
				#calcula as posicoes de desenho
				plt.clf()
				nx.draw(call_graph,pos,cmap=plt.cm.plasma,node_size=sizes,node_color=colors,with_labels=False)
				# desenha a raiz maior e em cor diferente
				#nx.draw_networkx_nodes(call_graph,pos,nodelist=[root],node_size=300,node_color='k')
				plt.savefig("/home/will/PHD/results/graphs/"+filename+".png")
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
	nx.draw_networkx_nodes(hub_ego,pos,nodelist=[root],node_size=300,cmap=plt.cm.plasma)
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

def average_graph(function_averages):
	with plt.style.context('ggplot'):
		plt.figure(figsize=(16,9))
		plt.title(u'Functions call average after injection')
		plt.ylabel(u'calls average')
		plt.xlabel(u'level')
		for function, avg in function_averages.iteritems():
			x = range(len(avg))			
			plt.plot(x, avg, label=function)
			plt.yscale('log')
		plt.legend(loc=4)
	
		plt.savefig("average.png")
		plt.show()

#===============================================
#===============================================
#===============================================
if __name__ == "__main__":

	#carrega o grafo
	g = load_graph_from_dot("/home/will/workspace/dr/analysis-24-09/vim_oct1_2015.dot")
	#insere a sequencia de chamadas original no grafo	
	seq = load_call_sequence("/home/will/PHD/results/master.out")
	h = merge_sequence_graph(g,seq)

	#fault_types = ("ldeg.*", "hdeg.*")
	#calcula o diametro, que eh a maior quantidade de niveis
	#que pode ser necessario percorrer
	diameter = nx.diameter(h)

	injections = read_fault_file("hdeg.csv")
	
	for function, faults in injections.iteritems():
		print "===="
		print function
		for i in range(diameter):
			#avg, totals = calls_compare_by_level(h,"vim_free","/home/will/PHD/results/" , fault_type, i)
			avg, totals = calls_compare_by_level(h,function, faults, i)
			print "Level"+str(i)+": "+str(avg)
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
