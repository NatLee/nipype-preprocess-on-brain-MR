from typing import List

import numpy as np
from sklearn.cluster import KMeans

def extract_features(data:np.ndarray) -> np.ndarray:
    x_idx, y_idx, z_idx = np.where(data > 0)
    features = []
    for x, y, z in zip(x_idx, y_idx, z_idx):
        features.append([data[x, y, z], x, y, z])
    return np.array(features)


def kmeans_cluster(data:np.ndarray, n_clusters:int) -> np.ndarray:
    features = extract_features(data)
    intensities = features[..., 0].reshape((-1, 1))
    kmeans_model = KMeans(
        n_clusters=n_clusters,
        init="k-means++",
        verbose=0,
        random_state=42,
        max_iter=100,
        tol=1e-6
    ).fit(intensities)

    labels = np.zeros(data.shape)
    for l, f in zip(kmeans_model.labels_, features):
        labels[int(f[1]), int(f[2]), int(f[3])] = l + 1

    return labels

def get_target_labels(labels:np.ndarray, data:np.ndarray) -> List[int]:
    labels_set = np.unique(labels)
    mean_intensities = []
    for label in labels_set[1:]:
        label_data = data[np.where(labels == label)]
        mean_intensities.append(np.mean(label_data))
    gm_target_intensity = np.median(mean_intensities)  # GM
    wm_target_intensity = np.max(mean_intensities)  # WM
    csf_target_intensity = np.min(mean_intensities)  # CSF
    target_labels = [
        mean_intensities.index(gm_target_intensity) + 1, # +1 because labels start at 1
        mean_intensities.index(wm_target_intensity) + 1,
        mean_intensities.index(csf_target_intensity) + 1
    ]
    return target_labels


def segment(labels:np.ndarray, data:np.ndarray, target:int):
    # =====================
    mask = np.copy(labels).astype(np.float32)
    mask[np.where(mask != target)] = 0.333
    mask[np.where(mask == target)] = 1.
    data = data.astype(np.float32)
    matter = np.multiply(data, mask)
    # =====================
    return matter