from flask import Flask
from flask_cors import CORS
from flask_restful import Api

from config import UPLOAD_FOLDER
from routes.upload import UploadResource
from routes.download import DownloadResource
from routes.delete import DeleteResource
from routes.search import SearchResource
from routes.transform import TransformResource
from routes.list import ListResource


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

    CORS(app)
    api = Api(app)

    # Enregistrement des endpoints REST
    api.add_resource(UploadResource, "/upload")
    api.add_resource(ListResource, "/images")
    api.add_resource(DownloadResource, "/download/<string:image_id>")
    api.add_resource(DeleteResource, "/delete/<string:image_id>")
    api.add_resource(SearchResource, "/search")
    api.add_resource(TransformResource, "/transform/<string:image_id>")

    @app.route("/health")
    def healthcheck():
        return {"status": "ok"}

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=5000, debug=True)

