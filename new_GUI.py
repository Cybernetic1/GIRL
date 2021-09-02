# TO-DO:
# * What would be training example?  Probably manipulation of relation graphs
# * 

import os
from numpy import * 		# used in plotting
import chart_studio.plotly as py	# communicate with external plotly server
import plotly.graph_objs as go

from GIRL import Evolve, maxGens, maxDepth, popSize, \
	bouts, crossRate, mutationRate, cache, board

# title("Genetic evolution of logic rules")

# Install this Flask extension:
#	pip3 install flask-sse
#	sudo apt install redis-server (needed?)

from flask import Flask, send_from_directory
from flask_sse import sse
from multiprocessing import Process

app = Flask(__name__, static_folder="web/")
app.config["REDIS_URL"] = "redis://localhost"
app.register_blueprint(sse, url_prefix='/SSE')

@app.route('/evolve')
def start_evolve():
	# from genetic_programming import Evolve, maxGens, maxDepth, popSize, \
	#	bouts, crossRate, mutationRate, cache
	# global maxGens, popSize, maxDepth, bouts, crossRate, mutationRate
	# global best
	# maxGens = int(text1.get("1.0", tk.END)[:-1])

	# execute the algorithm as a process:
	heavy_process = Process(target=Evolve, daemon=True)
	heavy_process.start()
	return "Evolve started!"

@app.route('/send')
def send_message():
	sse.publish({"message": "Hello!"}, type='message')
	return "Message sent!"

@app.route('/favicon.ico')
def favicon():
	return send_from_directory(app.root_path,
		'favicon.ico', mimetype='image/vnd.microsoft.icon')

def draw_board():
	global board
	# Send through SSE to GUI.js such that it plots the board
	sse.publish({"data" : "".join(map("".join,board))}, type="message")
	return

# def start_server():
app.run(host='127.0.0.1', port=7000)

print("Here?")

def plot_population(pop):
	screen2.fill((0x00,0x00,0x00))
	H = 500
	h = float(H) - 3.0
	x = 1.0
	dx = 999.0 / len(pop)
	# dn = int(math.ceil(dx))
	dn = int(dx)
	ymax = abs(pop[-1]['fitness'])
	print(ymax)
	for child in pop:
		z = child['fitness']
		x += dx
		if z < 0.0:
			pygame.draw.line(screen2, (0xFF,0x00,0x00), [int(x),H], [int(x),H+int(z*1.0)], dn)
		else:
			y = h / (1.0 + math.exp(-0.001*z))
			# y = int(z * h / ymax)
			# if math.isnan(y):
			#	y = H - 3
			# elif y > H - 3:
			#	y = H - 3
			pygame.draw.line(screen2, (0x00,0x00,0xFF), [int(x),H], [int(x),H-y], dn)
	pygame.display.flip()

"""
def butt_train_pop():
	from genetic_programming import Evolve, maxGens, maxDepth, popSize, \
		bouts, crossRate, mutationRate, cache
	# global maxGens, popSize, maxDepth, bouts, crossRate, mutationRate
	# global best
	maxGens = int(text1.get("1.0", tk.END)[:-1])
	popSize = int(text1c.get("1.0", tk.END)[:-1])
	maxDepth = int(text1b.get("1.0", tk.END)[:-1])
	bouts = int(text1a.get("1.0", tk.END)[:-1])
	# p_repro = float(text0c.get("1.0", tk.END)[:-1])
	crossRate = float(text0b.get("1.0", tk.END)[:-1])
	mutationRate = float(text0a.get("1.0", tk.END)[:-1])

	# execute the algorithm
	Evolve()
	print("Done!")
	from subprocess import call
	call(["beep"])

def butt_export_graph():
	s = text2.get("1.0", tk.END)
	if s == "\n":
		fname = "formula.dot"
	else:
		fname = s[:-1]
	print("Exporting best formula as graph....")
	export_tree_as_graph(best['target'], fname)
	from subprocess import call
	call(["dot", "-Tpng", "-O", fname])
	call(["eog", fname + ".png"])

def butt_print_best():
	# print "condition = "
	# print print_tree(best['cond'])
	print("target = ")
	print(print_tree(best['target']))

def butt_verify_best():
	sum_fitness = 0.0
	sum_squares = 0.0
	num_tests = 100
	for i in range(0, num_tests):
		time = random.randint(100, datasize - 10)
		target = eval_tree(best['target'], time)
		profit = fitness(best['target'])
		print("[", time, "]", round(target,2), round(profit,2))
		sum_fitness += profit
		sum_squares += (profit * profit)
	print("total profit =", round(sum_fitness,2))
	avg = sum_fitness / num_tests
	print("average profit per day =", round(avg,2))
	print("variance =", math.sqrt(sum_squares / num_tests - avg * avg))

def butt_verify_best_full():
	sum_fitness = 0.0
	sum_squares = 0.0
	N = float(datasize - 110) / 100.0
	for i in range(0, datasize - 110):
		print(round(i / N, 0), "%\r", end=' ')
		time = i + 100
		# target = eval_tree(best['target'], time)
		profit = fitness(best['target'])
		# print "[", time, "]", round(target,2), round(profit,2)
		sum_fitness += profit
		sum_squares += (profit * profit)
	print("total profit =", sum_fitness)
	N = float(datasize - 110)
	print("N =", N)
	avg = sum_fitness / N
	print("average profit =", avg)
	print("variance =", math.sqrt(sum_squares / N - avg * avg))

def butt_export_Excel():
	print("Saving to Excel....")
	s = textC.get("1.0", tk.END)
	if s == "\n":
		f = open("results.csv", 'w')
	else:
		f = open(s[:-1], 'w')
	N = float(datasize - 110) / 100.0
	for i in range(0, datasize - 110):
		print(round(i / N, 0), "%\r", end=' ')
		sys.stdout.flush()
		time = i + 100
		target = eval_tree(best['target'], time)
		profit = fitness(best['target'])
		f.write(str(round(target,2)) + ",")
		f.write(str(round(profit,2)) + "\n")
	print()
	# f.write("\n")
	f.close()

def butt_save_best():
	s = text8.get("1.0", tk.END)
	if s == "\n":
		f = open("formula", 'wb')
	else:
		f = open(s[:-1], 'wb')
	import pickle
	pickle.dump(best, f, pickle.HIGHEST_PROTOCOL)
	f.close()
	print("Formula saved")

def butt_load_best():
	s = text7.get("1.0", tk.END)
	if s == "\n":
		f = open("formula", 'rb')
	else:
		f = open(s[:-1], 'rb')
	import pickle
	best = pickle.load(f)
	f.close()
	cache.append(best)
	print("Formula loaded into cache")

def butt_input_best():
	s = text9.get("1.0", tk.END)
	s2 = s[:-1]
	s = s2.replace("+", "operator.add")
	s2 = s.replace("-", "operator.sub")
	s = s2.replace("*", "operator.mul")
	s2 = s.replace("/", "operator.div")
	target = eval(s2)
	print(target)
	best = {
		'target' : target,
		'fitness' : fitness(target, None, 500)
		}
	cache.append(best)
	print("Formula read into cache, current cache size =", len(cache))
	msgA.config(text = "cache size = " + str(len(cache)))

def butt_write_best():
	s = text8.get("1.0", tk.END)
	if s == "\n":
		import glob #, os
		# os.chdir("~/fintech")
		maxnum = 0
		suffix = ""
		for fname in glob.glob("f[0-9]*"):
			s = fname.split('.')
			num = int(s[0][1:])
			if num > maxnum:
				maxnum = num
				if len(s) == 2: suffix = s[1]
		fname = "f" + str(maxnum + 1)
	else:
		fname = s[:-1]
	f = open(fname, 'w')
	print(best['target'], file=f)
	f.close()
	print("Formula written to:", fname)

def butt_read_best():
	s = text7.get("1.0", tk.END)
	if s == "\n":
		import glob #, os
		# os.chdir("~/fintech")
		maxnum = 0
		suffix = ""
		for fname in glob.glob("f[0-9]*"):
			s = fname.split('.')
			print(s)
			num = int(s[0][1:])
			if num > maxnum:
				maxnum = num
				if len(s) == 2: suffix = s[1]
		fname = "f" + str(maxnum) + ('' if suffix == "" else '.' + suffix)
	else:
		import glob
		matches = glob.glob(s[:-1] + "*")
		if matches == []:
			fname = s[:-1]
		else:
			fname = matches[0]
	f = open(fname, 'r')
	s = f.read()
	f.close()
	s2 = s.replace("<built-in function add>", "operator.add")
	s = s2.replace("<built-in function sub>", "operator.sub")
	s2 = s.replace("<built-in function mul>", "operator.mul")
	s = s2.replace("<built-in function div>", "operator.div")
	target = eval(s)
	# print target
	global best
	best = {
		'target' : target,
		'fitness' : fitness(target, None, 500)
		}
	cache.append(best)
	print("Formula read into cache, current cache size =", len(cache))
	msgA.config(text = "cache size = " + str(len(cache)))

def butt_clear_cache():
	cache = []
	print("Cache cleared")
	msgA.config(text = "cache size = " + str(len(cache)))

# [s] save best formula\n\
# [l] load best formula\n\
button2 = tk.Button(root, text="Train population", command=butt_train_pop)
button2.grid(row=0,column=0,sticky=tk.W)

tk.Label(root,text="ℙ(crossover)",foreground='grey').grid(row=1, column=1, sticky=tk.W)
text0b = tk.Text(root,height=1,width=10)
text0b.grid(row=1,column=1,sticky=tk.E)
text0b.insert(tk.END, str(crossRate))
text0b.configure(state=tk.DISABLED,foreground='grey')

tk.Label(root,text="ℙ(mutate)").grid(row=1, column=2, sticky=tk.W)
text0a = tk.Text(root, height=1, width=10)
text0a.grid(row=1,column=2,sticky=tk.E)
text0a.insert(tk.END, str(mutationRate))
# tk.Label(root, text="P(___)").grid(row=0, column=2, sticky=tk.W)
# text0c = tk.Text(root, height=1, width=10)
# text0c.grid(row=1,column=2,sticky=tk.E)
# text0c.insert(tk.END, str(0.0))

tk.Label(root,text="population size").grid(row=2, column=1, sticky=tk.W)
text1c = tk.Text(root,height=1,width=10)
text1c.grid(row=2,column=1,sticky=tk.E)
text1c.insert(tk.END, str(popSize))

tk.Label(root,text="# generations").grid(row=2, column=2, sticky=tk.W)
text1 = tk.Text(root, height=1, width=10)
text1.grid(row=2,column=2,sticky=tk.E)
text1.insert(tk.END, str(maxGens))

tk.Label(root,text="bouts").grid(row=3, column=1, sticky=tk.W)
text1a = tk.Text(root, height=1, width=10)
text1a.grid(row=3,column=1,sticky=tk.E)
text1a.insert(tk.END, str(bouts))

tk.Label(root,text="depth",foreground='grey').grid(row=3, column=2, sticky=tk.W)
text1b = tk.Text(root, height=1, width=10)
text1b.grid(row=3,column=2,sticky=tk.E)
text1b.insert(tk.END, str(maxDepth))
text1b.configure(state=tk.DISABLED,foreground='grey')

button3 = tk.Button(root,text="export Rete network as graph", command=butt_export_graph, state=tk.DISABLED)
button3.grid(row=4,column=0,sticky=tk.W)
text2 = tk.Text(root, height=1, width=50)
text2.grid(row=4,column=1,columnspan=2)
text2.insert(tk.END, "rete_network.dot")
text2.configure(state=tk.DISABLED,foreground='grey')

button4 = tk.Button(root,text="examine rules", command=butt_print_best, state=tk.DISABLED)
button4.grid(row=5,column=0,sticky=tk.W)

button5 = tk.Button(root,text="verify rules", command=butt_verify_best, state=tk.DISABLED)
button5.grid(row=6,column=0,sticky=tk.W)

button6 = tk.Button(root,text="verify rules with full history", command=butt_verify_best_full, state=tk.DISABLED)
button6.grid(row=7,column=0,sticky=tk.W)

button7 = tk.Button(root,text="read rules from file", command=butt_read_best, state=tk.DISABLED)
button7.grid(row=8,column=0,sticky=tk.W)
text7 = tk.Text(root, height=1, width=50)
text7.grid(row=8,column=1,columnspan=2)
# text7.insert(tk.END, "f1")

button8 = tk.Button(root,text="write rules to file", command=butt_write_best, state=tk.DISABLED)
button8.grid(row=9,column=0,sticky=tk.W)
text8 = tk.Text(root, height=1, width=50)
text8.grid(row=9,column=1,columnspan=2)
# text8.insert(tk.END, "f1")

button9 = tk.Button(root,text="insert rule in Lisp format", command=butt_input_best, state=tk.DISABLED)
button9.grid(row=10,column=0,sticky=tk.W)
text9 = tk.Text(root, height=1, width=50)
text9.grid(row=10,column=1,columnspan=2)
text9.insert(tk.END, "(loves john mary)")
text9.configure(state=tk.DISABLED,foreground='grey')

buttonA = tk.Button(root,text="clear rules cache", command=butt_clear_cache, state=tk.DISABLED)
buttonA.grid(row=11,column=0,sticky=tk.W)
msgA = tk.Message(root, width=100, text="cache size = " + str(len(cache)))
msgA.grid(row=11,column=1,sticky=tk.W)

buttonC = tk.Button(root,text="save as Excel", command=butt_export_Excel, state=tk.DISABLED)
buttonC.grid(row=12,column=0,sticky=tk.W)
textC = tk.Text(root, height=1, width=50)
textC.grid(row=12,column=1,columnspan=2)
textC.insert(tk.END, "rules.csv")
textC.configure(state=tk.DISABLED,foreground='grey')

buttonD = tk.Button(root, text="quit", command=exit)
buttonD.grid(row=13,column=0)
# buttonD = tk.Button(root, text="Plot OHLC", command=plot_OHLC)
# buttonD.grid(row=13,column=0)
msg = tk.Message(root, width=800, text="(C) YKY 2019")
msg.grid(row=14,column=0,columnspan=3,sticky=tk.E)
root.update()
"""
