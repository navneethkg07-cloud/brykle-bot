import asyncio
from commands.orders import OrdersCog
from commands.sales import SalesCog


class DummyContext:
    def __init__(self):
        self.sent = []
        self.message = type('Message', (), {'attachments': []})()

    async def send(self, content=None, embed=None):
        self.sent.append((content, embed))


class DummyBot:
    def __init__(self):
        self.cogs = {}

    def add_cog(self, cog):
        self.cogs[cog.__class__.__name__] = cog

    def get_cog(self, name):
        return self.cogs.get(name)


async def main():
    bot = DummyBot()
    orders_cog = OrdersCog(bot)
    sales_cog = SalesCog(bot)
    bot.add_cog(orders_cog)
    bot.add_cog(sales_cog)

    ctx = DummyContext()
    await orders_cog.order.callback(orders_cog, ctx, 'Aditya', '2', 'Groot', 'for', '80')
    print('ORDER:', ctx.sent[-1][1].title, '::', ctx.sent[-1][1].description)

    ctx2 = DummyContext()
    await orders_cog.orders.callback(orders_cog, ctx2)
    print('ORDERS:', ctx2.sent[-1][1].title, '::', ctx2.sent[-1][1].description)

    ctx3 = DummyContext()
    await sales_cog.sold.callback(sales_cog, ctx3, 'Aditya', '2', 'Groot')
    print('SOLD:', ctx3.sent[-1][1].title, '::', ctx3.sent[-1][1].description)

    ctx4 = DummyContext()
    await sales_cog.sold.callback(sales_cog, ctx4, 'Aditya', 'Groot', 'for', '80')
    print('SOLD_DIRECT:', ctx4.sent[-1][1].title, '::', ctx4.sent[-1][1].description)


asyncio.run(main())
