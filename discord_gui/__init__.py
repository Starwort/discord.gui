from discord.ext import commands
import discord
import asynctk as tk
from tkinter.ttk import Checkbutton, Separator
from asynctk.scrolledtext import AsyncScrolledText
from asynctk import messagebox
import asyncio
import sys
import arrow

class MockSTDIO:
    '''pretends to be a stdio interface but redirects to a text widget'''
    def __init__(self, io_type, text_widget):
        self.text_widget = text_widget
        self.io_type = io_type
        if io_type == 'stdout':
            self.original_io = sys.stdout
            sys.stdout = self
        elif io_type == 'stderr':
            self.original_io = sys.stderr
            sys.stderr = self

    def write(self, text):
        self.text_widget['state'] = 'normal'
        self.text_widget.insert(tk.END, text)
        self.text_widget['state'] = 'disabled'
        self.original_io.write(text)

    def flush(self, *args, **kw):
        self.original_io.flush(*args, **kw)

    def __del__(self):
        if self.io_type == 'stdout':
            self.original_io = sys.stdout
        elif self.io_type == 'stderr':
            self.original_io = sys.stderr

class GUI(commands.Cog, tk.AsyncTk):
    def __init__(self, bot: commands.Bot):
        tk.AsyncTk.__init__(self, loop=bot.loop)
        self.bot = bot
        self.current_command = None
        self.running_commands = {}
        
        self.command_frame = tk.AsyncFrame(self)
        self.command_frame.text = AsyncScrolledText(self.command_frame, state='disabled', width=40, height=10)
        
        self.statistics_frame = tk.AsyncFrame(self)
        self.statistics_frame.guilds = tk.AsyncLabel(self.statistics_frame, text=f'Guilds: {len(bot.guilds)}')
        self.statistics_frame.channels = tk.AsyncLabel(self.statistics_frame, text=f'Channels: {len([i for i in bot.get_all_channels()])}')
        self.statistics_frame.users = tk.AsyncLabel(self.statistics_frame, text=f'Users: {len(bot.users)}')
        self.statistics_frame.emoji = tk.AsyncLabel(self.statistics_frame, text=f'Emoji: {len(bot.emojis)}')

        self.stdout_frame = tk.AsyncFrame(self)
        self.stdout_frame.text = AsyncScrolledText(self.stdout_frame, state='disabled', width=40, height=10)
        self.stdout = MockSTDIO('stdout', self.stdout_frame.text)
        
        self.stderr_frame = tk.AsyncFrame(self)
        self.stderr_frame.text = AsyncScrolledText(self.stderr_frame, state='disabled', width=40, height=10)
        self.stderr = MockSTDIO('stderr', self.stderr_frame.text)
        
        self.command_editing_frame = tk.AsyncFrame(self)
        self.command_editing_frame.option_button = tk.AsyncMenubutton(self.command_editing_frame, text='Choose a command')

        menu = tk.AsyncMenu(self.command_editing_frame.option_button)
        self.command_editing_frame.option_button['menu'] = menu
        self._menu = menu
        for name, object in bot.all_commands.items():
            menu.add_command(label=name, command=self.make_option(object))

        self.command_cache = bot.all_commands.copy()

        self.command_editing_frame.hidden_var = tk.IntVar(self)
        self.command_editing_frame.enabled_var = tk.IntVar(self)
        self.command_editing_frame.help = AsyncScrolledText(self.command_editing_frame, width=40, height=10)
        self.command_editing_frame.help_submit = tk.AsyncButton(self.command_editing_frame, text='Submit Helpstring', callback=self.submit_helpstring)
        self.command_editing_frame.hidden = Checkbutton(self.command_editing_frame, text='Hidden:', command=self.set_hidden, variable=self.command_editing_frame.hidden_var)
        self.command_editing_frame.enabled = Checkbutton(self.command_editing_frame, text='Enabled:', command=self.set_enabled, variable=self.command_editing_frame.enabled_var)

        
        tk.AsyncLabel(self.command_frame, text='Command info:').pack()
        self.command_frame.text.pack()

        tk.AsyncLabel(self.statistics_frame, text='Statistics:').pack()
        self.statistics_frame.guilds.pack()
        self.statistics_frame.channels.pack()
        self.statistics_frame.users.pack()

        tk.AsyncLabel(self.stdout_frame, text='STDOut:').pack()
        self.stdout_frame.text.pack()

        tk.AsyncLabel(self.stderr_frame, text='STDErr:').pack()
        self.stderr_frame.text.pack()

        tk.AsyncLabel(self.command_editing_frame, text='Modify commands:').grid(row=0, column=0, columnspan=2)
        Separator(self.command_editing_frame).grid(row=1, column=0, columnspan=2)
        tk.AsyncLabel(self.command_editing_frame, text='Command:', anchor=tk.W).grid(row=2, column=0)
        self.command_editing_frame.option_button.grid(row=2, column=1)
        self.command_editing_frame.help.grid(row=3, column=0, columnspan=2)
        self.command_editing_frame.help_submit.grid(row=4, column=0, columnspan=2)
        self.command_editing_frame.hidden.grid(row=5, column=0)
        self.command_editing_frame.enabled.grid(row=5, column=1)

        self.command_frame.grid(row=0, column=0)
        self.statistics_frame.grid(row=0, column=1)
        self.stdout_frame.grid(row=1, column=0)
        self.stderr_frame.grid(row=2, column=0)
        self.command_editing_frame.grid(row=1, column=1, rowspan=2)

        self.wm_protocol('WM_DELETE_WINDOW', self.cog_unload)

    def make_option(self, command):
        def callback():
            self.current_command = command
            self.command_editing_frame.help.delete(1.0, tk.END)
            self.command_editing_frame.help.insert(1.0, command.help or '')
            self.command_editing_frame.hidden_var.set(int(command.hidden))
            self.command_editing_frame.enabled_var.set(int(command.enabled))
        return callback

    @commands.Cog.listener()
    async def on_ready(self):
        self.wm_title(f'{self.bot.user} | Debug GUI')
        self.statistics_frame.guilds['text'] = f'Guilds: {len(self.bot.guilds)}'
        self.statistics_frame.channels['text'] = f'Channels: {len([i for i in self.bot.get_all_channels()])}'
        self.statistics_frame.users['text'] = f'Users: {len(self.bot.users)}'
        self.statistics_frame.emoji['text'] = f'Emoji: {len(self.bot.emojis)}'

    def cog_unload(self):
        del self.stdout
        del self.stderr
        asyncio.ensure_future(self.destroy())

    async def submit_helpstring(self):
        if self.current_command is None:
            await messagebox.showerror('No command selected for which to submit the helpstring!')
            return
        self.current_command.help = self.command_editing_frame.help.get('1.0','end-1c')

    def set_hidden(self):
        if self.current_command is None:
            asyncio.ensure_future(messagebox.showerror('No command selected for which to hide/show!'))
            return
        self.current_command.hidden = self.command_editing_frame.hidden_var.get()

    def set_enabled(self):
        if self.current_command is None:
            asyncio.ensure_future(messagebox.showerror('No command selected for which to enable/disable!'))
            return
        self.current_command.enabled = self.command_editing_frame.enabled_var.get()

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        time = arrow.now() - self.running_commands.pop((ctx.author.id, ctx.channel.id, ctx.command.qualified_name))
        wid = self.command_frame.text
        wid['state'] = 'normal'
        wid.insert(tk.END, f'[Finished in {round(time.total_seconds() * 1000, 1)}ms] {ctx.author.name}: {ctx.prefix}{ctx.command.qualified_name}\n')
        wid['state'] = 'disabled'

    @commands.Cog.listener()
    async def on_command(self, ctx):
        init = arrow.now()
        self.running_commands[ctx.author.id, ctx.channel.id, ctx.command.qualified_name] = init
        wid = self.command_frame.text
        wid['state'] = 'normal'
        wid.insert(tk.END, f'[{init.format("HH:mm")}] {ctx.author.name}: {ctx.prefix}{ctx.command.qualified_name}\n')
        wid['state'] = 'disabled'

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        self.statistics_frame.guilds['text'] = f'Guilds: {len(self.bot.guilds)}'

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        self.statistics_frame.guilds['text'] = f'Guilds: {len(self.bot.guilds)}'

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        self.statistics_frame.channels['text'] = f'Channels: {len([i for i in self.bot.get_all_channels()])}'

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        self.statistics_frame.channels['text'] = f'Channels: {len([i for i in self.bot.get_all_channels()])}'

    @commands.Cog.listener()
    async def on_member_join(self, member):
        self.statistics_frame.users['text'] = f'Users: {len(self.bot.users)}'

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        self.statistics_frame.users['text'] = f'Users: {len(self.bot.users)}'

    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild, before, after):
        self.statistics_frame.emoji['text'] = f'Emoji: {len(self.bot.emojis)}'

    async def runme(self):
        while True:
            try:
                await self.tick()
                try:
                    if self.command_cache != self.bot.all_commands:
                        for name, object in self.bot.all_commands.items():
                            if name in self.command_cache:
                                continue
                            self._menu.add_command(label=name, command=self.make_option(object))
                        self.command_cache = self.bot.all_commands.copy()
                except:
                    import traceback
                    traceback.print_exc()
            except:
                return
            await asyncio.sleep(0.01)

def setup(bot):
    cog = GUI(bot)
    bot.add_cog(cog)
    bot.loop.create_task(cog.runme())