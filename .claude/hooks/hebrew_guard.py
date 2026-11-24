#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# כלל 1 (ברוך, 24.11.2026): שיחה שהתחילה בעברית נשארת כולה בעברית, כולל כל שורה שנכתבת בין פעולה לפעולה.
# הבדיקה הזו היא האכיפה של הכלל. אותו קובץ בדיוק יושב בכל המאגרים של ברוך (המקור: business-baruch-hazan).
# שלושה מצבים, לפי הארגומנט:
#   prompt  (UserPromptSubmit) - בתחילת כל תור: תזכורת לכלל, אם השיחה התחילה בעברית.
#   post    (PostToolUse)      - אחרי כל פעולה: אם השורה האחרונה שנכתבה לברוך יצאה באנגלית, הערה מיידית לתקן.
#   stop    (Stop)             - לפני סוף התור: בודק את כל מה שנכתב בתור, גם שורות ביניים. משפט אנגלי אחד מחזיר לכתיבה מחדש.
# מה לא נחשב אנגלית: קוד, פקודות, שמות קבצים ונתיבים, קישורים, מיילים, ושם מוצר של עד שלוש מילים בתוך משפט בעברית.
import sys, json, re, os, hashlib

HE = re.compile(r"[֐-׿]")
LAT = re.compile(r"[A-Za-z]")
WORD = r"[A-Za-z][A-Za-z'’\-]*"
RUN4 = re.compile(rf"\b{WORD}(?:[ ,]+{WORD}){{3,}}\b")  # ארבע מילים לועזיות ברצף = משפט באנגלית
RULE = ("כלל 1: השיחה הזו בעברית. כל מה שנכתב לברוך, כולל שורות ביניים בין פעולות, שאלות, סיכומים וכתוביות, "
        "נכתב בעברית בלבד. קוד, פקודות ושמות קבצים נשארים כמו שהם. לפני כל פלט: בודקים שאין בו משפט באנגלית.")


def clean(text):
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"`[^`\n]*`", " ", text)
    text = re.sub(r"https?://\S+|www\.\S+|\S+@\S+", " ", text)
    text = re.sub(r"(?:[A-Za-z]:)?\S*[/\\]\S*", " ", text)  # נתיבים
    text = re.sub(r"\b\w+\.(?:py|js|json|md|sh|yml|yaml|html|css|txt|db)\b", " ", text)
    text = re.sub(r"<[^>\n]+>", " ", text)
    return text


def english_bits(text):
    """מחזיר את הקטעים שנכתבו באנגלית (עד חמישה)."""
    bad = []
    for line in clean(text).splitlines():
        for seg in re.split(r"(?<=[.!?:;])\s+", line):
            seg = seg.strip(" -*#>|\t")
            if not seg:
                continue
            words = re.findall(WORD, seg)
            he = len(HE.findall(seg))
            if RUN4.search(seg) or (he == 0 and len(words) >= 3):
                bad.append(seg[:120])
    return bad[:5]


def is_prompt(o):
    """הודעה אמיתית של ברוך (לא תוצאה של כלי ולא הודעת מערכת פנימית)."""
    if o.get("type") != "user" or o.get("isMeta"):
        return None
    c = o.get("message", {}).get("content")
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        if any(isinstance(b, dict) and b.get("type") == "tool_result" for b in c):
            return None
        t = "\n".join(b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text")
        return t or None
    return None


def strip_system(t):
    return re.sub(r"<(system-reminder|command-[a-z]+|local-command-[a-z]+)>.*?</\1>", " ", t, flags=re.S)


def load(path):
    first, turn = None, []
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    o = json.loads(line)
                except Exception:
                    continue
                p = is_prompt(o)
                if p is not None:
                    p = strip_system(p)
                    if first is None and (HE.search(p) or LAT.search(p)):
                        first = p
                    turn = []
                    continue
                if o.get("type") == "assistant":
                    for b in o.get("message", {}).get("content", []):
                        if isinstance(b, dict) and b.get("type") == "text" and b.get("text", "").strip():
                            turn.append(b["text"])
    except Exception:
        pass
    return first, turn


def hebrew_chat(first, current=""):
    s = first or current or ""
    return len(HE.findall(s)) > 0 and len(HE.findall(s)) >= len(LAT.findall(s)) * 0.5


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "stop"
    try:
        d = json.load(sys.stdin)
    except Exception:
        return 0
    first, turn = load(d.get("transcript_path", ""))

    if mode == "prompt":
        if hebrew_chat(first, d.get("prompt", "")):
            print(RULE)
        return 0

    if not hebrew_chat(first):
        return 0

    if mode == "post":
        if not turn:
            return 0
        last = turn[-1]
        bad = english_bits(last)
        if not bad:
            return 0
        # לא מעירים פעמיים על אותה שורה
        key = hashlib.sha1(last.encode("utf-8")).hexdigest()[:16]
        mark = os.path.join(os.environ.get("TMPDIR", "/tmp"), f"hebrew-guard-{d.get('session_id', 'x')}")
        try:
            if os.path.exists(mark) and open(mark).read() == key:
                return 0
            open(mark, "w").write(key)
        except Exception:
            pass
        msg = "כלל 1: השורה האחרונה שנכתבה לברוך יצאה באנגלית (" + " | ".join(bad[:2]) + "). מעכשיו כל שורה בעברית בלבד."
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": msg}}, ensure_ascii=False))
        return 0

    # stop
    if d.get("stop_hook_active"):
        return 0
    bad = []
    for t in turn:
        bad += english_bits(t)
    if bad:
        msg = ("כלל 1 נשבר: בתור הזה יצאו לברוך משפטים באנגלית: " + " | ".join(bad[:3]) +
               ". כתוב עכשיו את התשובה הסופית מחדש, כולה בעברית (כולל מה שנאמר בשורות הביניים), בלי התנצלות ארוכה.")
        sys.stderr.buffer.write(msg.encode("utf-8"))
        return 2
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception:
        sys.exit(0)
