from quart import Quart
import subprocess
import shlex
import platform

from webnetem.linux import LinuxThrottler
from webnetem.macos import MacosThrottler


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
    system = platform.system()
    if system == "Linux":
        klass = LinuxThrottler
    elif system == "Darwin":
        klass = MacosThrottler
    else:
        raise Exception("Linux only")
    nic = "eth0"
    inbound = True
    include = []
    exclude = ["dport=22", "sport=22"]
    netem = klass(nic, inbound, include, exclude, app.logger)
    netem.initialize()
    app.run()
