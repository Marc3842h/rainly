from rainly import rainly
from flask import request
from flask import jsonify
from flask import abort
import simplejson as json
import requests

# https://travis-ci.org/
# https://docs.travis-ci.com/user/notifications/#Webhooks-Delivery-Format

@rainly.app.route("/travis/<string:unique_id>/<string:secret>", methods="POST")
def travis_ci(unique_id, secret):
    # Webhook will look like this:
    # https://canary.discordapp.com/api/webhooks/<unique_id>/<secret>

    # TravisCI sends always "application/x-www-form-urlencoded" as Content-Type
    if request.content_type != "application/x-www-form-urlencoded":
        return abort(500)

    payload = json.loads(request.args.get("payload"))

    color = 0

    if int(payload["result"]) == 0:
        color = 0x008000  # Success - Green
    elif int(payload["result"]) == 1:
        color = 0xFF0000  # Failure - Red
    else:
        color = 0x808080  # Unknown - Grey

    discord_payload = json.dumps(
        {
            "content": "embeds",
            "username": "Travis CI",
            "avatar_url": "https://travis-ci.org/images/logos/TravisCI-Mascot-1.png",
            "embeds": {
                "title": "Build " + payload["status_message"],
                "description": "`" + str(payload["commit"])[0:7] + "`: " + payload["state"],
                "url": payload["build_url"],
                "color": color
            }
        }
    )

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "rainly (https://github.com/Marc3842h/rainly)"
    }

    req = requests.post("https://canary.discordapp.com/api/webhooks/" + unique_id + "/" + secret,
                        json=discord_payload, headers=headers)
    if not req.ok:
        abort(500)

