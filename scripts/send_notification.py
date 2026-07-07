import os
import sys
import urllib.request
from pathlib import Path


def post_ntfy(topic, message):
    url = topic if topic.startswith("http") else f"https://ntfy.sh/{topic}"
    request = urllib.request.Request(
        url,
        data=message.encode("utf-8"),
        method="POST",
        headers={
            "Title": "Video Notice Alert",
            "Tags": "movie_camera,mega",
            "Priority": "default",
        },
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        print(f"ntfy sent: {response.status}")


def main():
    message_path = Path(sys.argv[1])
    message = message_path.read_text(encoding="utf-8").strip()
    if not message:
        print("notification skipped: empty message")
        return 0

    ntfy_topic = os.environ.get("NTFY_TOPIC", "").strip()
    if ntfy_topic:
        post_ntfy(ntfy_topic, message)
    else:
        print("notification skipped: NTFY_TOPIC secret is not set")

    return 0


if __name__ == "__main__":
    sys.exit(main())
