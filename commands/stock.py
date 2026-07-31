from typing import Optional

from discord.ext import commands

from config import logger
from utils.embeds import error_embed, info_embed, success_embed
from utils.helpers import normalize_text
from utils.sheets import get_stock_sheet


class StockCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="stockadd")
    async def stockadd(self, ctx: commands.Context, quantity: Optional[str] = None, *product_parts: str):
        if not quantity or not product_parts:
            await ctx.send(embed=error_embed("Invalid command", "Usage: `!stockadd <Quantity> <Product>`"))
            return

        try:
            qty = int(quantity)
        except ValueError:
            await ctx.send(embed=error_embed("Invalid quantity", "Quantity must be an integer."))
            return

        product = " ".join(product_parts).strip()
        if not product:
            await ctx.send(embed=error_embed("Invalid command", "Product name is required."))
            return

        sheet = get_stock_sheet()
        records = sheet.get_all_records()
        found = False
        for index, row in enumerate(records, start=2):
            if normalize_text(row.get("Product", "")) == normalize_text(product):
                current_stock = int(row.get("Stock", 0) or 0)
                sheet.update_cell(index, 2, current_stock + qty)
                found = True
                break

        if not found:
            sheet.append_row([product, qty])

        logger.info("Stock updated for %s", product)
        await ctx.send(embed=success_embed("Stock updated", f"Added {qty} to {product}."))

    @commands.command(name="stockremove")
    async def stockremove(self, ctx: commands.Context, quantity: Optional[str] = None, *product_parts: str):
        if not quantity or not product_parts:
            await ctx.send(embed=error_embed("Invalid command", "Usage: `!stockremove <Quantity> <Product>`"))
            return

        try:
            qty = int(quantity)
        except ValueError:
            await ctx.send(embed=error_embed("Invalid quantity", "Quantity must be an integer."))
            return

        product = " ".join(product_parts).strip()
        sheet = get_stock_sheet()
        records = sheet.get_all_records()
        for index, row in enumerate(records, start=2):
            if normalize_text(row.get("Product", "")) == normalize_text(product):
                current_stock = max(0, int(row.get("Stock", 0) or 0) - qty)
                sheet.update_cell(index, 2, current_stock)
                await ctx.send(embed=success_embed("Stock updated", f"Removed {qty} from {product}."))
                return

        await ctx.send(embed=info_embed("Stock", f"{product} does not exist yet."))

    @commands.command(name="stock")
    async def stock(self, ctx: commands.Context):
        sheet = get_stock_sheet()
        records = sheet.get_all_records()
        if not records:
            await ctx.send(embed=info_embed("Stock", "No stock items found."))
            return

        sorted_items = sorted(records, key=lambda r: normalize_text(r.get("Product", "")))
        lines = [f"{row.get('Product', '')}: {row.get('Stock', 0)}" for row in sorted_items]
        await ctx.send(embed=info_embed("Stock Inventory", "\n".join(lines)))


async def setup(bot: commands.Bot):
    await bot.add_cog(StockCog(bot))
