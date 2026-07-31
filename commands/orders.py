from datetime import datetime
from typing import Optional

from discord.ext import commands

from config import logger
from utils.embeds import error_embed, info_embed
from utils.helpers import normalize_text
from utils.sheets import get_stock_quantity


class OrdersCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.pending_orders: list[dict] = []

    @commands.command(name="order")
    async def order(self, ctx: commands.Context, *args):
        if len(args) < 5:
            await ctx.send(embed=error_embed("Invalid command", "Usage: `!order <Person> <Quantity> <Product> for <Price>`"))
            return

        if args[-2].lower() != "for":
            await ctx.send(embed=error_embed("Invalid command", "Usage: `!order <Person> <Quantity> <Product> for <Price>`"))
            return

        person = args[0]
        quantity = args[1]
        product = " ".join(args[2:-2]).strip()
        price = args[-1]

        if not person or not quantity or not product or not price:
            await ctx.send(embed=error_embed("Invalid command", "Usage: `!order <Person> <Quantity> <Product> for <Price>`"))
            return

        try:
            qty = int(quantity)
            price_value = int(price)
        except ValueError:
            await ctx.send(embed=error_embed("Invalid values", "Quantity and price must be integers."))
            return

        order = {
            "person": person,
            "product": product,
            "quantity": qty,
            "price": price_value,
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
        }
        self.pending_orders.append(order)
        stock = get_stock_quantity(product)
        logger.info("Pending order created for %s", product)
        await ctx.send(
            embed=info_embed(
                "Order Added",
                f"Person : {person}\nProduct : {product}\nQuantity : {qty}\nPrice : ₹{price_value}\n\nCurrent Stock : {stock}",
            )
        )

    @commands.command(name="orders")
    async def orders(self, ctx: commands.Context):
        if not self.pending_orders:
            await ctx.send(embed=info_embed("Pending Orders", "No pending orders."))
            return

        lines = []
        for order in self.pending_orders:
            lines.append(f"{order['person']}\n{order['quantity']} {order['product']}\n₹{order['price']}")
        await ctx.send(embed=info_embed("Pending Orders", "\n\n".join(lines)))

    def find_matching_order(self, person: str, product: str, quantity: int) -> Optional[dict]:
        for order in self.pending_orders:
            if (
                normalize_text(order.get("person", "")) == normalize_text(person)
                and normalize_text(order.get("product", "")) == normalize_text(product)
                and int(order.get("quantity", 0)) == quantity
            ):
                return order
        return None

    def remove_order(self, order: dict) -> None:
        if order in self.pending_orders:
            self.pending_orders.remove(order)


async def setup(bot: commands.Bot):
    await bot.add_cog(OrdersCog(bot))
