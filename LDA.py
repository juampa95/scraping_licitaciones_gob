"""
La idea es partir de los archivos top_100_procesos.csv y agruparlos por tematica.
Por ello se usara un LDA (Latent Dirichlet Allocation).
Deberemos pre-procesar el texto para quitar algunas palabras y separarlas en tokens
"""
import pandas as pd
import nltk
from nltk import word_tokenize
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import TfidfVectorizer
import re
from collections import Counter
from nltk.stem import PorterStemmer, WordNetLemmatizer, LancasterStemmer
from nltk.corpus import wordnet
import numpy as np

df = pd.read_csv('top_100_procesos.csv',sep = ';')
df.head()
vectorizer = CountVectorizer()
dtm = vectorizer.fit_transform(df['Nombre descriptivo de proceso'])

lda_model = LatentDirichletAllocation(n_components=10) # ajusta el número de temas que quieres identificar
lda_model.fit(dtm)

doc_topic_distr = lda_model.transform(dtm)

df['tema'] = [doc_topic_distr[i].argmax() for i in range(len(df))]

df[df['tema']==5]

# EL resultado fue malo. Voy a probar preprocesar los datos antes de ingresarlos en el LDA

# PASOS

# 1- Pasar todo el texto a minusculas

df['Nombre descriptivo de proceso'] = df['Nombre descriptivo de proceso'].apply(lambda x : x.lower())

# 2- Tokenizar

token_list = [word_tokenize(each) for each in df['Nombre descriptivo de proceso']]
tokens = [item for sublist in token_list for item in sublist]

len(set(tokens))

# 3- Quitar signos de puntuacion

# df['procesos_sin_punt'] = df['Nombre descriptivo de proceso'].apply(lambda x : re.sub('[^A-Za-z0-9 ]+', ' ', x))
#
# token_list = [word_tokenize(each) for each in df['procesos_sin_punt']]
# tokens = [item for sublist in token_list for item in sublist]

# Quita solo 4 tokens. Y viendo los datos, tenemos algunas palabras que tienen "-" intermedios.

# 4- Quitar stopwords y palabras de alta/baja frecuencia

noise_words = []

stopwords_corpus = nltk.corpus.stopwords
esp_stop_words = stopwords_corpus.words('spanish')
noise_words.extend(esp_stop_words)

print(f'en español tenemos {len(noise_words)} stopwords.')

# Palabras de alta y baja frecuencia. Vamos a usar un umbral del 1%

one_percentile = int(len(set(tokens))*0.01)
top_1_percentile = Counter(tokens).most_common(one_percentile)
top_1_percentile[:10]

bottom_1_percentile = Counter(tokens).most_common()[-one_percentile:]
bottom_1_percentile[:10]
# Al parecer las palabras que menos se repiten pueden ser mas. Vamos a agregar algunas

bottom_1_percentile = Counter(tokens).most_common()[-200:]
bottom_1_percentile[:200]

# No vamos a quitar las palabras que no tienen frecuencia porque hay demasiadas palabras que estan 1 sola vez.

noise_words.extend([word for word,val in top_1_percentile])

# 2 de las 4 palabras que agregamos, ya estaban en la lista. Una fue 'de' y la otra 'y'. Por lo que las sacamos

noise_words = set(noise_words)

# 5- stemming y Lemantización - despues lo vamos a probar -

porter = PorterStemmer()
lancaster = LancasterStemmer()
lemmatizer = WordNetLemmatizer()

#####################################################
# Armamos una lista partiendo de la lista de tokens y quitando las palabras que se encuentren
# en la lista de palabras a quitar "noise_words" creada anteriormente.

tokenize_data = [list(filter(lambda token : token not in noise_words,t)) for t in token_list]

# Crear una instancia del vectorizador TfidfVectorizer
tfidf_vectorizer = TfidfVectorizer(tokenizer=lambda x: x, preprocessor=lambda x: x)

# Transformar los datos en matriz tf-idf
tfidf = tfidf_vectorizer.fit_transform(tokenize_data)

# Crear una instancia del modelo LDA
lda_model = LatentDirichletAllocation(n_components=10, random_state=0)

# Entrenar el modelo con los datos transformados
lda_model.fit(tfidf)

# Obtener los temas para cada documento
topics = lda_model.transform(tfidf)

topics

topic_indices = np.argmax(topics, axis=1)

topic_indices

df = df.assign(tema2 = topic_indices)

df

df[df['tema2']==1]

# El resultado sigue siendo malo. Voy a tener que buscar una forma diferente de clasificarlos. Quiza usando mas datos.
# Ya que para esta prueba solo utilice un top 100 y quiza sean pocos registros
