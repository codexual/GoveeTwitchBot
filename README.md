# 💡 Govee Twitch Bot

Control your **Govee smart lights** live on Twitch using simple chat commands!  
Perfect for **IRL streamers**, **VTubers**, or anyone who wants their audience to interact with their lighting in real-time.

---

## ✨ Features

- ✅ Supports multiple Govee devices
- 🟢 Color control via Twitch chat (e.g., `!red`, `!blue`, etc.)
- 💡 Admin power commands to turn lights on/off
- 🧑‍💼 Admin-only control toggles
- 📉 Built-in Govee API rate limiting
- ⏱ Cooldown per user (customizable)
- 📊 `!status` command shows uptime and API usage
- 🪵 Detailed timestamped logging

---

## 🔧 Requirements

- Python 3.8+
- [Twitch OAuth Token](https://twitchtokengenerator.com/)
- Govee Developer API Key
- `requests` and `twitchio` Python modules

Install dependencies:

```bash
pip install twitchio requests
```

---

## 🧪 Twitch Commands

### 🔓 Admin-Only Commands

| Command        | Description                                        |
|----------------|----------------------------------------------------|
| `!on` / `!lightson`     | Turn all Govee lights **ON**                     |
| `!off` / `!lightsoff`   | Turn all Govee lights **OFF**                    |
| `!gon` / `!goveeon`     | Enable color commands for users                 |
| `!goff` / `!goveeoff`   | Disable color commands for users                |
| `!status`               | Check bot status, uptime, API usage, and admins |

> Admin usernames are defined in the `TWITCH_CONFIG['admin_users']` list.

---

### 🌈 User Color Commands (when enabled)

| Command    | Effect                          |
|------------|----------------------------------|
| `!red`     | Set lights to red               |
| `!green`   | Set lights to green             |
| `!blue`    | Set lights to blue              |
| `!yellow`  | Set lights to yellow            |
| `!purple`  | Set lights to purple            |
| `!pink`    | Set lights to pink              |
| `!orange`  | Set lights to orange            |
| `!white`   | Set lights to white             |
| `!cyan`    | Set lights to cyan              |
| `!magenta` | Set lights to magenta           |
| `!lime`    | Set lights to lime              |
| `!teal`    | Set lights to teal              |
| `!lavender`| Set lights to lavender          |
| `!brown`   | Set lights to brown             |
| `!gold`    | Set lights to gold              |
| `!silver`  | Set lights to silver            |
| `!black`   | Turn off lights (sets brightness to 0%) |

> Default user cooldown: **2 seconds**
>  
> Commands will be ignored if color control is disabled via `!goff`.

---

## 🔑 How to Access the Govee Developer API

### Step 1: Get a Govee API Key

1. Go to the official [Govee Developer Portal](https://developer.govee.com/)
2. Sign in with your Govee account.
3. Click **"Apply for API Key"**
4. Your key will look like:
   ```
   xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   ```

---

## 🔍 How to List Your Govee Devices

Once you have your API key, you can find your Govee devices using PowerShell or `curl`.

### ✅ PowerShell

```powershell
$response = Invoke-RestMethod -Method Get `
  -Uri "https://developer-api.govee.com/v1/devices" `
  -Headers @{ "Govee-API-Key" = "YOUR_API_KEY_HERE" }

$response.data.devices | Format-List
```

### ✅ curl

```bash
curl -X GET "https://developer-api.govee.com/v1/devices" \
  -H "Govee-API-Key: YOUR_API_KEY_HERE"
```

Each device will have:

- `device`: Unique device ID
- `model`: Model name (e.g., `H6195`)
- `deviceName`: Your device’s nickname in the Govee app

---

## ⚙️ Configuration

Edit the `TWITCH_CONFIG` and `GOVEE_CONFIG` dictionaries in the Python script:

```python
TWITCH_CONFIG = {
    'token': 'oauth:YOUR_TWITCH_OAUTH_TOKEN',
    'prefix': '!',
    'initial_channels': ['yourchannel'],
    'admin_users': ['yourchannel', 'mod1']
}

GOVEE_CONFIG = {
    'api_key': 'YOUR_GOVEE_API_KEY',
    'devices': [
        {
            'device_id': 'YOUR_DEVICE_ID',
            'model': 'H6195',
            'name': 'Main Light'
        }
    ],
    'rate_limit': {
        'max_requests': 90,
        'period': 60,
        'user_cooldown': 2
    }
}
```

---

## ✅ Example Log Output

```text
[2025-06-20 01:10:03] 💬 codexual: !purple
[2025-06-20 01:10:03] 🎨 codexual requested color: purple (128, 0, 128)
[2025-06-20 01:10:03] 🔧 Preparing command for Main Light: color={'r': 128, 'g': 0, 'b': 128}
[2025-06-20 01:10:03] 📊 Rate limit: 12/90 requests in last 60s
[2025-06-20 01:10:03] 🌐 Sending to Main Light: color={'r': 128, 'g': 0, 'b': 128}
[2025-06-20 01:10:04] ✅ Main Light success: color={'r': 128, 'g': 0, 'b': 128}
```

---

## 📎 Credits

Created by [Codexual](https://twitch.tv/codexual)

Feel free to fork, modify, or contribute!

---

## 🚨 Disclaimer

This project is not affiliated with Govee or Twitch. Use at your own risk.  
Ensure your API usage stays within [Govee's rate limits](https://developer.govee.com/faq).
