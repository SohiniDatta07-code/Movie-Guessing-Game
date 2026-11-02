
from flask import Flask, render_template, request, redirect, url_for, session
import random

app = Flask(__name__)

app.secret_key = "movie-game-secret-key"

# Original movie list (kept for future use)
movies = [
    "anand",
    "drishyam",
    "nayakan",
    "anbe sivam",
    "gol maal",
    "vikram vedha",
    "black friday",
    "dangal",
    "manichithrathazhu",
    "taare zameen par"
]

# Maximum incorrect attempts
MAX_ATTEMPTS = 7


# Create hidden movie name with 25% letters/numbers revealed
def create_question(movie):

    question = [
        "*" if character.isalnum() else character
        for character in movie
    ]

    # Find positions containing letters or numbers
    character_positions = [
        i for i, character in enumerate(movie)
        if character.isalnum()
    ]

    # Reveal approximately 25% of characters
    hint_count = max(1, len(character_positions) // 4)

    hint_positions = random.sample(
        character_positions, hint_count
    )

    for position in hint_positions:
        question[position] = movie[position]

    return "".join(question)


# Check whether a character exists in the movie
def is_present(character, movie):
    return character in movie


# Reveal correctly guessed characters
def unlock(question, movie, character):

    new_question = ""

    for i in range(len(movie)):

        if movie[i] == character:
            new_question += character

        else:
            new_question += question[i]

    return new_question


# Welcome page
@app.route("/")
def home():

    # Clear previous game information
    session.clear()

    return render_template("index.html")


# Player registration
@app.route("/players", methods=["GET", "POST"])
def players():

    if request.method == "POST":

        player1 = request.form.get("player1", "").strip()
        player2 = request.form.get("player2", "").strip()

        if not player1 or not player2:
            return "Please enter both player names."

        session["player1"] = player1
        session["player2"] = player2

        return redirect(url_for("select_movie"))

    return render_template("players.html")


# Player 1 selects a movie
@app.route("/select_movie", methods=["GET", "POST"])
def select_movie():

    if "player1" not in session or "player2" not in session:
        return redirect(url_for("players"))

    if request.method == "POST":

        selected_movie = request.form.get(
            "movie", ""
        ).strip().casefold()

        if len(selected_movie) < 2:
            return "Please enter a valid movie name."

        # Save selected movie
        session["selected_movie"] = selected_movie

        # Reset previous game information
        session.pop("question", None)
        session.pop("guessed_letters", None)
        session.pop("wrong_attempts", None)

        return redirect(url_for("game"))

    return render_template("select_movie.html")


# Player 2 guessing page
@app.route("/game", methods=["GET", "POST"])
def game():

    if "selected_movie" not in session:
        return redirect(url_for("players"))

    movie = session["selected_movie"]

    # Initialize a fresh game
    if "question" not in session:

        session["question"] = create_question(movie)
        session["guessed_letters"] = []
        session["wrong_attempts"] = 0

    message = ""

    if request.method == "POST":

        action = request.form.get("action")

        # OPTION 1: Guess the complete movie name
        if action == "full_guess":

            full_guess = request.form.get(
                "full_guess", ""
            ).strip().casefold()

            if not full_guess:

                message = "Please enter the complete movie name."

            elif full_guess == movie:

                return render_template(
                    "result.html",
                    winner=session["player2"],
                    movie=movie
                )

            else:

                session["wrong_attempts"] += 1

                message = "Incorrect movie name! One attempt lost."

        # OPTION 2: Guess one letter or number
        elif action == "letter":

            character = request.form.get(
                "letter", ""
            ).strip().casefold()

            if len(character) != 1 or not character.isalnum():

                message = "Please enter one letter or number."

            elif character in session["guessed_letters"]:

                message = "You have already guessed this character."

            else:

                guessed_letters = session["guessed_letters"]
                guessed_letters.append(character)
                session["guessed_letters"] = guessed_letters

                if is_present(character, movie):

                    session["question"] = unlock(
                        session["question"],
                        movie,
                        character
                    )

                    message = "Correct guess! Well done."

                else:

                    session["wrong_attempts"] += 1

                    message = "Incorrect character! One attempt lost."

        # Check winning condition
        if session["question"] == movie:

            return render_template(
                "result.html",
                winner=session["player2"],
                movie=movie
            )

        # Check losing condition
        if session["wrong_attempts"] >= MAX_ATTEMPTS:

            return render_template(
                "result.html",
                winner=None,
                movie=movie
            )

    # Calculate remaining attempts
    remaining_attempts = (
        MAX_ATTEMPTS - session["wrong_attempts"]
    )

    return render_template(
        "game.html",
        player=session["player2"],
        question=session["question"],
        message=message,
        remaining_attempts=remaining_attempts
    )

@app.route("/restart_game", methods=["POST"])
def restart_game():

    session.clear()

    return redirect(url_for("home"))
if __name__ == "__main__":
    app.run(debug=True)

