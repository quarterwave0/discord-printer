import discord
from escpos import printer

from dotenv import load_dotenv
from os import getenv
from PIL import Image
import requests
from io import BytesIO
from datetime import datetime, time, timedelta

load_dotenv()

idVendor = int(getenv("PRINTER_VENDOR"), 16)
idProduct = int(getenv("PRINTER_ID"), 16)
printerProfile = getenv("PRINTER_PROFILE")

normalChannels = [int(ch) for ch in getenv("NORMAL_CHANNELS").split(",")]
invertedChannels = [int(ch) for ch in getenv("INVERTED_CHANNELS").split(",")]

activeTimes = [time(hour=int(t)) for t in getenv("ACTIVE_TIMES").split(",")]

p = printer.Usb(idVendor, idProduct, 0, profile=printerProfile)

user_ratelimit_progress = {}

def checkValid(message: discord.Message):
	if(message.channel.id in invertedChannels and
		(message.content is not None or
		message.attachments is not [])):
			return True

	if(message.channel.id not in normalChannels or #is it in an active channel
		message.content is None and message.attachments is [] or #is it empty
		datetime.now().time() >= activeTimes[1] or #is it too late
		datetime.now().time() <= activeTimes[0] #is it too early
	):
		return False
	return True

def rateLimiter(message: discord.Message):
	if message.author.id not in user_ratelimit_progress:
		user_ratelimit_progress[message.author.id] = [datetime.now()]
		return True
	else:
		user_ratelimit_progress[message.author.id].append(datetime.now()) #message just sent, did it exceed rl?

		for i, msg_stamp in enumerate(user_ratelimit_progress[message.author.id]):
			if datetime.now() - msg_stamp > timedelta(minutes=2, seconds=0): #more than 2 mins ago, clear it
				user_ratelimit_progress[message.author.id].pop(i)

		if len(user_ratelimit_progress[message.author.id]) <= 5: #after all of that, are they under rl?
			return True
	return False


def formatImage(image):
	w, h = image.size

	if w > 512 and h > 512:
		image = image.resize((512, 512))
	elif w > 512:
		image = image.resize((512, h))
	elif h > 512:
		image = image.resize((w, 512))

	return image

def retrieveAttachments(message: discord.Message):
	images = []

	if message.attachments is not []:
		for attachment in message.attachments[:2]: #only ever parse 3 files
			if(attachment.content_type=='image/jpeg' or #is it declared as an image
				attachment.content_type=='image/png' and
				attachment.size < 1_000_000 #not too big
			):
				r = requests.get(attachment.url)
				try:
					with Image.open(BytesIO(r.content)) as img:
						img.verify()
						img = Image.open(BytesIO(r.content))
					images.append(formatImage(img))
				except(IOError, SyntaxError):
					pass

		return images
	return []

class BotClient(discord.Client):

	async def on_ready(self):
		print(f'Logged on as {self.user}!')

	async def on_message(self, message: discord.Message):

		if message.author == self.user:
			return

		if checkValid(message) and rateLimiter(message):

			if message.channel.id in invertedChannels:
				p.set(invert=True)

			p.text(f"{message.author}: ")
			if message.content is not None:
				p.textln(message.content)
				pass

			if message.channel.id in invertedChannels:
				p.set(invert=False)

			images = retrieveAttachments(message)
			if images is not []:
				for image in images:
					p.image(image)

			p.ln()
			await message.add_reaction('🧾')

intents = discord.Intents.default()
intents.message_content = True

client = BotClient(intents=intents)
client.run(getenv("DISCORD_TOKEN"))