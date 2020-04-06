import re
import argparse
import unicodedata
import inflect
import time
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from scipy.ndimage.filters import gaussian_filter1d
import datetime

def remove_non_ascii(words):
    new_words = []
    for word in words:
        new_word = unicodedata.normalize('NFKD', word).encode('ascii', 'ignore').decode('utf-8', 'ignore')
        new_words.append(new_word)
    return ' '.join(new_words)

def replace_numbers(words):
    """Replace all interger occurrences in list of tokenized words with textual representation"""
    p = inflect.engine()
    new_words = []
    for word in words:
        if word.isdigit():
            new_word = p.number_to_words(word)
            new_words.append(new_word)
        else:
            new_words.append(word)
    return ' '.join(new_words)

def preprocess(message):
	message = replace_numbers(message.split())
	message = re.sub('[#$%&*+/<=>[\]^_{|}~]','',message)
	message = message.strip().lower()
	message = remove_non_ascii(message.split(' '))		
	return message
        

def post_processing():
	global first_person, second_person, all_dates
	
	first_date = all_dates[0]
	last_date = all_dates[-1]

	total_days = (last_date - first_date).days
	
	final_dates = [all_dates[0]]
	final_first_person = [first_person[0]]
	final_second_person = [second_person[0]]
	for i in range(1,total_days):
		new_date = final_dates[i-1] + datetime.timedelta(days=1)
		final_dates.append(new_date)
		if new_date in all_dates:
			index = all_dates.index(new_date)
			final_first_person.append(first_person[index])
			final_second_person.append(second_person[index])
		else:
			final_first_person.append(0)
			final_second_person.append(0)
	return final_first_person, final_second_person, final_dates	
	
def calculate_stats(file_name):
	global to_delete, input_file, first_person, timestamp_pattern, forwarded_chat_pattern, second_person, date_pattern, all_dates
	file_name = str(file_name)+ ".txt"
	first_name = ""
	second_name = "" 
	date = ""
	last = 0
	message = ""
	first = 0
	second = 0
	with open("all_individual_convos/"+input_file,"r", encoding="utf8") as f:
			for line in f.readlines():
				write = 1
				for sentence in to_delete:
					if sentence in line:
						write = 0
						break
				try:
					if write:
						if len(forwarded_chat_pattern.findall(line)) > 0:
								continue
						elif len(date_pattern.findall(line[:20])) > 0:
								if date != date_pattern.findall(line[:20])[0]:
										first_person.append(first)
										second_person.append(second)
										if date != "":
												all_dates.append(datetime.datetime.strptime(date, '%d/%m/%Y'))
										date = date_pattern.findall(line)[0]
										first = 0
										second = 0
						if first_name == "":
								dash = line.find("-")
								colon = line.index(":",dash)
								first_name = line[dash + 2 : colon]
								if first_name[0] == '+':
										first_name_pattern = re.compile("\d{1,2}/\d{1,2}/\d{1,4},\s\d{1,2}:\d{1,2}\s-\s\+[\d\s]+")
								else:
										first_name_pattern = re.compile("\d{1,2}/\d{1,2}/\d{1,4},\s\d{1,2}:\d{1,2}\s-\s"+first_name)
								message = line[colon+2:].strip()
								last = 1							#tells us whether user 1 sent the last message or user 2
								continue
						elif (len(first_name_pattern.findall(line)) == 0) and second_name == "":
								if len(timestamp_pattern.findall(line)) == 0:
									message = message +  " " + line.strip()
								else:
										dash = line.index("-")
										colon = line.index(":",dash)
										second_name = line[dash + 2 : colon]
										if second_name[0] == '+':
												second_name_pattern = re.compile("\d{1,2}/\d{1,2}/\d{1,4},\s\d{1,2}:\d{1,2}\s-\s\+[\d\s]+")
										else:
												second_name_pattern = re.compile("\d{1,2}/\d{1,2}/\d{1,4},\s\d{1,2}:\d{1,2}\s-\s"+second_name)
										message = preprocess(message)
										if message != "":
												first += len(message.split(' '))
										message = line[colon+2:].strip()
										last = 2
								continue
						if len(first_name_pattern.findall(line))>0:
								if last == 1:
										colon = line.index(":",line.index("-"))
										message = message + " " + line[colon+2:].strip()
								else:
										last = 1
										message = preprocess(message)
										if message != "":
												second += len(message.split(' '))
										colon = line.index(":",line.index("-"))
										message = line[colon+2:].strip()
						elif len(second_name_pattern.findall(line))>0:
								if last == 2:
										colon = line.index(":",line.index("-"))
										message = message + " " + line[colon+2:].strip()
								else:
										last = 2
										message = preprocess(message)
										if message != "":
												first += len(message.split(' '))
										colon = line.index(":",line.index("-"))
										message = line[colon+2:].strip()
						else:
								pass
				except Exception as e:
						print(e)
						pass
	message = preprocess(message)
	if last == 2:
			if message != "":
					second += len(message.split(' '))
	else:
			if message != "":
					first += len(message.split(' '))
	first_person.append(first)
	second_person.append(second)
	all_dates.append(datetime.datetime.strptime(date, '%d/%m/%Y'))
	return first_name, second_name

if __name__ == '__main__':
		parser = argparse.ArgumentParser(description="Providing conversation text file names.")
		parser.add_argument("--input_file", type=str, help="The path to the conversation text file")
		parser.add_argument("--sigma", type=float, help="The smoothing applied in the graph", default=1)
		args = parser.parse_args()
		input_file = args.input_file
		sigma = args.sigma
		to_delete = [
			"Messages to this chat and calls are now secured with end-to-end encryption",
			"<Media omitted>",
			"(file attached)",
			"You're currently chatting with their new number. Tap to add it to your contacts.",
			"This message was deleted",
			"security code changed. Tap for more info.",
			"This chat is with a business account. Tap for more info."
		]
		timestamp_pattern = re.compile("\d{1,2}/\d{1,2}/\d{1,4},\s\d{1,2}:\d{1,2}\s-\s")
		forwarded_chat_pattern = re.compile("\[\d{1,2}/\d{1,2},\s\d{1,2}:\d{1,2}\s[A|P]M\]\s[\w\s]+:")
		date_pattern = re.compile("\d{1,2}/\d{1,2}/\d{2,4}")
		first_person = []
		second_person = []
		all_dates = []
		
		start = time.time()
		first_name, second_name = calculate_stats(input_file)
		print("Total time taken for the execution is: " + str(time.time()- start))
		
		first_person = first_person[1:]
		second_person = second_person[1:]

		first_person, second_person, all_dates = post_processing()

		first_person = np.asarray(first_person, dtype=np.int32).reshape((1,len(first_person)))
		second_person = np.asarray(second_person, dtype=np.int32).reshape((1,len(second_person)))
		all_dates = np.asarray(all_dates).reshape((1,len(all_dates)))

		f = gaussian_filter1d(first_person[0], sigma=sigma)
		s = gaussian_filter1d(second_person[0], sigma=sigma)

		fig, ax = plt.subplots(figsize=(18,6))
		locator = mdates.MonthLocator()
		fmt = mdates.DateFormatter('%b-%y')
		X = plt.gca().xaxis
		X.set_major_locator(locator)
		X.set_major_formatter(fmt)
		ax.set_xlim(all_dates[0][0],all_dates[0][-1])
		plt.plot(all_dates[0],f, c='b', label=first_name)
		plt.plot(all_dates[0],s, c='r', label=second_name)
		plt.ylabel('Number of words exchanged everyday')
		plt.xlabel('Time')
		plt.legend()
		plt.show()
