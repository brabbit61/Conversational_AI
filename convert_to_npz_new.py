import os
import pandas as pd
import keras
from keras.preprocessing.text import Tokenizer
import matplotlib.pyplot as plt
import numpy as np
from keras.preprocessing.sequence import pad_sequences
import argparse
import multiprocessing
import time

def save_npz(row):
		global train_data, maxlen, num_words
		final_data = np.zeros((1,maxlen,num_words))
		for i in range(maxlen):
				if train_data.iloc[row,i] == 0:
						pass
				else:
						final_data[0,i,train_data.iloc[row,i]-1] = 1
		np.savez_compressed("cleaned_data_npz/sentence_"+str(row)+".npz", data=final_data)
		del final_data
		print(row)

if __name__ == '__main__':
		parser = argparse.ArgumentParser(description="Converting text files to NPZ and CSV format")
		parser.add_argument("--input_file", type=str, help="The path to the CSV file with all the conversations.", default="all_conversations.csv")
		parser.add_argument("--output_file", type=str, help="The path to the CSV file with all the sentences converted to vectors.", default="training_sequences.csv")
		parser.add_argument("--maxlen", type=int, help="Length of vectors that are inputted to the LSTM network.", default=50)
		parser.add_argument("--num_words", type=int, help="Number of distinct words to keep in the dictionary", default=10000)
		parser.add_argument("--numthreads", type=int, help="Number of threads to save the npz files", default=8)
		args = parser.parse_args()
		input_file = args.input_file
		output_file = args.output_file
		maxlen = args.maxlen		#max length input into the lstm
		num_words = args.num_words		#max number of words allowed in the vocabulary
		numthreads = args.numthreads

		dataset = pd.read_csv(input_file)
		data = [l.strip() for l in list(dataset.iloc[:,1])]		#all the sentences in the dataset are stored as strings
		print("\nShape of the dataset: ")
		print(dataset.shape)

		sequences_data = []		#all the sentences are converted and stored as a sequence of numbers
		tokenizer = Tokenizer(num_words=num_words, filters='#$%&*+-/<=>@[\\]^_`{|}~\t\n', split=' ', char_level= False)
		tokenizer.fit_on_texts(data[:])
		for i in data:
				sequences_data.append(tokenizer.texts_to_sequences([i])[0])
		print("Text converted to sequences successfully.")


		structured_data = []		#all sequences 
		for sequence in sequences_data:
				if len(sequence) < maxlen:
						structured_data.append(sequence)
				else:
						while len(sequence) > maxlen:
								sub_sequence = sequence[:maxlen]
								sequence = sequence[maxlen:]
								structured_data.append(sub_sequence)
						if len(sequence) > 0:
								structured_data.append(sequence)
		train_data = pad_sequences(structured_data, maxlen, padding="pre")  #all the sequences converted to the same length, the maxlen, the shape of this is (number of samples, maxlen)
		print("Sequences padded successfully.")
		train_data = pd.DataFrame(train_data)
		train_data.to_csv(output_file)
		
		pool = multiprocessing.Pool(processes=numthreads)	
		start = time.process_time()
		pool.map(save_npz, range(train_data.shape[0]))
		print("Time taken for the execution: " + str(time.process_time()-start))
