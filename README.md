# ArrJanitor
A python script designed to clean up Radarr/Sonarr downloads in Deluge. Designed to be ran in UnRaid.


## Why ArrJanitor? 

Radarr & Sonarr handling downloads is great. And Deluge is a great client. However, I couldn't find a good solution for actually deleting torrents that have been upgraded & replaced with higher quality versons. Radarr v3 does have some support for seed time/ratio limits, however this applies globally to all torrents. I want to seed a torrent indefineitly unless it has been replaced. 

That's where ArrJanitor comes in.


## What is ArrJanitor?

A small python script to interface between Radarr/Sonarr instances and Deluge. It implments logic to check on media that Radarr/Sonarr have replaced with a higher quality verson but the old torrent is still active inside of Deluge. 

The script identifies duplicates by movieId (Radarr) and episodId + seriesID (Sonarr). If there are duplicates and if the torrents have passed the desired target_seed_time, then it will attempt to delete the torrent and data. The script will keep the most recent copy to be grabbed by Radarr/Sonarr. ArrJanitor will only remove files that have been upgraded within a single instance of Radarr. Example being if Radarr and Radarr4k download the same movie, ArrJanitor will not consider this a duplicate.

## Where?

The script was designed to be ran in UnRaid via userscripts with python 3.8 installed. However, any OS with a python >3.6 enviroment should be able to run it. 

## How? 

To get this up and running on UnRaid, you must install:
* [UserScripts](https://forums.unraid.net/topic/48286-plugin-ca-user-scripts/)
* [NerdPack](https://forums.unraid.net/topic/35866-unraid-6-nerdpack-cli-tools-iftop-iotop-screen-kbd-etc/)


Within NerdPack, enable the following:

* python3
* libffi
* python-pip
* python-setuptools

From there, go to UserScripts....













