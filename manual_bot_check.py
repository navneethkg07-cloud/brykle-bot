import asyncio
from types import SimpleNamespace

import bot as bot_module
import commands.accounts as accounts_mod
import commands.orders as orders_mod
import commands.sales as sales_mod
import commands.stock as stock_mod


class FakeSheet:
    def __init__(self, headers):
        self.headers = headers
        self._rows = []

    def append_row(self, row):
        self._rows.append(list(row))

    def get_all_records(self):
        return [
            {self.headers[i]: row[i] for i in range(len(self.headers))}
            for row in self._rows
        ]

    def update_cell(self, row_index, col_index, value):
        self._rows[row_index - 2][col_index - 1] = value


class DummyContext:
    def __init__(self, author_name="Tester"):
        self.message = SimpleNamespace(attachments=[])
        self.author = SimpleNamespace(display_name=author_name)
        self.sent = []

    async def send(self, content=None, embed=None):
        self.sent.append((content, embed))


async def main():
    fake_accounts = FakeSheet(["Date", "Person", "Type", "Amount", "Notes", "Proof"])
    fake_sales = FakeSheet(["Date", "Customer", "Order", "Payment"])
    fake_stock = FakeSheet(["Product", "Stock"])

    def get_stock_quantity(product):
        for row in fake_stock.get_all_records():
            if str(row.get("Product", "")).lower() == str(product).lower():
                return int(row.get("Stock", 0) or 0)
        return 0

    accounts_mod.get_accounts_sheet = lambda: fake_accounts
    orders_mod.get_stock_quantity = get_stock_quantity
    sales_mod.get_sales_sheet = lambda: fake_sales
    sales_mod.get_stock_sheet = lambda: fake_stock
    stock_mod.get_stock_sheet = lambda: fake_stock
    stock_mod.get_stock_quantity = get_stock_quantity

    await bot_module.bot.load_extension("commands.accounts")
    await bot_module.bot.load_extension("commands.stock")
    await bot_module.bot.load_extension("commands.orders")
    await bot_module.bot.load_extension("commands.sales")

    accounts_cog = bot_module.bot.get_cog("AccountsCog")
    stock_cog = bot_module.bot.get_cog("StockCog")
    orders_cog = bot_module.bot.get_cog("OrdersCog")
    sales_cog = bot_module.bot.get_cog("SalesCog")

    def capture(cog, method_name, *args, **kwargs):
        ctx = DummyContext()
        coroutine = getattr(cog, method_name)(ctx, *args, **kwargs)
        return asyncio.get_running_loop().create_task(coroutine)

    async def run_and_print(label, func):
        ctx = DummyContext()
        await func(ctx)
        content, embed = ctx.sent[-1]
        print(f"[{label}] title={embed.title if embed else None} | desc={embed.description if embed else None}")

    await run_and_print("invest", lambda ctx: accounts_cog.invest(ctx, "Navaneeth", "10000", "Initial", "Fund"))
    await run_and_print("spent", lambda ctx: accounts_cog.spent(ctx, "Navaneeth", "1200", "Filament"))
    await run_and_print("reimburse", lambda ctx: accounts_cog.reimburse(ctx, "Navaneeth", "500", "Petrol"))
    await run_and_print("balance", lambda ctx: accounts_cog.balance(ctx))
    await run_and_print("balance_navaneeth", lambda ctx: accounts_cog.balance(ctx, "Navaneeth"))
    await run_and_print("business", lambda ctx: accounts_cog.business(ctx))
    await run_and_print("history", lambda ctx: accounts_cog.history(ctx, "Navaneeth"))
    await run_and_print("stockadd", lambda ctx: stock_cog.stockadd(ctx, "25", "Groot"))
    await run_and_print("stockremove", lambda ctx: stock_cog.stockremove(ctx, "2", "Groot"))
    await run_and_print("stock", lambda ctx: stock_cog.stock(ctx))
    await run_and_print("order", lambda ctx: orders_cog.order(ctx, "2", "Groot", "for", "80"))
    await run_and_print("orders", lambda ctx: orders_cog.orders(ctx))
    await run_and_print("sold", lambda ctx: sales_cog.sold(ctx, "2", "Groot"))
    await run_and_print("sold_direct", lambda ctx: sales_cog.sold(ctx, "Groot", "for", "80"))
    await run_and_print("help", lambda ctx: bot_module.help_command(ctx))

    print("\nFinal account rows:", fake_accounts.get_all_records())
    print("Final sales rows:", fake_sales.get_all_records())
    print("Final stock rows:", fake_stock.get_all_records())
    print("Pending orders:", orders_cog.pending_orders)


asyncio.run(main())
