from discord import ButtonStyle, Embed, Interaction, Color#, MessageInteraction
from discord.ui import View, Button, button

import datetime
from zoneinfo import ZoneInfo
import math


def get_formatted_time(timezone = "America/Chicago"):
    return datetime.datetime.now(tz=ZoneInfo(timezone)).strftime("%H:%M:%S")


class PrivateView(View):

    def __init__(self, author, *args, **kwargs):

        self.author = author
        super().__init__(*args, **kwargs)

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message("You cannot interact with a View created by someone else!", ephemeral=True, delete_after=5)
            return False

        return True


class DataHandler(PrivateView):

    def __init__(self, author, *items, timeout = 180, data = None, per_page = 10, title = "Embed", back_callback = None, select_callback = None):
        super().__init__(author, *items, timeout=timeout)

        self.data = data
        self.per_page = per_page
        self.current_page = 0
        self.max_pages = math.ceil(len(data) / per_page)
        self.current_selection = 0
        self.max_selections = len(data)
        self.title = title
        self.back_callback = back_callback
        self.select_callback = select_callback

    async def update(self, interaction, selection = False):

       embed = await self.generate_embed(selection)
       await interaction.response.edit_message(embed = embed, view = self)

    async def generate_embed(self, selection = False):

         # Parse the first page of our data
        parsed_data = await self.get_page_data(self.current_page, selection)

        # Create an initial embed with the first page of our data
        embed = Embed(color=Color.light_grey())
        embed.add_field(name = self.title, value = parsed_data)

        return embed

    async def get_page_data(self, page, selection = False):
        
        # Grab the data in the specified range, and parse it line-by-line into a readable format
        parsed_data = ""
        starting = (page * self.per_page)
        ending = ((page + 1) * self.per_page)
        for data in self.data[starting:ending]:
            index = self.data.index(data)
            if selection and self.current_selection == index:
                parsed_data += "**--> {index})** {data}\n".format(index = index + 1, data = data)
                continue
            parsed_data += "**{index})** {data}\n".format(index = index + 1, data = data)

        # Return the parsed data
        return parsed_data


class BrowseData(DataHandler):

    @button(label = "<< First", style = ButtonStyle.red)
    async def go_to_first(self, button: Button, interaction: Interaction):

        self.current_page = 0
        await self.update(interaction)

    @button(label = "< Prev", style = ButtonStyle.red)
    async def go_to_previous(self, button: Button, interaction: Interaction):

        self.current_page -= 1
        if self.current_page < 0:
            self.current_page = self.max_pages - 1
        await self.update(interaction)

    @button(label = "Next >", style = ButtonStyle.green)
    async def go_to_next(self, button: Button, interaction: Interaction):
        
        self.current_page += 1
        if self.current_page > (self.max_pages - 1):
            self.current_page = 0
        await self.update(interaction)

    @button(label = "Last >>", style = ButtonStyle.green)
    async def go_to_last(self, button: Button, interaction: Interaction):
        
        self.current_page = self.max_pages - 1
        await self.update(interaction)

    @button(label = "Back", style = ButtonStyle.grey)
    async def enter_control_panel(self, button: Button, interaction: Interaction):

        if self.back_callback:
            await self.back_callback(interaction)


class SelectData(DataHandler):

    @button(label = "Select", style = ButtonStyle.blurple)
    async def select(self, button: Button, interaction: Interaction):

        if self.select_callback:
            await self.select_callback(interaction, self.current_selection)

    @button(label = "< Prev", style = ButtonStyle.red)
    async def go_to_previous(self, button: Button, interaction: Interaction):

        # Lower our selection
        self.current_selection -= 1
        if self.current_selection < 0:
            self.current_selection = self.max_selections - 1
        
        # Recalculate the page based on the selection and go to it
        self.current_page = math.floor(self.current_selection / self.max_selections)
        if self.current_page < 0:
            self.current_page = self.max_pages - 1
        await self.update(interaction, selection = True)

    @button(label = "Next >", style = ButtonStyle.green)
    async def go_to_next(self, button: Button, interaction: Interaction):
        
        # Raise our selection
        self.current_selection += 1
        if self.current_selection > (self.max_selections - 1):
            self.current_selection = 0

        # Recalculate the page based on the selection and go to it
        self.current_page = math.floor(self.current_selection / self.max_selections)
        if self.current_page > (self.max_pages - 1):
            self.current_page = 0
        await self.update(interaction, selection = True)

    @button(label = "Back", style = ButtonStyle.grey)
    async def enter_control_panel(self, button: Button, interaction: Interaction):

        if self.back_callback:
            await self.back_callback(interaction)
