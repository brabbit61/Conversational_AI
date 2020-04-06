import os

def process(line):
				words = line.split(' ')
				new_words = []
				for i,word in enumerate(words):
								s = word
								for r in replace_list:
												if s.find(r)>=0:
																s = s.replace(r,main_word)
								new_words.append(s)
				new_line = ' '.join(new_words)
				return new_line

replace_list = [' !']
main_word = '!'
main_dir = 'cleaned_data_text/'
for file_name in os.listdir(main_dir):
				new_file = open('new_files/'+file_name,'w')
				with open(main_dir+file_name,'r') as f:
								for line in f.readlines():
												new_file.write(process(line))
								new_file.close()
for file_name in os.listdir('new_files'):
				os.rename('new_files/'+file_name, main_dir+file_name)

