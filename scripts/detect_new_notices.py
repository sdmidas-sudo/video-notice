import json
import os
import sys
from pathlib import Path


def load_notices(path):
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return payload.get("notices", [])


def notice_key(notice):
    return notice.get("id") or notice.get("url") or f"{notice.get('source')}::{notice.get('title')}"


def write_github_output(values):
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        return
    with open(output_path, "a", encoding="utf-8") as output:
        for key, value in values.items():
            output.write(f"{key}={value}\n")


def main():
    old_path = Path(sys.argv[1])
    new_path = Path(sys.argv[2])
    message_path = Path(sys.argv[3])

    old_keys = {notice_key(notice) for notice in load_notices(old_path)}
    new_notices = load_notices(new_path)
    newly_detected = [notice for notice in new_notices if notice_key(notice) not in old_keys]

    lines = []
    if newly_detected:
        lines.append(f"영상공고 새 공고 {len(newly_detected)}건이 감지되었습니다.")
        lines.append("")
        for notice in newly_detected[:10]:
            keywords = ", ".join(notice.get("matchedKeywords", []))
            lines.append(f"- [{notice.get('source')}] {notice.get('title')}")
            lines.append(f"  키워드: {keywords or '확인 필요'}")
            lines.append(f"  링크: {notice.get('url')}")
    else:
        lines.append("새로 감지된 영상공고가 없습니다.")

    message_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_github_output(
        {
            "new_count": str(len(newly_detected)),
            "has_new": "true" if newly_detected else "false",
        }
    )
    print(f"new notices: {len(newly_detected)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
