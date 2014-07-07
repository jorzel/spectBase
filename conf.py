#!/usr/bin/python
# -*- coding: utf-8 -*- 
import os
import sys
import csv
from tkFileDialog import askopenfilename

#load database if you want to add data to existing csv file
def loadDatabase():
	data = askopenfilename(title="Please select your .csv file")
	header = list()
	exam_list = list()
	try:
		with open(data, 'rb') as csvfile:
			reader = csv.reader(csvfile, delimiter=';', quoting=csv.QUOTE_NONE)	
			rownum = 0				
			i = 0	
			for row in reader:
				if rownum == 0:
					header = row
					rownum += 1
				elif rownum != 0:
					exam_list.append(row) 
		print("Database "+ data + " loaded")
	except Exception:
		print("Database cannot be loaded")	

	print header
	return (header, exam_list)

#write your output csv file
def writeCsv(filename, header, exams):	
	with open(filename, 'w') as csvfile:
		out = csv.writer(csvfile, delimiter=';')
		out.writerow(header)
		out.writerows(exams)
	

#check if string (a) is a member of a list (b)
#return list index if true or -1 if false
def ismember(a,b):
	ind=0	
	for i in b:
		if(str(a).lower()==str(i).lower()):
			return ind 
		ind +=1
	return -1		


#read configuration (.csv) file
def readConf():
	data = askopenfilename(title="Please select your config.csv file")
	data_path = os.path.abspath(data)
	print(data_path)
	header = list()
	exam_list = list()
	try:
		with open(data, 'rb') as csvfile:
			dialect = csv.Sniffer().sniff(csvfile.read(), delimiters=';,')
			csvfile.seek(0)
			reader = csv.reader(csvfile, dialect, quoting=csv.QUOTE_NONE)	
			rownum = 0				
			i = 0	
			for row in reader:
				if rownum == 0:
					header = row
					rownum += 1
				elif rownum != 0:
					exam_list.append(row) 
		if(ismember("B0", header)==-1):
			print("Error! There has to be 'B0' column in the config.csv")
			return ("empty", "empty", -1)
		id_index = ismember("id", header)
		if((id_index)==-1):
			print("Error! There has to be 'id' column in the config.csv")
			return ("empty", "empty", -1) 
		if(ismember("study", header)==-1):
			print("Error! There has to be 'study' column in the config.csv")
			return ("empty", "empty", -1)
		if(ismember("analysis", header)==-1):
			print("Error! There has to be 'analysis' column in the config.csv")
			return ("empty", "empty", -1)
	
		print("Config.csv file has been read properly. This is an exam list included in config.csv file:")
		id_index = ismember("id", header)
		study_index = ismember("study", header)
		#for i in exam_list[:]:
			#print(os.path.join(i[id_index], i[study_index]))
		return (header, exam_list, data_path)
	except Exception:
		print("Error! The config.csv file cannot be open properly")



