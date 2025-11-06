# CSC 480 Porject: Connect 4 AI

## Set Up
- Make a new python virtual environment and activate it (optional)
- Run `pip install -r requirements.txt`
- Run `uvicorn main:app --reload --port 8000` to start the backend 
- In a new terminal window navigate to the `connect-4-ai` directory
- Run `npm install`
- Run `npm run dev` to start the frontend


- 1- Project Description.
	- For our project we are making a Connect 4 bot that uses logic and the 
  state of the board to make the best decision. We will have different modes so the bot 
  can be harder or easier to beat. The input will be the state of the board and the output will 
  be making a next move or determining if it is a win, loss, or draw. This bot will be logic-based.
- 2- Data. 
	- Rules of Connect 4 which will be obtained by the internet
 	- Strategies for Connect 4 
- 3- Platform. 
  - We will have a logic-based environment where 
the agent will be given the rules and strategies on how to play Connect 4. 
The user interface will be web-based where we will be using React and FAST API for front and backend. 
- 4- Implementation plan. 
	- We will have a logic-based environment where the agent will be given the 
rules and strategies on how to play Connect 4. The user interface will be web-based 
where we will be using React and FAST API for front and backend. The website will consist of a difficulty level, game board and win/lose score. 
- 5- Testing plan. 
	 - We will test the outcome including the winner and number of moves taken to win against 
a range we expect for each level of difficulty for our model. 
We will test it by playing with the bot on the different difficulty levels and also evaluating its 
strategy based on our own. We will be playing and seeing if the moves are random or if they are strategic by setting up different scenarios. 
- 6- Future expansion. 
	- Future expansions could include building different grid shapes, having a defensive and offensive model, 
  and implementing different game modes similar to Connect 4. Other expansions could be multi-player instead of 
  just two player or allowing coins to go on different sides of the board instead of just the top.

