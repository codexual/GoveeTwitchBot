from twitchio.ext import commands
import requests
import time
from typing import List, Dict
from datetime import datetime

# ======================
# CONFIGURATION SECTION
# ======================

# Twitch Configuration
TWITCH_CONFIG = {
    'token': 'oauth:your_oauth_here',
    'prefix': '!',
    'initial_channels': ['YOUR_TWITCH_CHANNEL'],
    'admin_users': ['your_twitch_channel', 'mod1', 'mod2']  # Lowercase only
}

# Govee Configuration
GOVEE_CONFIG = {
    'api_key': 'YOUR_GOVEE_API_KEY',
    'devices': [
        {
            'device_id': 'YOUR_DEVICE_ID',
            'model': 'H6195',
            'name': 'Main Light'
        },
        #{
        #    'device_id': 'YOUR_DEVICE_ID',
        #    'model': 'H619D',
        #    'name': 'Basement RGB Lights'
        #},
        #Add more devices if needed
    ],
    'rate_limit': {
        'max_requests': 90,  # Stay under Govee's 100/min limit
        'period': 60,       # 60 second window
        'user_cooldown': 2  # Reduced from 5 to 2 seconds
    }
}

COLORS = {
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'yellow': (255, 255, 0),
    'purple': (128, 0, 128),
    'pink': (255, 192, 203),
    'orange': (255, 165, 0),
    'white': (255, 255, 255),
    'cyan': (0, 255, 255),
    'magenta': (255, 0, 255),
    'lime': (0, 255, 0),
    'teal': (0, 128, 128),
    'lavender': (230, 230, 250),
    'brown': (165, 42, 42),
    'gold': (255, 215, 0),
    'silver': (192, 192, 192),
    'black': (0, 0, 0)
}

# ======================
# BOT IMPLEMENTATION
# ======================

class GoveeTwitchBot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=TWITCH_CONFIG['token'],
            prefix=TWITCH_CONFIG['prefix'],
            initial_channels=TWITCH_CONFIG['initial_channels']
        )
        self.admin_users = [user.lower() for user in TWITCH_CONFIG['admin_users']]
        self.commands_enabled = True  # Controls whether commands are active
        self.last_command_time = {}   # For user cooldowns
        self.request_times = []      # For rate limiting
        self.total_requests = 0      # For daily limit tracking
        self.start_time = datetime.now()

    def log(self, message: str):
        """Enhanced logging with timestamps"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")

    async def event_ready(self):
        self.log(f'✅ Bot logged in as | {self.nick}')
        self.log(f'🔌 Connected to {len(GOVEE_CONFIG["devices"])} Govee devices:')
        for device in GOVEE_CONFIG['devices']:
            self.log(f"  - {device['name']} (ID: {device['device_id']})")
        self.log(f'👑 Admin users: {", ".join(self.admin_users)}')
        self.log(f'⚙️ Commands are currently: {"ENABLED" if self.commands_enabled else "DISABLED"}')

    async def event_message(self, message):
        if message.echo:
            return
            
        # Log all incoming messages for debugging
        self.log(f"💬 {message.author.name}: {message.content}")
        
        # Only process commands if they're enabled or from admin
        if not self.commands_enabled and message.author.name.lower() not in self.admin_users:
            self.log(f"🚫 Command ignored (disabled): {message.content}")
            return
            
        # Check user cooldown
        user = message.author.name.lower()
        current_time = time.time()
        if user in self.last_command_time:
            elapsed = current_time - self.last_command_time[user]
            if elapsed < GOVEE_CONFIG['rate_limit']['user_cooldown']:
                self.log(f"⏳ Cooldown active for {user} ({elapsed:.1f}s < {GOVEE_CONFIG['rate_limit']['user_cooldown']}s)")
                return

        await self.handle_commands(message)

    async def check_rate_limit(self):
        """Enforce Govee API rate limits with detailed logging"""
        current_time = time.time()
        window_start = current_time - GOVEE_CONFIG['rate_limit']['period']
        
        # Remove old requests from tracking
        self.request_times = [t for t in self.request_times if t > window_start]
        current_count = len(self.request_times)
        
        # Log current rate limit status
        self.log(f"📊 Rate limit: {current_count}/{GOVEE_CONFIG['rate_limit']['max_requests']} requests in last {GOVEE_CONFIG['rate_limit']['period']}s")
        
        # Check if we've hit the limit
        if current_count >= GOVEE_CONFIG['rate_limit']['max_requests']:
            time_to_wait = window_start + GOVEE_CONFIG['rate_limit']['period'] - current_time
            self.log(f"⚠️ Rate limit reached. Waiting {time_to_wait:.1f} seconds")
            time.sleep(time_to_wait)
            return False
        
        # Check daily limit
        if self.total_requests >= 10000:
            self.log("⚠️ Daily API limit reached! Commands disabled.")
            self.commands_enabled = False
            return False
            
        return True

    async def send_govee_command(self, device: Dict, cmd_name: str, value):
        """Send command with rate limiting and detailed logging"""
        self.log(f"🔧 Preparing command for {device['name']}: {cmd_name}={value}")
        
        if not await self.check_rate_limit():
            self.log("🚨 Command blocked by rate limiting")
            return False
            
        url = "https://developer-api.govee.com/v1/devices/control"
        headers = {
            "Govee-API-Key": GOVEE_CONFIG['api_key'],
            "Content-Type": "application/json"
        }
        payload = {
            "device": device['device_id'],
            "model": device['model'],
            "cmd": {
                "name": cmd_name,
                "value": value
            }
        }
        
        try:
            self.log(f"🌐 Sending to {device['name']}: {cmd_name}={value}")
            resp = requests.put(url, json=payload, headers=headers, timeout=5)
            self.request_times.append(time.time())
            self.total_requests += 1
            
            if resp.status_code == 200:
                self.log(f"✅ {device['name']} success: {cmd_name}={value}")
                return True
            else:
                self.log(f"❌ {device['name']} error {resp.status_code}: {resp.text}")
                return False
        except Exception as e:
            self.log(f"🔥 Command failed to {device['name']}: {str(e)}")
            return False

    async def control_all_devices(self, cmd_name: str, value):
        """Control all devices with detailed logging"""
        self.log(f"🔄 Sending '{cmd_name}={value}' to all devices")
        results = []
        for device in GOVEE_CONFIG['devices']:
            success = await self.send_govee_command(device, cmd_name, value)
            results.append(success)
            if not success:
                break  # Stop if we hit rate limit
        return all(results)

    # ======================
    # COMMAND IMPLEMENTATION
    # ======================

    async def set_color(self, ctx, color_name: str, rgb: tuple):
        """Handle color commands with permissions"""
        user = ctx.author.name.lower()
        self.last_command_time[user] = time.time()
        self.log(f"🎨 {user} requested color: {color_name} {rgb}")
        
        if color_name == 'black':
            success = await self.control_all_devices("brightness", 0)
            if success:
                await ctx.send('⚫ All lights turned off')
        else:
            color_success = await self.control_all_devices("color", {"r": rgb[0], "g": rgb[1], "b": rgb[2]})
            bright_success = await self.control_all_devices("brightness", 100)
            if color_success and bright_success:
                await ctx.send(f'🎨 All lights set to {color_name}!')

    # Generate all color commands dynamically
    def create_color_command(color_name, rgb):
        async def cmd(self, ctx):
            await self.set_color(ctx, color_name, rgb)
        return cmd

    for color_name, rgb in COLORS.items():
        cmd = create_color_command(color_name, rgb)
        cmd.__name__ = f'cmd_{color_name}'
        locals()[color_name] = commands.command(name=color_name)(cmd)

    @commands.command(name='on', aliases=['lightson'])
    async def turn_on(self, ctx):
        """Turn on all lights (works even when commands are disabled)"""
        if ctx.author.name.lower() not in self.admin_users:
            self.log(f"🚫 Unauthorized power on attempt by {ctx.author.name}")
            return
            
        self.log(f"💡 Admin {ctx.author.name} turning lights ON")
        success = await self.control_all_devices("turn", "on")
        if success:
            await self.control_all_devices("brightness", 100)
            await ctx.send('💡 All lights turned on!')

    @commands.command(name='off', aliases=['lightsoff'])
    async def turn_off(self, ctx):
        """Turn off all lights (works even when commands are disabled)"""
        if ctx.author.name.lower() not in self.admin_users:
            self.log(f"🚫 Unauthorized power off attempt by {ctx.author.name}")
            return
            
        self.log(f"💡 Admin {ctx.author.name} turning lights OFF")
        success = await self.control_all_devices("turn", "off")
        if success:
            await ctx.send('💡 All lights turned off.')

    @commands.command(name='goveeon', aliases=['gon', 'enable'])
    async def enable_commands(self, ctx):
        """Enable color commands (admin only)"""
        if ctx.author.name.lower() not in self.admin_users:
            self.log(f"🚫 Unauthorized enable attempt by {ctx.author.name}")
            return
            
        self.commands_enabled = True
        self.log(f"🟢 Commands ENABLED by {ctx.author.name}")
        await ctx.send('🤖 Govee commands ENABLED - color commands are now active!')

    @commands.command(name='goveeoff', aliases=['goff', 'disable'])
    async def disable_commands(self, ctx):
        """Disable color commands (admin only)"""
        if ctx.author.name.lower() not in self.admin_users:
            self.log(f"🚫 Unauthorized disable attempt by {ctx.author.name}")
            return
            
        self.commands_enabled = False
        self.log(f"🔴 Commands DISABLED by {ctx.author.name}")
        await ctx.send('🤖 Govee commands DISABLED - color commands are now inactive')

    @commands.command(name='status')
    async def bot_status(self, ctx):
        """Check bot status"""
        status = "🟢 ONLINE" if self.commands_enabled else "🔴 OFFLINE"
        uptime = datetime.now() - self.start_time
        remaining = max(0, 10000 - self.total_requests)
        
        status_msg = (
            f"{status} | Uptime: {str(uptime).split('.')[0]}\n"
            f"📊 API uses: {self.total_requests}/10000 ({remaining} remaining)\n"
            f"👑 Admins: {', '.join(self.admin_users)}\n"
            f"💡 Power commands: !on/!off\n"
            f"🤖 Bot control: !gon/!goff"
        )
        
        await ctx.send(status_msg)

if __name__ == "__main__":
    bot = GoveeTwitchBot()
    bot.run()
