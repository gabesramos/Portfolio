# YMViewer
As of today, Yale's IMs lack a structured organization. Colleges have to individually create GroupMe chats for each sport, making communication both harder and less efficient. YMViever’s idea came to centralize and facilitate the IM organization process at Yale. It is a user-friendly website that provides a way of interacting with the Intramurals at Yale, allowing administrators to create games and users (including admins) to register for them. It also centralizes the standings system and updates it automatically, letting users to look at recent game results and the Tyng Cup standings for their residential colleges.


## What I learned:
- Use of Jinja, HTML, Python, JavaScript and SQL in harmony to create a dynamic webpage
- Effective database management
- Visual web design
- Logic processes to ensure functions don't interfere with one another
- Consumer and managing-side functions

** Project authors: Gabriel Saavedra, Bassel Dahleh, and Arthur Starling. 
Featured on Yale and Harvard's CS50 2024 Websites: https://www.cs50.yale.edu/2024/summer/


# Instructions and more info:

## Where to Compile?

The website was designed to run in the cs50.dev environment. To do so, you only have to run **flask run** in the console. The database can be seen using **phpliteadmin data.db**
- Not too much of an issue

## Libraries to Install
    pip3 install cs50
    pip3 install pytz
    pip3 install requests
    pip3 install flask
    pip3 install Flask-session

## Login Page:


On the login page, the user has to insert their username and password. There is also the option to **register** if you do not have an account on the website.


## Registration Page:


Here, the user creates an account. The user must insert a username, create a password (that contains at least four letters, one symbol, and one number), repeat the password (to avoid typos), choose their residential college, and insert an admin code if they own one. We strongly encourage you to first create an account without an admin code, just leaving it blank. After you explore our website without an Admin Code, please create another account. This time, include the code “rescoadmin” on the Admin Code slot. You now have an Admin account. In the next few paragraphs, we will discuss the User interface, and we will then proceed to make comments about the features that are unique to the Admin interface.


# Regular User Page:


## First Page (Upcoming Games):


After logging in, the user lands on the Upcoming Games page. Here, you will first see the Upcoming Games for your Residential College. This page can be accessed at all times by clicking the YMViewer logo. All the current games are fictional, but we are aware that, during the IM season, it is likely that many games will appear. Therefore, you can use our filter to select the specific sport you want to look at for games. Each game has its own “box” including the two Residential Colleges involved in the matchup, the sport, the description, the date and time, the location, and an Event & Sign Up Info button.


When you click the Event & Sign Up Info button, you can see more details of the event, including which players are already signed up for that specific game. This works as a Confirmation/More Details page. Once you click the Sign Up button again, you are now signed up for the game. After doing this, you should be redirected to the initial page and receive a flash confirmation of your registration for the game.


## Standings:


You also have the option of looking at the Standings. These are the Tyng Cup standings currently. As more games happen, the scores are updated. You will be able to see that happening when you are exercising your Admin functions later. On the Standings page, you can see a small introduction to the Tyng Cup right below the graph with each college’s points. If you scroll down a little more, you can see a News Ticker that features some of the recent games’ outcomes. Scrolling down even more, you can see a table featuring the games played, wins, losses, draws, and points of each college. Please note that we do not have enough data to include the previous games, so this just keeps track of our fictional games.


## Previous Games:


On this page, you can see the results of the previous games. It looks good, doesn’t it?


## View profile:


This is only supposed to be a cool page with an animation. You can see your college’s crest, your username, your college, and your college wins. And, of course, you can see a cool motivational video on the back. Keep running!


## Log Out:


The Logout button simply logs out the user and takes them back to the login page.


# Admin Page:


## First Page (Upcoming Games):


Now, let’s see the additional Admin functionalities. As an Admin, your index page looks a bit different. Firstly, you can not only see the upcoming games but also the past ones so you can update the scores of them. Also, for each game, you have three buttons: Info, Update Game Results, and Delete Game.


Sign Up works in a similar way. As an admin, you can sign up for games like a regular user.


When you click on the Update Game Results button, you will be able to update the result of that specific game. You will enter the score for each of the teams and then click on Update Results.


Finally, the Delete Game button will allow you to delete a game once you click it.


## Create Game


This is a page unique to admins. When you click that, you can create a new event. You select a sport from the dropdown menu. Team 1, by default, is your own residential college. You then select Team 2, create a description, select a location, and add a date and time. After that, you are all set and you can click on the Create Event button. Once you create it, it will appear for all the relevant users and admins (whose colleges are one of the teams involved in the game).


## Standings


Same as regular user. However, please note that after you update the scores for games, the relevant college(s)’s score will update. Also, the relevant colleges’ info will be updated on the table.


## Previous Games:


Same as regular user. However, note that when you update the scores for games in the past, this specific game’s result will appear here. If you update the scores for a game in the future, it will not appear, because it does not make sense. The reason why it is possible to do that is that each Residential College is supposed to have one Admin only. Therefore, we gave a lot of power to accounts with this feature.


## View profile:


Same as regular user. However, there is also a small admin indicator there.


## Log Out:

Same as regular user.


# Note:

Error message screen used to show Handsome Dan along with meme text. Not working as of 5/30/24

# Presentation Video
Here is a link to a YouTube video where we give a visual presentation about the website: https://www.youtube.com/watch?v=V1kukCzO1yE
