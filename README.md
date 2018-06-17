# Meshwell - Play together, mesh well.
A gamer matchmaking system, developed using Python on the Django framework.  
**Backend:** Django-REST MVC/MTV API with Database integration.  
**Frontend:** HTML, Bootstrap, JavaScript and Python.  
*Hosting provided by Amazon Web Servers, **Ubuntu 16.04** distribution.*

## The service
Meshwell is designed to provide users with a streamlined alternative to the current state of matchmaking in the gaming industry.  
Where currently players meet others in game and sometimes find people that they enjoy playing with, Meshwell provides the alternative of queueuing dynamically and finding other players that wish to play like you do (be it competitively or casually, teamwork or solo focused).  
Using our algorithm, we find other players that match your playstyle and provide you with a secure, private Discord channel to play your session together.  
Additionally, we offer the ability to queue for future timeslots, as we understand that it's difficult to find playeres who can play at the same time as you.  

## VoIP
Through the creation of a Discord bot, Meshwell has integrated the website with chat functionality.
Prior to session commencement (10 minutes) each player in a session is sent a private discord message (as long as they have connected their account) with a link to a secure channel to speak in.
Post-session (10 minutes) the channel is deleted and players can queue again.

## API
Meshwell has a ReST API which third-parties can use to obtain a glimpse into the playstyles of different players.
This API is private however, so a request must be made for access.

## References
**Project Trello:** https://trello.com/b/OnRJLnFj/capstone-programming-project  
**Discord:** https://discord.gg/dafqTZq