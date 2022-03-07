"""Flask Application for the backend API server."""
import ast
import json
import os
from importlib import resources
import re

import numpy as np
import pandas as pd
from flask import Flask, Response, request

from api import resources as api_resources, logger

FRONTEND_ADDRESS = os.environ.get("FRONTEND_ADDRESS", None)
BIRDS_FILENAME = "birds.csv.gz"

app = Flask("backend_api")  # pylint: disable=invalid-name
_logger = logger.setup(__name__)


@app.route("/api/health")
def ping_test():
    """Backend API ping test."""
    return _json_response(data={"status": "ok"})


@app.route("/api/random/<state>/<int:N>")
def random(state, N):
    """Return random sample of N birds in state."""
    _logger.info("Getting %d random birds for %s...", N, state)
    birds = _read_birds()

    sampled = birds.loc[(slice(None), f"USA-{state.upper()}"), :].sample(N, replace=False)
    sampled["image"] = sampled.images.apply(np.random.choice)
    return _json_response(
        data=sampled[["common_name", "image"]].to_dict(orient="records")
    )


@app.route("/api/common/<state>/<int:N>")
def common(state, N):
    """Return N most common birds in state."""
    _logger.info("Getting %d most common birds for %s...", N, state)
    birds = _read_birds()

    sampled = (
        birds.sort_values(by="abundance_mean", ascending=False)
        .loc[(slice(None), f"USA-{state.upper()}"), :]
        .iloc[:N]
    )
    sampled["image"] = sampled.images.apply(np.random.choice)
    return _json_response(
        data=sampled[["common_name", "image"]].to_dict(orient="records")
    )


@app.route("/api/get")
def get():
    """Return specific birds."""
    _logger.info("Getting specific birds...")
    requested_birds = request.args.get("birds", default=None, type=str)
    requested_birds = requested_birds.split(",") if requested_birds is not None else []
    requested_birds = [
        bird.strip().lower().replace("'", "").replace(r"[- ]{1}", "_")
        for bird in requested_birds
    ]
    print(requested_birds)
    if requested_birds:
        birds = _read_birds()
        sampled = (
            birds.loc[(requested_birds, slice(None)), :]
            .groupby("common_name")
            .first()
            .reset_index()
        )
        print(sampled)
        sampled["image"] = sampled.images.apply(np.random.choice)
        return _json_response(
            data=sampled[["common_name", "image"]].to_dict(orient="records")
        )
    return _json_response(data=[])


def _json_response(data):
    """Return a Flask response with the mimetype set to JSON."""
    resp = Response(json.dumps(data), mimetype="application/json")
    resp.headers["Access-Control-Allow-Origin"] = FRONTEND_ADDRESS
    return resp


def _read_birds():
    with resources.path(package=api_resources, resource=BIRDS_FILENAME) as filename:
        return pd.read_csv(
            filename,
            index_col=("programmatic_name", "region_code"),
            converters={"images": ast.literal_eval},
        )
