from flask import Blueprint, request, jsonify
from app.db import get_db

follows_bp = Blueprint("follows", __name__)


# FOLLOW / UNFOLLOW TOGGLE
@follows_bp.route("/toggle", methods=["POST"])
def toggle_follow():
    data = request.json

    follower_id = data.get("follower_id")
    following_id = data.get("following_id")

    # validation
    if not follower_id or not following_id:
        return jsonify({"error": "Missing fields"}), 400

    # prevent self-follow
    if follower_id == following_id:
        return jsonify({"error": "You cannot follow yourself"}), 400

    conn = get_db()
    cursor = conn.cursor()

    try:
        # check if already following
        sql_check = """
        SELECT id FROM follows
        WHERE follower_id=%s AND following_id=%s
        """
        cursor.execute(sql_check, (follower_id, following_id))
        existing = cursor.fetchone()

        # UNFOLLOW
        if existing:
            sql_delete = """
            DELETE FROM follows
            WHERE follower_id=%s AND following_id=%s
            """
            cursor.execute(sql_delete, (follower_id, following_id))
            conn.commit()

            return jsonify({
                "message": "Unfollowed",
                "following": False
            })

        # FOLLOW (safe insert)
        sql_insert = """
        INSERT IGNORE INTO follows (follower_id, following_id)
        VALUES (%s, %s)
        """
        cursor.execute(sql_insert, (follower_id, following_id))
        conn.commit()

        return jsonify({
            "message": "Followed",
            "following": True
        })

    finally:
        conn.close()


# GET FOLLOWERS COUNT
@follows_bp.route("/followers/<int:user_id>", methods=["GET"])
def followers_count(user_id):
    conn = get_db()
    cursor = conn.cursor()

    try:
        sql = """
        SELECT COUNT(*) AS total_followers
        FROM follows
        WHERE following_id=%s
        """
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()

        return jsonify(result)

    finally:
        conn.close()


# GET FOLLOWING COUNT
@follows_bp.route("/following/<int:user_id>", methods=["GET"])
def following_count(user_id):
    conn = get_db()
    cursor = conn.cursor()

    try:
        sql = """
        SELECT COUNT(*) AS total_following
        FROM follows
        WHERE follower_id=%s
        """
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()

        return jsonify(result)

    finally:
        conn.close()


# CHECK IF FOLLOWING
@follows_bp.route("/check", methods=["POST"])
def check_follow():
    data = request.json

    follower_id = data.get("follower_id")
    following_id = data.get("following_id")

    if not follower_id or not following_id:
        return jsonify({"error": "Missing fields"}), 400

    conn = get_db()
    cursor = conn.cursor()

    try:
        sql = """
        SELECT id FROM follows
        WHERE follower_id=%s AND following_id=%s
        """
        cursor.execute(sql, (follower_id, following_id))
        result = cursor.fetchone()

        return jsonify({
            "following": result is not None
        })

    finally:
        conn.close()


# GET FOLLOWERS LIST
@follows_bp.route("/followers-list/<int:user_id>", methods=["GET"])
def followers_list(user_id):
    conn = get_db()
    cursor = conn.cursor()

    try:
        sql = """
        SELECT users.id, users.username, users.profile_pic
        FROM follows
        JOIN users ON follows.follower_id = users.id
        WHERE follows.following_id=%s
        """
        cursor.execute(sql, (user_id,))
        data = cursor.fetchall()

        return jsonify(data)

    finally:
        conn.close()


# GET FOLLOWING LIST
@follows_bp.route("/following-list/<int:user_id>", methods=["GET"])
def following_list(user_id):
    conn = get_db()
    cursor = conn.cursor()

    try:
        sql = """
        SELECT users.id, users.username, users.profile_pic
        FROM follows
        JOIN users ON follows.following_id = users.id
        WHERE follows.follower_id=%s
        """
        cursor.execute(sql, (user_id,))
        data = cursor.fetchall()

        return jsonify(data)

    finally:
        conn.close()