from aiohttp import web
import asyncio
import os
import utils

app = web.Application()
routes = web.RouteTableDef()
a_check = os.environ["dbl_auth"]


@routes.get("/")
async def home(request):
    HOME_PAGE_HTML = """
    <head>
    <title>Chuck | Home</title>
    </head>
    <body>
    <center>
        <h1>Hello, World!</h1>
        <a href="https://statuspage.freshping.io/65327-Chuck/">Check Status Page</a>
    </center>
    </body>
    """
    return web.Response(body=HOME_PAGE_HTML, content_type="text/html")


@routes.get("/commands")
async def commands(request):
    COMMANDS_PAGE_HTML = ""
    for cog, cmds in utils.HELP_INFO.items():
        x = "<h2>" + cog.capitalize() + "</h2>\n"
        for name, cmd in cmds.items():
            x += f"\n<h3>{name.capitalize()}</h3>\n<p>{cmd['description']}</p>\n<ul><li>SYNTAX: {cmd['syntax']}</li>\n<li>EXAMPLE: {cmd['example']}</li>\n</ul>\n"
        COMMANDS_PAGE_HTML += x
    return web.Response(body=COMMANDS_PAGE_HTML, content_type="text/html")


@routes.post("/dbl_post")
async def dbl_post(request):
    a = request.headers["Authorization"]
    if a != a_check:
        return
    d = await request.json()
    asyncio.create_task(app.bot.vote(d, 0))
    return web.Response(text="")


app.add_routes(routes)
