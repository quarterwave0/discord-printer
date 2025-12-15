# Have you ever wanted physical reciepts of your discord channel?
Well, I did.

##  Setup instructions if you wanted that for some reason:
1. Make a discord bot and get the token.
2. Get your printer working with [python-escpos](https://python-escpos.readthedocs.io/en/latest/)
3. Set up a .env with the following headers:
```
PRINTER_VENDOR = "{vendor code}"
PRINTER_ID = "{printer ID}"
PRINTER_PROFILE = "{printer profile}"

DISCORD_TOKEN= "{bot ID}"

NORMAL_CHANNELS = {channel ID for normal channels}
INVERTED_CHANNELS = {channel ID for privileged channels}
ACTIVE_TIMES = "{hour (24hr code) the bot becomes active},{hour (24hr code) the bot turns off}"
```
4. Make the main file work
5. Regret
