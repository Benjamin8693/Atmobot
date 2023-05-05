from typing import List

import discord
from discord import ui


class ItemView(ui.View):
    def __init__(self, entries: List[discord.Embed], *, timeout: float = 180.0):
        super().__init__(timeout=timeout)

        self.entries = entries

        self.current_page = 1
        self.total_entries = len(self.entries)

    def format_entry(self, entry: discord.Embed) -> discord.Embed:
        return entry.set_footer(
            text=f"Showing page {self.current_page}/{self.total_entries}"
        )

    def get_current_page(self) -> discord.Embed:
        # Make sure our page is always in bounds.
        self.current_page = min(self.current_page, self.total_entries)
        self.current_page = max(self.current_page, 1)

        # Return the formatted embed entry to display.
        entry = self.entries[self.current_page - 1]
        return self.format_entry(entry)

    async def update(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            embed=self.get_current_page(), view=self
        )

    @ui.button(style=discord.ButtonStyle.primary, emoji="⏪")
    async def goto_first_button(
        self, _button: ui.Button, interaction: discord.Interaction, 
    ):
        self.current_page = 1
        await self.update(interaction)

    @ui.button(style=discord.ButtonStyle.primary, emoji="⬅️")
    async def back_button(self, _button: ui.Button, interaction: discord.Interaction, ):
        self.current_page -= 1
        await self.update(interaction)

    @ui.button(style=discord.ButtonStyle.primary, emoji="➡️")
    async def forward_button(
        self, _button: ui.Button, interaction: discord.Interaction, 
    ):
        self.current_page += 1
        await self.update(interaction)

    @ui.button(style=discord.ButtonStyle.primary, emoji="⏩")
    async def goto_last_button(
        self, _button: ui.Button, interaction: discord.Interaction, 
    ):
        self.current_page = self.total_entries
        await self.update(interaction)

#    @ui.button(style=discord.ButtonStyle.red, emoji="⏹️")
#    async def stop_button(self, interaction: discord.Interaction, button: ui.Button):
#        self.stop()
#
#        button.disabled = True
#        await self.update(interaction)

    async def start(self, interaction: discord.Interaction):
        res = interaction.response

        # When we only have one embed to show, we don't need to paginate.
        if self.total_entries == 1:
            await interaction.followup.send(embed=self.entries[0])
        else:
            await interaction.followup.send(embed=self.get_current_page(), view=self)
            await self.wait()
