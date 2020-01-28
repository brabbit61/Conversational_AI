import os
import pandas as pd
from keras.preprocessing.text import Tokenizer
import matplotlib.pyplot as plt

dataset = pd.read_csv("all_conversations.csv")
data = list(dataset.iloc[:,1])
data = [l.strip() for l in data]

file_len = [len(i) for i in data]
frequency_len = [0]*(max(file_len)+1)
for inp in data:
		frequency_len[len(inp)] += 1
#plt.bar([i for i in range(max(file_len)+1)], height = frequency_len)
plt.bar([i for i in range(400)], height = frequency_len[:400])
plt.xlabel("Length of sentences")
plt.ylabel("Frequency of sentences")
plt.show()


tok = Tokenizer(num_words=None, filters='#$%&*+-/<=>@[\\]^_`{|}~\t\n',lower=True, split=' ', char_level=False)
tok.fit_on_texts(data)
words = tok.word_counts

one = 0
two = 0
three = 0
for i in words:
		if words[i] == 1:
				one += 1
				two += 1
				three += 1
		elif words[i] == 2:
				two += 1
				three += 1
		elif words[i] == 3:
				three += 1
print("\n\n\nTotal number of messages: "+ str(len(data)))
print("Total number of unique words in the vocabulary are: "+str(len(words)))
print("Number of words occuring only once: "+str(one))
print("Number of words occuring twice or less thance twice: "+str(two))
print("Number of words occuring thrice or less thance thrice: "+str(three))
print("Above values must be considered while selecting the maxlen value for the LSTM network.")
