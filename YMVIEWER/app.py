import os
import datetime
import json
import re

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, usd

# Configure application
app = Flask(__name__)
# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///data.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Show all listed events"""

    # today's date obtained via datetime library
    today = datetime.date.today()
    # DELETEING SELECTED GAME TO AVOID conflicts later
    db.execute("DELETE FROM selected_game WHERE user_id=?", session["user_id"])
    # drop selected_game table from query, so that user can select another game!!!!
    # MUST HAPPEN AT INDEX PAGE TO PICK A GAME AGAIN!!!

    # only admin users can see games that occurred before today
    if session["admin_status"] == 1:
        current_games = db.execute(
            "SELECT id, Sport_type, Desc, Location, Date, Time, Team1_id, Team2_id FROM Games ORDER BY date DESC, time"
        )
    else:
        current_games = db.execute(
            "SELECT id, Sport_type, Desc, Location, Date, Time, Team1_id, Team2_id FROM Games WHERE date>=? ORDER BY date, time",
            today,
        )

    # all user data, college data selected for sake of convenience, user_college_id too
    # all using sql select query searche
    userdata = db.execute("SELECT * FROM users WHERE id=?", session["user_id"])

    user_college_id = db.execute(
        "SELECT college_id FROM users WHERE id=?", session["user_id"]
    )[0]["college_id"]

    colleges = db.execute("SELECT * FROM Colleges")

    # homepage index tempalte rendered with all info gathered
    return render_template(
        "index.html",
        current_games=current_games,
        colleges=colleges,
        userdata=userdata,
        user_college_id=user_college_id,
        today=today,
    )


@app.route("/filter_by_sports", methods=["GET", "POST"])
@login_required
def filter_by_sports():
    """SORT COLLEGES BY SPORTS"""
    if request.method == "POST":
        # today's date obtained via datetime library
        today = datetime.date.today()

        # this function allows you to filter by selected sport based on a drop down menu
        userdata = db.execute("SELECT * FROM users WHERE id=?", session["user_id"])

        user_college_id = db.execute(
            "SELECT college_id FROM users WHERE id=?", session["user_id"]
        )[0]["college_id"]

        colleges = db.execute("SELECT * FROM Colleges")

        # data grabbed for sake of convenience

        sportfilter = request.form.get("sportfilter")

        # form element gets the sportfilter value, which is then used to query for only specific games
        if sportfilter != "All":
            current_games = db.execute(
                "SELECT id, Sport_type, Desc, Location, Date, Time, Team1_id, Team2_id FROM Games WHERE Sport_type=? ORDER BY time",
                sportfilter,
            )
        else:
            if session["admin_status"] == 1:
                current_games = db.execute(
                    "SELECT id, Sport_type, Desc, Location, Date, Time, Team1_id, Team2_id FROM Games ORDER BY date DESC, time"
                )
            else:
                current_games = db.execute(
                    "SELECT id, Sport_type, Desc, Location, Date, Time, Team1_id, Team2_id FROM Games WHERE date>=? ORDER BY date, time",
                    today,
                )

        return render_template(
            "index.html",
            current_games=current_games,
            colleges=colleges,
            userdata=userdata,
            user_college_id=user_college_id,
            today=today,
        )
    else:
        redirect("/")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """Show user profile"""

    # page grabs information from the users table to display
    username = db.execute("SELECT username FROM users WHERE id=?", session["user_id"])[
        0
    ]["username"]

    user_college_id = db.execute(
        "SELECT college_id FROM users WHERE id=?", session["user_id"]
    )[0]["college_id"]

    colleges = db.execute("SELECT * FROM Colleges")

    admin_status = db.execute(
        "SELECT admin_status FROM users WHERE id=?", session["user_id"]
    )[0]["admin_status"]

    for college in colleges:
        collegeName = college["college_name"]

    return render_template(
        "profile.html",
        colleges=colleges,
        collegeName=collegeName,
        username=username,
        user_college_id=user_college_id,
        admin_status=admin_status,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        session["user_name"] = db.execute(
            "SELECT username FROM users WHERE id = ?", session["user_id"]
        )[0]["username"]

        session["admin_status"] = db.execute(
            "SELECT admin_status FROM users WHERE id = ?", session["user_id"]
        )[0]["admin_status"]

        username = request.form.get("username")

        # Redirect user to home page
        flash(f"Welcome back, {username}!")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # this system is put in place to make sure that the user follows password requirements for security
    letterCheck = re.compile(r"[a-zA-Z].*[a-zA-Z].*[a-zA-Z].*[a-zA-Z]")
    numberCheck = re.compile(r"\d")
    symbolCheck = re.compile(r"[!@#\$%\^&\*]")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        resco_id = request.form.get("resco")
        admin_code = request.form.get("admin_code")

        # maybe have a request.form.get for profile picture - resize after
        # Ensure username was submitted - > ENSURE USERNAME NOT TAKEN
        if not request.form.get("username"):
            return apology("must provide username", 400)
        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)
        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must confirm password", 400)
        elif not request.form.get("password"):
            return apology("must provide password", 400)
        elif not request.form.get("resco"):
            return apology("must select a residential college", 400)

        # ensure passwords match
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords must match", 400)

        # Ensure the username is unique by checking the database and seeing if there is any match
        elif (
            len(
                db.execute(
                    "SELECT * FROM users WHERE username = ?",
                    request.form.get("username"),
                )
            )
            == 1
        ):
            return apology("username taken, please try again", 400)

        elif (
            not letterCheck.search(password)
            or not numberCheck.search(password)
            or not symbolCheck.search(password)
        ):
            flash("Password must contain at least 4 letters, 1 number, and 1 symbol")
            return render_template("register.html")

        admin_status = 0

        if admin_code == "rescoadmin":
            admin_status = 1

        db.execute("SELECT * FROM users WHERE username = ?", username)

        # INSERT USERNAME into database
        db.execute(
            "INSERT INTO users (username, hash, college_id, admin_status) VALUES(?, ?, ?, ?)",
            username,
            generate_password_hash(password),
            resco_id,
            admin_status,
        )

        # Query again new user

        # Remember which user has logged in
        session["user_id"] = db.execute(
            "SELECT * FROM users WHERE username = ?", username
        )[0]["id"]

        session["user_name"] = db.execute(
            "SELECT username FROM users WHERE id = ?", session["user_id"]
        )[0]["username"]

        session["admin_status"] = db.execute(
            "SELECT admin_status FROM users WHERE id = ?", session["user_id"]
        )[0]["admin_status"]

        # Redirect user to home page
        flash(f"Account successfully created. Welcome, {username}!")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    """Create a post citing the intramural event type,"""

    # Function only reserved to admin users

    # today's date obtained via datetime library
    today = datetime.date.today()

    # All users' data, the user's respective college id
    # selected via SQL query searches=
    userdata = db.execute("SELECT * FROM users")

    user_college_id = db.execute(
        "SELECT college_id FROM users WHERE id=?", session["user_id"]
    )[0]["college_id"]

    colleges = db.execute("SELECT * FROM Colleges")
    # locations serve to grab from and input into the google maps API, which then displays them on the info section of each game posted
    locations = [
        "Benjamin Franklin College",
        "Berkeley College",
        "Brady Squash Center",
        "Branford College",
        "Carol McPhillips Roberts Field House",
        "Coxe Cage",
        "Cross Campus",
        "Cullman-Heyman Tennis Center",
        "Cuyler Athletic Complex",
        "Davenport College",
        "Dewitt Cuyler Athletic Complex",
        "DeWitt Family Stadium",
        "Dwyne Track",
        "Ezra Stiles College",
        "Gales Ferry Boathouse",
        "George H.W. Bush Field",
        "Gilder Boathouse",
        "Grace Hopper College",
        "Ingalls Rink",
        "Johnson Field",
        "Jonathan Edwards College",
        "Kiputh Exhibition Pool",
        "McNay Family Sailing Center",
        "Morse College",
        "Outdoor Education Center",
        "Pauli Murray College",
        "Payne Whitney Gymnasium",
        "Pierson College",
        "Ray Tomkins House",
        "Reese Stadium",
        "Saybrook College",
        "Silliman College",
        "Smilow Field Center",
        "Timothy Dwight College",
        "Trumbull College",
        "Tsai Lacrosse Field House",
        "Yale Bowl",
        "Yale Golf Course",
    ]

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Elements from within the form are obtained via get functions
        # These are the event details
        sport = request.form.get("sport")
        desc = request.form.get("desc")
        location = request.form.get("location")
        date = request.form.get("date")
        time = request.form.get("time")
        team1 = request.form.get("team1")
        team2 = request.form.get("team2")

        # These if conditionals ensure that no field is left empty, returning an error message if the admin does not fill them out
        if not sport:
            return apology("must provide sport", 400)
        elif not location:
            return apology("must provide location", 400)
        elif not date or not time:
            return apology("must provide date and time of event", 400)
        elif not team1 or not team2:
            return apology("must provide residential college teams", 400)

        # INSERT information INTO GAMES table
        # FOR LATER INCLUDE USER_ID COLUMN IN GAMES TO IDENTIFY WHICH USER CREATED WHICH POST

        db.execute(
            "INSERT INTO Games (Sport_type, Desc, Location, Date, Time, Team1_id, Team2_id, match_user_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            sport,
            desc,
            location,
            date,
            time,
            team1,
            team2,
            session["user_id"],
        )
        # redirects user to the home page
        return redirect("/")

    # This else statement, for when the user has not yet committed any information via the form, is responsible for
    # displaying the create.html template, and updating it with the correct information
    else:
        return render_template(
            "create.html",
            today=today,
            userdata=userdata,
            user_college_id=user_college_id,
            colleges=colleges,
            locations=locations,
        )


@app.route("/open_signup_page", methods=["GET", "POST"])
@login_required
def open_signup_page():
    """Open a page showing event details"""

    # This page is not the one that actually commits a command to register a user to an event,
    # but rather, is responsible for displaying the signup.html template, and updating it with the correct information
    # based on the event that the user picked

    if request.method == "POST":
        # selects data from all colleges
        colleges = db.execute("SELECT * FROM Colleges")

        # selects game id from what was carried over from the open_signup_page() function
        game_id = request.form.get("game_id")

        # INSERTS user's id, alongside specfic game_id to refer back to, into the selected_game table
        # which is responsible for carrying over game information into specific tables

        db.execute(
            "INSERT INTO selected_game (selected_game_id, user_id) VALUES(?, ?)",
            game_id,
            session["user_id"],
        )

        # selects all game information based on the game_id carried over from the open_signup_page
        selected_game = db.execute("SELECT * FROM Games WHERE id=?", game_id)

        # all users registered to this specifc game
        all_registered = db.execute("SELECT * FROM Registered WHERE game_id=?", game_id)

        # This return statement commits the brings over the specific game details into the signup.html template,
        # which the user is then redirected to.
        return render_template(
            "signup.html",
            selected_game=selected_game[0],
            colleges=colleges,
            all_registered=all_registered,
            game_id=game_id,
        )
    else:
        # if commit fails, user is redirected back to homepage
        return render_template("/")


@app.route("/signup", methods=["GET", "POST"])
@login_required
def signup():
    """Sign up into a currently existing event"""
    # User reached route via POST (as by submitting a form via POST)
    # match event id to page. Drag information from database regarding event details
    # display on an HTML template using flask

    # Details regarding game_id, all college data, the user's specific college_id and username, and all rows
    # containing data of all users SPECIFICALLY registered to a certain game
    # selected via SQL Query search

    game_id = db.execute(
        "SELECT selected_game_id FROM selected_game WHERE user_id=?", session["user_id"]
    )[0]["selected_game_id"]

    colleges = db.execute("SELECT * FROM Colleges")

    user_college_id = db.execute(
        "SELECT college_id FROM users WHERE id=?", session["user_id"]
    )[0]["college_id"]

    username = db.execute("SELECT username FROM users WHERE id=?", session["user_id"])[
        0
    ]["username"]

    all_registered = db.execute("SELECT * FROM Registered WHERE game_id=?", game_id)

    # Loop used to display user's residential college in flash message later
    for college in colleges:
        if user_college_id == college["id"]:
            my_collegeName = college["college_name"]

    if request.method == "POST":
        # This if statement commits the information of a user
        # registering to a specific game

        # Ensures that the user does not register twice to the samme game
        for registered in all_registered:
            if registered["user_id"] == session["user_id"]:
                return apology("cannot register into game twice", 400)

        # DELETES row of selected_game containing the user's id, so that it can be filled with new
        # specific game data for other query searches, and when opening other pages
        # like update_results or signup
        db.execute("DELETE FROM selected_game WHERE user_id=?", session["user_id"])

        # If all goes well, inserts new registration entry into database, containing user data
        db.execute(
            "INSERT INTO Registered (game_id, user_id, college_id, username) VALUES(?, ?, ?, ?)",
            game_id,
            session["user_id"],
            user_college_id,
            username,
        )

        flash(f"You have signed up for the game! GO {my_collegeName} !!!")
        return redirect("/")


@app.route("/open_results_update_page", methods=["GET", "POST"])
@login_required
def open_results_update_page():
    """Open a page showing event details, this time used for the updating scores page"""

    # Function only reserved to admin users

    # This page is not the one that actually commits a command to update scores of an existing game,
    # but rather, is responsible for displaying the update_results.html template, and updating it with the correct information
    # based on the event that the user picked

    if request.method == "POST":
        # selects all data from the colleges table
        colleges = db.execute("SELECT * FROM Colleges")

        # selects game id from what was carried over from the open_signup_page() function
        game_id = request.form.get("game_id")

        # INSERTS user's id, alongside specfic game_id to refer back to, into the selected_game table
        # which is responsible for carrying over game information into specific tables
        db.execute(
            "INSERT INTO selected_game (selected_game_id, user_id) VALUES(?, ?)",
            game_id,
            session["user_id"],
        )

        # selects all game information based on the game_id carried over from the open_signup_page
        selected_game = db.execute("SELECT * FROM Games WHERE id=?", game_id)

        # all users registered to this specifc game
        all_registered = db.execute("SELECT * FROM Registered WHERE game_id=?", game_id)

        # This return statement commits the brings over the specific game details into the update_results.html template,
        # which the user is then redirected to.
        return render_template(
            "update_results.html",
            selected_game=selected_game[0],
            colleges=colleges,
            all_registered=all_registered,
            game_id=game_id,
        )

    else:
        # if commit fails, then user is redirected to the homepage
        return render_template("/")


@app.route("/update_results", methods=["GET", "POST"])
@login_required
def update_results():
    """Update the results of an existing game"""

    # Function only reserved to admin users

    # User reached route via POST (as by submitting a form via POST)
    # match event id to page. Drag information from database regarding event details
    # display on an HTML template using flask

    # Details regarding game_id, and the college ids of each team in a specific match
    # selected via SQL Query search

    game_id = db.execute(
        "SELECT selected_game_id FROM selected_game WHERE user_id=?", session["user_id"]
    )[0]["selected_game_id"]

    selected_game_Team1_id = db.execute(
        "SELECT Team1_id FROM Games WHERE id=?", game_id
    )[0]["Team1_id"]

    selected_game_Team2_id = db.execute(
        "SELECT Team2_id FROM Games WHERE id=?", game_id
    )[0]["Team2_id"]

    if request.method == "POST":
        # DELETES row of selected_game containing the user's id, so that it can be filled with new
        # specific game data for other query searches, and when opening other pages
        # like update_results or signup
        db.execute("DELETE FROM selected_game WHERE user_id=?", session["user_id"])

        # Respective team scores obtained from page
        team1_score = request.form.get("team1_score")
        team2_score = request.form.get("team2_score")

        new_winner_id = 0

        # current scores of respective college teams obtained via SQL Query search
        old_team1_score = db.execute(
            "SELECT total_points FROM Colleges WHERE id=?", selected_game_Team1_id
        )[0]["total_points"]
        old_team2_score = db.execute(
            "SELECT total_points FROM Colleges WHERE id=?", selected_game_Team2_id
        )[0]["total_points"]

        # Conditionals for how game results, winning records are obtained
        # if team1 beats team2, then the winner_id is changed to 1
        # and a new set of 5 points is added to the original total point count
        # of team 1
        if team1_score > team2_score:
            new_winner_id = 1
            new_team1_score = old_team1_score + 5
            db.execute(
                "UPDATE Colleges SET total_points=? WHERE id=?",
                new_team1_score,
                selected_game_Team1_id,
            )

        # if team2 beats team1, then the winner_id is changed to 2
        # and a new set of 5 points is added to the the original total_point count
        # of team 2
        elif team2_score > team1_score:
            new_winner_id = 2
            new_team2_score = old_team2_score + 5
            db.execute(
                "UPDATE Colleges SET total_points=? WHERE id=?",
                new_team2_score,
                selected_game_Team2_id,
            )

        # if team1 and team2 tie, then the winner_id is changed to 1
        # and a new set of 2 points is added to the original total point count
        # of both teams
        elif team1_score == team2_score:
            new_winner_id = 0
            new_team1_score = old_team1_score + 2
            new_team2_score = old_team2_score + 2
            db.execute(
                "UPDATE Colleges SET total_points=? WHERE id=?",
                new_team1_score,
                selected_game_Team1_id,
            )
            db.execute(
                "UPDATE Colleges SET total_points=? WHERE id=?",
                new_team2_score,
                selected_game_Team2_id,
            )

        # The Games table row specific to this selected game is updated with the new
        # scores and the new winner (or no winner)
        db.execute(
            "UPDATE Games SET Team1_score=?, Team2_score=?, Winner_id=? WHERE id=?",
            team1_score,
            team2_score,
            new_winner_id,
            game_id,
        )

        flash("Scores successfully updated!!!")
        return redirect("/")


@app.route("/delete_game", methods=["GET", "POST"])
@login_required
def delete_game():
    """Open a page showing the games that you have created"""

    # Function only reserved to admin users

    # DELETES a selected game from the Games table completely

    game_id = request.form.get("game_id")

    db.execute("DELETE FROM Games WHERE id=?", game_id)

    # today's date obtained via datetime library
    today = datetime.date.today()
    # drop selected_game table from query, so that user can select another game!!!!
    # MUST HAPPEN AT INDEX PAGE TO PICK A GAME AGAIN!!!
    db.execute("DELETE FROM selected_game WHERE user_id=?", session["user_id"])

    # this is to have all of the game data ready once the admin returns to the home page

    # selects all current_game data
    current_games = db.execute(
        "SELECT id, Sport_type, Desc, Location, Date, Time, Team1_id, Team2_id FROM Games ORDER BY date DESC, time"
    )

    # selects all elements of rown where user_id equals session user id
    userdata = db.execute("SELECT * FROM users WHERE id=?", session["user_id"])

    # selects college_id of user where id equals session user id
    user_college_id = db.execute(
        "SELECT college_id FROM users WHERE id=?", session["user_id"]
    )[0]["college_id"]

    # selects data of all colleges
    colleges = db.execute("SELECT * FROM Colleges")

    # redirects back to homepage, index.html template
    # all data selected carries over
    # selected game is now deleted
    return render_template(
        "index.html",
        current_games=current_games,
        colleges=colleges,
        userdata=userdata,
        user_college_id=user_college_id,
        today=today,
    )


@app.route("/stats", methods=["GET", "POST"])
@login_required
def stats():
    """DATA VISUALIZATION OF RANKINGS OF COLLEGES"""

    # today's date obtained via the datetime library
    today = datetime.date.today()

    # All college data based on points, and all game data obtained via sql query searches
    colleges = db.execute("SELECT * FROM Colleges ORDER BY total_points DESC")
    games = db.execute(
        "SELECT * FROM games WHERE Winner_id>=0 ORDER BY date DESC, time DESC"
    )

    rank = 0

    # College, wins, losses, draws, and ranking determined via winner_id of each respective game
    for college in colleges:
        rank += 1
        college["wins"] = 0
        college["losses"] = 0
        college["draws"] = 0
        college["ranking"] = rank
        # Updating wins and losses based on winner id results from the games table
        for game in games:
            # if our selected college is team1
            if college["id"] == game["Team1_id"]:
                if game["Winner_id"] == 0:
                    college["draws"] += 1
                elif game["Winner_id"] == 1:
                    college["wins"] += 1
                else:
                    college["losses"] += 1
            # if our selected college is team2
            elif college["id"] == game["Team2_id"]:
                if game["Winner_id"] == 0:
                    college["draws"] += 1
                elif game["Winner_id"] == 2:
                    college["wins"] += 1
                else:
                    college["losses"] += 1

    names_list = []
    total_points = []
    color = []

    # list of college names, points, and colors (in hex code) obtained via loop
    for college in colleges:
        names_list.append(college["college_name"])
        total_points.append(college["total_points"])
        color.append(college["color"])

    # respective team names and emblems selected by looping through all games
    for game in games:
        for college in colleges:
            if game["Team1_id"] == college["id"]:
                game["Team1"] = college["full_college_name"]
                game["Logo1"] = college["image_link"]
            if game["Team2_id"] == college["id"]:
                game["Team2"] = college["full_college_name"]
                game["Logo2"] = college["image_link"]

    return render_template(
        "stats.html",
        names=json.dumps(names_list),
        points=json.dumps(total_points),
        color=json.dumps(color),
        colleges=colleges,
        games=games,
    )


@app.route("/past_games", methods=["GET", "POST"])
@login_required
def past_games():
    """DATA VISUALIZATION OF RANKINGS OF COLLEGES"""

    # NOTE: THIS FUNCION IS COPIED TWICE BECAUSE THE PREVIOUS GAMES TABLE AND THE GRAPHS
    # WERE CREATED ON THE SAME PAGE, BUT HAD TO BE SEPARATED
    # HOWEVER, THEY BOTH USE A LOT OF THE SAME DATA
    # SO THE ONLY DIFFERENCES BETWEEN THESE FUNCTIONS IS THE NAME AND THE RENDERED TEMPLATE

    # today's date obtained via the datetime library
    today = datetime.date.today()

    # All college data based on points, and all game data obtained via sql query searches
    colleges = db.execute("SELECT * FROM Colleges ORDER BY total_points DESC")
    games = db.execute(
        "SELECT * FROM games WHERE Winner_id>=0 ORDER BY date DESC, time DESC"
    )

    rank = 0

    # College, wins, losses, draws, and ranking determined via winner_id of each respective game
    for college in colleges:
        rank += 1
        college["wins"] = 0
        college["losses"] = 0
        college["draws"] = 0
        college["ranking"] = rank
        # Updating wins and losses based on winner id results from the games table
        for game in games:
            # if our selected college is team1
            if college["id"] == game["Team1_id"]:
                if game["Winner_id"] == 0:
                    college["draws"] += 1
                elif game["Winner_id"] == 1:
                    college["wins"] += 1
                else:
                    college["losses"] += 1
            # if our selected college is team2
            elif college["id"] == game["Team2_id"]:
                if game["Winner_id"] == 0:
                    college["draws"] += 1
                elif game["Winner_id"] == 2:
                    college["wins"] += 1
                else:
                    college["losses"] += 1

    names_list = []
    total_points = []
    color = []

    # list of college names, points, and colors (in hex code) obtained via loop
    for college in colleges:
        names_list.append(college["college_name"])
        total_points.append(college["total_points"])
        color.append(college["color"])

    # respective team names and emblems selected by looping through all games
    for game in games:
        for college in colleges:
            if game["Team1_id"] == college["id"]:
                game["Team1"] = college["full_college_name"]
                game["Logo1"] = college["image_link"]
            if game["Team2_id"] == college["id"]:
                game["Team2"] = college["full_college_name"]
                game["Logo2"] = college["image_link"]

    return render_template(
        "past_games.html",
        names=json.dumps(names_list),
        points=json.dumps(total_points),
        color=json.dumps(color),
        colleges=colleges,
        games=games,
    )
