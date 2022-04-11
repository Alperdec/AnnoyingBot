# AnnoyingBot
Grammar bot is a nuisance to discord servers. He listens to the chat channel and checks for spelling errors and snarkily suggests words to fix those spelling errors.
Those who spell correctly are awarded points. Those who spell incorrectly are punished with removal of points. If one asks the grammarbot to display the leaderboard he does so willingly and happily.

## details
**A discord bot**

Grammarbot uses the spellcheck module I built to check and correct user's chats. In addition to this it is connected to a RESTful API built using **express** and **javascript** and stores points on **firestore**. 
The source code for this can be found in **/grammarbot/grammarbot-backend/functions/index.js**

The pointsystem module can be found in **util.py**

