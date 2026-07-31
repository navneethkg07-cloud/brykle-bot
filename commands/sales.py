from discord.ext import commands

from config import logger
from utils.embeds import error_embed, success_embed
from utils.helpers import current_date, normalize_text
from utils.sheets import get_sales_sheet, get_stock_sheet


class SalesCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _update_stock(self, stock_sheet: object, product: str, quantity: int) -> None:
        records = stock_sheet.get_all_records()
        for index, row in enumerate(records, start=2):
            if normalize_text(row.get("Product", "")) == normalize_text(product):
                current_stock = max(0, int(row.get("Stock", 0) or 0) - quantity)
                stock_sheet.update_cell(index, 2, current_stock)
                break

    async def _record_sale(self, ctx: commands.Context, person: str, product: str, quantity: int, price: str | int) -> None:
        sheet = get_sales_sheet()
        sheet.append_row([current_date(), person, product, price])

        stock_sheet = get_stock_sheet()
        self._update_stock(stock_sheet, product, quantity)

        orders_cog = self.bot.get_cog("OrdersCog")
        if orders_cog:
            pending_order = orders_cog.find_matching_order(person, product, quantity)
            if pending_order is not None:
                orders_cog.remove_order(pending_order)

        logger.info("Recorded sale for %s", product)
        await ctx.send(embed=success_embed("Sale recorded", f"Person : {person}\nProduct : {product}\nPayment : ₹{price}"))

    @commands.command(name="sold")
    async def sold(self, ctx: commands.Context, *args):
        if not args:
            await ctx.send(embed=error_embed("Invalid command", "Usage: `!sold <Person> <Quantity> <Product>` or `!sold <Person> <Product> for <Price>`"))
            return

        if len(args) >= 3 and args[-2].lower() == "for":
            person = args[0]
            product = " ".join(args[1:-2]).strip()
            price = args[-1]
            quantity = 1
        else:
            if len(args) < 3:
                await ctx.send(embed=error_embed("Invalid command", "Usage: `!sold <Person> <Quantity> <Product>` or `!sold <Person> <Product> for <Price>`"))
                return
            person = args[0]
            quantity = args[1]
            product = " ".join(args[2:]).strip()
            price = 0

        try:
            quantity_value = int(quantity)
        except (TypeError, ValueError):
            await ctx.send(embed=error_embed("Invalid quantity", "Quantity must be an integer."))
            return

        orders_cog = self.bot.get_cog("OrdersCog")
        if orders_cog and len(args) >= 3 and args[-2].lower() != "for":
            pending_order = orders_cog.find_matching_order(person, product, quantity_value)
            if pending_order is not None:
                quantity_value = pending_order["quantity"]
                price = pending_order["price"]

        await self._record_sale(ctx, person, product, quantity_value, price)


async def setup(bot: commands.Bot):
    await bot.add_cog(SalesCog(bot))
