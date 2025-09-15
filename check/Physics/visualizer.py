"""
Visualization module for clustering results with PCA, t-SNE and hybrid dimensionality reduction.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from collections import Counter

class ClusterVisualizer:
    def __init__(self, output_dir='data/plots'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def plot_cluster_sizes(self, cluster_results, prefix=''):
        """Plot cluster size distributions."""
        print(f"\nPlotting cluster size distributions for {prefix}...")
        
        n_methods = len(cluster_results)
        fig, axes = plt.subplots(n_methods, 1, figsize=(12, 5*n_methods))
        if n_methods == 1:
            axes = [axes]
        
        for ax, (method, labels) in zip(axes, cluster_results.items()):
            # Count cluster sizes
            cluster_sizes = Counter(labels)
            sizes = list(cluster_sizes.values())
            
            # Plot histogram
            ax.hist(sizes, bins=30, edgecolor='black')
            ax.set_title(f'Cluster Size Distribution - {method}')
            ax.set_xlabel('Cluster Size')
            ax.set_ylabel('Number of Clusters')
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, f'{prefix}cluster_sizes.png'))
        plt.close()
        
    def _plot_2d_clusters(self, embeddings_2d, labels, method, title, filename):
        """Helper function to create 2D scatter plots."""
        plt.figure(figsize=(12, 8))
        scatter = plt.scatter(embeddings_2d[:, 0], embeddings_2d[:, 1],
                            c=labels, cmap='tab20', alpha=0.6)
        plt.colorbar(scatter)
        plt.title(title)
        plt.xlabel('First Component')
        plt.ylabel('Second Component')
        plt.savefig(filename)
        plt.close()

    def plot_pca_visualization(self, embeddings, cluster_results, prefix=''):
        """Create PCA visualization of clusters."""
        print(f"\nGenerating PCA visualizations for {prefix}...")
        
        # Perform PCA
        pca = PCA(n_components=2)
        embeddings_2d = pca.fit_transform(embeddings)
        explained_var = pca.explained_variance_ratio_
        
        # Plot for each clustering result
        for method, labels in cluster_results.items():
            title = f'PCA Visualization - {method}\nExplained variance: {explained_var[0]:.2%}, {explained_var[1]:.2%}'
            filename = os.path.join(self.output_dir, f'{prefix}pca_{method}.png')
            self._plot_2d_clusters(embeddings_2d, labels, method, title, filename)

    def plot_tsne_visualization(self, embeddings, cluster_results, prefix=''):
        """Create t-SNE visualization of clusters."""
        print(f"\nGenerating t-SNE visualizations for {prefix}...")
        
        # Perform t-SNE
        tsne = TSNE(n_components=2, random_state=42, perplexity=30)
        embeddings_2d = tsne.fit_transform(embeddings)
        
        # Plot for each clustering result
        for method, labels in cluster_results.items():
            title = f't-SNE Visualization - {method}'
            filename = os.path.join(self.output_dir, f'{prefix}tsne_{method}.png')
            self._plot_2d_clusters(embeddings_2d, labels, method, title, filename)

    def plot_hybrid_visualization(self, embeddings, cluster_results, prefix=''):
        """Create hybrid PCA+t-SNE visualization of clusters."""
        print(f"\nGenerating hybrid PCA+t-SNE visualizations for {prefix}...")
        
        # First reduce to 50 dimensions with PCA
        pca = PCA(n_components=50)
        embeddings_50d = pca.fit_transform(embeddings)
        explained_var_50d = np.sum(pca.explained_variance_ratio_)
        
        # Then apply t-SNE
        tsne = TSNE(n_components=2, random_state=42, perplexity=30)
        embeddings_2d = tsne.fit_transform(embeddings_50d)
        
        # Plot for each clustering result
        for method, labels in cluster_results.items():
            title = f'Hybrid PCA(50d) + t-SNE Visualization - {method}\nPCA explained variance (50d): {explained_var_50d:.2%}'
            filename = os.path.join(self.output_dir, f'{prefix}hybrid_{method}.png')
            self._plot_2d_clusters(embeddings_2d, labels, method, title, filename)
            
    def plot_metrics_comparison(self, metrics, prefix=''):
        """Plot comparison of clustering metrics."""
        print(f"\nPlotting metrics comparison for {prefix}...")
        
        # Extract metrics for comparison
        methods = list(metrics.keys())
        silhouette_scores = [metrics[m].get('silhouette_score', 0) for m in methods]
        calinski_scores = [metrics[m].get('calinski_harabasz_score', 0) for m in methods]
        n_clusters = [metrics[m]['n_clusters'] for m in methods]
        
        # Create subplots
        fig, axes = plt.subplots(3, 1, figsize=(12, 15))
        
        # Plot silhouette scores
        axes[0].bar(methods, silhouette_scores)
        axes[0].set_title('Silhouette Scores by Method')
        axes[0].set_xticklabels(methods, rotation=45)
        axes[0].grid(True, alpha=0.3)
        
        # Plot Calinski-Harabasz scores
        axes[1].bar(methods, calinski_scores)
        axes[1].set_title('Calinski-Harabasz Scores by Method')
        axes[1].set_xticklabels(methods, rotation=45)
        axes[1].grid(True, alpha=0.3)
        
        # Plot number of clusters
        axes[2].bar(methods, n_clusters)
        axes[2].set_title('Number of Clusters by Method')
        axes[2].set_xticklabels(methods, rotation=45)
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, f'{prefix}metrics_comparison.png'))
        plt.close()
