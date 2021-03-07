This is a Python bot that uses the Riot Games API to pull stats from the popular video game League of Legends and prints them in easy-to-read tables in the popular messaging app Discord. The actual game client only shows your stats on a global leaderboard, making it difficult to directly compare your progress in different aspects of the game to that of your friends. This Python bot allows the user to easily compare and share their video game stats in an easy and simple way.

## Usage

The `$add` and `$remove` commands allow you to easily to add and remove players from the database of names that the bot will pull stats for.

![add/remove command](https://github.com/malhamb/LoLStatsBot/blob/main/doc/add_remove.png)

The `$level` command will print a sorted table of players and their in-game level.

![levels command](https://github.com/malhamb/LoLStatsBot/blob/main/doc/levels.png)

The `$mastery <champion name>` command will print a sorted table of players and their mastery scores for a given champion.

![ashe command](https://github.com/malhamb/LoLStatsBot/blob/main/doc/mastery_ashe.png)
![lucian command](https://github.com/malhamb/LoLStatsBot/blob/main/doc/mastery_lucian.png)

The `$ranks` command will print a table of players sorted by their rank.

![ranks command](https://github.com/malhamb/LoLStatsBot/blob/main/doc/ranks.png)
