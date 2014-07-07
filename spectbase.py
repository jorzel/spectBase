#!/usr/bin/python
# -*- coding: utf-8 -*- 
import os
import sys
import re
import conf
import lcmodel
from Tkinter import *
from ttk import *
from tkFileDialog import askopenfilename
from tkFileDialog import askdirectory 

scanner_set = ['bruker', 'ge', 'siemens']
b0_set = ['3t', '7t']

#Main Gui class definition
class Gui(Frame):  
	def __init__(self, parent):
		Frame.__init__(self, parent)   
		self.parent = parent
		self.header_conf = list()
		self.exams_conf = list()
		self.header = list()
		self.exams = list()		

		self.exam_list = list()
		self.starter = 0
		
		self.initUI()
		self.centerWindow()
		parent.protocol("WM_DELETE_WINDOW", self.handler)

	#close gui
	def handler(self):
		self.parent.destroy()
		self.parent.quit()

	def centerWindow(self):
		w = 400
		h = 400

		sw = self.parent.winfo_screenwidth()
		sh = self.parent.winfo_screenheight()

		x = (sw - w)/2
		y = (sh - h)/2
		self.parent.geometry('%dx%d+%d+%d' % (w,h,x,y))

	#Clear data buffer
	def clear(self):
		self.header_conf = list()
		self.exams_conf = list()
		self.header = list()
		self.exams = list()		

		self.exam_list = list()
		self.starter = 0	

		self.exam_list = []
		self.lb.delete(0,END)	

	#Read configuration (.csv) file
	def readConfig(self):
		self.header_conf, self.exams_conf, data_path = conf.readConf()
		for i in self.exams_conf:
			self.exams.append(i)
		if(len(self.header) == 0):
			for i in self.header_conf:
				self.header.append(i)
		self.exam_list = []
		self.lb.delete(0,END)
		id_index = conf.ismember("id", self.header_conf)
		study_index = conf.ismember("study", self.header_conf)
		for i in self.exams_conf[:]:
			print(os.path.join(i[id_index], i[study_index]))
			self.exam_list.append(os.path.join(i[id_index], i[study_index]))
		
		for i in self.exam_list[:]:
			self.lb.insert(END, i)

	#load existing database
	def loadBase(self):
		self.header, self.exams = conf.loadDatabase()
		self.starter = len(self.exams)				
		for i in self.exams_conf:
			self.exams.append(i)

	#start analyze data from config file  
	def startAnalysis(self):
		num_exams = len(self.exams)-self.starter	
		dest_dir = askdirectory(title='Select destination path')
		print("The program start analyzing your data")
		if(str(dest_dir) == "()"):
			print(" Error! You have not defined destination directory... The program breaks the action") 
		else:
			print("Destination path: "+ dest_dir)
			home = os.path.expanduser('~')
			data_path = './data'

			file_list = list()

			for i in self.exams[self.starter:]:
				id_index = conf.ismember("id", self.header)
				study_index = conf.ismember("study", self.header)
				exam_path = os.path.join(data_path, i[id_index], i[study_index])
				print("Conversion left %d" %num_exams)
				print("Now processing: " +exam_path)
				num_exams -= 1

				scanner_index = conf.ismember("scanner", self.header)
				scanner = i[scanner_index]
				if(conf.ismember(str(scanner).lower(), scanner_set) ==-1):
					print("Error! The field dedicated to 'scanner' has not been filled properly...") 	
					print("This exam will be ommited. Please check your 'config.csv' file")
					continue 
				b0_index = conf.ismember("b0", self.header)
				b0 = i[b0_index]
				if(conf.ismember(str(b0).lower(), b0_set) ==-1):
					print("Error! The field dedicated to 'b0' has not been filled properly...") 	
					print("This exam will be ommited. Please check your 'config.csv' file\n") 
					continue
				analysis_index = conf.ismember("analysis", self.header)
				analysis = i[analysis_index]

				if (str(analysis).lower() == "lcmodel"):
					[self.header, i]=lcmodel.analyzeSpectrum(exam_path, dest_dir, scanner, b0, self.header, i)			
				else:
					print("Error! The field dedicated to 'anylysis' has not been filled properly...") 	
					print("This exam will be ommited. Please check your 'config.csv' file") 

			#print(self.header)
			#print(self.exams)
			output_file = os.path.join(dest_dir, 'results.csv')
			if os.path.exists(output_file):
				os.system("rm "+ output_file)
			os.system("touch "+ output_file)
			conf.writeCsv(output_file, self.header, self.exams)
		print("The analysis is completed")


	def initUI(self):
		self.parent.title("spectBase Interface")
		self.style = Style()
		self.style.theme_use("default")

		frame = Frame(self, relief=RAISED, borderwidth=2)
		frame.pack(fill=BOTH, expand=1)
		self.pack(fill=BOTH, expand=1) 

		lbl = Label(frame, text="Your config.csv content:")
		lbl.grid(row=0, column=0)

		self.lb = Listbox(frame, width = 25, height = 15)
		self.lb.grid(row=1, column=0, columnspan=1, rowspan = 12)

		readconfButton = Button(frame, text="Read Config File", width=20, command=self.readConfig) 
		readconfButton.grid(row=1, column=1, sticky=N, padx=5)

		loadbaseButton = Button(frame, text="Load Existing Database", width=20, command=self.loadBase) 
		loadbaseButton.grid(row=2, column=1, sticky=N, padx=5)

		startButton = Button(frame, text="Start Analysis", width=20, command=self.startAnalysis) 
		startButton.grid(row=3, column=1, sticky=N, padx=5)

		clearButton = Button(frame, text="Clear all", width=20, command=self.clear)
		clearButton.grid(row=12, column=1, sticky=S, padx=5)
 

		quitButton = Button(self, text="Quit", command=self.handler)
		quitButton.pack(side=RIGHT)		
		   

def main():
	root = Tk()
	app = Gui(root)
	root.mainloop()  

if __name__ == '__main__':
	main()
