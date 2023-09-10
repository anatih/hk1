> Никита Михалкин:
# эти библиотеки нам уже знакомы
import pandas as pd
import numpy as np

# модуль sparse библиотеки scipy понадобится
# для работы с разреженными матрицами (об этом ниже)
from scipy.sparse import csr_matrix

# из sklearn мы импортируем алгоритм k-ближайших соседей
from sklearn.neighbors import NearestNeighbors

# прочитаем внешние файлы (перед этим их необходимо импортировать) и преобразуем в датафрейм
movies = pd.read_csv('/content/submission.csv')
ratings = pd.read_csv('/content/gardening_test.tsv',sep='\t')


# и ratings.csv (здесь также удаляем ненужный столбец timestamp)
ratings.drop(['device_id','local_date', 'price'], axis = 1, inplace = True)
ratings.head(3)

# для этого воспользуемся функцией pivot и создадим сводную таблицу (pivot table)
# по горизонтали будут фильмы, по вертикали - пользователи, значения - оценки
ratings = ratings.drop_duplicates(['receipt_id', 'item_id'])
user_item_matrix = ratings.pivot(index='receipt_id', columns='item_id', values='quantity')
user_item_matrix.head()

# пропуски NaN нужно преобразовать в нули
# параметр inplace = True опять же поможет сохранить результат
user_item_matrix.fillna(0, inplace = True)
user_item_matrix.head()

# посмотрим на размерность матрицы "пользователи х фильмы"
user_item_matrix.shape

# вначале сгруппируем (объединим) пользователей, возьмем только столбец rating
# и посчитаем, сколько было оценок у каждого пользователя
users_votes = ratings.groupby('item_id')['quantity'].agg('count')

# сделаем то же самое, только для фильма
movies_votes = ratings.groupby('receipt_id')['quantity'].agg('count')

# теперь создадим фильтр (mask)
user_mask = users_votes[users_votes > 50].index
movie_mask = movies_votes[movies_votes > 10].index

# применим фильтры и отберем фильмы с достаточным количеством оценок
user_item_matrix = user_item_matrix.loc[movie_mask,:]

# а также активных пользователей
user_item_matrix = user_item_matrix.loc[:,user_mask]

# посмотрим сколько пользователей и фильмов осталось
user_item_matrix.shape

# преобразуем разреженную матрицу в формат csr
# метод values передаст функции csr_matrix только значения датафрейма
csr_data = csr_matrix(user_item_matrix.values)

# посмотрим на первые записи
# сопоставьте эти значения с исходной таблицей выше
print(csr_data[:2,:5])

# остается только сбросить индекс с помощью reset_index()
# это необходимо для удобства поиска фильма по индексу
user_item_matrix = user_item_matrix.rename_axis(None, axis = 1).reset_index()
user_item_matrix.head()

# воспользуемся классом NearestNeighbors для поиска расстояний
knn = NearestNeighbors(metric = 'cosine', algorithm = 'brute', n_neighbors = 20, n_jobs = -1)

# обучим модель
knn.fit(csr_data)

# ждя начала определимся, сколько рекомендаций мы хотим получить
recommendations = 20

# и на основе какого фильма
search_word = 'Семена огурец Кураж F1 5 шт Престиж'

# для начала найдем фильм в заголовках датафрейма movies
movie_search = ratings[ratings['name'].str.contains(search_word)]
movie_search

# вариантов может быть несколько, для простоты всегда будем брать первый вариант
# через iloc[0] мы берем первую строку столбца ['movieId']
movie_id = movie_search.iloc[0]['receipt_id']

# далее по индексу фильма в датасете movies найдем соответствующий индекс
# в матрице предпочтений
movie_id = movie_search[movie_search['receipt_id'] == movie_id].index[0]
movie_id

# теперь нужно найти индексы и расстояния фильмов, которые похожи на наш запрос
# воспользуемся методом kneighbors()
distances, indices = knn.kneighbors(csr_data[movie_id], n_neighbors = recommendations + 1)

# индексы рекомендованных фильмов
indices

# расстояния до них
distances

# уберем лишние измерения через squeeze() и преобразуем массивы в списки с помощью tolist()
indices_list = indices.squeeze().tolist()
distances_list = distances.squeeze().tolist()

# далее с помощью функций zip и list преобразуем наши списки
indices_distances = list(zip(indices_list, distances_list))

# в набор кортежей (tuple)
print(type(indices_distances[0]))

> Никита Михалкин:
# и посмотрим на первые три пары/кортежа
print(indices_distances[:3])
# остается отсортировать список по расстояниям через key = lambda x: x[1] (то есть по второму элементу)
# в возрастающем порядке reverse = False
indices_distances_sorted = sorted(indices_distances, key = lambda x: x[1], reverse = False)

# и убрать первый элемент с индексом 901 (потому что это и есть "Матрица")
indices_distances_sorted = indices_distances_sorted[1:]
indices_distances_sorted

# создаем пустой список, в который будем помещать название фильма и расстояние до него
recom_list = []

# в цикле будем поочередно проходить по кортежам
for ind_dist in indices_distances_sorted:

    # искать movieId в матрице предпочтений
    matrix_movie_id = user_item_matrix.iloc[ind_dist[0]]['receipt_id']

    # выяснять индекс этого фильма в датафрейме movies
    id = user_item_matrix[user_item_matrix['receipt_id'] == matrix_movie_id].index[0]  # Исправление здесь

  

    # помещать каждую пару в питоновский словарь
    # который, в свою очередь, станет элементом списка recom_list
    recom_list.append({'Title': title, 'Distance': dist})

#
recom_list[0]

# остается преобразовать наш список в датафрейм
# индекс будем начинать с 1, как и положено рейтингу
recom_df = pd.DataFrame(recom_list, index = range(1, recommendations + 1))
recom_df
