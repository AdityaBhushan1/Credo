![discord.py Version](https://img.shields.io/badge/lib-discord.py%201.7.0-blue) ![Language](https://img.shields.io/badge/lang-Python%203.8.6-green) [![Discord Bots](https://top.gg/api/widget/status/782867672626364456.svg)](https://top.gg/bot/782867672626364456) [![Discord Bots](https://top.gg/api/widget/servers/782867672626364456.svg)](https://top.gg/bot/782867672626364456) [![Discord Bots](https://top.gg/api/widget/upvotes/782867672626364456.svg)](https://top.gg/bot/782867672626364456) [![Discord Bots](https://top.gg/api/widget/owner/782867672626364456.svg)](https://top.gg/bot/782867672626364456) ![Made with](https://img.shields.io/badge/Made%20With-LOVE-%23fa4b4b?style=flat-square)
![MIT License](https://img.shields.io/github/license/Arthurdw/Reaction-Role?style=flat-square)

<br />
<p align="center">
    <img src="https://cdn.discordapp.com/avatars/782867672626364456/64eabde0064a9e15e4d6cc2a0570c5e7.jpeg?size=1024" alt="Logo" width="80" height="80">

  <h3 align="center">Tea Bot</h3>

  <p align="center">
    A very powerful, multipurpose bot!
    <br />
    <br />
    <a href="https://discord.gg/YSJVbxj9nw">Discord Server</a>
    ·
    <a href="https://discord.com/oauth2/authorize?client_id=782867672626364456&permissions=2147483647&scope=bot">Invite Tea Bot</a>
    <br/>

  </p>
</p>

# Seting Up Tea Bot
##### Note: The Given Steps Are For A Linux Machine If You Have Some Knowledege Of Programming Or Linux So You Can Create A Virual Env By Your Self
## Step 1
#### Create A Virtual Enviroment:
##### 1. Open Terminal In You Cloned Folder
##### 2. Run This In Your Terminal `curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3`
##### 3. Run `poetry install`
##### 4. Activate Virtual Env By Running `poetry shell`

## Step 2
#### Entring All The Crendentials:
##### 1. Now Fill Out All Details Inside `ex_config.py`
##### 2. Now Rename `ex_config.py` -> `config.py`

## Step 3
#### Seting Up Data Base:
##### 1. Open Terminal And Connect To Your Postgres User In PSQL In Your Terminal
##### 2. Run This `CREATE DATABASE teabotdb;` To Create Db For Bot
##### 3. Then Change Database TO `teabotdb` In PSQL 
##### 4. Then Open `schemas.sql` And Then Run All The Command In That File.

## Step 4
#### Running The Bot:
##### 1. brfore running create a file inside src folder named `prefixes.json` and `{}` put those brackets inside the file
##### 2. Now Run This Command `./run.sh`

#### You Have Succefulluy Setuped The Bot

## Note: 
I would prefer if you don't run an instance of my bot. Just [`Invite The Bot`](https://discord.com/oauth2/authorize?client_id=782867672626364456&permissions=2147483647&scope=bot) on your server. The source here is provided for educational purposes for discord.py.

<!-- CONTRIBUTION -->

# How do I contribute?

If you are looking forward to contribute to the project, we welcome you. kindly open an issue first for discussion.
It's also a good option to join the [`Support Server`](https://discord.gg/aBM5xz6) and get into touch with anyone having `@Tea Bot Developer` role.
