from flask import request
from flask_restful import Resource


class SearchResource(Resource):
    def post(self):
        """
        Recherche d'objets similaires.
        Étapes prévues :
        - Recevoir l'image requête et/ou sélection d'objet
        - Extraire descripteurs
        - Comparer aux descripteurs stockés en base
        - Retourner les images les plus pertinentes
        """
        payload = request.get_json(force=True)
        # TODO: implémenter la logique de recherche
        return {"results": [], "received": payload}, 200

