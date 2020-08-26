from quart import Quart
import subprocess
import shlex
import platform

from webnetem.netimpair import NetemInstance


app = Quart(__name__)


@app.route("/")
async def index():
    return {}


@app.route("/shape", methods=["POST"])
async def shape():
    return {}


@app.route("/reset")
async def reset():
    netem.teardown()
    return {"result": "OK"}


if __name__ == "__main__":
    if platform.system() != "Linux":
        raise Exception("Linux only")
    nic = "eth0"
    inbound = True
    include = []
    exclude = ["dport=22", "sport=22"]
    netem = NetemInstance(nic, inbound, include, exclude, app.logger)
    netem.initialize()
    app.run()
