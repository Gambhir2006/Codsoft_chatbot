import re
import time
import sys
from datetime import datetime

CHAT_HISTORY = "chat_history.txt"
BOT_NAME = "Gambhir Jha"

# ----- helper utils --------------------------------------------------------
def simulate_typing(text, delay=0.02):
    """Print text like a human typing."""
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write("\n")
    sys.stdout.flush()

def _clean(s):
    if not isinstance(s, str):
        return ""
    return s.strip().lower()

def tiny_similarity(a, b):
    if not a or not b:
        return 0.0
    a, b = a.lower(), b.lower()
    i = 0
    matches = 0
    for ch in b:
        if i < len(a) and ch == a[i]:
            matches += 1
            i += 1
        else:
            try:
                i = a.index(ch, i) + 1
                matches += 1
            except ValueError:
                pass
    denom = (len(a) + len(b)) / 2
    return matches / denom if denom else 0.0

def log_conversation(user_msg, bot_msg):
    try:
        ts = datetime.now().isoformat()
        with open(CHAT_HISTORY, "a", encoding="utf-8") as f:
            f.write(f"{ts} USER: {user_msg}\n")
            f.write(f"{ts} BOT: {bot_msg}\n")
    except Exception:
        pass

# ----- FAQ data ------------------------------------------------------------
FAQS = {
    "who made you": "I was created by Gambhir Jha as a simple demo chatbot.",
    "what is your name": "My name is Gambhir Jha.",
    "version": "This is v0.1-alpha (handmade, not perfect).",
    "what can you do": "I can chat, do basic math, tell time, and answer a few FAQs."
}

# ----- regex patterns ------------------------------------------------------
RE_GREETING = re.compile(r"\b(hi|hello|hey|yo|hiya)\b", re.I)
RE_TIME = re.compile(r"\b(time|what(?:'s| is) the time|current time)\b", re.I)
RE_HELP = re.compile(r"\bhelp\b", re.I)
RE_EXIT = re.compile(r"\b(bye|exit|quit|goodbye)\b", re.I)
RE_ADD = re.compile(r"(?:add|sum|plus|\+)\s*(?:of)?\s*([+-]?\d+)\s*(?:and|,|\s)?\s*([+-]?\d+)", re.I)
RE_SUB = re.compile(r"(?:subtract|minus|less)\s*([+-]?\d+)\s*(?:and|from|,|\s)?\s*([+-]?\d+)", re.I)
RE_MATH_INFIX = re.compile(r"([+-]?\d+)\s*([\+\-])\s*([+-]?\d+)")
RE_FAQ_SIMPLE = re.compile(r"(who made you|what is your name|version|what can you do)", re.I)

# ----- handlers ------------------------------------------------------------
def handle_greeting():
    return "Hey! 👋 How can I help you today?"

def handle_time():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"It's {now} (local time)."

def handle_help():
    return (
        "Here’s what I can do:\n"
        "- Say hi (hi, hello)\n"
        "- Tell time (time)\n"
        "- Math: add 4 and 5 / 7 + 3\n"
        "- Math: subtract 10 and 3 / 10 - 3\n"
        "- FAQs: who made you, version\n"
        "- Exit: bye / exit\n"
    )

def parse_math(msg):
    m = RE_ADD.search(msg)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        return f"{a} + {b} = {a + b}"

    m = RE_SUB.search(msg)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        if "from" in msg:
            return f"{b} - {a} = {b - a}"
        return f"{a} - {b} = {a - b}"

    m = RE_MATH_INFIX.search(msg)
    if m:
        a, op, b = int(m.group(1)), m.group(2), int(m.group(3))
        return f"{a} {op} {b} = {a + b if op == '+' else a - b}"

    return None

def handle_faq(msg):
    m = RE_FAQ_SIMPLE.search(msg)
    if m:
        return FAQS.get(m.group(1).lower())

    best = ("", 0)
    for q, ans in FAQS.items():
        score = tiny_similarity(q, msg)
        if score > best[1]:
            best = (ans, score)

    return best[0] if best[1] > 0.4 else None

def fallback_response():
    return "Sorry, I didn’t understand that. Type 'help' to see what I can do."

# ----- main loop -----------------------------------------------------------
WELCOME = (
    f"Hi! I'm {BOT_NAME} 🤖\n"
    "Type 'help' to see commands. Type 'bye' to exit.\n"
)

def main_loop():
    simulate_typing(WELCOME, delay=0.005)
    while True:
        try:
            msg = input("You> ").strip()
            if not msg:
                continue

            cleaned = _clean(msg)

            if RE_EXIT.search(cleaned):
                reply = "Bye! 👋 Take care."
                simulate_typing(reply)
                log_conversation(msg, reply)
                break

            if RE_HELP.search(cleaned):
                reply = handle_help()
                simulate_typing(reply, 0.005)
                log_conversation(msg, reply)
                continue

            if RE_GREETING.search(cleaned):
                reply = handle_greeting()
                simulate_typing(reply)
                log_conversation(msg, reply)
                continue

            if RE_TIME.search(cleaned):
                reply = handle_time()
                simulate_typing(reply)
                log_conversation(msg, reply)
                continue

            math_res = parse_math(cleaned)
            if math_res:
                simulate_typing(math_res)
                log_conversation(msg, math_res)
                continue

            faq_res = handle_faq(cleaned)
            if faq_res:
                simulate_typing(faq_res)
                log_conversation(msg, faq_res)
                continue

            reply = fallback_response()
            simulate_typing(reply)
            log_conversation(msg, reply)

        except KeyboardInterrupt:
            simulate_typing("\nSession interrupted. Bye!")
            break

if __name__ == "__main__":
    print("[debug] starting Gambhir Jha chatbot v0.1")
    time.sleep(0.2)
    main_loop()
    print("Session ended. (chat history saved)")
