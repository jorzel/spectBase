#!/usr/bin/python
# -*- coding: utf-8 -*- 
import os
import sys
import re

from Tkinter import Tk
from tkFileDialog import askdirectory
Tk().withdraw() 


def search( pattern = 'fid.refscan$' ):
	source_dir = askdirectory(title='Select search path')

	#wyszukiwanie folderow zawierajacych plik pattern
	file_list = []
	for root, subFolders, files in os.walk(source_dir):  
		for file in files:
			if re.search(pattern,file):
				file_list.append(root)  
				print(os.path.join(root,file))
	num_items = len(file_list)
	print(num_items)
	return file_list





