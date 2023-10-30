#!/usr/bin/python3
"""places_reviews module"""
from api.v1.views import app_views
from flask import abort, jsonify
from models import storage
from models.place import Place
from models.review import Review
from models.user import User


@app_views.route('/places/<place_id>/reviews', methods=['GET'],
                 strict_slashes=False)
def get_reviews_from_place(place_id):
    """Retrieve a list of reviews of a place"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    reviews = [review.to_dict() for review in place.reviews]
    return jsonify(reviews)


@app_views.route('/reviews/<review_id>', methods=['GET'],
                 strict_slashes=False)
def get_review(review_id):
    """Retrieve a review object"""
    review = storage.get(Review, review_id)
    if review is None:
        abort(404)
    return jsonify(review.to_dict())


@app_views.route('/reviews/<review_id>', methods=['DELETE'],
                 strict_slashes=False)
def delete_review(review_id):
    """Deletes a review"""
    review = storage.get(Review, review_id)
    if review is None:
        abort(404)
    review.delete()
    storage.save()
    return jsonify({}), 200


@app_views.route('/api/v1/places/<place_id>/reviews', methods=['POST'],
                 strict_slashes=False)
def create_review(place_id):
    """"Creates a review"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    request = request.get_json()
    if not request:
        abort(400, 'Not a JSON')
    if 'user_id' not in request:
        abort(400, 'Missing user_id')
    user = storage.get(User, request['user_id'])
    if user is None:
        abort(404)
    if 'text' not in request:
        abort(400, 'Missing text')
    review = Review(**request)
    review.save()
    return jsonify(review.to_dict()), 201


@app_views.route('/api/v1/reviews/<review_id>', methods=['PUT'],
                 strict_slashes=False)
def update_review(review_id):
    """Update a review"""
    review = storage.get(Review, review_id)
    if review is None:
        abort(404)
    request = request.get_json()
    if not request:
        abort(400, 'Not a JSON')

    for key, value in request.items():
        if key not in ['id', 'user_id', 'place_id',
                       'created_at', 'updated_at']:
            setattr(review, key, value)
    storage.save()
    return jsonify(review.to_dict()), 200
