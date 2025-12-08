"""
Fonctions d'extraction de descripteurs visuels :
- Histogrammes de couleurs (RGB, HSV)
- Couleurs dominantes (K-means)
- Descripteurs de Tamura (rugosité, contraste, orientation)
- Filtres de Gabor
- Moments de Hu
- Histogramme des orientations (HOG)
"""

import cv2
import numpy as np
from typing import Any, Dict, List, Tuple
from sklearn.cluster import KMeans
from skimage import feature, filters
from skimage.feature import local_binary_pattern
from scipy import ndimage
from scipy.spatial.distance import cdist


def extract_color_histogram_rgb(image: np.ndarray, bins: int = 256) -> Dict[str, List[float]]:
    """
    Calcule les histogrammes de couleurs RGB.
    
    Args:
        image: Image en format BGR (OpenCV)
        bins: Nombre de bins pour l'histogramme
    
    Returns:
        Dictionnaire avec les histogrammes R, G, B
    """
    # Convertir BGR vers RGB
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    hist_r = cv2.calcHist([rgb_image], [0], None, [bins], [0, 256]).flatten()
    hist_g = cv2.calcHist([rgb_image], [1], None, [bins], [0, 256]).flatten()
    hist_b = cv2.calcHist([rgb_image], [2], None, [bins], [0, 256]).flatten()
    
    # Normaliser
    hist_r = (hist_r / (hist_r.sum() + 1e-7)).tolist()
    hist_g = (hist_g / (hist_g.sum() + 1e-7)).tolist()
    hist_b = (hist_b / (hist_b.sum() + 1e-7)).tolist()
    
    return {
        "r": hist_r,
        "g": hist_g,
        "b": hist_b
    }


def extract_color_histogram_hsv(image: np.ndarray, bins: int = 180) -> Dict[str, List[float]]:
    """
    Calcule les histogrammes de couleurs HSV.
    
    Args:
        image: Image en format BGR (OpenCV)
        bins: Nombre de bins pour l'histogramme
    
    Returns:
        Dictionnaire avec les histogrammes H, S, V
    """
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    hist_h = cv2.calcHist([hsv_image], [0], None, [bins], [0, 180]).flatten()
    hist_s = cv2.calcHist([hsv_image], [1], None, [256], [0, 256]).flatten()
    hist_v = cv2.calcHist([hsv_image], [2], None, [256], [0, 256]).flatten()
    
    # Normaliser
    hist_h = (hist_h / (hist_h.sum() + 1e-7)).tolist()
    hist_s = (hist_s / (hist_s.sum() + 1e-7)).tolist()
    hist_v = (hist_v / (hist_v.sum() + 1e-7)).tolist()
    
    return {
        "h": hist_h,
        "s": hist_s,
        "v": hist_v
    }


def extract_dominant_colors(image: np.ndarray, k: int = 5) -> List[Dict[str, Any]]:
    """
    Extrait les couleurs dominantes en utilisant K-means.
    
    Args:
        image: Image en format BGR (OpenCV)
        k: Nombre de couleurs dominantes à extraire
    
    Returns:
        Liste de dictionnaires avec les couleurs dominantes (RGB) et leurs proportions
    """
    # Convertir BGR vers RGB et redimensionner pour accélérer
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    h, w = rgb_image.shape[:2]
    
    # Redimensionner si l'image est trop grande
    if h * w > 100000:
        scale = np.sqrt(100000 / (h * w))
        new_h, new_w = int(h * scale), int(w * scale)
        rgb_image = cv2.resize(rgb_image, (new_w, new_h))
    
    # Reshaper pour K-means
    pixels = rgb_image.reshape(-1, 3)
    
    # Appliquer K-means
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(pixels)
    
    # Obtenir les couleurs dominantes et leurs proportions
    labels = kmeans.labels_
    colors = kmeans.cluster_centers_.astype(int)
    
    # Calculer les proportions
    unique, counts = np.unique(labels, return_counts=True)
    proportions = counts / len(labels)
    
    # Trier par proportion décroissante
    sorted_indices = np.argsort(proportions)[::-1]
    
    dominant_colors = []
    for idx in sorted_indices:
        dominant_colors.append({
            "rgb": colors[unique[idx]].tolist(),
            "proportion": float(proportions[idx])
        })
    
    return dominant_colors


def extract_tamura_descriptors(image: np.ndarray) -> Dict[str, float]:
    """
    Extrait les descripteurs de Tamura : rugosité, contraste, orientation.
    
    Args:
        image: Image en niveaux de gris
    
    Returns:
        Dictionnaire avec rugosité, contraste, orientation
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    
    # Rugosité (Roughness)
    # Basée sur la variance locale des tailles de fenêtre
    roughness = _calculate_roughness(gray)
    
    # Contraste
    contrast = _calculate_contrast(gray)
    
    # Orientation (Directionality)
    directionality = _calculate_directionality(gray)
    
    return {
        "roughness": float(roughness),
        "contrast": float(contrast),
        "directionality": float(directionality)
    }


def _calculate_roughness(gray: np.ndarray) -> float:
    """Calcule la rugosité de Tamura."""
    h, w = gray.shape
    max_scale = min(5, min(h, w) // 2)
    
    best_sizes = np.zeros((h, w))
    
    for scale in range(2, max_scale + 1):
        # Calculer la moyenne locale pour différentes tailles de fenêtre
        kernel = np.ones((scale, scale), np.float32) / (scale * scale)
        local_mean = cv2.filter2D(gray.astype(np.float32), -1, kernel)
        
        # Calculer la différence entre les moyennes de fenêtres adjacentes
        diff_h = np.abs(local_mean[scale:, :] - local_mean[:-scale, :])
        diff_v = np.abs(local_mean[:, scale:] - local_mean[:, :-scale])
        
        # Pour chaque pixel, prendre le maximum des différences
        diff_max = np.zeros((h, w))
        diff_max[scale:, :] = np.maximum(diff_max[scale:, :], diff_h)
        diff_max[:, scale:] = np.maximum(diff_max[:, scale:], diff_v)
        
        # Mettre à jour la meilleure taille si la différence est plus grande
        mask = diff_max > best_sizes
        best_sizes[mask] = diff_max[mask]
    
    return np.mean(best_sizes)


def _calculate_contrast(gray: np.ndarray) -> float:
    """Calcule le contraste de Tamura."""
    # Contraste basé sur l'écart-type et le kurtosis
    std = np.std(gray)
    mean = np.mean(gray)
    
    # Kurtosis (aplatissement)
    kurtosis = np.mean(((gray - mean) / (std + 1e-7)) ** 4)
    
    # Formule de contraste de Tamura
    alpha4 = kurtosis
    contrast = std / (alpha4 ** 0.25) if alpha4 > 0 else std
    
    return contrast


def _calculate_directionality(gray: np.ndarray) -> float:
    """Calcule la directionnalité de Tamura."""
    # Calculer les gradients
    gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    
    # Magnitude et direction
    magnitude = np.sqrt(gx**2 + gy**2)
    direction = np.arctan2(gy, gx + 1e-7) * 180 / np.pi
    
    # Seuil pour ignorer les gradients faibles
    threshold = np.percentile(magnitude, 75)
    mask = magnitude > threshold
    
    if mask.sum() == 0:
        return 0.0
    
    # Histogramme des directions (16 bins)
    hist, _ = np.histogram(direction[mask], bins=16, range=(-180, 180))
    hist = hist.astype(float)
    hist = hist / (hist.sum() + 1e-7)
    
    # Calculer la directionnalité (pic dans l'histogramme)
    # Plus il y a de pics, moins c'est directionnel
    peaks = 0
    for i in range(len(hist)):
        if hist[i] > 0.1:  # Seuil pour considérer un pic
            peaks += 1
    
    directionality = 1.0 - (peaks / 16.0)
    
    return directionality


def extract_gabor_descriptors(image: np.ndarray, num_orientations: int = 8, num_scales: int = 4) -> List[float]:
    """
    Extrait les descripteurs basés sur les filtres de Gabor.
    
    Args:
        image: Image en niveaux de gris
        num_orientations: Nombre d'orientations
        num_scales: Nombre d'échelles
    
    Returns:
        Liste des descripteurs Gabor (moyennes des réponses filtrées)
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    
    gray = gray.astype(np.float32) / 255.0
    
    descriptors = []
    frequencies = [0.1, 0.2, 0.3, 0.4][:num_scales]
    
    for freq in frequencies:
        for orientation in range(num_orientations):
            theta = orientation * np.pi / num_orientations
            
            # Créer le filtre de Gabor
            gabor_kernel = cv2.getGaborKernel(
                (21, 21),
                5.0,  # sigma
                theta,
                2 * np.pi * freq,  # lambda
                0.5,  # gamma
                0,  # psi
                ktype=cv2.CV_32F
            )
            
            # Appliquer le filtre
            filtered = cv2.filter2D(gray, cv2.CV_32F, gabor_kernel)
            
            # Extraire la moyenne et l'écart-type comme descripteurs
            descriptors.append(float(np.mean(filtered)))
            descriptors.append(float(np.std(filtered)))
    
    return descriptors


def extract_hu_moments(image: np.ndarray) -> List[float]:
    """
    Extrait les moments de Hu (7 moments invariants).
    
    Args:
        image: Image en niveaux de gris
    
    Returns:
        Liste des 7 moments de Hu
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    
    # Calculer les moments
    moments = cv2.moments(gray)
    
    # Calculer les moments de Hu
    hu_moments = cv2.HuMoments(moments).flatten()
    
    # Log transform pour normaliser (les valeurs sont très petites)
    hu_moments = -np.sign(hu_moments) * np.log10(np.abs(hu_moments) + 1e-10)
    
    return hu_moments.tolist()


def extract_hog_descriptor(image: np.ndarray, orientations: int = 9, pixels_per_cell: Tuple[int, int] = (8, 8),
                           cells_per_block: Tuple[int, int] = (2, 2)) -> List[float]:
    """
    Extrait l'histogramme des orientations (HOG - Histogram of Oriented Gradients).
    
    Args:
        image: Image en niveaux de gris
        orientations: Nombre de bins d'orientation
        pixels_per_cell: Taille de la cellule en pixels
        cells_per_block: Nombre de cellules par bloc
    
    Returns:
        Vecteur HOG aplati
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    
    # Calculer le descripteur HOG
    hog_features = feature.hog(
        gray,
        orientations=orientations,
        pixels_per_cell=pixels_per_cell,
        cells_per_block=cells_per_block,
        block_norm='L2-Hys',
        visualize=False,
        feature_vector=True
    )
    
    return hog_features.tolist()


def extract_descriptors(image_path: str) -> Dict[str, Any]:
    """
    Extrait tous les descripteurs visuels d'une image.
    
    Args:
        image_path: Chemin vers l'image
    
    Returns:
        Dictionnaire contenant tous les descripteurs extraits
    """
    # Charger l'image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Impossible de charger l'image : {image_path}")
    
    # Extraire tous les descripteurs
    descriptors = {
        # Histogrammes de couleurs
        "color_histogram_rgb": extract_color_histogram_rgb(image),
        "color_histogram_hsv": extract_color_histogram_hsv(image),
        
        # Couleurs dominantes
        "dominant_colors": extract_dominant_colors(image, k=5),
        
        # Descripteurs de Tamura
        "tamura": extract_tamura_descriptors(image),
        
        # Filtres de Gabor
        "gabor": extract_gabor_descriptors(image, num_orientations=8, num_scales=4),
        
        # Moments de Hu
        "hu_moments": extract_hu_moments(image),
        
        # Histogramme des orientations (HOG)
        "hog": extract_hog_descriptor(image, orientations=9, pixels_per_cell=(8, 8), cells_per_block=(2, 2))
    }
    
    return descriptors
