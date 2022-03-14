"""Flask Application for the backend API server."""
import json
import os

from flask import Flask, Response, request

from . import resources as database, logger

FRONTEND_ADDRESS = os.environ.get("FRONTEND_ADDRESS", "http://localhost:3000")
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://camen@localhost:5432")
BIRDS_FILENAME = "birds.csv.gz"

app = Flask("backend_api")  # pylint: disable=invalid-name
_logger = logger.setup(__name__)


@app.route("/api/health")
def ping_test():
    """Backend API ping test."""
    return _json_response(data={"status": "ok"})


@app.route("/api/random/<state>/<int:num_birds>")
def random(state, num_birds):
    """Return random sample of N birds in state."""
    _logger.info(
        "Getting 1 image for each of %d random birds in %s...",
        num_birds,
        state,
    )
    birds = database.get_random_birds(
        state=state, n_birds=num_birds, n_images=1, url=DATABASE_URL
    )
    return _json_response(birds)


@app.route("/api/common/<state>/<int:num_birds>")
def common(state, num_birds):
    """Return N most common birds in state."""
    _logger.info(
        "Getting 1 image for each of %d most common birds in %s...", num_birds, state
    )
    birds = database.get_common_birds(
        state=state, n_birds=num_birds, n_images=1, url=DATABASE_URL
    )
    return _json_response(birds)


@app.route("/api/genus")
def genus(state, num_birds):
    """Return birds from the same genus."""
    _logger.info("Getting 1 image for each bird in %s...", genus)
    birds = database.get_genus(genus=genus, n_images=1, url=DATABASE_URL)
    return _json_response(birds)


@app.route("/api/get")
def get():
    """Return specific birds."""
    _logger.info("Getting specific birds...")
    requested_birds = request.args.get("birds", default=None, type=str)
    requested_birds = requested_birds.split(",") if requested_birds is not None else []
    requested_birds = tuple(
        bird.strip().lower().replace("'", "").replace(r"[- ]{1}", "_")
        for bird in requested_birds
    )
    if requested_birds:
        birds = database.get_specific_birds(
            birds=requested_birds, n_images=1, url=DATABASE_URL
        )
        return _json_response(birds)
    return _json_response([])


@app.route("/api/bad_image")
def bad_image():
    """Mark images for deletion."""
    filepath = request.args.get("filepath", default=None, type=str)
    _logger.info("Attempting to mark %s for deletion...", filepath)
    if filepath is not None:
        bird = database.mark_image_for_deletion(filepath=filepath, url=DATABASE_URL)
        return _json_response(bird)
    return _json_response([])


def _json_response(data):
    """Return a Flask response with the mimetype set to JSON."""
    resp = Response(json.dumps(data), mimetype="application/json")
    resp.headers["Access-Control-Allow-Origin"] = FRONTEND_ADDRESS
    return resp
