"""Project_4.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1pU2bnmbO50CifS4Up019sh6VvbGpg2bu

#Modules
"""

import numpy as np
import matplotlib.pyplot as plt
import os
from google.colab import drive
import pandas as pd
import zipfile
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from tabulate import tabulate

"""#Data Extraction"""

# Authenticate and mount Google Drive
drive.mount('/content/drive')

!ls "/content/drive/MyDrive/GE-461/Project 4/ge461_pw13_data.zip"

# Path to zip file inside Google Drive
zip_path = '/content/drive/MyDrive/GE-461/Project 4/ge461_pw13_data.zip'

# Specify the name of the CSV file inside the zip file
csv_filename = 'falldetection_dataset.csv'

# Extract the CSV file from the zip archive
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extract(csv_filename, '/content/')

# Load the CSV file into a DataFrame
df = pd.read_csv(f'/content/{csv_filename}', header=None)

# Separate features (X) and labels (y)
X = df.iloc[:, 2:]
y = df.iloc[:, 1]

# Display the shape of X and y
print("Shape of X:", X.shape)
print("Shape of y:", y.shape)

# Display the first few rows of X and y to verify
print("\nFeatures (X):")
print(X.head())

print("\nLabels (y):")
print(y.head())

# Update y to numeric values: "F" (Fall) -> 1, "NF" (Non-Fall) -> 0
y = (y == 'F').astype(int)

"""#Part A

##PCA
"""

# Standardize the features
#scaler = MinMaxScaler()
#X_scaled = scaler.fit_transform(X)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)


# Perform PCA to extract top two principal components
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

# Calculate the variance explained by each principal component
explained_variance_ratio = pca.explained_variance_ratio_
print("Variance explained by PC1 and PC2:", explained_variance_ratio)

# Visualize the PCA results with categorical labels (F: Fall, NF: Non-Fall)
plt.figure(figsize=(8, 6))
plt.scatter(X_pca[y == 1, 0], X_pca[y == 1, 1], label='Fall', color='red', alpha=0.5)
plt.scatter(X_pca[y == 0, 0], X_pca[y == 0, 1], label='Non-Fall', color='blue', alpha=0.5)
plt.title('PCA: Top Two Principal Components (Categorical Labels)')
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.legend()
plt.show()

"""##K-Means"""

# Try different numbers of clusters (N)
num_clusters = [2, 3, 4, 5, 6]

# Visualize clustering results for each number of clusters (N)
plt.figure(figsize=(15, 8))

for i, n in enumerate(num_clusters, start=1):
    # Initialize k-means clustering with n clusters
    kmeans = KMeans(n_clusters=n, n_init=10, random_state=42)
    cluster_labels = kmeans.fit_predict(X_pca)
    # Calculate silhouette score
    silhouette_avg = silhouette_score(X_pca, cluster_labels)
    # Calculate Davies-Bouldin Index
    davies_bouldin_avg = davies_bouldin_score(X_pca, cluster_labels)
    # Plot clusters in a subplot
    plt.subplot(2, 3, i)
    plt.scatter(X_pca[:, 0], X_pca[:, 1], c=cluster_labels, cmap='viridis', alpha=0.5)
    plt.title(f'Clusters (N={n})\nSilhouette Score: {silhouette_avg:.2f}, Davies-Bouldin Index: {davies_bouldin_avg:.2f}')
    plt.xlabel('Principal Component 1')
    plt.ylabel('Principal Component 2')
    plt.colorbar(label='Cluster')

plt.tight_layout()
plt.show()

# Initialize k-means clustering with N=2 clusters
kmeans_2 = KMeans(n_clusters=2, n_init=10, random_state=42)
cluster_labels_2 = kmeans_2.fit_predict(X_pca)

# Adjust cluster labels to match the encoding of original action labels
cluster_labels_adjusted = 1 - cluster_labels_2  # Flip labels (0 -> 1, 1 -> 0)

# Calculate accuracy (percentage overlap) between cluster memberships and original labels
accuracy_2 = accuracy_score(y, cluster_labels_adjusted)

# Calculate percentage of correct classifications
percentage_correct = accuracy_2 * 100

print(f"Percentage of Correct Classifications (N=2 Clusters): {percentage_correct:.2f}%")

"""#Part B"""

# Split the data into training (60%), validation (20%), and testing (20%) sets
X_train_val, X_test, y_train_val, y_test = train_test_split(X, y, test_size=0.20, random_state=42)
X_train, X_val, y_train, y_val = train_test_split(X_train_val, y_train_val, test_size=0.25, random_state=42)

# Standardize the features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_val_scaled = scaler.transform(X_val)
X_test_scaled = scaler.transform(X_test)

# Define parameter grids for SVM and MLP classifiers
param_grid_svm = {'C': [0.2, 2, 20], 'gamma': [0.1,0.01, 0.001], 'kernel': ['linear', 'rbf','sigmoid'], 'class_weight':['none']}
param_grid_mlp = {'hidden_layer_sizes': [(25,), (50,), (25, 25)], 'activation': ['relu', 'tanh'], 'alpha': [0.001, 0.01,0.1], 'solver':['adam', 'sgd']}

# Initialize StratifiedKFold for 5-fold cross-validation
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# Intermediate Results Storage
svm_results = []
mlp_results = []

# Perform grid search and cross-validation for SVM classifier
best_svm_clf = None
best_svm_accuracy = 0
for C in param_grid_svm['C']:
    for gamma in param_grid_svm['gamma']:
        for kernel in param_grid_svm['kernel']:
            avg_val_accuracy = 0
            for train_index, val_index in skf.split(X_train_val, y_train_val):
                X_train_fold, X_val_fold = X_train_val.iloc[train_index], X_train_val.iloc[val_index]
                y_train_fold, y_val_fold = y_train_val.iloc[train_index], y_train_val.iloc[val_index]

                X_train_fold_scaled = scaler.fit_transform(X_train_fold)
                X_val_fold_scaled = scaler.transform(X_val_fold)

                svm_clf = SVC(C=C, gamma=gamma, kernel=kernel)
                svm_clf.fit(X_train_fold_scaled, y_train_fold)
                y_val_pred_svm = svm_clf.predict(X_val_fold_scaled)
                val_accuracy = accuracy_score(y_val_fold, y_val_pred_svm)
                avg_val_accuracy += val_accuracy / 5
            svm_results.append([C, gamma, kernel, avg_val_accuracy])
            if avg_val_accuracy > best_svm_accuracy:
                best_svm_accuracy = avg_val_accuracy
                best_svm_clf = SVC(C=C, gamma=gamma, kernel=kernel)

# Perform grid search and cross-validation for MLP classifier
best_mlp_clf = None
best_mlp_accuracy = 0

for hidden_layer_sizes in param_grid_mlp['hidden_layer_sizes']:
    for activation in param_grid_mlp['activation']:
        for alpha in param_grid_mlp['alpha']:
            avg_val_accuracy = 0
            for train_index, val_index in skf.split(X_train_val, y_train_val):
                X_train_fold, X_val_fold = X_train_val.iloc[train_index], X_train_val.iloc[val_index]
                y_train_fold, y_val_fold = y_train_val.iloc[train_index], y_train_val.iloc[val_index]

                X_train_fold_scaled = scaler.fit_transform(X_train_fold)
                X_val_fold_scaled = scaler.transform(X_val_fold)

                mlp_clf = MLPClassifier(hidden_layer_sizes=hidden_layer_sizes, activation=activation, alpha=alpha)
                mlp_clf.fit(X_train_fold_scaled, y_train_fold)
                y_val_pred_mlp = mlp_clf.predict(X_val_fold_scaled)
                val_accuracy = accuracy_score(y_val_fold, y_val_pred_mlp)
                avg_val_accuracy += val_accuracy / 5  # Average validation accuracy across folds
            mlp_results.append([hidden_layer_sizes, activation, alpha, avg_val_accuracy])
            if avg_val_accuracy > best_mlp_accuracy:
                best_mlp_accuracy = avg_val_accuracy
                best_mlp_clf = MLPClassifier(hidden_layer_sizes=hidden_layer_sizes, activation=activation, alpha=alpha)

# Display Results in a Table
print("\nSVM Classifier Results:")
headers_svm = ["C", "Gamma", "Kernel", "Avg. Validation Accuracy"]
print(tabulate(svm_results, headers=headers_svm, floatfmt=".4f"))

print("\nMLP Classifier Results:")
headers_mlp = ["Hidden Layer Sizes", "Activation", "Alpha", "Avg. Validation Accuracy"]
print(tabulate(mlp_results, headers=headers_mlp, floatfmt=".4f"))

# Initialize scaler for data normalization
scaler = StandardScaler()

# Evaluate the best SVM classifier on the testing set
X_train_scaled_svm = scaler.fit_transform(X_train)
best_svm_clf.fit(X_train_scaled_svm, y_train)
X_test_scaled_svm = scaler.transform(X_test)
y_test_pred_svm = best_svm_clf.predict(X_test_scaled_svm)
accuracy_test_svm = accuracy_score(y_test, y_test_pred_svm)
report_svm = classification_report(y_test, y_test_pred_svm, output_dict=True)

# Evaluate the best MLP classifier on the testing set
X_train_scaled_mlp = scaler.fit_transform(X_train)
best_mlp_clf.fit(X_train_scaled_mlp, y_train)
X_test_scaled_mlp = scaler.transform(X_test)
y_test_pred_mlp = best_mlp_clf.predict(X_test_scaled_mlp)
accuracy_test_mlp = accuracy_score(y_test, y_test_pred_mlp)
report_mlp = classification_report(y_test, y_test_pred_mlp, output_dict=True)

# Create DataFrame to summarize testing results
data = {
    'Classifier': ['Best SVM', 'Best MLP'],
    'Testing Accuracy': [accuracy_test_svm, accuracy_test_mlp],
    'Precision (weighted avg)': [report_svm['weighted avg']['precision'], report_mlp['weighted avg']['precision']],
    'Recall (weighted avg)': [report_svm['weighted avg']['recall'], report_mlp['weighted avg']['recall']],
    'F1-score (weighted avg)': [report_svm['weighted avg']['f1-score'], report_mlp['weighted avg']['f1-score']]
}

test_results_df = pd.DataFrame(data)
print("Testing Results:")
print(test_results_df)