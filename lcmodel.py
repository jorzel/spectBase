#!/usr/bin/python
# -*- coding: utf-8 -*- 
import os
import sys
import re
import shutil
import csv
import search_database
import conf

#binary to raw file conversion
def bin2raw(file_path, dest_path, scanner):
	if (str(scanner).lower() == "bruker"):
		convert_bin2raw = ('~/.lcmodel/other/my-bin2raw ' + os.path.join(file_path,'fid ') +os.path.join(dest_path+'/ ' +'met'))
		os.system(convert_bin2raw)
		if os.path.exists(os.path.join(file_path,'fid.refscan')):			
			convert_ws_bin2raw = ('~/.lcmodel/other/my-bin2raw ' + os.path.join(file_path, 'fid.refscan ') +os.path.join(dest_path+'/ '+'h2o'))
			os.system(convert_ws_bin2raw)	
		else:
			print('No fid.refscan in: %s' %file_path)
	elif (str(scanner).lower() == "siemens"):
		for root, subFolders, files in os.walk(file_path):  
			for file in files:
				if re.search('.rda',file):
					convert_bin2raw = ('~/.lcmodel/siemens/bin2raw ' +os.path.join(root,file) +' '+os.path.join(dest_path+'/ ' +'met'))
					os.system(convert_bin2raw)


#read data and parameters from spreadsheet.csv and table file
def readCsv(path, header, exam, scaling_factor):
	print("Scaling factor:"+str(scaling_factor))
	if len(header) != 0:
		values = ['']*len(header)
	else:
		values = 0 
	file_path = os.path.join(path, 'table')
	filename = open(file_path, 'r')
	for line in filename:
		if (re.compile('FWHM = ').findall(line)):
			expression = re.compile('FWHM = \S+').findall(line)
			for word in expression:
				fwhm_string = str(re.findall('\S[^=^0-9]+', word)[0]).strip()
				fwhm_ppm = map(float, re.findall('\d+.\d+', word))			

		if (re.compile('hzpppm= ').findall(line)):
			expression = re.compile('hzpppm= \S+').findall(line)	
			for word in expression:
				freq = map(float, re.findall('\d+.\d+[e+]*\d+', word))
				fwhm_value = freq[0]*fwhm_ppm[0]

				if (conf.ismember(str(fwhm_string), header) >=0):
					trait_index = conf.ismember(str(fwhm_string), header)
					values[trait_index] = fwhm_value
				else:
					#remove white spaces and add to the header 
					header.append(fwhm_string)	
					values.append(fwhm_value)
	filename.close()

	filename = open(file_path, 'r')
	for line in filename:
		if (re.compile('S/N = ').findall(line)):
			expression = re.compile('S/N = \s+[0-9]+').findall(line)
			for word in expression:
				snr_string = str(re.findall('\S[^=^0-9]+', word)[0]).strip()
				snr_value = map(float, re.findall('\d+', word))[0]
				
				if (conf.ismember(str(snr_string), header) >=0):
					trait_index = conf.ismember(str(snr_string), header)
					values[trait_index] = snr_value
				else:
					#remove white spaces and add to the header 
					header.append(snr_string)	
					values.append(snr_value)
	filename.close()

	file_path = os.path.join(path, 'spreadsheet.csv')
	with open(file_path, 'rb') as csvfile:
		dialect = csv.Sniffer().sniff(csvfile.read(), delimiters=';,')
		csvfile.seek(0)
		reader = csv.reader(csvfile, dialect, quoting=csv.QUOTE_NONE)	
		rownum = 0				
		file_row = list()	
		for row in reader:
			if rownum == 0:
				file_header = row[2::3]
				rownum += 1
			elif rownum != 0:
				file_row.append(row[2::3])
	
		for row in file_row:
			for i, metabolite in enumerate(file_header):		
				#if it is impossible to find meteabolite in the header, add it to the header		
				if (conf.ismember(str(metabolite), header) >=0):
					metabolite_index = conf.ismember(str(metabolite), header)
					values[metabolite_index] = (float(row[i]))/scaling_factor
				else:
					header.append(metabolite)	
					values.append((float(row[i]))/scaling_factor)

	for v in values[len(exam):]:
		exam.append(v)
	return (header, exam)


#get basic information about spectrum
def getInfo(file_path, scanner, b0, header, exam):
	scaling_factor = 1
	home = os.path.expanduser("~")	
	base_path = os.path.join(home,'.lcmodel/basis-sets')
	#try:
	if (str(scanner).lower() == "bruker"):
		head_only = open(os.path.join(file_path, 'method'), 'rb').read()
		if (re.compile('PVM_RepetitionTime=').findall(head_only)):
			expression = re.compile('PVM_RepetitionTime=\S+').findall(head_only)
			for word in expression:
				TR_string = 'TR'
				TR_value = map(int, re.findall('\d+', word))[0]		
		if (re.compile('PVM_EchoTime=').findall(head_only)):
			expression = re.compile('PVM_EchoTime=\S+').findall(head_only)
			for word in expression:
				TE_string = 'TE'
				TE_value = map(int, re.findall('\d+', word))[0]	
		if (re.compile('PVM_NAverages=').findall(head_only)):
			expression = re.compile('PVM_NAverages=\S+').findall(head_only)
			for word in expression:
				NAvg_string = 'NAvg'
				NAvg_value = map(int, re.findall('\d+', word))[0]
		if (re.compile('PVM_RefScanNA=').findall(head_only)):
			expression = re.compile('PVM_RefScanNA=\S+').findall(head_only)
			for word in expression:
				Ref_NAvg = map(int, re.findall('\d+', word))[0]
				Ref_NAvg_value = map(int, re.findall('\d+', word))[0]
		if (re.compile('PVM_RefScanRG=').findall(head_only)):
			expression = re.compile('PVM_RefScanRG=\S+').findall(head_only)
			for word in expression:
				Ref_RG = map(int, re.findall('\d+', word))[0]

		if (TE_value == 20):
			basis_set_dir = os.path.join(base_path, scanner, b0, 'gamma_press_te20.basis')
		elif (TE_value == 25):
			basis_set_dir = os.path.join(base_path, scanner, b0, 'gamma_press_te25.basis')
		elif (TE_value == 35):
			basis_set_dir = os.path.join(base_path, scanner, b0, 'gamma_press_te35.basis')
		elif (TE_value == 136):
			basis_set_dir = os.path.join(base_path, scanner, b0, 'gamma_press_te136.basis')
		elif (TE_value == 270):
			basis_set_dir = os.path.join(base_path, scanner, b0, 'gamma_press_te270.basis')
		else:
			basis_set_dir = ''
			print("No basis-set matching to your file")
		if (conf.ismember(str(TE_string), header) >=0):
			trait_index = conf.ismember(str(TE_string), header)
			exam[trait_index] = TE_value
		if (conf.ismember(str(TR_string), header) >=0):
			trait_index = conf.ismember(str(TR_string), header)
			exam[trait_index] = TR_value
		if (conf.ismember(str(NAvg_string), header) >=0):
			trait_index = conf.ismember(str(NAvg_string), header)
			exam[trait_index] = NAvg_value

		acqp = open(os.path.join(file_path, 'acqp'), 'rb').read()
		if (re.compile('RG=').findall(head_only)):
			expression = re.compile('RG=\S+').findall(head_only)
			for word in expression:
				RG = map(int, re.findall('\d+', word))[0]
				scaling_factor = (NAvg_value/Ref_NAvg_value)/(RG/Ref_RG)

	elif (str(scanner).lower() == "siemens"):
		for root, subFolders, files in os.walk(file_path):  
			for file in files:
				if re.search('.rda',file):
					file_path = os.path.join(root,file)
					file_content = open(file_path, 'rb').read()
					istr = file_content.find(">>> Begin of header <<<")
					iend = file_content.find(">>> End of header <<<")
					head_only = file_content[istr:iend] 

					if (re.compile('TR:').findall(head_only)):
						expression = re.compile('TR: \S+').findall(head_only)
						for word in expression:
							TR_string = re.findall('\S[^:^0-9]+', word)[0]
							TR_value = map(int, re.findall('\d+', word))[0]		
					if (re.compile('TE:').findall(head_only)):
						expression = re.compile('TE: \S+').findall(head_only)
						for word in expression:
							TE_string = re.findall('\S[^:^0-9]+', word)[0]
							TE_value = map(int, re.findall('\d+', word))[0]	
					if (re.compile('NumberOfAverages:').findall(head_only)):
						expression = re.compile('NumberOfAverages: \S+').findall(head_only)
						for word in expression:
							NAvg_string = 'NAvg'
							NAvg_value = map(int, re.findall('\d+', word))[0]		
					
					if (TE_value == 30):
						basis_set_dir = os.path.join(base_path, scanner, b0, 'gamma_press_te30.basis')
					elif (TE_value == 135):
						basis_set_dir = os.path.join(base_path, scanner, b0, 'gamma_press_te135.basis')
					elif (TE_value == 270):
						basis_set_dir = os.path.join(base_path, scanner, b0, 'gamma_press_te270.basis')
					else:
						basis_set_dir = ''
						print("No basis-set matching to your file")

					if (conf.ismember(str(TE_string), header) >=0):
						trait_index = conf.ismember(str(TE_string), header)
						exam[trait_index] = TE_value
					if (conf.ismember(str(TR_string), header) >=0):
						trait_index = conf.ismember(str(TR_string), header)
						exam[trait_index] = TR_value
					if (conf.ismember(str(NAvg_string), header) >=0):
						trait_index = conf.ismember(str(NAvg_string), header)
						exam[trait_index] = NAvg_value

		
	#except Exception:
	#	print ("Error! There is a problem with your basis_set file or your filepath")
		
	return (basis_set_dir, header, exam, scaling_factor)

#analyze spectrum
def analyzeSpectrum(file_path, dest_dir, scanner, b0, header, exam):
	path, study_nr = os.path.split(file_path)
	path, patient_name = os.path.split(path)
	name = patient_name+'_'+study_nr
	basis_set_dir, header, exam, scaling_factor = getInfo(file_path, scanner.lower(), b0.lower(), header, exam)

	patient_dir = os.path.join(dest_dir,name)

	if not os.path.exists(patient_dir):	
		os.mkdir(patient_dir)
	if not os.path.exists(os.path.join(patient_dir,'h2o/')):	
		os.mkdir(os.path.join(patient_dir,'h2o/'))	
	if not os.path.exists(os.path.join(patient_dir, 'met/')):	
		os.mkdir(os.path.join(patient_dir,'met/'))


	#conversion from binary file to RAW using lcmodel scripts
	try:
		bin2raw(file_path, patient_dir, scanner)
	except Exception:
		print("Errror! There is a problem with lcmodel bin2raw script")

	#duplicating cpStart file to create custom parameters
	shutil.copy(os.path.join(patient_dir,'met/cpStart'), os.path.join(patient_dir,'met/myControl'))
	if os.path.exists(os.path.join(patient_dir,'h2o/RAW')):
		water_path = os.path.join(patient_dir,'h2o/RAW')
	csv_path = os.path.join(patient_dir,'spreadsheet.csv')
	table_path = os.path.join(patient_dir,'table')
	coord_path = os.path.join(patient_dir,'coord')


	file_content = list()
	source = open(os.path.join(patient_dir,'met/myControl'), 'r')
	for line in source.readlines():
		file_content.append(line)
	file_content.insert(0, "$LCMODL\n")
	file_content.insert(len(file_content), "\n$END")
	file_content.insert(len(file_content)-1, "filbas= '"+basis_set_dir+"'\n")
	file_content.insert(len(file_content)-1, "filcsv= '"+csv_path+"'\n")
	file_content.insert(len(file_content)-1, "filtab= '"+table_path+"'\n")
	file_content.insert(len(file_content)-1, "filcoo= '"+coord_path+"'\n")
	if os.path.exists(os.path.join(patient_dir,'h2o/RAW')):
		file_content.insert(len(file_content)-1, "filh2o= '" +water_path+"'\n")	
		file_content.insert(len(file_content)-1, "dows= T\n")	
		file_content.insert(len(file_content)-1, "doecc= F\n")	
	file_content.insert(len(file_content)-1, "lcsv= 11\n")	
	file_content.insert(len(file_content)-1, "ltable= 7\n")
	file_content.insert(len(file_content)-1, "lcoord= 9\n")

	source.close()
	dest = open(os.path.join(patient_dir,'met/myControl'), 'w')	
	for line in xrange(len(file_content)):
		dest.write(file_content[line])
	dest.close()
	
	command = ('~/.lcmodel/bin/lcmodel < ' +os.path.join(patient_dir,'met/myControl'))
	os.system(command)

	output_pdf = ('ps2pdf ' +os.path.join(patient_dir, 'ps ') +os.path.join(patient_dir,name+'.pdf'))
	os.system(output_pdf)
	delete_ps = ('rm '+os.path.join(patient_dir,'ps'))
	os.system(delete_ps)

	#try:
	[header, exam] = readCsv(patient_dir, header, exam, scaling_factor)

	#except Exception:
	#	print("Error! Problem with opening: "+os.path.join(patient_dir, 'spreadsheet.csv') + " file")
	
	return (header, exam)

