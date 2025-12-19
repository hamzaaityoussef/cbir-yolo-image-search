"""
Fonctions de calcul de similarité entre descripteurs visuels.
Utilise différentes métriques de distance pour comparer les descripteurs.
"""

import numpy as np
from typing import Dict, Any, List, Tuple


def euclidean_distance(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Calcule la distance euclidienne entre deux vecteurs."""
    return float(np.linalg.norm(vec1 - vec2))


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Calcule la similarité cosinus entre deux vecteurs (0 = identique, 1 = différent)."""
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 1.0
    
    similarity = dot_product / (norm1 * norm2)
    # Convertir en distance (0 = identique, 1 = différent)
    return float(1.0 - similarity)


def chi_square_distance(hist1: np.ndarray, hist2: np.ndarray) -> float:
    """Calcule la distance Chi-square entre deux histogrammes."""
    epsilon = 1e-10
    diff = hist1 - hist2
    sum_hist = hist1 + hist2 + epsilon
    chi_sq = np.sum((diff ** 2) / sum_hist)
    return float(chi_sq)


def compare_descriptors(desc1: Dict[str, Any], desc2: Dict[str, Any], 
                       weights: Dict[str, float] = None) -> float:
    """
    Compare deux ensembles de descripteurs et retourne un score de similarité global.
    
    Args:
        desc1: Premier ensemble de descripteurs
        desc2: Deuxième ensemble de descripteurs
        weights: Poids pour chaque type de descripteur (optionnel)
    
    Returns:
        Score de similarité global (0 = identique, plus élevé = plus différent)
    """
    if weights is None:
        # Poids par défaut pour chaque type de descripteur
        weights = {
            "color_histogram": 0.2,
            "dominant_colors": 0.15,
            "tamura": 0.15,
            "gabor": 0.2,
            "hu_moments": 0.15,
            "hog": 0.15
        }
    
    total_distance = 0.0
    total_weight = 0.0
    
    # Comparer les histogrammes RGB
    if "color_histogram_rgb" in desc1 and "color_histogram_rgb" in desc2:
        rgb1 = desc1["color_histogram_rgb"]
        rgb2 = desc2["color_histogram_rgb"]
        
        for channel in ["r", "g", "b"]:
            if channel in rgb1 and channel in rgb2:
                hist1 = np.array(rgb1[channel])
                hist2 = np.array(rgb2[channel])
                dist = chi_square_distance(hist1, hist2)
                total_distance += dist * weights["color_histogram"] / 3
                total_weight += weights["color_histogram"] / 3
    
    # Comparer les histogrammes HSV
    if "color_histogram_hsv" in desc1 and "color_histogram_hsv" in desc2:
        hsv1 = desc1["color_histogram_hsv"]
        hsv2 = desc2["color_histogram_hsv"]
        
        for channel in ["h", "s", "v"]:
            if channel in hsv1 and channel in hsv2:
                hist1 = np.array(hsv1[channel])
                hist2 = np.array(hsv2[channel])
                dist = chi_square_distance(hist1, hist2)
                total_distance += dist * weights["color_histogram"] / 3
                total_weight += weights["color_histogram"] / 3
    
    # Comparer les couleurs dominantes
    if "dominant_colors" in desc1 and "dominant_colors" in desc2:
        colors1 = desc1["dominant_colors"]
        colors2 = desc2["dominant_colors"]
        
        # Extraire les couleurs RGB
        rgb1 = np.array([c["rgb"] for c in colors1])
        rgb2 = np.array([c["rgb"] for c in colors2])
        
        # Distance minimale entre les couleurs (Hungarian algorithm simplifié)
        min_dist = 0.0
        for c1 in rgb1:
            min_dist_to_c1 = min([euclidean_distance(c1, c2) for c2 in rgb2])
            min_dist += min_dist_to_c1
        
        min_dist /= len(rgb1)
        # Normaliser (RGB va de 0 à 255, donc max distance = sqrt(3*255^2))
        min_dist = min_dist / (255 * np.sqrt(3))
        
        total_distance += min_dist * weights["dominant_colors"]
        total_weight += weights["dominant_colors"]
    
    # Comparer les descripteurs de Tamura
    if "tamura" in desc1 and "tamura" in desc2:
        tamura1 = desc1["tamura"]
        tamura2 = desc2["tamura"]
        
        tamura_vec1 = np.array([
            tamura1.get("roughness", 0),
            tamura1.get("contrast", 0),
            tamura1.get("directionality", 0)
        ])
        tamura_vec2 = np.array([
            tamura2.get("roughness", 0),
            tamura2.get("contrast", 0),
            tamura2.get("directionality", 0)
        ])
        
        dist = euclidean_distance(tamura_vec1, tamura_vec2)
        # Normaliser approximativement
        dist = dist / 10.0  # Ajuster selon les valeurs typiques
        
        total_distance += dist * weights["tamura"]
        total_weight += weights["tamura"]
    
    # Comparer les descripteurs Gabor
    if "gabor" in desc1 and "gabor" in desc2:
        try:
            gabor1 = np.array(desc1["gabor"]).flatten()  # Aplatir en 1D
            gabor2 = np.array(desc2["gabor"]).flatten()  # Aplatir en 1D
            
            # Gérer les différences de taille
            if len(gabor1) != len(gabor2):
                # Utiliser la taille minimale (tronquer)
                min_size = min(len(gabor1), len(gabor2))
                gabor1 = gabor1[:min_size]
                gabor2 = gabor2[:min_size]
            
            if len(gabor1) > 0 and len(gabor2) > 0:
                dist = cosine_similarity(gabor1, gabor2)
                total_distance += dist * weights["gabor"]
                total_weight += weights["gabor"]
        except Exception as e:
            # Si erreur, ignorer ce descripteur
            print(f"Erreur comparaison Gabor: {str(e)}")
    
    # Comparer les moments de Hu
    if "hu_moments" in desc1 and "hu_moments" in desc2:
        try:
            hu1 = np.array(desc1["hu_moments"])
            hu2 = np.array(desc2["hu_moments"])
            
            # Les moments de Hu ont toujours 7 valeurs, mais vérifions quand même
            if len(hu1) != len(hu2):
                min_len = min(len(hu1), len(hu2))
                hu1 = hu1[:min_len]
                hu2 = hu2[:min_len]
            
            dist = euclidean_distance(hu1, hu2)
            # Normaliser
            dist = dist / 10.0
            
            total_distance += dist * weights["hu_moments"]
            total_weight += weights["hu_moments"]
        except Exception as e:
            print(f"Erreur comparaison Hu moments: {str(e)}")
    
    # Comparer HOG
    if "hog" in desc1 and "hog" in desc2:
        try:
            hog1 = np.array(desc1["hog"]).flatten()  # Aplatir en 1D
            hog2 = np.array(desc2["hog"]).flatten()  # Aplatir en 1D
            
            # Gérer les différences de taille (HOG dépend de la taille de l'image)
            if len(hog1) != len(hog2):
                # Utiliser la taille minimale (tronquer)
                min_size = min(len(hog1), len(hog2))
                hog1 = hog1[:min_size]
                hog2 = hog2[:min_size]
            
            if len(hog1) > 0 and len(hog2) > 0:
                dist = cosine_similarity(hog1, hog2)
                total_distance += dist * weights["hog"]
                total_weight += weights["hog"]
        except Exception as e:
            # Si erreur, ignorer ce descripteur
            print(f"Erreur comparaison HOG: {str(e)}")
    
    # Normaliser par le poids total
    if total_weight > 0:
        return total_distance / total_weight
    
    return float('inf')


def search_similar_images(query_descriptors: Dict[str, Any], 
                         all_images: List[Dict[str, Any]], 
                         top_k: int = 10,
                         search_by_objects: bool = False) -> List[Tuple[str, float, Dict[str, Any]]]:
    """
    Recherche les images les plus similaires à partir des descripteurs de requête.
    
    Args:
        query_descriptors: Descripteurs de l'image/objet requête
        all_images: Liste de toutes les images avec leurs descripteurs
        top_k: Nombre de résultats à retourner
        search_by_objects: Si True, compare avec les descripteurs des objets, sinon avec l'image complète
    
    Returns:
        Liste de tuples (image_id, score_similarité, info_objet) triés par similarité croissante
        info_objet contient l'index de l'objet le plus similaire si search_by_objects=True
    """
    similarities = []
    
    for image in all_images:
        image_id = str(image["_id"])
        detected_objects = image.get("detected_objects", [])
        
        if search_by_objects:
            # Comparer avec les descripteurs de chaque objet dans l'image
            best_distance = float('inf')
            best_object_info = None
            
            for obj_idx, obj in enumerate(detected_objects):
                obj_descriptors = obj.get("descriptors", {})
                
                if not obj_descriptors:
                    continue
                
                try:
                    # Calculer la distance avec cet objet
                    distance = compare_descriptors(query_descriptors, obj_descriptors)
                    
                    if distance < best_distance:
                        best_distance = distance
                        best_object_info = {
                            "object_index": obj_idx,
                            "object_class": obj.get("class"),
                            "confidence": obj.get("confidence")
                        }
                except Exception as e:
                    # Ignorer les erreurs de comparaison pour cet objet
                    print(f"Erreur comparaison avec objet {obj_idx} de l'image {image_id}: {str(e)}")
                    continue
            
            if best_object_info is not None:
                similarities.append((image_id, best_distance, best_object_info))
        else:
            # Comparer avec les descripteurs de l'image complète
            image_descriptors = image.get("descriptors", {})
            
            if not image_descriptors:
                continue
            
            try:
                # Calculer la distance de similarité
                distance = compare_descriptors(query_descriptors, image_descriptors)
                similarities.append((image_id, distance, None))
            except Exception as e:
                print(f"Erreur comparaison avec image {image_id}: {str(e)}")
                continue
    
    # Trier par distance (plus petit = plus similaire)
    similarities.sort(key=lambda x: x[1])
    
    # Retourner les top_k
    return similarities[:top_k]

