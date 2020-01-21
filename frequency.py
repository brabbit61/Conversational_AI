import os
import re
import argparse
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter1d
import datefinder

parser = argparse.ArgumentParser(description="Providing conversation text file names.")
parser.add_argument("--input_file", type=str, help="The path to the conversation text file")
args = parser.parse_args()
input_file = args.input_file

to_delete = ["Messages to this chat and calls are now secured with end-to-end encryption","<Media omitted>","(file attached)","You're currently chatting with their new number. Tap to add it to your contacts.","This message was deleted","security code changed. Tap for more info."]
#input_name = "Jenit" #will be needed when the final conversational model generates well on all data
timestamp_pattern = re.compile("\d{1,2}/\d{1,2}/\d{1,4},\s\d{1,2}:\d{1,2}\s-\s")
forwarded_chat_pattern = re.compile("\[\d{1,2}/\d{1,2},\s\d{1,2}:\d{1,2}\s[A|P]M\]\s[\w\s]+:")
date_pattern = re.compile("\d{1,2}/\d{1,2}/\d{2,4}")
first_person = []
second_person = []
first = 0
second = 0

with open("all_individual_convos/"+input_file,"r") as f:
	first_name = ""
	second_name = "" 
	date = ""
	for line in f.readlines():
		write = 1
		for d in to_delete:
			if d in line:
				write = 0
				break
		try:
			if write:
				if len(forwarded_chat_pattern.findall(line)) > 0:
					continue
				elif len(date_pattern.findall(line)) > 0:
					if date != date_pattern.findall(line)[0] :
						first_person.append(first)
						second_person.append(second)
						date = date_pattern.findall(line)[0]
						first = 0
						second = 0

				if first_name == "":
					dash = line.find("-")
					colon = line.index(":",dash)
					first_name = line[dash + 2 : colon]
					first_name_pattern = re.compile("\d{1,2}/\d{1,2}/\d{1,4},\s\d{1,2}:\d{1,2}\s-\s"+first_name)
					first += 1
					last = 1                #tells us whether user 1 sent the last message or user 2
					continue
				elif (len(first_name_pattern.findall(line)) == 0) and second_name == "":
					if len(timestamp_pattern.findall(line)) == 0: #the message has a new line character hence it belongs to the previous sender
					#if len(list(datefinder.find_dates(line))) == 0: #the message has a new line character hence it belongs to the previous sender
						pass
					else:	    #its user 2's message
						dash = line.index("-")
						colon = line.index(":",dash)
						second_name = line[dash + 2 : colon]
						second_name_pattern = re.compile("\d{1,2}/\d{1,2}/\d{1,4},\s\d{1,2}:\d{1,2}\s-\s"+second_name)
						second += 1
						last = 2
						continue
				if len(first_name_pattern.findall(line))>0:
					first += 1 
					last = 1
				elif len(second_name_pattern.findall(line))>0:
					second += 1
					last = 2
				else:
					continue
		except Exception as e:
			pass
first_person.append(first)
second_person.append(second)
first_person = np.asarray(first_person[1:], dtype=np.int32)
second_person = np.asarray(second_person[1:], dtype=np.int32)
print(len(first_person))
frequency_of_texts = first_person + second_person
print(sum(frequency_of_texts))
f = gaussian_filter1d(frequency_of_texts, sigma=1.1)
plt.plot(f, c='b')
plt.ylabel('Number of text messages everyday')
plt.xlabel('Time')
plt.show()

