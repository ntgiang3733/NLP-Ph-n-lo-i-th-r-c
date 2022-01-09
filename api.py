from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from flask_cors import CORS

from pyvi import ViTokenizer
import pandas as pd
from gensim.parsing.preprocessing import strip_non_alphanum, strip_multiple_whitespaces,preprocess_string, split_alphanum, strip_short, strip_numeric
import re
import numpy as np
from sklearn.metrics import accuracy_score

import services as services

xl_file_train = pd.ExcelFile("./data_train.xlsx")
dfs_train = xl_file_train.parse('Sheet1')

xl_file_test = pd.ExcelFile("./data_test.xlsx")
dfs_test = xl_file_test.parse('Sheet1')

old_document = []
old_document_test = []
document = []
label = []
label_test = []

for d in dfs_train.Document:
    old_document.append(d)

for l in dfs_train.Label:
    label.append(l)

for d in dfs_test.Document:
    old_document_test.append(d)

for l in dfs_test.Label:
    label_test.append(l)

document = [services.raw_text_preprocess(d) for d in old_document]

document_test = [services.raw_text_preprocess(d) for d in old_document_test]

set_words = []

for doc in document:
    words = doc.split(' ')
    set_words += words
    set(set_words)

vectors = []

for doc in document:
    vector = np.zeros(len(set_words))
    for i, word in enumerate(set_words):
        if word in doc:
            vector[i] = 1
    vectors.append(vector)
np.shape(vectors)

spam = 0
non_spam = 0
for l in label:
    if l == 1:
        spam += 1
    else:
        non_spam += 1

spam_coef = services.smoothing(spam, (spam+non_spam))
non_spam_coef = services.smoothing(non_spam, (spam+non_spam))

bayes_matrix = np.zeros((len(set_words), 4))

for i, word in enumerate(set_words):
    app_spam = 0
    app_nonspam = 0
    nonapp_spam = 0
    nonapp_nonspam = 0
    for k, v in enumerate(vectors):
        if v[i] == 1:
            if label[k] == 1:
                app_spam += 1
            else:
                app_nonspam += 1
        else:
            if label[k] == 1:
                nonapp_spam += 1
            else:
                nonapp_nonspam += 1

    bayes_matrix[i][0] = services.smoothing(app_spam, spam)
    bayes_matrix[i][1] = services.smoothing(app_nonspam, non_spam)
    bayes_matrix[i][2] = services.smoothing(nonapp_spam, spam)
    bayes_matrix[i][3] = services.smoothing(nonapp_nonspam, non_spam)



log = np.zeros(2)

predict_spam = spam_coef  # P(spam)
predict_non_spam = non_spam_coef  # P(non_spam)

index = 0

for i, v in enumerate(vector):
    if v == 0:
        predict_spam *= bayes_matrix[i][2]  # P(xi|cj)
        predict_non_spam *= bayes_matrix[i][3]
    else:
        predict_spam *= bayes_matrix[i][0]
        predict_non_spam *= bayes_matrix[i][1]

    if predict_spam < 1e-10:
        predict_spam *= 1000
        log[0] += 1

    if predict_non_spam < 1e-10:
        predict_non_spam *= 1000
        log[1] += 1

pred = [services.predict(d, set_words, spam_coef, non_spam_coef, bayes_matrix) for d in document_test]
accuracy_score(label_test, pred)
result = accuracy_score(label_test, pred)

app = Flask(__name__)
CORS(app)
api = Api(app)

RESULT = {
    'old_document': old_document,
    'old_document_test': old_document_test,
    'document' : document,
    'label': label,
    'label_test': label_test,
    'pred': pred,
    'result': result
}

parser = reqparse.RequestParser()
parser.add_argument('task')

class Result(Resource):
    def get(self):
        return RESULT

api.add_resource(Result, '/result')

if __name__ == '__main__':
    app.run(debug=True)