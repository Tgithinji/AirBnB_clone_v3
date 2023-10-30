#!/usr/bin/python3
"""
Create a new view for user objects that handles
all default RESTFul API actions
"""
from models.place import Place
from models.user import User
from models.amenity import Amenity
from models.city import City
from models.state import State
from models import storage
from flask import Flask, request, jsonify, abort
from api.v1.views import app_views
from flasgger.utils import swag_from


@app_views.route('/cities/<city_id>/places',
                 methods=['GET'], strict_slashes=False)
def get_places(city_id):
    """
    Retrieves the list of all Place objects of a City
    """
    city = storage.get(City, city_id)
    if city is None:
        abort(404)

    places = [place.to_dict() for place in city.places]
    return jsonify(places)


@app_views.route('/places/<place_id>', methods=['GET'], strict_slashes=False)
def get_place(place_id):
    """
    Retrieves a Place object.
    """
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    return jsonify(place.to_dict())


@app_views.route('/places/<place_id>',
                 methods=['DELETE'], strict_slashes=False)
def delete_place(place_id):
    """
    Deletes a Place object
    """
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    storage.delete(place)
    storage.save()
    return jsonify({})


@app_views.route('/cities/<city_id>/places',
                 methods=['POST'], strict_slashes=False)
def create_place(city_id):
    """
    Creates a Place
    """
    city = storage.get(City, city_id)
    if city is None:
        abort(404)

    if not request.is_json:
        abort(400, description="Not a JSON")

    data = request.get_json()
    if "user_id" not in data:
        abort(400, description="Missing user_id")
    if "name" not in data:
        abort(400, description="Missing name")

    user = storage.get(User, data['user_id'])
    if user is None:
        abort(404)

    place = Place(**data)
    place.city_id = city.id
    place.save()
    return jsonify(place.to_dict()), 201


@app_views.route('/places/<place_id>',
                 methods=['PUT'], strict_slashes=False)
def update_place(place_id):
    """
    Updates a Place object
    """
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)

    if not request.is_json:
        abort(400, description="Not a JSON")

    data = request.get_json()
    ignore_keys = ["id", "user_id", "city_id", "created_at", "updated_at"]
    for key, value in data.items():
        if key not in ignore_keys:
            setattr(place, key, value)
    place.save()
    return jsonify(place.to_dict())


@app_views.route('/places_search',
                 methods=['POST'], strict_slashes=False)
def places_search():
    """
    Search for places
    """
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Not a JSON"}), 400

    states = data.get("states", [])
    cities = data.get("cities", [])
    amenities = data.get("amenities", [])

    places = []

    if not states and not cities:
        places = list(storage.all(Place).values())
    else:
        for state_id in states:
            state = storage.get(State, state_id)
            if state:
                places.extend(state.places)

        for city_id in cities:
            city = storage.get(City, city_id)
            if city:
                places.extend(city.places)

    places = list({place.id: place for place in places}.values())

    if amenities:
        filtered_places = []
        for place in places:
            if all(
                    amenity_id in place.amenity_ids for amenity_id in amenities
                    ):
                filtered_places.append(place)
        places = filtered_places

    return jsonify([place.to_dict() for place in places])
