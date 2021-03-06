# _*_ coding: utf-8 _*_

"""
Search the best parameters of TF-IDF feature extractor (`TfidfVectorizer`)
where the prediction model is support vector machine (SVM).

Author: StrongXGP
Date:   2018/07/20
"""

import gc
import os
import pandas as pd
from time import time
from pprint import pprint
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer

# ============================================================================
# Load data

print("Loading data...")
data_file = "../../raw_data/train_set.csv"
df_data = pd.read_csv(data_file)

X_text = df_data['word_seg']  # words of samples (documents)
y = df_data['class']  # labels (1 ~ 19)
num_classes = max(y)
print("The number of samples is: %d" % len(X_text))
print("The number of classes is: %d" % num_classes)

del df_data
gc.collect()

# ============================================================================
# Search the best parameter

print("Start searching best value of 'min_df'...")

results = []
min_df_candidates = [3, 5, 10, 20]
for i in range(len(min_df_candidates)):
    print()
    print("min_df = %s" % min_df_candidates[i])

    # Vectorizer's hyper-parameters
    vect_params = {
        'ngram_range': (1, 2),
        'min_df': min_df_candidates[i],
        'max_df': 0.9,
        'max_features': 200000,
        'sublinear_tf': True
    }
    vectorizer = TfidfVectorizer(**vect_params)
    print("Vectorizer's hyper-parameters:")
    pprint(vect_params)

    print("Extract features...")
    t0_extract = time()
    X = vectorizer.fit_transform(X_text)
    print("Done in %.3f seconds" % (time() - t0_extract))
    print("Extract finished! ( ^ _ ^ ) V")

    print("Split data into training and validation set...")
    X_train, X_val, y_train, y_val = train_test_split(X, y, train_size=0.8, test_size=0.2, random_state=42)

    print("Start training...")
    clf = LinearSVC()
    t0_train = time()
    clf.fit(X_train, y_train - 1)  # labels must be in (0, 18)
    print("Done in %.3f seconds" % (time() - t0_train))
    print("Training finish! ( ^ _ ^ ) V ")

    pred_train = clf.predict(X_train) + 1
    pred_val = clf.predict(X_val) + 1
    acc_train = accuracy_score(y_train, pred_train)
    acc_val = accuracy_score(y_val, pred_val)
    f1_train = f1_score(y_train, pred_train, average='weighted')
    f1_val = f1_score(y_val, pred_val, average='weighted')
    print("Train Accuracy: %.2f, Validate Accuracy: %.2f" % (acc_train * 100, acc_val * 100))
    print("Train F1 Score: %.5f, Validate F1 Score: %.5f" % (f1_train, f1_val))

    result = [min_df_candidates[i], acc_train, acc_val, f1_train, f1_val]
    results.append(result)

# ============================================================================
# Save result

# Output directory
out_dir = os.path.abspath(os.path.join(os.path.curdir, "results"))
if not os.path.exists(out_dir):
    os.makedirs(out_dir)
print()
print("Writing to {}".format(out_dir))

print("Saving the results...")
df_res = pd.DataFrame(results, columns=['min_df', 'acc_train', 'acc_val', 'f1_train', 'f1_val'])
filename = "svm-tfidf-tuning-results-" + str(int(time())) + ".csv"
df_res.to_csv(os.path.join(out_dir, filename), index=False)
