import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA



class DataDrivenRankingSystem:
    def __init__(self, file_path, n): # inputting the pre-processed dat
        self.file_path = file_path
        self.df = self.load_data() 
        self.original_df = self.df.copy()
        self.features = None
        self.kmeans = None
        self.clusters = n

    def load_data(self):
        return pd.read_csv(self.file_path)

    def scaling_data(self):
        self.df = self.df.dropna()
        self.features = self.df.select_dtypes(include=[float, int]).columns
        scaler = StandardScaler()
        self.cc= scaler.fit_transform(self.df[self.features])

    def kmeans_clustering(self, n_clusters):   # Kmeans
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        labels = kmeans.fit_predict(self.df[self.features])
        score = silhouette_score(self.df[self.features], labels)
        return labels, score

    def hierarchical_clustering(self, n_clusters):   # Herierar
        hierarchical = AgglomerativeClustering(n_clusters=n_clusters)
        labels = hierarchical.fit_predict(self.df[self.features])
        score = silhouette_score(self.df[self.features], labels)
        return labels, score

    def dbscan_clustering(self):     # DBSCAN
        dbscan = DBSCAN()
        labels = dbscan.fit_predict(self.df[self.features])
        if len(set(labels)) > 1:
            score = silhouette_score(self.df[self.features], labels)
        else:
            score = -1
        return labels, score

    def best_clusters(self, n):
        best_labels = None
        best_score = -1
        best_method = None

        kmeans_labels, kmeans_score = self.kmeans_clustering(n)
        if kmeans_score > best_score:
            best_score = kmeans_score
            best_labels = kmeans_labels
            best_method = 'KMeans'

        hierarchical_labels, hierarchical_score = self.hierarchical_clustering(n)
        if hierarchical_score > best_score:
            best_score = hierarchical_score
            best_labels = hierarchical_labels
            best_method = 'Hierarchical'

        dbscan_labels, dbscan_score = self.dbscan_clustering()
        if dbscan_score > best_score:
            best_score = dbscan_score
            best_labels = dbscan_labels
            best_method = 'DBSCAN'

        return best_labels, best_score, best_method

    def cluster_data(self, n_clusters):
        labels, score, method = self.best_clusters(n_clusters)
        self.df['Cluster'] = labels
        self.original_df['Cluster'] = labels 
        return method, score

    def rank_clusters(self):
        cluster_means = self.df.groupby('Cluster').mean()
        cluster_means['Rank'] = cluster_means.mean(axis=1).rank(ascending=False)
        return cluster_means.sort_values('Rank') 

    def save_data(self, output_file):
        self.original_df.to_csv(output_file, index=False)  # Save the original data with clusters 

    def plot_clusters(self):
        pca = PCA(n_components=2)    # using PCA for best two features
        principal_components = pca.fit_transform(self.df[self.features])
        plt.figure(figsize=(10, 6))
        plt.scatter(principal_components[:, 0], principal_components[:, 1], c=self.df['Cluster'], cmap='viridis', marker='o')
        plt.xlabel('Principal Component 1')
        plt.ylabel('Principal Component 2')
        plt.title('Cluster Plot')
        plt.colorbar(label='Cluster')
        plt.show()
        
    # def plot_clusters(self):
    #     plt.figure(figsize=(10, 6))
    #     plt.scatter(self.df[self.features[0]], self.df[self.features[1]], c=self.df['Cluster'], cmap='viridis', marker='o')
    #     plt.xlabel(self.features[0])
    #     plt.ylabel(self.features[1])
    #     plt.title('Cluster Plot')
    #     plt.colorbar(label='Cluster')
    #     plt.show()    

    def process(self, output_file):   # calling all the functions
        self.scaling_data()
        method, score = self.cluster_data(3)
        ranked_clusters = self.rank_clusters()
        self.save_data(output_file)
        self.plot_clusters()
        print(f"Best Clustering Method: {method}")
     #    print('\n')
        print(f"Best Silhouette Score: {score}")
     #    print('\n')
        return ranked_clusters

if __name__ == "__main__":
    cricket_ranking_system = DataDrivenRankingSystem('/Users/rahuljogi/Desktop/@S4/ML/Project__/Datasets/BBL/pre_processed_data_bbl_ball.csv',3)
    cricket_ranking = cricket_ranking_system.process('/Users/rahuljogi/Desktop/@S4/ML/Project__/Results/BBL_clustered.csv')
    print(cricket_ranking.head(5))