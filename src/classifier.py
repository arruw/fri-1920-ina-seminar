import pandas as pd
from sklearn.model_selection import train_test_split, cross_validate
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn import preprocessing, neighbors
from sklearn.ensemble import BaggingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score
from sklearn.feature_selection import VarianceThreshold
from statistics import mean, stdev
from sklearn.metrics import plot_confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from random import randint, seed

best_avg_method = 0 # resource alloc best avg method
classifiers = ['SVC', 'KNN', 'RNDF']
link_prediction_methods = ['resource_allocation',
													 'jaccard_coefficient',
													 'preferential_attachment',
													 'community',
													 'sorensen_neighbours']
N_OF_RUNS = 10 # number of times we build the model

def compute_ca(aucs,X_test,model):
  rowValues = X_test.to_numpy()
  predictions = []
  for (index,_),rowData in zip(X_test.iterrows(),rowValues):
    predictions.append((index,model.predict(rowData.reshape(1,-1))[0])) # row index and class
  correct = 0
  n = len(predictions)
  for index,bestMethod in predictions:
    if aucs[index][bestMethod] >= aucs[index][best_avg_method]:
      correct += 1
  return correct/n

def info(runScores):
  for classifier,scores in zip(classifiers,runScores):
    print(f'{classifier} mean CA: {round(mean(scores)*100,3)}, stdev: {round(stdev(scores)*100,3)}')

if __name__ == '__main__':
  dataset = pd.read_csv('data/precomputed_with_classes_3.csv')
  target = dataset['class'].astype(int)
  aucs = dataset.iloc[:,-5:].to_numpy()
  dataset.drop(['r','name','download_url']+link_prediction_methods, 1, inplace=True)
  dataset = pd.get_dummies(dataset) # one hot encode categorical attributes

  cor = dataset.corr()
  cor_target = abs(cor['class'])
  relevant_features = cor_target[cor_target > 0.03]
  #print(relevant_features)

  selected_columns = ['C_avg']
  dataset.drop(dataset.columns.difference(selected_columns), 1, inplace=True)

  scores = [[] for i in range(len(classifiers))] # scores for every method and run
  seed(42) # for reproducability

  for run in range(N_OF_RUNS):
    print(f'Run {run}/{N_OF_RUNS}')
    X_train, X_test, y_train, y_test = train_test_split(dataset,target,test_size=0.2,random_state=randint(0,10000))

    model = SVC()
    model.fit(X_train, y_train)
    scores[0].append(compute_ca(aucs,X_test,model))

    model2 = neighbors.KNeighborsClassifier(n_neighbors=3)
    model2.fit(X_train, y_train)
    scores[1].append(compute_ca(aucs,X_test,model2))

    model3 = RandomForestClassifier(n_estimators=100)
    model3.fit(X_train, y_train)
    scores[2].append(compute_ca(aucs,X_test,model3))

  info(scores)