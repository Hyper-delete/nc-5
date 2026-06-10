import asyncio
import json
import os
import random
import logging
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from typing import Optional
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters
from telegram.ext import PrefixHandler
import telegram.error
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Running"

def run_web():
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )

Thread(target=run_web, daemon=True).start()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("BotCore")

TOKENS = [
"8883815099:AAEmj9icuagChneBbPOhtWcdAnf68LFDIGA",
"8964057044:AAHHmgkQYztA6xJSOglu4c7glFBSxr4Vo60",
"8961755422:AAFMmERXyyLXbxiJTvRwHUJ5CdKkT-J9GoQ",
"8960024186:AAG9CEgnX64PN5b3m5wXyWCiIbRXA1h-Crc",
"8962375187:AAGUoxfWRW1TSsbB0Srfcc0KiNNtjTizcJI",
"8860890636:AAFfVg0jOtdfnXV8qNKqwFGbePQTptpJll8",
"8951204614:AAGdL8-eywiz8PN_HMW_ISHnBcDQ8NDK-h0",
"8884934520:AAF_yNGMr5vO75afC5c84TAz6DPvotjt9Z4",
"8836288331:AAHCsJKQd3DMZFtdbu_TXOx9-7f4vd9HbbI",
"8990073356:AAHu7jRNsa8LLK1XQLt6O4iX7CCXbKWQyXQ",
"8604371108:AAE4RFJJWTXCYXi5tXuRV8Klh3rMU4xAHdU",
"8370807942:AAFPBjVJoQpl21ySPRgCLzid7AgDT-EzinU",
"8695046233:AAFPLirdc2_QDRq5rILApBobfTCO5P81ZQs",
"8402293493:AAGUfPQc6is7VsKRLQXqEJXSdX31K4aUT0Q",
"8789540801:AAHNhIF-PjRZk7ezTHO9aakdDPzIWjJ7-xw",
"8630602121:AAEneKvkhGPmkDcYINBdZfgboNlkg6T-uXI",
"8761689455:AAEEhb_66ON8oDJfIVO6HH4Iv1uyijBbmY4"
]


OWNER_IDS = [7623391678, 8399044122]

SUDO_FILE = "sudo_users.json"

NC_SPEED = 0.01
SPAM_SPEED = 0.1

NCEMO_EMOJIS = [
    "😀","😃","😄","😁","😆","😅","😂","🤣","😭","😉","😗","😚","😘","🥰","😍",
    "🤩","🥳","🫠","🙃","🙂","🥲","🥹","😊","☺️","😌","😏","🤤","😋","😛","😝",
    "😜","🤪","🥴","😔","🥺","😬","😑","😐","😶","🫥","🤐","🫡","🤔","🤫","🫢",
    "🤭","🥱","🤗","🫣","😱","🤨","🧐","😒","🙄","😮‍💨","😤","😠","😡","🤬","😞",
    "😓","😟","😥","😢","☹️","🙁","🫤","😕","😰","😨","😧","😦","😮","😯","😲",
    "😳","🤯","😖","😣","😩","😵","😵‍💫","🫨","🥶","🥵","🤢","🤮","😴","😪","🤧",
    "🤒","🤕","😷","😇","🤠","🤑","🤓","😎","🥸",
]

RAID_TEXTS = [
    "🌙་༘࿐","⭐་༘࿐","🌸་༘࿐","🪐་༘࿐","🌈་༘࿐","🌻་༘࿐","⚡་༘࿐","🌹་༘࿐",
    "🔮་༘࿐","🎶་༘࿐","🌊་༘࿐","❄️་༘࿐","🔥་༘࿐","🌼་༘࿐","🕊️་༘࿐","🍀་༘࿐",
    "🎭་༘࿐","🦋་༘࿐","🪄་༘࿐","🏹་༘࿐","🐚་༘࿐","🪷་༘࿐","🌿་༘࿐","☀️་༘࿐",
    "🎇་༘࿐","◈","◆","◉","▷","◍","◯","◐","◑","◒","◓","◖","◗","◧","◨","◩",
    "◪","◫","◬","◭","◮","◎","▣","▤","▥","▦","▧","▨","▩","▪","▫","▬","▲","△",
    "▼","▽","◇","○","●","◦","☯","☮","☘","☀","☁","☂","☾","☄","⚝","⚘",
]

deletenc_TEXTS = [
    "×🌼×","×🌻×","×🪻×","×🏵️×","×💮×","×🌸×","×🪷×","×🌷×",
    "×🌺×","×🥀×","×🌹×","×💐×","×💋×","×❤️‍🔥×","×❤️‍🩹×","×❣️×",
    "×♥️×","×💟×","×💌×","×💕×","×💞×","×💓×","×💗×","×💖×",
    "×💝×","×💘×","×🩷×","×🤍×","×🩶×","×🖤×","×🤎×","×💜×",
    "×🩵×","×💛×","×🧡×","×❤️×",
]


@dataclass
class TaskEntry:
    task: asyncio.Task
    chat_id: int
    command: str
    owner_id: int
    created: float = field(default_factory=lambda: asyncio.get_event_loop().time())


class TaskManager:
    def __init__(self):
        self._tasks: dict[str, TaskEntry] = {}
        self._cleanup_handle: Optional[asyncio.Task] = None

    def _key(self, chat_id: int, command: str) -> str:
        return f"{chat_id}:{command}"

    async def start_cleanup_loop(self):
        self._cleanup_handle = asyncio.create_task(self._cleanup_routine())

    async def _cleanup_routine(self):
        while True:
            await asyncio.sleep(30)
            dead = [k for k, v in self._tasks.items() if v.task.done()]
            for k in dead:
                del self._tasks[k]

    def register(self, chat_id: int, command: str, owner_id: int, coro) -> asyncio.Task:
        key = self._key(chat_id, command)
        old = self._tasks.get(key)
        if old and not old.task.done():
            old.task.cancel()
        task = asyncio.create_task(coro)
        self._tasks[key] = TaskEntry(task=task, chat_id=chat_id, command=command, owner_id=owner_id)
        return task

    def register_multi(self, chat_id: int, command: str, owner_id: int, coros: list) -> list[asyncio.Task]:
        tasks = []
        for i, coro in enumerate(coros):
            key = f"{chat_id}:{command}:{i}"
            old = self._tasks.get(key)
            if old and not old.task.done():
                old.task.cancel()
            task = asyncio.create_task(coro)
            self._tasks[key] = TaskEntry(task=task, chat_id=chat_id, command=command, owner_id=owner_id)
            tasks.append(task)
        return tasks

    async def stop(self, chat_id: int, command: str) -> int:
        prefix = self._key(chat_id, command)
        hit = {k: v for k, v in self._tasks.items() if k.startswith(prefix)}
        for v in hit.values():
            v.task.cancel()
        for v in hit.values():
            try:
                await v.task
            except (asyncio.CancelledError, Exception):
                pass
        for k in hit:
            self._tasks.pop(k, None)
        return len(hit)

    async def stop_chat(self, chat_id: int) -> int:
        prefix = f"{chat_id}:"
        hit = {k: v for k, v in self._tasks.items() if k.startswith(prefix)}
        for v in hit.values():
            v.task.cancel()
        for v in hit.values():
            try:
                await v.task
            except (asyncio.CancelledError, Exception):
                pass
        for k in hit:
            self._tasks.pop(k, None)
        return len(hit)

    async def stop_all(self) -> int:
        snapshot = dict(self._tasks)
        for v in snapshot.values():
            v.task.cancel()
        for v in snapshot.values():
            try:
                await v.task
            except (asyncio.CancelledError, Exception):
                pass
        count = len(snapshot)
        self._tasks.clear()
        return count

    def active_count(self) -> int:
        return sum(1 for v in self._tasks.values() if not v.task.done())

    def summary(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for v in self._tasks.values():
            if not v.task.done():
                out[v.command] = out.get(v.command, 0) + 1
        return out


class StorageManager:
    def __init__(self, path: str):
        self._path = path
        self._data: set[int] = set()
        self._load()

    def _load(self):
        if os.path.exists(self._path):
            try:
                with open(self._path, "r") as f:
                    self._data = set(int(x) for x in json.load(f))
            except Exception:
                self._data = set()

    def save(self):
        with open(self._path, "w") as f:
            json.dump(list(self._data), f)

    def add(self, uid: int):
        self._data.add(uid)
        self.save()

    def remove(self, uid: int) -> bool:
        if uid in self._data:
            self._data.discard(uid)
            self.save()
            return True
        return False

    def __contains__(self, uid: int) -> bool:
        return uid in self._data

    @property
    def members(self) -> set[int]:
        return set(self._data)


sudo_store = StorageManager(SUDO_FILE)
task_mgr = TaskManager()
slide_targets: set[int] = set()
slidespam_targets: set[int] = set()
autoreply_data: dict[int, dict[str, str]] = {}
apps: list = []
bots: list = []
dead_bots: dict[int, set] = {}


def is_authorized(uid: int) -> bool:
    return uid in OWNER_IDS or uid in sudo_store


def mark_dead(bot, chat_id: int):
    if chat_id not in dead_bots:
        dead_bots[chat_id] = set()
    dead_bots[chat_id].add(id(bot))
    log.warning("Bot %s marked dead for chat %s (403)", str(bot.token[:10]), chat_id)


def get_alive_bots(chat_id: int) -> list:
    if chat_id not in dead_bots:
        return bots
    return [b for b in bots if id(b) not in dead_bots[chat_id]]


async def gcnc_loop(bot, chat_id: int, base: str):
    i = 0
    n = len(RAID_TEXTS)
    while True:
        try:
            await bot.set_chat_title(chat_id, f"{base} {RAID_TEXTS[i % n]}")
            i += 1
            await asyncio.sleep(NC_SPEED)
        except telegram.error.RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except (telegram.error.Forbidden, telegram.error.BadRequest):
            mark_dead(bot, chat_id)
            return
        except asyncio.CancelledError:
            raise
        except Exception:
            await asyncio.sleep(1.0)


async def ncemo_loop(bot, chat_id: int, base: str):
    i = 0
    n = len(NCEMO_EMOJIS)
    while True:
        try:
            emo = NCEMO_EMOJIS[i % n]
            await bot.set_chat_title(chat_id, f"{emo} {base} {emo}")
            i += 1
            await asyncio.sleep(NC_SPEED)
        except telegram.error.RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except (telegram.error.Forbidden, telegram.error.BadRequest):
            mark_dead(bot, chat_id)
            return
        except asyncio.CancelledError:
            raise
        except Exception:
            await asyncio.sleep(1.0)


async def ncbaap_loop(bot, chat_id: int, base: str):
    i = 0
    nr = len(RAID_TEXTS)
    ne = len(NCEMO_EMOJIS)
    while True:
        try:
            await bot.set_chat_title(chat_id, f"{base} {RAID_TEXTS[i % nr]}")
            await bot.set_chat_title(chat_id, f"{NCEMO_EMOJIS[i % ne]} {base} {NCEMO_EMOJIS[i % ne]}")
            i += 1
            await asyncio.sleep(NC_SPEED)
        except telegram.error.RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except (telegram.error.Forbidden, telegram.error.BadRequest):
            mark_dead(bot, chat_id)
            return
        except asyncio.CancelledError:
            raise
        except Exception:
            await asyncio.sleep(1.0)


async def nctime_loop(bot, chat_id: int, base: str):
    ist = timezone(timedelta(hours=5, minutes=30))
    while True:
        try:
            now = datetime.now(timezone.utc).astimezone(ist)
            ts = now.strftime("%H:%M:%S") + f":{now.microsecond // 10000:02d}"
            await bot.set_chat_title(chat_id, f"{base} {ts}")
        except telegram.error.RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except (telegram.error.Forbidden, telegram.error.BadRequest):
            mark_dead(bot, chat_id)
            return
        except asyncio.CancelledError:
            raise
        except Exception:
            await asyncio.sleep(1.0)


async def deletencgodspeed_loop(bot, chat_id: int, base: str):
    i = 0
    nd = len(deletenc_TEXTS)
    nr = len(RAID_TEXTS)
    while True:
        try:
            await bot.set_chat_title(chat_id, f"{base} {deletenc_TEXTS[i % nd]} {RAID_TEXTS[i % nr]}")
            await bot.set_chat_title(chat_id, f"{deletenc_TEXTS[i % nd]} {base} {RAID_TEXTS[i % nr]}")
            i += 1
        except telegram.error.RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except (telegram.error.Forbidden, telegram.error.BadRequest):
            mark_dead(bot, chat_id)
            return
        except asyncio.CancelledError:
            raise
        except Exception:
            await asyncio.sleep(1.0)


async def spam_loop(bot, chat_id: int, text: str):
    while True:
        try:
            await bot.send_message(chat_id, text)
            await asyncio.sleep(SPAM_SPEED)
        except telegram.error.RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except (telegram.error.Forbidden, telegram.error.BadRequest):
            mark_dead(bot, chat_id)
            return
        except asyncio.CancelledError:
            raise
        except Exception:
            await asyncio.sleep(1.0)


async def handle_gcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_authorized(uid):
        return
    if not context.args:
        return await update.message.reply_text("⚠️ !gcnc <name>")
    base = " ".join(context.args)
    cid = update.message.chat_id
    await task_mgr.stop(cid, "gcnc")
    alive = get_alive_bots(cid)
    if not alive:
        return await update.message.reply_text("❌ No bots have admin in this chat")
    task_mgr.register_multi(cid, "gcnc", uid, [gcnc_loop(b, cid, base) for b in alive])
    await update.message.reply_text(f"⚡ GC NC Started! ({len(alive)} bots)")


async def handle_ncemo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_authorized(uid):
        return
    if not context.args:
        return await update.message.reply_text("⚠️ !ncemo <name>")
    base = " ".join(context.args)
    cid = update.message.chat_id
    await task_mgr.stop(cid, "ncemo")
    alive = get_alive_bots(cid)
    if not alive:
        return await update.message.reply_text("❌ No bots have admin in this chat")
    task_mgr.register_multi(cid, "ncemo", uid, [ncemo_loop(b, cid, base) for b in alive])
    await update.message.reply_text(f"🌹 Emoji NC Started! ({len(alive)} bots)")


async def handle_ncbaap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_authorized(uid):
        return
    if not context.args:
        return await update.message.reply_text("⚠️ !ncbaap <name>")
    base = " ".join(context.args)
    cid = update.message.chat_id
    await task_mgr.stop(cid, "ncbaap")
    alive = get_alive_bots(cid)
    if not alive:
        return await update.message.reply_text("❌ No bots have admin in this chat")
    task_mgr.register_multi(cid, "ncbaap", uid, [ncbaap_loop(b, cid, base) for b in alive])
    await update.message.reply_text(f"💀🔥 NCBAAP ACTIVATED! ({len(alive)} bots)")


async def handle_nctime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_authorized(uid):
        return
    if not context.args:
        return await update.message.reply_text("⚠️ !nctime <name>")
    base = " ".join(context.args)
    cid = update.message.chat_id
    await task_mgr.stop(cid, "nctime")
    alive = get_alive_bots(cid)
    if not alive:
        return await update.message.reply_text("❌ No bots have admin in this chat")
    task_mgr.register_multi(cid, "nctime", uid, [nctime_loop(b, cid, base) for b in alive])
    await update.message.reply_text(f"🕒 Time NC Started! ({len(alive)} bots)")


async def handle_deletencgodspeed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_authorized(uid):
        return
    if not context.args:
        return await update.message.reply_text("⚠️ !deletencgodspeed <name>")
    base = " ".join(context.args)
    cid = update.message.chat_id
    await task_mgr.stop(cid, "deletencgodspeed")
    alive = get_alive_bots(cid)
    if not alive:
        return await update.message.reply_text("❌ No bots have admin in this chat")
    task_mgr.register_multi(cid, "deletencgodspeed", uid, [deletencgodspeed_loop(b, cid, base) for b in alive])
    await update.message.reply_text(f"👑🔥 GOD SPEED ACTIVATED! ({len(alive)} bots)")


async def handle_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_authorized(uid):
        return
    if not context.args:
        return await update.message.reply_text("⚠️ !spam <text>")
    text = " ".join(context.args)
    cid = update.message.chat_id
    await task_mgr.stop(cid, "spam")
    alive = get_alive_bots(cid)
    if not alive:
        return await update.message.reply_text("❌ No bots available for this chat")
    task_mgr.register_multi(cid, "spam", uid, [spam_loop(b, cid, text) for b in alive])
    await update.message.reply_text(f"💥 SPAM STARTED! ({len(alive)} bots)")


async def handle_stopspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_authorized(uid):
        return
    count = await task_mgr.stop(update.message.chat_id, "spam")
    await update.message.reply_text("🛑 Spam Stopped!" if count else "❌ No active spam")


async def handle_targetslide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_authorized(uid):
        return
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to a user's message")
    tid = update.message.reply_to_message.from_user.id
    slide_targets.add(tid)
    await update.message.reply_text(f"🎯 Slide target added: {tid}")


async def handle_slidespam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_authorized(uid):
        return
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to a user's message")
    tid = update.message.reply_to_message.from_user.id
    slidespam_targets.add(tid)
    await update.message.reply_text(f"💥 Slide spam started: {tid}")


async def handle_stopslide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_authorized(uid):
        return
    if update.message.reply_to_message:
        tid = update.message.reply_to_message.from_user.id
        a = tid in slide_targets
        b = tid in slidespam_targets
        slide_targets.discard(tid)
        slidespam_targets.discard(tid)
        await update.message.reply_text(f"🛑 Slide stopped: {tid}" if a or b else "❌ Not targeted")
    else:
        slide_targets.clear()
        slidespam_targets.clear()
        await update.message.reply_text("🛑 All slides stopped!")


async def handle_autoreply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_authorized(uid):
        return
    if not context.args or len(context.args) < 2:
        return await update.message.reply_text("⚠️ !autoreply <trigger> <reply>")
    trigger = context.args[0].lower()
    reply = " ".join(context.args[1:])
    cid = update.message.chat_id
    if cid not in autoreply_data:
        autoreply_data[cid] = {}
    autoreply_data[cid][trigger] = reply
    await update.message.reply_text(f"🤖 Auto-reply set!\nTrigger: {trigger}\nReply: {reply}")


async def handle_stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_authorized(uid):
        return
    cid = update.message.chat_id
    if context.args:
        cmd = context.args[0].lower()
        count = await task_mgr.stop(cid, cmd)
        await update.message.reply_text(f"🛑 Stopped {cmd} ({count})" if count else f"❌ No active {cmd}")
    else:
        count = await task_mgr.stop_chat(cid)
        slide_targets.clear()
        slidespam_targets.clear()
        autoreply_data.pop(cid, None)
        await update.message.reply_text(f"🛑 Stopped {count} tasks" if count else "❌ No active tasks")


async def handle_stopall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_authorized(uid):
        return
    count = await task_mgr.stop_all()
    slide_targets.clear()
    slidespam_targets.clear()
    autoreply_data.clear()
    await update.message.reply_text(f"⏹ ALL STOPPED! ({count} tasks)")


async def handle_addsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in OWNER_IDS:
        return
    if update.message.reply_to_message:
        t = update.message.reply_to_message.from_user.id
    elif context.args:
        try:
            t = int(context.args[0])
        except ValueError:
            return await update.message.reply_text("❌ Invalid ID")
    else:
        return await update.message.reply_text("⚠️ Reply or: !addsudo <id>")
    sudo_store.add(t)
    await update.message.reply_text(f"✅ SUDO added: {t}")


async def handle_delsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in OWNER_IDS:
        return
    if update.message.reply_to_message:
        t = update.message.reply_to_message.from_user.id
    elif context.args:
        try:
            t = int(context.args[0])
        except ValueError:
            return await update.message.reply_text("❌ Invalid ID")
    else:
        return await update.message.reply_text("⚠️ Reply or: !delsudo <id>")
    if t in OWNER_IDS:
        return await update.message.reply_text("❌ Cannot remove owner")
    await update.message.reply_text(f"🗑 Removed: {t}" if sudo_store.remove(t) else "❌ Not in SUDO")


async def handle_listsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    lines = [f"👑 {x}" for x in OWNER_IDS] + [f"⭐ {x}" for x in sudo_store.members]
    await update.message.reply_text("👑 Users:\n" + "\n".join(lines))


async def handle_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    s = task_mgr.summary()
    t = "\n".join(f"  {k}: {v}" for k, v in s.items())
    await update.message.reply_text(
        f"📊 Status\n🤖 Bots: {len(bots)}\n⚡ Tasks: {task_mgr.active_count()}\n"
        f"🎯 Slides: {len(slide_targets)}\n💥 SlideSpam: {len(slidespam_targets)}\n"
        f"🤖 Autoreplies: {sum(len(v) for v in autoreply_data.values())}\n"
        f"⏱ NC: {NC_SPEED}s | Spam: {SPAM_SPEED}s\n"
        + (f"\n📋 Tasks:\n{t}" if t else "")
    )


async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    await update.message.reply_text(
        "╭─────────────────────────╮\n"
        "│  ✦ 𝗗𝗘𝗟𝗘𝗧𝗘 × 𝗣𝗘𝗔𝗖𝗘 ✦  │\n"
        "╰─────────────────────────╯\n\n"
        "🔄 NC: !gcnc !ncemo !ncbaap !nctime !deletencgodspeed\n"
        "💥 SPAM: !spam !stopspam\n"
        "🎯 SLIDE: !targetslide !slidespam !stopslide\n"
        "🤖 AUTO: !autoreply <trigger> <reply>\n"
        "🛑 STOP: !stop [cmd] !stopall\n"
        "📊 INFO: !status !myid !help\n"
        "👑 SUDO: !addsudo !delsudo !listsudo"
    )


async def handle_myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🆔 {update.effective_user.id}")


async def msg_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.from_user:
        return
    uid = update.message.from_user.id
    cid = update.message.chat_id
    mid = update.message.message_id

    if uid in slide_targets and bots:
        for t in RAID_TEXTS[:3]:
            try:
                await random.choice(bots).send_message(cid, t, reply_to_message_id=mid)
            except Exception:
                pass
            await asyncio.sleep(0.05)

    if uid in slidespam_targets and bots:
        for t in RAID_TEXTS:
            try:
                await random.choice(bots).send_message(cid, t, reply_to_message_id=mid)
            except Exception:
                pass
            await asyncio.sleep(0.02)

    if update.message.text and cid in autoreply_data:
        low = update.message.text.lower()
        for trigger, reply in autoreply_data[cid].items():
            if trigger in low:
                try:
                    await random.choice(bots).send_message(cid, reply, reply_to_message_id=mid)
                except Exception:
                    pass
                break


def build_app(token: str) -> Application:
    app = Application.builder().token(token).build()
    cmds = {
        "help": handle_help, "gcnc": handle_gcnc, "ncemo": handle_ncemo,
        "ncbaap": handle_ncbaap, "nctime": handle_nctime,
        "deletencgodspeed": handle_deletencgodspeed,
        "spam": handle_spam, "stopspam": handle_stopspam,
        "targetslide": handle_targetslide, "slidespam": handle_slidespam,
        "stopslide": handle_stopslide, "autoreply": handle_autoreply,
        "stop": handle_stop, "stopall": handle_stopall,
        "addsudo": handle_addsudo, "delsudo": handle_delsudo,
        "listsudo": handle_listsudo, "status": handle_status, "myid": handle_myid,
    }
    for cmd, fn in cmds.items():
        app.add_handler(PrefixHandler("!", cmd, fn))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, msg_handler), group=1)
    return app


async def run_all_bots():
    global apps, bots
    tokens = list(dict.fromkeys(t.strip() for t in TOKENS if t.strip()))
    if not tokens:
        log.error("No tokens. Fill TOKENS list.")
        return
    for tk in tokens:
        try:
            a = build_app(tk)
            apps.append(a)
            bots.append(a.bot)
        except Exception as e:
            log.error("Load fail: %s", e)
    for a in apps:
        try:
            await a.initialize()
            await a.start()
            await a.updater.start_polling(drop_pending_updates=True, allowed_updates=["message"])
        except Exception as e:
            log.error("Start fail: %s", e)
    await task_mgr.start_cleanup_loop()
    log.info("━━ Online ━━ Bots: %d | Owners: %s | Prefix: ! ━━", len(bots), OWNER_IDS)
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(run_all_bots())
    except KeyboardInterrupt:
        log.info("Shutdown")
    except Exception as e:
        log.error("Fatal: %s", e)
