import discord
from discord.ext import commands

from config import TOKEN, logger
from utils.embeds import info_embed
from utils.sheets import connect


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)


@bot.event
async def on_ready() -> None:
    logger.info("Brykle bot is online as %s", bot.user)


@bot.command(name="help")
async def help_command(ctx: commands.Context) -> None:
    help_text = (
        "**Brykle Finance Bot**\n\n"
        "**Accounts**\n"
        "`!invest <Person> <Amount> <Notes>`\n"
        "`!spent <Person> <Amount> <Notes>`\n"
        "`!reimburse <Person> <Amount> <Notes>`\n"
        "`!balance` or `!balance <Person>`\n"
        "`!business`\n"
        "`!history <Person>`\n\n"
        "**Stock**\n"
        "`!stockadd <Quantity> <Product>`\n"
        "`!stockremove <Quantity> <Product>`\n"
        "`!stock`\n\n"
        "**Orders**\n"
        "`!order <Person> <Quantity> <Product> for <Price>`\n"
        "`!orders`\n\n"
        "**Sales**\n"
        "`!sold <Person> <Quantity> <Product>`\n"
        "`!sold <Person> <Product> for <Price>`"
    )
    await ctx.send(embed=info_embed("Help", help_text))


async def load_cogs() -> None:
    for extension in ["commands.accounts", "commands.stock", "commands.orders", "commands.sales"]:
        await bot.load_extension(extension)


async def main() -> None:
    if not TOKEN:
        logger.error("TOKEN environment variable is not set.")
        raise SystemExit(1)

    try:
        connect()
    except Exception as exc:
        logger.exception("Google Sheets connection failed")
        raise SystemExit(1) from exc

    await load_cogs()
    await bot.start(TOKEN)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
