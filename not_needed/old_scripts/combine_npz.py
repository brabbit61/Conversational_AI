import os
import argparse
import pandas as pd
import numpy as np

parser = argparse.ArgumentParser(description="Converting npz files to a single large training set")
parser.add_argument("--input_folder", type=str, help="The path to the folder with the npz files.", default="cleaned_data_npz")
parser.add_argument("--output_folder", type=str, help="The path to the folder where the training set is to be stored. Deafault is current working directory", default="batches/")
parser.add_argument("--maxlen", type=int, help="Length of vectors that are inputted to the LSTM network.", default=150)
parser.add_argument("--num_words", type=int, help="Number of distinct words to keep in the dictionary", default=10000)
args = parser.parse_args()
input_folder = args.input_folder
output_folder = args.output_folder
maxlen = args.maxlen		#max length input into the lstm
num_words = args.num_words		#max number of words allowed in the vocabulary
directories = os.listdir(input_folder)

training_data = np.zeros((1, maxlen, num_words))
for i,input_file in enumerate(os.listdir(input_folder)):
		temp = np.load(input_folder+"/"+input_file)["data"]
		print(i)
		temp = np.reshape(temp, (1, maxlen, num_words))
		training_data = np.concatenate([training_data,temp])
		del temp
		if i % 100 == 0 and i > 0:
				np.savez_compressed(output_folder+"batch_"+str(int(i/100))+".npz", input_data=training_data[1:-1], output_data=training_data[2:])
				del training_data
				training_data = np.zeros((1, maxlen, num_words))
np.savez_compressed(output_folder+"batch_final.npz", data=training_data)
