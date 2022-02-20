import os
from typing import Optional, Union
from hikari import Embed, GatewayBot, Intents, events

class EoD(GatewayBot):
    def __init__(self, token: str):
        # Add intents for message reactions 
        super().__init__(token, intents=Intents.GUILD_MESSAGE_REACTIONS | Intents.GUILD_MESSAGES)

        # wait for ;eod to be sent
        self._event_manager.subscribe(events.GuildMessageCreateEvent, self.send_reaction_embed)

        # go to self.reaction_role when there's a reaction added or removed
        self._event_manager.subscribe(events.GuildReactionAddEvent, self.reaction_role)
        self._event_manager.subscribe(events.GuildReactionDeleteEvent, self.reaction_role)
        self.embed_id: Optional[int] = None

    # Handle ;eod messages then respond with an embed with an ok-hand reaction
    async def send_reaction_embed(self, event: events.GuildMessageCreateEvent):
        if event.content and event.content.startswith(';eod'):
            message = await event.message.respond(embed=Embed(title='React on this!'))
            await message.add_reaction('👌')
            self.embed_id = message.id
    
    # Handle reactions being added or removed on the embed
    async def reaction_role(self, event: Union[events.GuildReactionAddEvent, events.GuildReactionDeleteEvent]):
        
        # Is the reaction on the embed?
        if self.embed_id and event.message_id == self.embed_id:
            # If it is, get the guild and role called EoD
            guild = await event.app.rest.fetch_guild(event.guild_id)
            role = next(filter(lambda k: k[1].name == 'EoD', guild.roles.items()), None)
            
            if role is None:
                print(f'EoD role not found for guild {guild.name}')
                return 
            
            # Has a new reaction been added?
            if isinstance(event, events.GuildReactionAddEvent):
                # If it is, add the EoD role to the user
                await event.member.add_role(role[0])
                print('Reaction added')
            else:
                # Otherwise the reaction must've been removed. In which case, remove their EoD role
                user = guild.get_member(event.user_id) 
                assert user # ensure user exists
                await user.remove_role(role[0])
                print('Reaction removed')
            

# Get the token to run your discord bot
# To set the environmental variable:
#   PS Windows: $env:DISCORD_TOKEN="YOUR_TOKEN"
token = os.getenv('DISCORD_TOKEN')

# If token is none then there is no DISCORD_TOKEN in env
if token is None: 
    print('DISCORD_TOKEN not set in env')
    exit(1) # non-zero exit code is an error indication

# start up our bot 
bot = EoD(token)
bot.run()
