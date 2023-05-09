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
from sklearn.model_selection import (
    RandomizedSearchCV,
    StratifiedKFold,
    KFold
)
import gensim
from gensim.models.coherencemodel import CoherenceModel


df = pd.read_csv('top_100_procesos.csv', sep=';')
df.head()
vectorizer = CountVectorizer()
dtm = vectorizer.fit_transform(df['Nombre descriptivo de proceso'])

lda_model = LatentDirichletAllocation(n_components=10)  # ajusta el número de temas que quieres identificar
lda_model.fit(dtm)

doc_topic_distr = lda_model.transform(dtm)

df['tema'] = [doc_topic_distr[i].argmax() for i in range(len(df))]

df[df['tema'] == 5]

# EL resultado fue malo. Voy a probar preprocesar los datos antes de ingresarlos en el LDA

# PASOS

# 1- Pasar todo el texto a minusculas

df['Nombre descriptivo de proceso'] = df['Nombre descriptivo de proceso'].apply(lambda x: x.lower())

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

one_percentile = int(len(set(tokens)) * 0.01)
top_1_percentile = Counter(tokens).most_common(one_percentile)
top_1_percentile[:10]

bottom_1_percentile = Counter(tokens).most_common()[-one_percentile:]
bottom_1_percentile[:10]
# Al parecer las palabras que menos se repiten pueden ser mas. Vamos a agregar algunas

bottom_1_percentile = Counter(tokens).most_common()[-200:]
bottom_1_percentile[:200]

# No vamos a quitar las palabras que no tienen frecuencia porque hay demasiadas palabras que estan 1 sola vez.

noise_words.extend([word for word, val in top_1_percentile])

# 2 de las 4 palabras que agregamos, ya estaban en la lista. Una fue 'de' y la otra 'y'. Por lo que las sacamos

noise_words = set(noise_words)

# 5- stemming y Lemantización - despues lo vamos a probar -

porter = PorterStemmer()
lancaster = LancasterStemmer()
lemmatizer = WordNetLemmatizer()

#####################################################
# Armamos una lista partiendo de la lista de tokens y quitando las palabras que se encuentren
# en la lista de palabras a quitar "noise_words" creada anteriormente.

tokenize_data = [list(filter(lambda token: token not in noise_words, t)) for t in token_list]

# Crear una instancia del vectorizador TfidfVectorizer
tfidf_vectorizer = TfidfVectorizer(tokenizer=lambda x: x, preprocessor=lambda x: x)

# Transformar los datos en matriz tf-idf
tfidf = tfidf_vectorizer.fit_transform(tokenize_data)

# Crear una instancia del modelo LDA
lda_model_basic = LatentDirichletAllocation(n_components=10, random_state=0)

# Entrenar el modelo con los datos transformados
lda_model_basic.fit(tfidf)

# Obtener los temas para cada documento
topics_basic = lda_model_basic.transform(tfidf)

topic_indices_basic = np.argmax(topics_basic, axis=1)

topic_indices_basic

df_basic = df.assign(tema2=topic_indices_basic)

df_basic

df_basic[df_basic['tema2'] == 1]

# El resultado sigue siendo malo. Voy a tener que buscar una forma diferente de clasificarlos. Quiza usando mas datos.
# Ya que para esta prueba solo utilice un top 100 y quiza sean pocos registros


# Vamos a suponer que la tokenizacion esta bien hecha y vamos a pasar a hacer una optimizacion de hiperparametros

lda_base = LatentDirichletAllocation(random_state = 0,
                                     max_iter = 50)

grid_params = {'n_components': np.linspace(5, 20, num=10, endpoint=True).astype(int),
               'mean_change_tol': np.linspace(0.0001, 0.003, num=10, endpoint=True),
               'max_doc_update_iter': np.linspace(50, 200, num=10, endpoint=True).astype(int)
               }

lda_rscv = RandomizedSearchCV(lda_base,
                              grid_params,
                              cv = 5,
                              n_jobs = -1,
                              return_train_score = True,
                              n_iter= 20,
                              random_state = 7)

lda_rscv.fit(tfidf)

df_results = pd.DataFrame(lda_rscv.cv_results_)
df_results
lda_rscv.scorer_

lda_rscv.best_score_

lda_rscv.best_params_

# grid_params2 = {'n_components': np.linspace(3, 20, num=10, endpoint=True).astype(int),
#                'doc_topic_prior': None,
#                'topic_word_prior': None,
#                'learning_method': 'batch',
#                'max_iter': 10,
#                'evaluate_every': -1,
#                'total_samples': 1000000.0,
#                'perp_tol': 0.1,
#                'mean_change_tol': np.linspace(0.0001, 0.003, num=10, endpoint=True),
#                'max_doc_update_iter': np.linspace(50, 200, num=10, endpoint=True).astype(int),
#                'n_jobs': -1}

# Crear una instancia del modelo LDA
lda_model_1 = LatentDirichletAllocation(n_components=5,
                                        mean_change_tol=0.0023555555555555556,
                                        max_doc_update_iter=66,
                                        random_state=0)

# Entrenar el modelo con los datos transformados
lda_model_1.fit(tfidf)

# Obtener los temas para cada documento
topics_1 = lda_model_1.transform(tfidf)

topic_indices_1 = np.argmax(topics_1, axis=1)

df_1 = df.assign(tema2=topic_indices_1)

df_1[df_1['tema2'] == 1]

# Haciendo un analisis de este modelo y del anterior sin tuneo de hiperparametros, pude detectar que
# Existen palabras que se repiten mucho que no aportan nada y que las esta agurpando en la misma
# tematica, como por ejemplo "servicio","adquisición","concesión". Me gustaria quitarlas antes de probar
# algun modelo nuevo.

noise_words.update(["servicio","adquisición","concesión","convenio"])

tokenize_data = [list(filter(lambda token: token not in noise_words, t)) for t in token_list]
tfidf_vectorizer = TfidfVectorizer(tokenizer=lambda x: x, preprocessor=lambda x: x)
tfidf = tfidf_vectorizer.fit_transform(tokenize_data)
# Crear una instancia del modelo LDA
lda_model_basic = LatentDirichletAllocation(n_components=10, random_state=0)
lda_model_basic.fit(tfidf)
topics_basic = lda_model_basic.transform(tfidf)
topic_indices_basic = np.argmax(topics_basic, axis=1)

df_basic = df.assign(tema2=topic_indices_basic)

df_basic

df_basic[df_basic['tema2'] == 0]

for index, row in df_basic[df_basic['tema2'] == 1].iterrows():
    print(row['Nombre descriptivo de proceso'])

# No existe coherencia entre una fila y la otra, el modelo no funciona. Se prueba con tuneo de hiperparametros.
# Solo cambian los datos de entrenamiento por lo que se usa el mismo RandomizeSearchCV de antes

lda_rscv.fit(tfidf)

lda_rscv.best_params_


lda_model_2 = LatentDirichletAllocation(**(lda_rscv.best_params_),
                                        random_state=0)

# Entrenar el modelo con los datos transformados
lda_model_2.fit(tfidf)
topics_2 = lda_model_2.transform(tfidf)
topic_indices_2 = np.argmax(topics_2, axis=1)
df_2 = df.assign(tema2=topic_indices_2)

for index, row in df_2[df_2['tema2'] == 0].iterrows():
    print(row['Nombre descriptivo de proceso'])

# El resultado sigue sin ser bueno. Vamos a probar el LDA de Gensim en lugar de Sklear

cm = CoherenceModel(model=lda_rscv.best_estimator_, texts=tokenize_data, coherence='c_v')
coherence = cm.get_coherence()
