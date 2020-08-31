import platform
from quart import Quart, request

from webnetem.linux import LinuxThrottler
from webnetem.macos import MacosThrottler


app = Quart(__name__)


@app.route("/")
async def index():
    return app.throttler.status


@app.route("/shape", methods=["POST"])
async def shape():
    data = await request.get_json()
    return app.throttler.shape(data)


@app.route("/reset")
async def reset():
    return app.throttler.teardown()


def main():
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
    app.throttler = netem
    app.run(host="0.0.0.0", port=8888)


if __name__ == "__main__":
    main()
