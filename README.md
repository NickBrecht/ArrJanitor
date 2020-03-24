# ArrJanitor
A python script designed to clean up Radarr/Sonarr downloads in Deluge. Designed to be ran in UnRaid.


## Why ArrJanitor? 

Radarr & Sonarr handling downloads is great. And Deluge is a great client. However, I couldn't find a good solution for actually deleting torrents that have been upgraded & replaced with higher quality versons. Radarr v3 does have some support for seed time/ratio limits, however this applies globally to all torrents. I want to seed a torrent indefineitly unless it has been replaced. 

That's where ArrJanitor comes in.


## What is ArrJanitor?

A small python script to interface between Radarr/Sonarr instances and Deluge. It implments logic to check on media that Radarr/Sonarr have replaced with a higher quality verson but the old torrent is still active inside of Deluge. 

The script identifies duplicates by movieId (Radarr) and episodId + seriesID (Sonarr). If there are duplicates and if the torrents have passed the desired target_seed_time, then it will attempt to delete the torrent and data. The script will keep the most recent copy to be grabbed by Radarr/Sonarr.

## Where?

The script was designed to be ran in UnRaid via userscripts with python 3.8 installed. However, any OS with a python >3.6 enviroment should be able to run it. 

## How? 

To get this up and running on UnRaid, you must install:
* Userscripts
* NerdPack

Within NerdPack, enable the following:

* python3
* libffi
* python-pip
* python-setuptools

The script will attempt to leverage pip3 (installed by Nerdpack) to install pandas & requests.

From there, go to UserScripts....













