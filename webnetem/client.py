import requests

_SERVER = "http://localhost:8888"


def status():
    return requests.get(_SERVER).json()


def reset():
    return requests.get(_SERVER + "/reset").json()


def shape():
    data = {
        "up": {"delay": "15000ms", "queue_size": "25", "bw": "5Kbit/s", "loss": "7%"},
        "down": {"delay": "15000ms", "queue_size": "25", "bw": "5Kbit/s", "loss": "7%"},
    }

    return requests.post(_SERVER + "/shape", json=data).json()


print(status())
print(shape())
print(status())
#print(reset())
