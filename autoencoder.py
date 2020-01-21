import pandas as pd
import os
import argparse
import numpy as np
from keras.preprocessing.text import Tokenizer
from keras.callbacks.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from keras.callbacks.tensorboard_v1 import TensorBoard
from keras.layers import RepeatVector, Input, LSTM, Dense, Bidirectional, TimeDistributed
from keras.models import Model, Sequential
from keras.utils import plot_model, Sequence


def def_model(num_words, num_units):
		encoder_inputs = Input(shape=(None, num_words))
		encoder = LSTM(num_units, return_state=True)
		encoder_outputs, state_h, state_c = encoder(encoder_inputs)
		encoder_states = [state_h, state_c]
		decoder_inputs = Input(shape=(None, num_words))
		decoder_lstm = LSTM(num_units, return_sequences=True, return_state=True)
		decoder_outputs, _, _ = decoder_lstm(decoder_inputs, initial_state=encoder_states)
		decoder_dense = Dense(num_words, activation="softmax")

		model = Model([encoder_inputs, decoder_inputs], decoder_outputs)
		encoder_model = Model(encoder_inputs, encoder_states)
		decoder_state_input_h = Input(shape=(num_units,))
		decoder_state_input_c = Input(shape=(num_units,))
		decoder_state_inputs = [decoder_state_input_h,decoder_state_input_c]
		decoder_outputs, state_h, state_c = decoder_lstm(decoder_inputs, inital_state=decoder_states_inputs)
		decoder_states = [state_h, state_c]
		decoder_outputs = decoder_dense(decoder_outputs)
		decoder_model = Model([decoder_inputs] + decoder_states_inputs, [decoder_outputs] + decoder_states)
		
		return model, encoder_model, decoder_model

class DataGenerator(Sequence):
    def __init__(self, list_IDs, labels, batch_size=2, dim=150, n_features=10000, shuffle=False):
        self.dim = dim
        self.batch_size = batch_size
        self.labels = labels
        self.list_IDs = list_IDs
        self.n_features = n_features
        self.shuffle = shuffle
        self.on_epoch_end()

    def __len__(self):
        return int(np.floor(len(self.list_IDs) / self.batch_size))

    def __getitem__(self, index):
        indexes = self.indexes[index*self.batch_size:(index+1)*self.batch_size]
        list_IDs_temp = [self.list_IDs[k] for k in indexes]
        X, y = self.__data_generation(list_IDs_temp)
        return X, y

    def on_epoch_end(self):
        self.indexes = np.arange(len(self.list_IDs))
        if self.shuffle == True:
            np.random.shuffle(self.indexes)

    def __data_generation(self, list_IDs_temp):
        X = np.empty((self.batch_size, self.dim, self.n_features))
        y = np.empty((self.batch_size, self.dim, self.n_features), dtype=int)

        for i, ID in enumerate(list_IDs_temp):
            X[i,] = np.load("cleaned_data_npz/" + ID)["data"]
            y[i] = np.load("cleaned_data_npz/"+self.labels[ID])["data"]

        return X, y


parser = argparse.ArgumentParser(description="Importing the npz batches")
parser.add_argument("--input_folder", type=str, help="The path to the folder with processed conversations.", default="batches/")
parser.add_argument("--maxlen", type=str, help="The maximum length of any sentence.", default=150)
parser.add_argument("--num_words", type=str, help="The number of words in the vocabulary.", default=10000)
parser.add_argument("--num_units", type=str, help="The number of units in the LSTM network.", default=256)

args = parser.parse_args()
input_folder = args.input_folder
maxlen = args.maxlen
num_words = args.num_words
num_units = args.num_units

dataset = pd.read_csv("all_conversations.csv")
data = [l.strip() for l in list(dataset.iloc[:,1])]
tokenizer = Tokenizer(num_words=num_words, filters='#$%&*+-/<=>@[\\]^_`{|}~\t\n', split=' ', char_level= False)
tokenizer.fit_on_texts(data[:])

#model = Sequential()
x = Input(shape=(maxlen, num_words))
#m = Bidirectional(LSTM(num_units, activation="relu", input_shape=(None, maxlen, num_words)))(x)
m = Bidirectional(LSTM(num_units, activation="relu"))(x)
m = RepeatVector(maxlen)(m)
m = Bidirectional(LSTM(num_units, activation="relu", return_sequences=True))(m)
#model.add(Bidirectional(LSTM(num_units, activation="relu", return_sequences=True )))
#model.add(Bidirectional(LSTM(num_units, activation="relu", return_sequences=True )))
o = TimeDistributed(Dense(num_words))(m)
model = Model(inputs=x,outputs=o)

files = [i for i in os.listdir("/content/gdrive/My Drive/NLP_Project/cleaned_data_npz")]
files.sort()
partition = {}
l = int(0.85*len(files))
partition["train"] = [i for i in files[:l]]
partition["validation"] = [i for i in files[l:]]
train_labels = {}
val_labels = {}
for i in range(l-1):
		train_labels[files[i]] = files[i+1]
for i in range(l,len(files)-1):
		val_labels[files[i]] = files[i+1]

epochs = 1
modelcheckpoint = ModelCheckpoint("/content/gdrive/My Drive/NLP_Project/weights/", monitor="val_acc", save_best_only=False, verbose=1, save_weights_only=True)
earlystopping = EarlyStopping(monitor="val_loss", min_delta = 0.000001, patience= 1)
tensorboard = TensorBoard(log_dir="/content/gdrive/My Drive/NLP_Project/.logdir/")
reduce_plateau = ReduceLROnPlateau(monitor="val_loss", factor=0.3, patience=1, min_lr = 0.00001)
val_generator = DataGenerator(partition['validation'], val_labels, batch_size=12)
train_generator = DataGenerator(partition['train'], train_labels, batch_size=12)

model.compile(loss="mean_squared_logarithmic_error", optimizer="adam")
history = model.fit_generator(generator=train_generator,epochs = epochs, verbose=1, validation_data = val_generator, use_multiprocessing=True, workers=3, validation_freq=1, validation_steps=1, callbacks=[modelcheckpoint, earlystopping, tensorboard, reduce_plateau])
model.save("/content/gdrive/My Drive/NLP_Project/final.h5")
'''
for input_file in os.listdir(input_folder):
		dataset = np.load() 
tfidf_vectorizer = TfidfVectorizer(use_idf=True, smooth_idf=True)
#reindexed_data = reindexed_data.values
document_term_matrix = tfidf_vectorizer.fit_transform(reindexed_data)
n_topics = 1000 
lsa_model = TruncatedSVD(n_components=n_topics)
lsa_topic_matrix = lsa_model.fit_transform(document_term_matrix)
lsa_keys = get_keys(lsa_topic_matrix)
lsa_categories, lsa_counts = keys_to_counts(lsa_keys)
'''
