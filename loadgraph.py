import networkx as nx
import compare

if __name__ == "__main__":
	g = compare.load_graph_from_dot("/home/will/workspace/dr/analysis-24-09/vim_oct1_2015.dot")
	seq = compare.load_call_sequence("/home/will/PHD/results/master.out")
	#insere a sequencia de chamadas original (golden-run) no grafo	
	h = compare.merge_sequence_graph(g,seq,golden=True)
	#calcula o diametro, que eh a maior quantidade de niveis
	#que pode ser necessario percorrer	
	diameter = nx.diameter(h)

	while True:
		print "Digite o nome do arquivo de falhas:"
		fault_file = raw_input()
		#recarrega o compare.py com modificacoes
		reload(compare)
		
		injections = compare.read_fault_file(fault_file)

		function_averages = dict()
		for function, faults in injections.iteritems():
			print "===="
			print function
			avg_list = list()
			for i in range(diameter):
				#avg, totals = calls_compare_by_level(h,"vim_free","/home/will/PHD/results/" , fault_type, i)
				avg, totals = compare.calls_compare_by_level(h,function, faults, i)
				avg_list.append(avg)
				print "Level"+str(i)+": "+str(avg)
			function_averages[function] = avg_list
			print "\n"

		compare.average_graph(function_averages)
