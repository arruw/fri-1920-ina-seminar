import pandas as pd
from sklearn.model_selection import train_test_split, cross_validate
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn import preprocessing, neighbors
from sklearn.ensemble import BaggingClassifier
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score
from sklearn.feature_selection import VarianceThreshold
from statistics import mean
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import plot_confusion_matrix
from sklearn.ensemble import AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

if __name__ == '__main__':
  dataset = pd.read_csv('data/precomputed_with_classes_2.csv')
  target = dataset['class'].astype(int)
  
  cor = dataset.corr()
  cor_target = abs(cor['class'])
  relevant_features = cor_target[cor_target > 0.02]
  #print(relevant_features)

  dataset.drop(['r','name','download_url'], 1, inplace=True)
  dataset = pd.get_dummies(dataset) # s tem binariziramo vse atribute
  dataset.drop(dataset.columns.difference(['m','k_avg','C_avg','C','category_misc','category_protein']), 1, inplace=True)

  X_train, X_test, y_train, y_test = train_test_split(dataset,target,test_size=0.2,random_state=42)
  folds = 5

  model = SVC()
  model.fit(X_train, y_train)
  print("SVC: ", model.score(X_test, y_test))
  scores = cross_val_score(model, dataset, target, cv=folds)
  print("SVC cross: ", mean(scores))

  model2 = neighbors.KNeighborsClassifier()
  model2.fit(X_train, y_train)
  print("KNN: ",model2.score(X_test,y_test))
  scores = cross_val_score(model2, dataset, target, cv=folds)
  print("KNN cross: ",mean(scores))

  model3 = RandomForestClassifier()
  model3.fit(X_train, y_train)
  print("Random Forest: ",model3.score(X_test, y_test))
  scores = cross_val_score(model3, dataset, target, cv=folds)
  print("Random Forest cross: ", mean(scores))