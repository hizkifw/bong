import os
from chat import print_messages, init_messages, chat
import discord

print_messages(init_messages[:2])

channel_id = os.getenv("DISCORD_BOT_CHANNEL_ID")
channel_id = int(channel_id) if channel_id is not None and channel_id != "" else None

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

histories = {}


@client.event
async def on_message(message):
    # Skip if message from self
    if message.author == client.user:
        return

    # Skip if guild message but not in selected channel
    if message.guild and (channel_id is None or message.channel.id != channel_id):
        return

    # Skip if message is empty
    if len(message.content.strip()) == 0:
        return

    async with message.channel.typing():
        uid = message.author.id if not message.guild else message.channel.id
        if uid not in histories:
            histories[uid] = []

        if message.content.strip() == "!reset":
            histories[uid] = []
            await message.channel.send("Chat has been reset.")
            return

        print_messages([{"role": message.author.name, "content": message.content}])
        histories[uid] = chat(
            histories[uid],
            # If message is in a channel, prefix with the sender's name
            ("[" + message.author.name + "] " if message.guild else "")
            + message.content,
        )

    to_send = histories[uid][-1]["content"]
    while len(to_send) > 2000:
        msg = to_send[:2000]
        await message.channel.send(msg)
        to_send = to_send[2000:]
    if len(to_send) > 0:
        await message.channel.send(to_send)


client.run(os.getenv("DISCORD_BOT_TOKEN"))
