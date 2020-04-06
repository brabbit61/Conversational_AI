import os
import re
import argparse
import unicodedata
import inflect
import time
import multiprocessing
import math

def remove_non_ascii(words):
		new_words = []
		for word in words:
				if len(word) > 15:
						continue
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
	message = replace_numbers(message.split(' '))
	message = re.sub('[#$%&*+/<=>[\]^_{|}~]','',message)
	message = message.strip().lower()
	message = remove_non_ascii(message.split(' '))		
	return message
        
def clean(file_name):
	global input_folder, output_foler, timestamp_pattern, forwarded_chat_pattern
	file_name = str(file_name)+ ".txt"
	with open(input_folder+file_name,"r") as f:
#	with open("test/"+file_name,"r") as f:
			dialogues_seq = []
			print("Now parsing file: "+file_name)
			first_name = ""
			second_name = "" 
			output_file = open(output_folder+"clean_"+file_name,"w")
			message = ""
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
									output_file.write("User 1: "+ message+"\n")
								dialogues_seq.append(message)
								message = line[colon+2:].strip()
								last = 2
							continue
						if len(first_name_pattern.findall(line))>0:
							if last == 1:
								colon = line.index(":",line.index("-"))
								message = message + ". " + line[colon+2:].strip()
							else:
								last = 1
								message = preprocess(message)
								if message != "":
										output_file.write("User 2: "+ message+"\n")
								dialogues_seq.append(message.lower())
								colon = line.index(":",line.index("-"))
								message = line[colon+2:].strip()
						elif len(second_name_pattern.findall(line))>0:
							if last == 2:
								colon = line.index(":",line.index("-"))
								message = message + ". " + line[colon+2:].strip()
							else:
								last = 2
								message = preprocess(message)
								if message != "":
									output_file.write("User 1: "+ message+"\n")
								dialogues_seq.append(message)
								colon = line.index(":",line.index("-"))
								message = line[colon+2:].strip()
						else:
							pass
				except Exception as e:
					print(line)
					pass
			message = preprocess(message)
			if last == 2:
				if message != "":
					output_file.write("User 2: "+ message+"\n")
			else:
				if message != "":
					output_file.write("User 1: "+ message+"\n")
			dialogues_seq.append(message)
			output_file.close()


if __name__ == '__main__':
		parser = argparse.ArgumentParser(description="Providing folder names for the conversations.")
		parser.add_argument("--input_folder", type=str, help="The path to the folder with unprocessed conversations.", default="all_individual_convos/")
		parser.add_argument("--output_folder", type=str, help="The path to the folder with processed conversations.",default="cleaned_data_text/")
		parser.add_argument("--numthreads", type=int, help="The number of threads to run..",default=8)
		args = parser.parse_args()
		input_folder = args.input_folder
		output_folder = args.output_folder
		numthreads = args.numthreads

		to_delete = [
					"Messages to this chat and calls are now secured with end-to-end encryption",
					"<Media omitted>",
					"Missed video call",
					"Missed voice call",
					"(file attached)",
					"You're currently chatting with their new number. Tap to add it to your contacts.",
					"This message was deleted",
					"security code changed. Tap for more info.",
					"This chat is with a business account. Tap for more info."
		]
		#input_name = "Jenit" #will be needed when the final conversational model generates well on all data
		#delete_pattern = re.compile("\[\d{1,2}/\d{1,2},\s\d{1,2}:\d{1,2}\s[A|P]M\]\s\S+:\s\S+") #this is the pattern for a forwarded chat that needs to be excluded as it will already be included in another chat. Whenever this pattern is found, we must ignore the line.
		timestamp_pattern = re.compile("\d{1,2}/\d{1,2}/\d{1,4},\s\d{1,2}:\d{1,2}\s-\s")
		forwarded_chat_pattern = re.compile("\[\d{1,2}/\d{1,2},\s\d{1,2}:\d{1,2}\s[A|P]M\]\s[\w\s]+:")

		start = time.time()

		file_names = [f for f in os.listdir(input_folder)]
		files_per_thread = math.ceil(len(file_names)/numthreads)
		processes = []
		parts = [file_names[i:i+files_per_thread] for i in range(0,len(file_names), files_per_thread)]
		pool = multiprocessing.Pool(processes=numthreads)
		pool.map(clean,range(1, len(file_names)+1))
		print("Successfully parsed all files in the input folder")
		print("Total time taken for the execution is: " + str(time.time()- start))
