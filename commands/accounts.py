from typing import Optional

from discord.ext import commands

from config import logger
from utils.embeds import error_embed, info_embed, success_embed
from utils.helpers import current_date, format_currency, parse_amount
from utils.sheets import get_accounts_sheet


class AccountsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="invest")
    async def invest(self, ctx: commands.Context, person: Optional[str] = None, amount: Optional[str] = None, *notes_parts: str):
        if not person or not amount:
            await ctx.send(embed=error_embed("Invalid command", "Usage: `!invest <Person> <Amount> <Notes>`"))
            return

        try:
            amount_value = parse_amount(amount)
        except ValueError as exc:
            await ctx.send(embed=error_embed("Invalid amount", str(exc)))
            return

        notes = " ".join(notes_parts).strip() or "Initial Fund"
        proof = ""
        if ctx.message.attachments:
            proof = ctx.message.attachments[0].url

        try:
            sheet = get_accounts_sheet()
            sheet.append_row([current_date(), person, "Invest", amount_value, notes, proof])
            logger.info("Added invest entry for %s", person)
        except Exception as exc:
            logger.exception("Failed to add invest entry")
            await ctx.send(embed=error_embed("Google Sheets Error", "Could not save the transaction."))
            return

        await ctx.send(embed=success_embed("Investment recorded", f"{person} invested {format_currency(amount_value)}."))

    @commands.command(name="spent")
    async def spent(self, ctx: commands.Context, person: Optional[str] = None, amount: Optional[str] = None, *notes_parts: str):
        if not person or not amount:
            await ctx.send(embed=error_embed("Invalid command", "Usage: `!spent <Person> <Amount> <Notes>`"))
            return

        try:
            amount_value = parse_amount(amount)
        except ValueError as exc:
            await ctx.send(embed=error_embed("Invalid amount", str(exc)))
            return

        notes = " ".join(notes_parts).strip() or "Expense"
        proof = ""
        if ctx.message.attachments:
            proof = ctx.message.attachments[0].url

        try:
            sheet = get_accounts_sheet()
            sheet.append_row([current_date(), person, "Expense", amount_value, notes, proof])
            logger.info("Added expense entry for %s", person)
        except Exception:
            logger.exception("Failed to add expense entry")
            await ctx.send(embed=error_embed("Google Sheets Error", "Could not save the transaction."))
            return

        await ctx.send(embed=success_embed("Expense recorded", f"{person} spent {format_currency(amount_value)}."))

    @commands.command(name="reimburse")
    async def reimburse(self, ctx: commands.Context, person: Optional[str] = None, amount: Optional[str] = None, *notes_parts: str):
        if not person or not amount:
            await ctx.send(embed=error_embed("Invalid command", "Usage: `!reimburse <Person> <Amount> <Notes>`"))
            return

        try:
            amount_value = parse_amount(amount)
        except ValueError as exc:
            await ctx.send(embed=error_embed("Invalid amount", str(exc)))
            return

        notes = " ".join(notes_parts).strip() or "Reimbursement"
        try:
            sheet = get_accounts_sheet()
            sheet.append_row([current_date(), person, "Reimburse", amount_value, notes, ""])
            logger.info("Added reimbursement entry for %s", person)
        except Exception:
            logger.exception("Failed to add reimbursement entry")
            await ctx.send(embed=error_embed("Google Sheets Error", "Could not save the transaction."))
            return

        await ctx.send(embed=success_embed("Reimbursement recorded", f"{person} was reimbursed {format_currency(amount_value)}."))

    @commands.command(name="balance")
    async def balance(self, ctx: commands.Context, person: Optional[str] = None):
        try:
            sheet = get_accounts_sheet()
            rows = sheet.get_all_records()
        except Exception:
            logger.exception("Failed to read account balances")
            await ctx.send(embed=error_embed("Google Sheets Error", "Could not load balances."))
            return

        balances: dict[str, float] = {}
        for row in rows:
            name = str(row.get("Person", "")).strip()
            if person and name.lower() != person.lower():
                continue
            if not name:
                continue
            try:
                amount = float(row.get("Amount", 0) or 0)
            except (TypeError, ValueError):
                continue
            kind = str(row.get("Type", "")).strip().lower()
            balances[name] = balances.get(name, 0.0) + (amount if kind in {"invest", "reimburse"} else -amount if kind == "expense" else 0.0)

        if not balances:
            await ctx.send(embed=info_embed("No balances", "No transactions found yet."))
            return

        if person:
            target = next(iter(balances.items()))
            await ctx.send(embed=info_embed(f"Balance for {person}", f"{target[0]}: {format_currency(target[1])}"))
            return

        lines = [f"{name}: {format_currency(value)}" for name, value in sorted(balances.items())]
        await ctx.send(embed=info_embed("Balances", "\n".join(lines)))

    @commands.command(name="business")
    async def business(self, ctx: commands.Context):
        try:
            sheet = get_accounts_sheet()
            rows = sheet.get_all_records()
        except Exception:
            logger.exception("Failed to read business summary")
            await ctx.send(embed=error_embed("Google Sheets Error", "Could not load business summary."))
            return

        total_invest = 0.0
        total_expense = 0.0
        for row in rows:
            try:
                amount = float(row.get("Amount", 0) or 0)
            except (TypeError, ValueError):
                continue
            kind = str(row.get("Type", "")).strip().lower()
            if kind == "invest":
                total_invest += amount
            elif kind == "expense":
                total_expense += amount

        embed = info_embed("Business Summary", f"Total Invest: {format_currency(total_invest)}\nTotal Expense: {format_currency(total_expense)}\nBusiness Balance: {format_currency(total_invest - total_expense)}")
        await ctx.send(embed=embed)

    @commands.command(name="history")
    async def history(self, ctx: commands.Context, person: Optional[str] = None):
        if not person:
            await ctx.send(embed=error_embed("Invalid command", "Usage: `!history <Person>`"))
            return

        try:
            sheet = get_accounts_sheet()
            rows = sheet.get_all_records()
        except Exception:
            logger.exception("Failed to read history")
            await ctx.send(embed=error_embed("Google Sheets Error", "Could not load history."))
            return

        matches = [row for row in rows if str(row.get("Person", "")).strip().lower() == person.lower()]
        if not matches:
            await ctx.send(embed=info_embed("History", "No transactions found."))
            return

        lines = []
        for row in reversed(matches):
            lines.append(f"{row.get('Date', '')} | {row.get('Type', '')} | {format_currency(row.get('Amount', 0))} | {row.get('Notes', '')}")
        await ctx.send(embed=info_embed(f"History for {person}", "\n".join(lines)))


async def setup(bot: commands.Bot):
    await bot.add_cog(AccountsCog(bot))
