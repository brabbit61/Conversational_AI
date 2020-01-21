import pandas as pd
import argparse
import os
import numpy as np
from keras.preprocessing.text import Tokenizer

parser = argparse.ArgumentParser(description="Converting text files to excel")
parser.add_argument("--input_folder", type=str, help="The path to the folder with processed conversations.", default="cleaned_data_text/")
parser.add_argument("--output_folder", type=str, help="The path to the folder with processed conversations.", default="cleaned_data_csv/")
parser.add_argument("--num_words", type=str, help="The top n words to keep in the vocabulary.", default=10000)
args = parser.parse_args()
input_folder = args.input_folder
output_folder = args.output_folder
num_words = args.num_words


m=0
all_conversations = []
for input_file in os.listdir(input_folder):
		with open(input_folder+input_file,"r") as f:
				sequences = []
				count = 0
				for line in f.readlines():
						sequences.append(line[8:])
						all_conversations.append(line[8:])
						count += 1
						if len(line[8:]) > m:
								x = input_file
								l = line
								m = len(line[8:])
				dataset = pd.DataFrame({'Text':sequences})
				dataset.to_csv(output_folder+input_file[:-4]+".csv", index=False)
				del dataset
				print("Successfully converted "+input_file+" to csv format, wrote "+str(count)+" lines.")
D = pd.DataFrame({'Text':all_conversations})
D.to_csv("all_conversations.csv")
print("Successfully converted all files in "+input_folder+" to csv format")
print("\n\nMaximum length of a sentence: "+str(m)+" characters.")
print("\n\nFile name: "+x)
print("\n\nMessage: "+l)

data = [l.strip() for l in list(D.iloc[:,0])]
tokenizer = Tokenizer(num_words=num_words, filters='#$%&*+-/<=>@[\\]^_`{|}~\t\n', split=' ', char_level= False)
tokenizer.fit_on_texts(data[:])
x = tokenizer.word_counts
a = 0
c = 0
for i in x:
		if x[i] == 1:
				c+=1
		if x[i] == 1 or x[i] == 2:
				a+=1
print("Number of words occuring only once: "+str(c))
print("Number of words occuring twice or less thance twice: "+str(a))
