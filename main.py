import asyncio
import datetime
import logging

import asyncpg
import discord
from discord.ext import commands, tasks

import config


def to_emoji(num: int) -> str:
    return f"{num}\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}"


def from_emoji(emoji: str) -> int:
    number = emoji.removesuffix("\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}")
    return int(number)


def join_members(guild: discord.Guild, members: list[int]) -> str:
    fmt = []
    for member_id in members:
        member = guild.get_member(member_id)
        if not member:
            continue
        fmt.append(member.name)
    return ", ".join(fmt)


class BandBot(commands.Bot):
    pool: asyncpg.Pool

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


async def main() -> None:
    discord.utils.setup_logging()

    async with BandBot(
        command_prefix=commands.when_mentioned_or("!"),
        intents=discord.Intents.all(),
    ) as bot, asyncpg.create_pool(config.DATABASE) as pool:
        bot.pool = pool
        
        with open("schema.sql") as file:
            await bot.pool.execute(file.read())
        
        print(bot.pool)
        
        @tasks.loop(time=config.TASK_DATE)
        async def task():
            today = datetime.datetime.today().strftime("%A") # Monday, Tuesday, etc...
            logging.info(f"Task running on {today}")
            if today == config.DAY:
                channel = bot.get_channel(config.NOTIFY_CHANNEL)
                message = f"1) Monday: \n"\
                        f"2) Tuesday: \n"\
                        f"3) Wednesday: \n"\
                        f"4) Thursday: \n"\
                        f"5) Friday: \n"\
                        f"6) Saturday: \n"\
                            
                message = await channel.send(f"```\n{message}\n```")

                for i in range(1, 7):
                    await message.add_reaction(to_emoji(i))

                records = await bot.pool.fetch("SELECT message_id FROM messages")
                if records:
                    message_ids = [record["message_id"] for record in records]
                    for message_id in message_ids:
                        print(message_id)
                        fetched_message = await channel.fetch_message(message_id)
                        await fetched_message.delete()
                        await bot.pool.execute("DELETE FROM messages WHERE message_id = $1", message_id)

                await bot.pool.execute(
                    "INSERT INTO messages(message_id, monday, tuesday, wednesday, thursday, friday, saturday) VALUES ($1, $2, $3, $4, $5, $6, $7)",
                    message.id, [], [], [], [], [], [], # I'm sure there is a better way of doing this
                )

        @task.before_loop
        async def waiter():
            await bot.wait_until_ready()

        @bot.listen("on_raw_reaction_add")
        async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
            if payload.user_id == bot.user.id:
                return

            channel = bot.get_channel(payload.channel_id)
            fetched_message = await channel.fetch_message(payload.message_id)

            if fetched_message.author.id != bot.user.id:
                return
            
            try:
                weekday: int = from_emoji(str(payload.emoji))
            except:
                return
            
            formats = ["tfw 0-indexed", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
            column_name = formats[weekday]

            query: str = f"""
                INSERT INTO messages (message_id, {column_name}) VALUES ($1, ARRAY[$2]::BIGINT[])
                ON CONFLICT (message_id) DO UPDATE
                    SET {column_name} = ARRAY(SELECT DISTINCT * FROM UNNEST(messages.{column_name} || excluded.{column_name}))
                """
            await bot.pool.execute(query, payload.message_id, payload.user_id)

            format_specs = await bot.pool.fetchrow("SELECT * FROM messages WHERE message_id = $1", payload.message_id)

            if not format_specs:
                return
            
            message = f"1) Monday: {join_members(channel.guild, format_specs['monday'])}\n"\
                    f"2) Tuesday: {join_members(channel.guild, format_specs['tuesday'])}\n"\
                    f"3) Wednesday: {join_members(channel.guild, format_specs['wednesday'])}\n"\
                    f"4) Thursday: {join_members(channel.guild, format_specs['thursday'])}\n"\
                    f"5) Friday: {join_members(channel.guild, format_specs['friday'])}\n"\
                    f"6) Saturday: {join_members(channel.guild, format_specs['saturday'])}\n"\
            
            return await fetched_message.edit(content=f"```\n{message}\n```")

        @bot.listen("on_raw_reaction_remove")
        async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
            if payload.user_id == bot.user.id:
                return

            channel = bot.get_channel(payload.channel_id)
            fetched_message = await channel.fetch_message(payload.message_id)

            if fetched_message.author.id != bot.user.id:
                return
            
            try:
                weekday: int = from_emoji(str(payload.emoji))
            except:
                return
            
            formats = ["tfw 0-indexed", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
            column_name = formats[weekday]

            query: str = f"UPDATE messages SET {column_name} = ARRAY_REMOVE({column_name}, $2) WHERE message_id = $1"
            await bot.pool.execute(query, payload.message_id, payload.user_id)

            format_specs = await bot.pool.fetchrow("SELECT * FROM messages WHERE message_id = $1", payload.message_id)

            if not format_specs:
                return
            
            message = f"1) Monday: {join_members(channel.guild, format_specs['monday'])}\n"\
                    f"2) Tuesday: {join_members(channel.guild, format_specs['tuesday'])}\n"\
                    f"3) Wednesday: {join_members(channel.guild, format_specs['wednesday'])}\n"\
                    f"4) Thursday: {join_members(channel.guild, format_specs['thursday'])}\n"\
                    f"5) Friday: {join_members(channel.guild, format_specs['friday'])}\n"\
                    f"6) Saturday: {join_members(channel.guild, format_specs['saturday'])}\n"\
            
            return await fetched_message.edit(content=f"```\n{message}\n```")

        task.start()

        await bot.start(config.BOT_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())