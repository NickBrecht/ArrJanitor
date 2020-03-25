# ArrJanitor
A python script designed to clean up Radarr/Sonarr downloads in Deluge. Designed to be ran in UnRaid.


## Why ArrJanitor? 

Radarr & Sonarr handling downloads is great. And Deluge is a great client. However, I couldn't find a good solution for actually deleting torrents that have been upgraded & replaced with higher quality versions. There is some support for deleting torrents that reach certain seed time/ratio limits, however this applies globally to all torrents. There are also limitations typically in place on only deleting fully stopped torrents. Other alternatives involve automatically deleting a torrent when it is finished. Neither of these options are ideal for individuals using private trackers.

That's where ArrJanitor comes in.


## What is ArrJanitor?

A small python script to interface between Radarr/Sonarr instances and Deluge. It implements logic to check on media that Radarr/Sonarr have replaced with a higher quality version but the older lower quality torrent is still active inside of Deluge. 

The script identifies duplicates by movieId (Radarr) and episodeId + seriesID (Sonarr). If there are duplicates and if the torrents have passed the desired days_to_seed, then it will attempt to delete the torrent and data. The script will keep the most recent copy to be grabbed by Radarr/Sonarr. ArrJanitor will only remove files that have been upgraded within a single instance of Radarr. Example being if Radarr and Radarr4k download the same movie, ArrJanitor will not consider this a duplicate.

## Where?

The script was designed to be ran in UnRaid via userscripts with python 3.8 installed. However, any OS with a python >3.6 environment should be able to run it. 

## How? 

As stated this script should be OS agnostic however the original intent was/is to run within UnRaid. 

To get this up and running on UnRaid, you must install:
* [UserScripts](https://forums.unraid.net/topic/48286-plugin-ca-user-scripts/)
* [NerdPack](https://forums.unraid.net/topic/35866-unraid-6-nerdpack-cli-tools-iftop-iotop-screen-kbd-etc/)


Within NerdPack, enable the following:

* python3
* libffi
* python-pip
* python-setuptools

From there, go to UserScripts and add a new script called ArrJanitor.

Edit your newly created script and paste the contents of ArrJanitor.py. Make sure to remove the "#!/bin/bash" at the top that UserScripts automatically adds. Fill in your information for the relative Radarr, Sonarr, and Deluge URLs & API keys/passwords. If you're not running one of these services, just leave '' in place. For example, if you have 2 Radarr instances, 1 Sonarr, and Deluge, your configuration should look something like this:


![example image](https://i.imgur.com/Bw2Nco3.jpg)


ArrJanitor has a default days_to_seed value of 4. Changing this value will allow you to dial in how many days you want to keep lower grade torrents around for (0 will examine any completed torrent).



