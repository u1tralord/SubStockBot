# SubStockBot
This bot oversees the indexing of subreddits and trading of stocks on the subreddit: http://www.reddit.com/r/subredditstockmarket


TODO:

* Bot function: start buying and selling stocks automatically based on its calculated value
* Bot function: evaluate stock value
* fix info command.
* fix stock class to pull it's data from the db instead of always using initial data.
* impliment data to store a UTC value in a user's collection whenever they buy, sell, or inquiry to their account status.
* 		add a last_active variable to the user class and and set to to the current UTC every time they send a command