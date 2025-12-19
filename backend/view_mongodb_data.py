"""
Script pour visualiser les données MongoDB.
Permet d'afficher les images stockées avec leurs métadonnées, objets détectés et descripteurs.
"""

from models.image_model import ImageModel
from pprint import pprint
import json
from bson import json_util


def display_image_summary(image: dict):
    """Affiche un résumé d'une image."""
    print("\n" + "="*80)
    print(f"📷 Image: {image.get('filename', 'N/A')}")
    print(f"   ID: {image.get('_id')}")
    print(f"   Chemin: {image.get('path', 'N/A')}")
    print(f"   Date d'upload: {image.get('uploaded_at', 'N/A')}")
    
    detected_objects = image.get('detected_objects', [])
    print(f"\n   🎯 Objets détectés: {len(detected_objects)}")
    
    for i, obj in enumerate(detected_objects, 1):
        print(f"\n   Objet #{i}:")
        print(f"      - Classe: {obj.get('class', 'N/A')}")
        print(f"      - Confiance: {obj.get('confidence', 0)*100:.1f}%")
        print(f"      - Bounding Box: {obj.get('bbox', [])}")
        
        # Vérifier si les descripteurs sont présents
        descriptors = obj.get('descriptors', {})
        if descriptors:
            print(f"      - ✅ Descripteurs extraits:")
            print(f"         • Histogrammes RGB/HSV: {'Oui' if 'color_histogram_rgb' in descriptors else 'Non'}")
            print(f"         • Couleurs dominantes: {'Oui' if 'dominant_colors' in descriptors else 'Non'}")
            print(f"         • Tamura: {'Oui' if 'tamura' in descriptors else 'Non'}")
            print(f"         • Gabor: {'Oui' if 'gabor' in descriptors else 'Non'}")
            print(f"         • Moments de Hu: {'Oui' if 'hu_moments' in descriptors else 'Non'}")
            print(f"         • HOG: {'Oui' if 'hog' in descriptors else 'Non'}")
        else:
            print(f"      - ⚠️  Aucun descripteur pour cet objet")
    
    # Descripteurs de l'image complète
    image_descriptors = image.get('descriptors', {})
    if image_descriptors:
        print(f"\n   📊 Descripteurs de l'image complète:")
        print(f"      • Histogrammes RGB/HSV: {'Oui' if 'color_histogram_rgb' in image_descriptors else 'Non'}")
        print(f"      • Couleurs dominantes: {'Oui' if 'dominant_colors' in image_descriptors else 'Non'}")
        print(f"      • Tamura: {'Oui' if 'tamura' in image_descriptors else 'Non'}")
        print(f"      • Gabor: {'Oui' if 'gabor' in image_descriptors else 'Non'}")
        print(f"      • Moments de Hu: {'Oui' if 'hu_moments' in image_descriptors else 'Non'}")
        print(f"      • HOG: {'Oui' if 'hog' in image_descriptors else 'Non'}")


def list_all_images():
    """Liste toutes les images avec un résumé."""
    print("\n" + "="*80)
    print("📚 LISTE DE TOUTES LES IMAGES DANS MONGODB")
    print("="*80)
    
    images = ImageModel.all()
    
    if not images:
        print("\n❌ Aucune image trouvée dans la base de données.")
        print("   Uploadez des images via l'interface web pour commencer.")
        return
    
    print(f"\n✅ Total: {len(images)} image(s) trouvée(s)\n")
    
    for image in images:
        display_image_summary(image)
    
    print("\n" + "="*80)


def show_image_details(image_id: str):
    """Affiche les détails complets d'une image spécifique."""
    image = ImageModel.find_by_id(image_id)
    
    if not image:
        print(f"\n❌ Image avec ID '{image_id}' non trouvée.")
        return
    
    print("\n" + "="*80)
    print("📋 DÉTAILS COMPLETS DE L'IMAGE")
    print("="*80)
    
    # Convertir en JSON pour un affichage propre
    image_json = json.loads(json_util.dumps(image))
    pprint(image_json, width=100, indent=2)


def show_statistics():
    """Affiche des statistiques sur les images stockées."""
    images = ImageModel.all()
    
    if not images:
        print("\n❌ Aucune image dans la base de données.")
        return
    
    print("\n" + "="*80)
    print("📊 STATISTIQUES")
    print("="*80)
    
    total_images = len(images)
    total_objects = sum(len(img.get('detected_objects', [])) for img in images)
    
    # Compter les classes d'objets
    object_classes = {}
    for image in images:
        for obj in image.get('detected_objects', []):
            obj_class = obj.get('class', 'unknown')
            object_classes[obj_class] = object_classes.get(obj_class, 0) + 1
    
    # Compter les images avec descripteurs
    images_with_descriptors = sum(1 for img in images if img.get('descriptors'))
    objects_with_descriptors = sum(
        sum(1 for obj in img.get('detected_objects', []) if obj.get('descriptors'))
        for img in images
    )
    
    print(f"\n📷 Images totales: {total_images}")
    print(f"🎯 Objets détectés total: {total_objects}")
    print(f"📊 Images avec descripteurs: {images_with_descriptors}/{total_images}")
    print(f"📊 Objets avec descripteurs: {objects_with_descriptors}/{total_objects}")
    
    print(f"\n🏷️  Classes d'objets détectées:")
    for obj_class, count in sorted(object_classes.items(), key=lambda x: x[1], reverse=True):
        print(f"   - {obj_class}: {count} fois")


def export_to_json(filename: str = "mongodb_export.json"):
    """Exporte toutes les données MongoDB vers un fichier JSON."""
    images = ImageModel.all()
    
    if not images:
        print("\n❌ Aucune image à exporter.")
        return
    
    # Convertir en JSON
    images_json = json.loads(json_util.dumps(images))
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(images_json, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Données exportées vers '{filename}'")
    print(f"   {len(images)} image(s) exportée(s)")


if __name__ == "__main__":
    import sys
    
    print("\n" + "="*80)
    print("🔍 VISUALISEUR DE DONNÉES MONGODB - CBIR YOLO Image Search")
    print("="*80)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "list":
            list_all_images()
        elif command == "stats":
            show_statistics()
        elif command == "export":
            filename = sys.argv[2] if len(sys.argv) > 2 else "mongodb_export.json"
            export_to_json(filename)
        elif command == "show":
            if len(sys.argv) > 2:
                show_image_details(sys.argv[2])
            else:
                print("\n❌ Usage: python view_mongodb_data.py show <image_id>")
        else:
            print(f"\n❌ Commande inconnue: {command}")
            print("\nCommandes disponibles:")
            print("  list    - Liste toutes les images")
            print("  stats   - Affiche les statistiques")
            print("  show <id> - Affiche les détails d'une image")
            print("  export [filename] - Exporte les données en JSON")
    else:
        # Mode interactif par défaut
        print("\n📋 Menu:")
        print("1. Lister toutes les images")
        print("2. Afficher les statistiques")
        print("3. Exporter en JSON")
        print("4. Quitter")
        
        choice = input("\nVotre choix (1-4): ").strip()
        
        if choice == "1":
            list_all_images()
        elif choice == "2":
            show_statistics()
        elif choice == "3":
            filename = input("Nom du fichier (défaut: mongodb_export.json): ").strip()
            if not filename:
                filename = "mongodb_export.json"
            export_to_json(filename)
        elif choice == "4":
            print("\n👋 Au revoir!")
        else:
            print("\n❌ Choix invalide")

