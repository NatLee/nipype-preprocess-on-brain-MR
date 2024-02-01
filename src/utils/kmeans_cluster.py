from sklearn.cluster import KMeans
import numpy as np

from utils.extract_features import extract_features

def kmeans_cluster(data:np.ndarray, n_clusters:int):
    features = extract_features(data)
    intensities = features[..., 0].reshape((-1, 1))
    kmeans_model = KMeans(
        n_clusters=n_clusters,
        init="k-means++",
        precompute_distances=True,
        verbose=0,
        random_state=7,
        n_jobs=1,
        max_iter=1000,
        tol=1e-6
    ).fit(intensities)

    labels = np.zeros(data.shape)
    for l, f in zip(kmeans_model.labels_, features):
        labels[int(f[1]), int(f[2]), int(f[3])] = l + 1

    return labels