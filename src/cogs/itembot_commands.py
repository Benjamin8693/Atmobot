from typing import List, Optional
from fuzzywuzzy import process, fuzz
from operator import itemgetter

import discord
from discord import slash_command, option
from discord.ext import commands
from loguru import logger

from itembot.items import ItemView
from itembot import emojis, items_db

FIND_ITEM_QUERY = """
SELECT * FROM items
INNER JOIN locale_en ON locale_en.id == items.name
WHERE locale_en.data == ? COLLATE NOCASE
"""

FIND_SET_QUERY = """
SELECT * FROM set_bonuses
"""

SET_BONUS_NAME_QUERY = """
SELECT locale_en.data FROM set_bonuses
INNER JOIN locale_en ON locale_en.id == set_bonuses.name
WHERE set_bonuses.id == ?
"""

SPELL_NAME_ID_QUERY = """
SELECT locale_en.data FROM spells
INNER JOIN locale_en ON locale_en.id == spells.name
WHERE spells.template_id == ?
"""


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def fetch_item(self, name: str) -> List[tuple]:
        async with self.bot.db.execute(FIND_ITEM_QUERY, (name,)) as cursor:
            return await cursor.fetchall()

    async def fetch_set_bonus_name(self, set_id: int) -> Optional[tuple]:
        async with self.bot.db.execute(SET_BONUS_NAME_QUERY, (set_id,)) as cursor:
            return (await cursor.fetchone())[0]

    async def fetch_item_stats(self, item: int) -> List[str]:
        stats = []

        async with self.bot.db.execute(
            "SELECT * FROM item_stats WHERE item == ?", (item,)
        ) as cursor:
            async for row in cursor:
                a = row[3]
                b = row[4]

                rowTwo = row[2]

                if rowTwo == 1:
                    order, stat, no_value = items_db.translate_stat(a)
                    rounded_value = round(items_db.unpack_stat_value(b), 2)
                    if no_value:
                        stats.append((order, f"{stat}"))
                    else:
                        stats.append((order, f"+{int(rounded_value)}{stat}"))

                # Starting pips
                if rowTwo == 2:
                    if a != 0:
                        stats.append((131, f"+{a} {emojis.PIP}"))
                    if b != 0:
                        stats.append((132, f"+{b} {emojis.POWER_PIP}"))
                
                # Itemcards
                if rowTwo == 3:
                    async with self.bot.db.execute(SPELL_NAME_ID_QUERY, (a,)) as cursor:
                        card_name = (await cursor.fetchone())[0]
                    copies = b
                    stats.append((150, f"Gives {copies} {card_name}"))
                
                # Maycasts
                if rowTwo == 4:
                    async with self.bot.db.execute(SPELL_NAME_ID_QUERY, (a,)) as cursor:
                        card_name = (await cursor.fetchone())[0]
                    stats.append((151, f"Maycasts {card_name}"))

                # Speed bonus
                if rowTwo == 5:
                    stats.append((133, f"+{a}% {emojis.SPEED}"))

        stats = sorted(stats, key=itemgetter(0))
        _return_stats = []
        for order, stat in stats:
            _return_stats.append(stat)

        return _return_stats

    async def build_item_embed(self, row) -> discord.Embed:
        item_id = row[0]
        set_bonus = row[2]
        rarity = items_db.translate_rarity(row[3])
        jewels = row[4]
        kind = items_db.ItemKind(row[5])
        extra_flags = items_db.ExtraFlags(row[6])
        school = row[7]
        equip_level = row[8]
        min_pet_level = row[9]
        max_spells = row[10]
        max_copies = row[11]
        max_school_copies = row[12]
        deck_school = row[13]
        max_tcs = row[14]
        item_name = row[17]


        requirements = []
        if equip_level != 0:
            requirements.append(f"Level {equip_level}+")
        requirements.append(items_db.translate_equip_school(school))

        stats = []
        if items_db.ExtraFlags.PET_JEWEL in extra_flags:
            stats.append(f"Level {items_db.translate_pet_level(min_pet_level)}+")
        elif kind == items_db.ItemKind.DECK:
            stats.append(f"Max spells {max_spells}")
            stats.append(f"Max copies {max_copies}")
            stats.append(
                f"Max {items_db.translate_school(deck_school)} copies {max_school_copies}"
            )
            stats.append(f"Sideboard {max_tcs}")
        stats.extend(await self.fetch_item_stats(item_id))

        embed = (
            discord.Embed(
                color=items_db.make_school_color(school),
                description="\n".join(stats) or "\u200b",
            )
            .set_author(name=item_name, icon_url=items_db.get_item_icon_url(kind))
            .add_field(name="Requirements", value="\n".join(requirements))
        )

        if jewels != 0:
            embed = embed.add_field(
                name="Sockets", value=items_db.format_sockets(jewels)
            )

        if set_bonus != 0:
            set_name = await self.fetch_set_bonus_name(set_bonus)
            embed = embed.add_field(name="Set Bonus", value=set_name)

        embed.add_field(name="Rarity", value=rarity)

        return embed

    @slash_command(name = "gear", description="Finds a Wizard101 item by name. Credit to Valentin B and Major.", guild_ids = [bot.guild_id])
    @option(name = "Item Name", description = "Name of the item to look up", required = True)
    async def gear(
        self, 
        interaction: discord.Interaction, 
        *, 
        name: str
    ):
        logger.info("Requested item '{}'", name)

        await interaction.response.defer(ephemeral=False)

        rows = await self.fetch_item(name)
        if not rows:
            closest_names = process.extractOne(name, self.bot.item_list, scorer=fuzz.partial_ratio)
            closest_name = closest_names[0]
            logger.info("Failed to find '{}' instead searching for {}", name, closest_name)
            rows = await self.fetch_item(closest_name)

        view = ItemView([await self.build_item_embed(row) for row in rows])
        await view.start(interaction)


def setup(bot):
    bot.add_cog(Stats(bot))
