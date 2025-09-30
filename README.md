# Swedish Learning Bot

A Telegram bot for learning Swedish vocabulary. Look up any Swedish word to see all its grammatical forms.

## Features

- 124,000+ Swedish words
- Complete noun declensions (all 5 groups)
- Full verb conjugations
- Adjective forms with comparatives and superlatives
- Numbers with ordinal forms
- Recognizes inflected forms

## Tech Stack

- Python 3.13
- python-telegram-bot
- SALDO dictionary (Språkbanken)

## Usage

Send any Swedish word to the bot:
- `hund` → see all forms (hund, hunden, hundar, hundarna)
- `är` → recognizes as present tense of "vara"
- `fem` → shows ordinal form "femte"

## Commands

- `/start` - Welcome message
- `/help` - Usage guide
- `/examples` - Example words
- `/stats` - Dictionary stats
- `/feedback` - Contact info

## About

Personal project for learning Swedish. Built using SALDO (Swedish Language Bank) data from University of Gothenburg.

The bot loads the entire dictionary into memory for fast lookups.

## Contact

- GitHub: [@oleksii-shcherbak](https://github.com/oleksii-shcherbak)
- Telegram: @oleksii_shcherbak33
