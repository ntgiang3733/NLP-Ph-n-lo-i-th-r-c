from pyvi import ViTokenizer
import pandas as pd
from gensim.parsing.preprocessing import strip_non_alphanum, strip_multiple_whitespaces,preprocess_string, split_alphanum, strip_short, strip_numeric
import re 
import numpy as np
from sklearn.metrics import accuracy_score

def raw_text_preprocess(raw):
    raw = re.sub(r"http\S+", "", raw)
    raw = strip_non_alphanum(raw).lower().strip()
    raw = split_alphanum(raw)
    raw = strip_short(raw, minsize=2)
    raw = strip_numeric(raw)
    raw = ViTokenizer.tokenize(raw)

    return raw

def smoothing(a, b):
    return float((a+1)/(b+1))

def compare(predict_spam, predict_non_spam, log):
    while (log[0] > log[1]):
        predict_spam /= 10
        log[0] -= 1
        if predict_spam > predict_non_spam:
            return True

    while (log[1] > log[0]):
        predict_non_spam /= 10
        log[1] -= 1
        if predict_non_spam > predict_spam:
            return False

    if predict_spam > predict_non_spam:
        return True
    return False


def predict(mail, set_words, spam_coef, non_spam_coef, bayes_matrix):
    mail = raw_text_preprocess(mail)

    vector = np.zeros(len(set_words))
    for i, word in enumerate(set_words):
        if word in mail:
            vector[i] = 1
    log = np.zeros(2)

    predict_spam = spam_coef
    predict_non_spam = non_spam_coef

    for i, v in enumerate(vector):
        if v == 0:
            predict_spam *= bayes_matrix[i][2]
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

    if compare(predict_spam, predict_non_spam, log):
        return 1
    return 0
