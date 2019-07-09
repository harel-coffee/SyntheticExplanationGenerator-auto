import string
import numpy as np
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer


def _predict_proba(x, word_val):
    values = list()
    for w in x.split(' '):
        if w in word_val:
            values.append(word_val[w])

    if len(values) > 0:
        val = np.mean(values)
        val = (val - (-1)) / (1 - (-1))
        return val
    else:
        return 0.5


def preprocess_data(X):
    X_new = list()
    for s in X:
        s = s.translate(str.maketrans('', '', string.digits))
        s = s.translate(str.maketrans('', '', string.punctuation))
        s = s.lower()
        s = s.strip()
        s = s.strip('\n')
        s = s.strip('\r')
        s = s.strip('\r\n')
        s = s.rstrip()
        s = s.rstrip('\n')
        s = s.rstrip('\r')
        s = s.rstrip('\r\n')
        X_new.append(s)
    X = np.array(X_new)
    return X


def generate_synthetic_text_classifier(n_features, p=0.5):

    X_train = fetch_20newsgroups(subset='train', remove=('headers', 'footers', 'quotes'), categories=None).data
    X_train = preprocess_data(X_train)

    vectorizer = TfidfVectorizer(stop_words='english', lowercase=True, ngram_range=(1, 1),
                                 use_idf=False, smooth_idf=False, min_df=0.01)
    vectorizer.fit(X_train)

    feature_names = list(vectorizer.get_feature_names())
    nbr_terms = len(feature_names)
    selected_features = np.random.choice(range(nbr_terms), n_features, replace=False)
    word_val = dict()
    for i in selected_features:
        sign = np.random.choice([-1.0, 1.0], p=[p, 1 - p])
        val = np.random.random()
        word_val[feature_names[i]] = sign * val

    def predict_proba(X):
        proba = list()
        for x in X:
            val = _predict_proba(x, word_val)
            proba.append(np.array([1.0 - val, val]))
        proba = np.array(proba)
        return proba

    def predict(X):
        proba = predict_proba(X)
        return np.argmax(proba, axis=1)

    srbc = {
        'n_features': n_features,
        'words': word_val,
        'predict_proba': predict_proba,
        'predict': predict
    }

    return srbc


def get_word_importance_explanation(x, stc):
    words = stc['words']
    wx_val = dict()
    for w in x.split(' '):
        wx_val[w] = words.get(w, 0.0)

    return wx_val


def main():

    n_features = 100

    stc = generate_synthetic_text_classifier(n_features=n_features)

    predict = stc['predict']
    predict_proba = stc['predict_proba']
    words = stc['words']

    # print(words)

    X_test = fetch_20newsgroups(subset='test', remove=('headers', 'footers', 'quotes'), categories=None).data
    X_test = preprocess_data(X_test)

    Y_test = predict(X_test)
    # print(np.unique(Y_test, return_counts=True))
    # print(X_test[0])
    # print(Y_test[0])
    # print(_predict_proba(X_test[0], words))

    for x in X_test:
        expl_val = get_word_importance_explanation(x, stc)
        print(expl_val)
        break


if __name__ == "__main__":
    main()