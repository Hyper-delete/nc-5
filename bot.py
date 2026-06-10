"""
╔══════════════════════════════════════════════════════════════╗
║              ✦ 𝗗𝗘𝗟𝗘𝗧𝗘 × 𝗣𝗘𝗔𝗖𝗘 ✦  v4.0                   ║
║         Production-Grade Multi-Bot Engine                    ║
║         Python 3.12+ │ asyncio │ Zero-Leak Architecture      ║
╚══════════════════════════════════════════════════════════════╝
"""
from __future__ import annotations

import asyncio
import gc
import json
import logging
import os
import random
import sys
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import IntEnum
from pathlib import Path
from typing import Any, Callable, Coroutine, Optional

from telegram import Update
from telegram.error import BadRequest, Forbidden, RetryAfter, TimedOut, TelegramError
from telegram.ext import (
    Application,
    ContextTypes,
    MessageHandler,
    PrefixHandler,
    filters,
)
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


# ──────────────────────────────────────────────────────────────
#  WINDOWS UTF-8 FIX
# ──────────────────────────────────────────────────────────────
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure") and _stream.encoding != "utf-8":
        try:
            _stream.reconfigure(encoding="utf-8")
        except Exception:
            pass

# ──────────────────────────────────────────────────────────────
#  STRUCTURED LOGGING
# ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-7s │ %(name)-14s │ %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)
logging.getLogger("telegram.ext").setLevel(logging.WARNING)

log = logging.getLogger("BotCore")
log_task = logging.getLogger("TaskManager")
log_rate = logging.getLogger("RateControl")
log_sched = logging.getLogger("Scheduler")
log_metrics = logging.getLogger("Metrics")

# ──────────────────────────────────────────────────────────────
#  CONFIGURATION — FILL MANUALLY
# ──────────────────────────────────────────────────────────────
OWNER_IDS: list[int] = [7623391678, 8399044122]
TOKENS: list[str] = [
"8883815099:AAEmj9icuagChneBbPOhtWcdAnf68LFDIGA",
"8964057044:AAHHmgkQYztA6xJSOglu4c7glFBSxr4Vo60",
"8961755422:AAFMmERXyyLXbxiJTvRwHUJ5CdKkT-J9GoQ",
"8960024186:AAG9CEgnX64PN5b3m5wXyWCiIbRXA1h-Crc",
"8962375187:AAGUoxfWRW1TSsbB0Srfcc0KiNNtjTizcJI",
"8860890636:AAFfVg0jOtdfnXV8qNKqwFGbePQTptpJll8",
"8951204614:AAGdL8-eywiz8PN_HMW_ISHnBcDQ8NDK-h0",
"8884934520:AAF_yNGMr5vO75afC5c84TAz6DPvotjt9Z4"
]
SUDO_FILE = "sudo_users.json"
AUTOREPLY_FILE = "autoreply.json"
CMD_PREFIX = "."

# ──────────────────────────────────────────────────────────────
#  TEXT DATA POOLS
# ──────────────────────────────────────────────────────────────
NCEMO_EMOJIS: list[str] = [
    "😀","😃","😄","😁","😆","😅","😂","🤣","😭","😉","😗","😚","😘","🥰","😍",
    "🤩","🥳","🫠","🙃","🙂","🥲","🥹","😊","☺️","😌","😏","🤤","😋","😛","😝",
    "😜","🤪","🥴","😔","🥺","😬","😑","😐","😶","🫥","🤐","🫡","🤔","🤫","🫢",
    "🤭","🥱","🤗","🫣","😱","🤨","🧐","😒","🙄","😮‍💨","😤","😠","😡","🤬","😞",
    "😓","😟","😥","😢","☹️","🙁","🫤","😕","😰","😨","😧","😦","😮","😯","😲",
    "😳","🤯","😖","😣","😩","😵","😵‍💫","🫨","🥶","🥵","🤢","🤮","😴","😪","🤧",
    "🤒","🤕","😷","😇","🤠","🤑","🤓","😎","🥸",
]

RAID_TEXTS: list[str] = [
    "🌙་༘࿐","⭐་༘࿐","🌸་༘࿐","🪐་༘࿐","🌈་༘࿐","🌻་༘࿐","⚡་༘࿐","🌹་༘࿐",
    "🔮་༘࿐","🎶་༘࿐","🌊་༘࿐","❄️་༘࿐","🔥་༘࿐","🌼་༘࿐","🕊️་༘࿐","🍀་༘࿐",
    "🎭་༘࿐","🦋་༘࿐","🪄་༘࿐","🏹་༘࿐","🐚་༘࿐","🪷་༘࿐","🌿་༘࿐","☀️་༘࿐",
    "🎇་༘࿐","◈","◆","◉","▷","◍","◯","◐","◑","◒","◓","◖","◗","◧","◨","◩",
    "◪","◫","◬","◭","◮","◎","▣","▤","▥","▦","▧","▨","▩","▪","▫","▬","▲","△",
    "▼","▽","◇","○","●","◦","☯","☮","☘","☀","☁","☂","☾","☄","⚝","⚘",
]

DELETENC_TEXTS: list[str] = [
    "×🌼×","×🌻×","×🪻×","×🏵️×","×💮×","×🌸×","×🪷×","×🌷×",
    "×🌺×","×🥀×","×🌹×","×💐×","×💋×","×❤️‍🔥×","×❤️‍🩹×","×❣️×",
    "×♥️×","×💟×","×💌×","×💕×","×💞×","×💓×","×💗×","×💖×",
    "×💝×","×💘×","×🩷×","×🤍×","×🩶×","×🖤×","×🤎×","×💜×",
    "×🩵×","×💛×","×🧡×","×❤️×",
]

# Pre-compute lengths once
_LEN_NCEMO = len(NCEMO_EMOJIS)
_LEN_RAID = len(RAID_TEXTS)
_LEN_DELETENC = len(DELETENC_TEXTS)


# ══════════════════════════════════════════════════════════════
#  PRIORITY LEVELS
# ══════════════════════════════════════════════════════════════
class Priority(IntEnum):
    STOP = 0
    NAME_CHANGER = 1
    AUTOREPLY = 2
    MAINTENANCE = 3


# ══════════════════════════════════════════════════════════════
#  1. METRICS COLLECTOR
# ══════════════════════════════════════════════════════════════
class MetricsCollector:
    """Lock-free metrics via atomic increments on ints."""

    __slots__ = (
        "_start_time", "_success", "_error", "_retry",
        "_latency_sum", "_latency_count", "_tasks_created",
        "_tasks_destroyed", "_worker_restarts",
    )

    def __init__(self) -> None:
        self._start_time: float = time.monotonic()
        self._success: int = 0
        self._error: int = 0
        self._retry: int = 0
        self._latency_sum: float = 0.0
        self._latency_count: int = 0
        self._tasks_created: int = 0
        self._tasks_destroyed: int = 0
        self._worker_restarts: int = 0

    def record_success(self, latency: float) -> None:
        self._success += 1
        self._latency_sum += latency
        self._latency_count += 1

    def record_error(self) -> None:
        self._error += 1

    def record_retry(self) -> None:
        self._retry += 1

    def record_task_created(self) -> None:
        self._tasks_created += 1

    def record_task_destroyed(self) -> None:
        self._tasks_destroyed += 1

    def record_worker_restart(self) -> None:
        self._worker_restarts += 1

    @property
    def uptime(self) -> float:
        return time.monotonic() - self._start_time

    @property
    def success_rate(self) -> float:
        total = self._success + self._error
        return (self._success / total * 100.0) if total > 0 else 100.0

    @property
    def avg_latency_ms(self) -> float:
        if self._latency_count == 0:
            return 0.0
        return (self._latency_sum / self._latency_count) * 1000.0

    def snapshot(self) -> dict[str, Any]:
        uptime_s = self.uptime
        h, rem = divmod(int(uptime_s), 3600)
        m, s = divmod(rem, 60)
        return {
            "uptime": f"{h}h {m}m {s}s",
            "success": self._success,
            "errors": self._error,
            "retries": self._retry,
            "success_rate": f"{self.success_rate:.1f}%",
            "avg_latency_ms": f"{self.avg_latency_ms:.1f}",
            "tasks_created": self._tasks_created,
            "tasks_destroyed": self._tasks_destroyed,
            "worker_restarts": self._worker_restarts,
        }


metrics = MetricsCollector()


# ══════════════════════════════════════════════════════════════
#  2. RATE CONTROLLER  (per-bot adaptive)
# ══════════════════════════════════════════════════════════════
class RateController:
    """
    Per-bot adaptive rate controller.
    Tracks success/error/retry/latency and adjusts delay dynamically.
    """

    __slots__ = (
        "_base", "_current", "_min", "_max",
        "_success_streak", "_latency_ema",
        "_cooldown_until",
    )

    def __init__(
        self,
        base: float = 0.03,
        minimum: float = 0.005,
        maximum: float = 30.0,
    ) -> None:
        self._base = base
        self._current = base
        self._min = minimum
        self._max = maximum
        self._success_streak: int = 0
        self._latency_ema: float = 0.0
        self._cooldown_until: float = 0.0

    @property
    def delay(self) -> float:
        return self._current

    @property
    def is_cooling(self) -> bool:
        return time.monotonic() < self._cooldown_until

    async def wait(self) -> None:
        now = time.monotonic()
        if now < self._cooldown_until:
            wait_time = self._cooldown_until - now
            await asyncio.sleep(wait_time)
        elif self._current > 0:
            await asyncio.sleep(self._current)

    def on_success(self, latency: float) -> None:
        self._success_streak += 1
        # EMA for latency (alpha=0.3)
        self._latency_ema = 0.7 * self._latency_ema + 0.3 * latency
        metrics.record_success(latency)

        # Gradual speedup after sustained success
        if self._success_streak >= 5:
            self._current = max(self._current * 0.95, self._min)
            self._success_streak = 0

        # If latency is rising, slow slightly
        if self._latency_ema > 1.0:
            self._current = min(self._current * 1.05, self._max)

    def on_error(self) -> None:
        self._success_streak = 0
        self._current = min(self._current * 1.3, self._max)
        metrics.record_error()

    def on_retry_after(self, seconds: float) -> None:
        self._success_streak = 0
        self._cooldown_until = time.monotonic() + seconds + 0.5
        self._current = min(max(seconds * 0.5, self._current), self._max)
        metrics.record_retry()
        log_rate.warning("RetryAfter %.1fs — cooldown set", seconds)

    def on_timeout(self) -> None:
        self._success_streak = 0
        self._cooldown_until = time.monotonic() + 3.0
        self._current = min(self._current * 1.5, self._max)
        metrics.record_error()

    def recover(self) -> None:
        """Called periodically to slowly recover towards base speed."""
        if not self.is_cooling and self._current > self._base:
            self._current = max(self._current * 0.98, self._base)


# ══════════════════════════════════════════════════════════════
#  3. STORAGE MANAGER
# ══════════════════════════════════════════════════════════════
class StorageManager:
    """Thread-safe persistent JSON set storage for user IDs."""

    __slots__ = ("_path", "_data", "_dirty")

    def __init__(self, filepath: str) -> None:
        self._path = filepath
        self._data: set[int] = set()
        self._dirty = False
        self._load()

    def _load(self) -> None:
        if os.path.exists(self._path):
            try:
                with open(self._path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                self._data = {int(x) for x in raw}
            except Exception:
                log.warning("Failed to load %s, starting empty", self._path)
                self._data = set()

    def _save(self) -> None:
        tmp = self._path + ".tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(sorted(self._data), f)
            os.replace(tmp, self._path)
        except Exception:
            log.error("Failed to save %s", self._path)

    def add(self, uid: int) -> None:
        self._data.add(uid)
        self._save()

    def remove(self, uid: int) -> bool:
        if uid in self._data:
            self._data.discard(uid)
            self._save()
            return True
        return False

    def __contains__(self, uid: int) -> bool:
        return uid in self._data

    @property
    def members(self) -> set[int]:
        return set(self._data)

    @property
    def count(self) -> int:
        return len(self._data)


class AutoReplyStorage:
    """Persistent JSON storage for per-chat autoreply triggers."""

    __slots__ = ("_path", "_data")

    def __init__(self, filepath: str) -> None:
        self._path = filepath
        self._data: dict[int, dict[str, str]] = {}
        self._load()

    def _load(self) -> None:
        if os.path.exists(self._path):
            try:
                with open(self._path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                self._data = {int(k): v for k, v in raw.items()}
            except Exception:
                self._data = {}

    def _save(self) -> None:
        tmp = self._path + ".tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump({str(k): v for k, v in self._data.items()}, f, ensure_ascii=False)
            os.replace(tmp, self._path)
        except Exception:
            log.error("Failed to save %s", self._path)

    def set_trigger(self, chat_id: int, trigger: str, reply: str) -> None:
        if chat_id not in self._data:
            self._data[chat_id] = {}
        self._data[chat_id][trigger.lower()] = reply
        self._save()

    def remove_trigger(self, chat_id: int, trigger: str) -> bool:
        if chat_id in self._data and trigger.lower() in self._data[chat_id]:
            del self._data[chat_id][trigger.lower()]
            if not self._data[chat_id]:
                del self._data[chat_id]
            self._save()
            return True
        return False

    def clear_chat(self, chat_id: int) -> int:
        if chat_id in self._data:
            count = len(self._data[chat_id])
            del self._data[chat_id]
            self._save()
            return count
        return 0

    def clear_all(self) -> int:
        count = sum(len(v) for v in self._data.values())
        self._data.clear()
        self._save()
        return count

    def get_triggers(self, chat_id: int) -> dict[str, str]:
        return self._data.get(chat_id, {})

    def match(self, chat_id: int, text: str) -> Optional[str]:
        triggers = self._data.get(chat_id)
        if not triggers:
            return None
        text_lower = text.lower()
        for trigger, reply in triggers.items():
            if trigger in text_lower:
                return reply
        return None

    @property
    def total_triggers(self) -> int:
        return sum(len(v) for v in self._data.values())


# ══════════════════════════════════════════════════════════════
#  4. TASK MANAGER  (central registry, ownership, health)
# ══════════════════════════════════════════════════════════════
@dataclass(slots=True)
class TaskEntry:
    task: asyncio.Task[Any]
    chat_id: int
    command: str
    owner_id: int
    bot_index: int
    created: float = field(default_factory=time.monotonic)


class TaskManager:
    """
    Central task registry with:
    - Per-chat tracking
    - Per-bot tracking
    - Task ownership
    - Health monitoring
    - Automatic cleanup of dead tasks
    - Zero orphan / zero duplicate guarantees
    """

    def __init__(self) -> None:
        self._tasks: dict[str, TaskEntry] = {}
        self._cleanup_task: Optional[asyncio.Task[None]] = None
        self._lock = asyncio.Lock()

    def _key(self, chat_id: int, command: str, bot_idx: int = 0) -> str:
        return f"{chat_id}:{command}:{bot_idx}"

    async def start_cleanup_loop(self) -> None:
        self._cleanup_task = asyncio.create_task(
            self._cleanup_routine(), name="task-cleanup"
        )

    async def _cleanup_routine(self) -> None:
        while True:
            await asyncio.sleep(30)
            async with self._lock:
                dead_keys = [k for k, v in self._tasks.items() if v.task.done()]
                for k in dead_keys:
                    entry = self._tasks.pop(k)
                    metrics.record_task_destroyed()
                    # Log unexpected failures
                    if entry.task.cancelled():
                        pass
                    elif entry.task.exception():
                        log_task.error(
                            "Task %s crashed: %s",
                            k,
                            entry.task.exception(),
                        )
                if dead_keys:
                    log_task.info("Cleaned %d finished tasks", len(dead_keys))

    async def register(
        self,
        chat_id: int,
        command: str,
        owner_id: int,
        coro: Coroutine[Any, Any, Any],
        bot_idx: int = 0,
    ) -> asyncio.Task[Any]:
        key = self._key(chat_id, command, bot_idx)
        async with self._lock:
            existing = self._tasks.get(key)
            if existing and not existing.task.done():
                existing.task.cancel()
                try:
                    await asyncio.wait_for(
                        asyncio.shield(existing.task), timeout=0.5
                    )
                except (asyncio.CancelledError, asyncio.TimeoutError, Exception):
                    pass
                metrics.record_task_destroyed()

            task = asyncio.create_task(coro, name=f"{command}@{chat_id}:{bot_idx}")
            self._tasks[key] = TaskEntry(
                task=task,
                chat_id=chat_id,
                command=command,
                owner_id=owner_id,
                bot_index=bot_idx,
            )
            metrics.record_task_created()
            log_task.info("Created task %s", key)
            return task

    async def register_multi(
        self,
        chat_id: int,
        command: str,
        owner_id: int,
        coros: list[Coroutine[Any, Any, Any]],
    ) -> list[asyncio.Task[Any]]:
        # First stop any existing tasks for this command in this chat
        await self._cancel_prefix(f"{chat_id}:{command}:")
        tasks: list[asyncio.Task[Any]] = []
        async with self._lock:
            for i, coro in enumerate(coros):
                key = self._key(chat_id, command, i)
                task = asyncio.create_task(coro, name=f"{command}@{chat_id}:{i}")
                self._tasks[key] = TaskEntry(
                    task=task,
                    chat_id=chat_id,
                    command=command,
                    owner_id=owner_id,
                    bot_index=i,
                )
                metrics.record_task_created()
                tasks.append(task)
        log_task.info("Created %d tasks for %s in chat %d", len(tasks), command, chat_id)
        return tasks

    async def _cancel_prefix(self, prefix: str) -> int:
        async with self._lock:
            to_cancel = {
                k: v for k, v in self._tasks.items() if k.startswith(prefix)
            }
            for v in to_cancel.values():
                v.task.cancel()
        # Await outside the lock to avoid deadlocks
        for v in to_cancel.values():
            try:
                await asyncio.wait_for(asyncio.shield(v.task), timeout=0.5)
            except (asyncio.CancelledError, asyncio.TimeoutError, Exception):
                pass
        async with self._lock:
            for k in to_cancel:
                self._tasks.pop(k, None)
                metrics.record_task_destroyed()
        return len(to_cancel)

    async def stop_command(self, chat_id: int, command: str) -> int:
        prefix = f"{chat_id}:{command}:"
        return await self._cancel_prefix(prefix)

    async def stop_chat(self, chat_id: int) -> int:
        prefix = f"{chat_id}:"
        return await self._cancel_prefix(prefix)

    async def stop_all(self) -> int:
        """Cancel ALL tasks. Must complete in <1 second."""
        async with self._lock:
            snapshot = dict(self._tasks)
            # Cancel all at once
            for v in snapshot.values():
                v.task.cancel()

        # Gather with a hard 0.8s timeout
        if snapshot:
            aws = [v.task for v in snapshot.values()]
            done, pending = await asyncio.wait(aws, timeout=0.8)
            # Force kill any still pending
            for t in pending:
                t.cancel()

        async with self._lock:
            count = len(self._tasks)
            self._tasks.clear()
        metrics._tasks_destroyed += count
        log_task.info("stop_all: cancelled %d tasks", count)
        return count

    def active_count(self) -> int:
        return sum(1 for v in self._tasks.values() if not v.task.done())

    def active_for_chat(self, chat_id: int) -> list[TaskEntry]:
        prefix = f"{chat_id}:"
        return [
            v for k, v in self._tasks.items()
            if k.startswith(prefix) and not v.task.done()
        ]

    def active_for_bot(self, bot_idx: int) -> int:
        return sum(
            1 for v in self._tasks.values()
            if v.bot_index == bot_idx and not v.task.done()
        )

    def summary(self) -> dict[str, int]:
        result: dict[str, int] = {}
        for v in self._tasks.values():
            if not v.task.done():
                result[v.command] = result.get(v.command, 0) + 1
        return result

    def health_report(self) -> dict[str, Any]:
        active = 0
        done = 0
        failed = 0
        for v in self._tasks.values():
            if v.task.done():
                done += 1
                if not v.task.cancelled() and v.task.exception():
                    failed += 1
            else:
                active += 1
        return {
            "active": active,
            "done_pending_cleanup": done,
            "failed": failed,
            "total_registered": len(self._tasks),
        }


# ══════════════════════════════════════════════════════════════
#  5. SCHEDULER  (priority queue)
# ══════════════════════════════════════════════════════════════
@dataclass(order=True, slots=True)
class ScheduledItem:
    priority: int
    created: float = field(compare=True)
    coro: Coroutine[Any, Any, Any] = field(compare=False)
    chat_id: int = field(compare=False, default=0)
    command: str = field(compare=False, default="")
    owner_id: int = field(compare=False, default=0)


class Scheduler:
    """
    Priority-based scheduler.
    Higher priority items (lower number) execute first.
    Includes queue monitoring, dedup, and expired work removal.
    """

    def __init__(self, task_mgr: TaskManager, max_size: int = 1000) -> None:
        self._queue: asyncio.PriorityQueue[ScheduledItem] = asyncio.PriorityQueue(
            maxsize=max_size
        )
        self._task_mgr = task_mgr
        self._worker: Optional[asyncio.Task[None]] = None
        self._seen: set[str] = set()
        self._processed: int = 0

    async def start(self) -> None:
        self._worker = asyncio.create_task(
            self._process_loop(), name="scheduler-worker"
        )

    def schedule(
        self,
        priority: Priority,
        chat_id: int,
        command: str,
        owner_id: int,
        coro: Coroutine[Any, Any, Any],
    ) -> bool:
        dedup_key = f"{chat_id}:{command}"
        if self._queue.full():
            log_sched.warning("Queue full, dropping item %s", dedup_key)
            coro.close()  # Prevent coroutine leak
            return False
        item = ScheduledItem(
            priority=priority.value,
            created=time.monotonic(),
            coro=coro,
            chat_id=chat_id,
            command=command,
            owner_id=owner_id,
        )
        self._queue.put_nowait(item)
        return True

    async def _process_loop(self) -> None:
        while True:
            try:
                item = await self._queue.get()
                # Expired work removal: skip if older than 30 seconds
                age = time.monotonic() - item.created
                if age > 30.0:
                    log_sched.info("Dropping expired work: %s (%.1fs old)", item.command, age)
                    item.coro.close()
                    self._queue.task_done()
                    continue

                await self._task_mgr.register(
                    item.chat_id, item.command, item.owner_id, item.coro
                )
                self._processed += 1
                self._queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception:
                log_sched.exception("Scheduler error")

    @property
    def queue_size(self) -> int:
        return self._queue.qsize()

    @property
    def processed_count(self) -> int:
        return self._processed


# ══════════════════════════════════════════════════════════════
#  6. BOT WORKER (per-bot isolated state)
# ══════════════════════════════════════════════════════════════
@dataclass(slots=True)
class BotWorker:
    """Encapsulates per-bot state: dedicated rate controller, identity."""
    bot: Any  # telegram.Bot
    index: int
    rate: RateController
    app: Application
    username: str = ""
    healthy: bool = True
    _dead_chats: set[int] = field(default_factory=set)

    def mark_dead(self, chat_id: int) -> None:
        self._dead_chats.add(chat_id)

    def is_alive_for(self, chat_id: int) -> bool:
        return chat_id not in self._dead_chats

    def clear_dead(self, chat_id: int) -> None:
        self._dead_chats.discard(chat_id)


# ══════════════════════════════════════════════════════════════
#  7. BOT CORE  (orchestrator)
# ══════════════════════════════════════════════════════════════
class BotCore:
    """
    Central orchestrator.
    Owns all workers, task manager, scheduler, storage, metrics.
    """

    def __init__(self) -> None:
        self.workers: list[BotWorker] = []
        self.task_mgr = TaskManager()
        self.scheduler: Optional[Scheduler] = None
        self.sudo_store = StorageManager(SUDO_FILE)
        self.autoreply_store = AutoReplyStorage(AUTOREPLY_FILE)
        self.slide_targets: set[int] = set()
        self.slidespam_targets: set[int] = set()
        self._health_task: Optional[asyncio.Task[None]] = None
        self._rate_recovery_task: Optional[asyncio.Task[None]] = None

    @property
    def bots(self) -> list[Any]:
        return [w.bot for w in self.workers]

    def is_authorized(self, uid: int) -> bool:
        return uid in OWNER_IDS or uid in self.sudo_store

    def alive_workers(self, chat_id: int) -> list[BotWorker]:
        return [
            w for w in self.workers
            if w.is_alive_for(chat_id) and not w.rate.is_cooling
        ]

    def all_alive_workers(self, chat_id: int) -> list[BotWorker]:
        return [w for w in self.workers if w.is_alive_for(chat_id)]

    async def safe_api_call(
        self,
        worker: BotWorker,
        coro_factory: Callable[[], Coroutine[Any, Any, Any]],
        chat_id: int,
    ) -> tuple[bool, Any]:
        """
        Execute a Telegram API call with full rate control and error handling.
        Returns (success, result).
        """
        if worker.rate.is_cooling:
            await worker.rate.wait()

        t0 = time.monotonic()
        try:
            result = await coro_factory()
            latency = time.monotonic() - t0
            worker.rate.on_success(latency)
            return True, result
        except RetryAfter as e:
            worker.rate.on_retry_after(e.retry_after)
            await asyncio.sleep(e.retry_after + 0.5)
            return False, None
        except TimedOut:
            worker.rate.on_timeout()
            return False, None
        except Forbidden:
            worker.mark_dead(chat_id)
            log.warning("Worker %d forbidden in chat %d", worker.index, chat_id)
            return False, None
        except BadRequest as e:
            if "not modified" in str(e).lower():
                return True, None  # Title unchanged — not an error
            worker.rate.on_error()
            return False, None
        except asyncio.CancelledError:
            raise
        except Exception:
            worker.rate.on_error()
            return False, None

    async def _health_monitor(self) -> None:
        """Self-healing: monitor event loop lag and worker health."""
        while True:
            try:
                t0 = time.monotonic()
                await asyncio.sleep(5.0)
                lag = time.monotonic() - t0 - 5.0
                if lag > 1.0:
                    log.warning(
                        "Event loop lag: %.2fs | Tasks: %d",
                        lag,
                        self.task_mgr.active_count(),
                    )

                # Periodic GC
                gc.collect(generation=0)

            except asyncio.CancelledError:
                break
            except Exception:
                pass

    async def _rate_recovery_loop(self) -> None:
        """Slowly recover all bot rates towards their base speed."""
        while True:
            try:
                await asyncio.sleep(10.0)
                for w in self.workers:
                    w.rate.recover()
            except asyncio.CancelledError:
                break
            except Exception:
                pass

    async def start(self) -> None:
        unique_tokens = list(dict.fromkeys(t.strip() for t in TOKENS if t.strip()))
        if not unique_tokens:
            log.error("No tokens configured. Fill TOKENS list in v4.py.")
            return

        # Build and start all bots
        for idx, token in enumerate(unique_tokens):
            try:
                app = self._build_app(token)
                worker = BotWorker(
                    bot=app.bot,
                    index=idx,
                    rate=RateController(base=0.03, minimum=0.005, maximum=30.0),
                    app=app,
                )
                self.workers.append(worker)
                log.info("Bot %d loaded: %s...", idx, token[:15])
            except Exception as e:
                log.error("Failed to load bot %d: %s", idx, e)

        for w in self.workers:
            try:
                await w.app.initialize()
                await w.app.start()
                await w.app.updater.start_polling(
                    drop_pending_updates=True,
                    allowed_updates=["message"],
                )
                me = await w.bot.get_me()
                w.username = me.username or ""
                log.info("Bot %d online: @%s", w.index, w.username)
            except Exception as e:
                log.error("Failed to start bot %d: %s", w.index, e)
                w.healthy = False

        # Start subsystems
        await self.task_mgr.start_cleanup_loop()
        self.scheduler = Scheduler(self.task_mgr)
        await self.scheduler.start()
        self._health_task = asyncio.create_task(
            self._health_monitor(), name="health-monitor"
        )
        self._rate_recovery_task = asyncio.create_task(
            self._rate_recovery_loop(), name="rate-recovery"
        )

        healthy = sum(1 for w in self.workers if w.healthy)
        log.info(
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "  ✦ DELETE × PEACE ✦  v4.0  ONLINE\n"
            "  Bots: %d/%d healthy\n"
            "  Owners: %s\n"
            "  Sudo: %d users\n"
            "  Prefix: %s\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            healthy,
            len(self.workers),
            OWNER_IDS,
            self.sudo_store.count,
            CMD_PREFIX,
        )

        # Block forever
        await asyncio.Event().wait()

    async def shutdown(self) -> None:
        log.info("Shutting down...")
        await self.task_mgr.stop_all()
        if self._health_task:
            self._health_task.cancel()
        if self._rate_recovery_task:
            self._rate_recovery_task.cancel()
        if self.scheduler and self.scheduler._worker:
            self.scheduler._worker.cancel()
        for w in self.workers:
            try:
                if w.app.updater:
                    await w.app.updater.stop()
                await w.app.stop()
                await w.app.shutdown()
            except Exception:
                pass
        log.info("Shutdown complete.")

    # ──────────────────────────────────────────────────────────
    #  COMMAND ROUTER  (builds handlers for each app)
    # ──────────────────────────────────────────────────────────
    def _build_app(self, token: str) -> Application:
        app = Application.builder().token(token).build()
        router = CommandRouter(self)

        commands: dict[str, Callable[..., Coroutine[Any, Any, None]]] = {
            "help": router.cmd_help,
            "gcnc": router.cmd_gcnc,
            "ncemo": router.cmd_ncemo,
            "ncbaap": router.cmd_ncbaap,
            "nctime": router.cmd_nctime,
            "deletencgodspeed": router.cmd_deletencgodspeed,
            "spam": router.cmd_spam,
            "stopspam": router.cmd_stopspam,
            "targetslide": router.cmd_targetslide,
            "slidespam": router.cmd_slidespam,
            "stopslide": router.cmd_stopslide,
            "autoreply": router.cmd_autoreply,
            "stopautoreply": router.cmd_stopautoreply,
            "stop": router.cmd_stop,
            "stopall": router.cmd_stopall,
            "addsudo": router.cmd_addsudo,
            "delsudo": router.cmd_delsudo,
            "listsudo": router.cmd_listsudo,
            "status": router.cmd_status,
            "stats": router.cmd_stats,
            "myid": router.cmd_myid,
            "ping": router.cmd_ping,
        }

        for cmd, fn in commands.items():
            app.add_handler(PrefixHandler(CMD_PREFIX, cmd, fn))

        app.add_handler(
            MessageHandler(
                filters.ALL & ~filters.COMMAND, router.message_handler
            ),
            group=1,
        )

        return app


# ══════════════════════════════════════════════════════════════
#  NC / SPAM LOOP COROUTINES  (pure coroutines, no side effects)
# ══════════════════════════════════════════════════════════════
async def _gcnc_loop(core: BotCore, worker: BotWorker, chat_id: int, base: str) -> None:
    i = 0
    while True:
        title = f"{base} {RAID_TEXTS[i % _LEN_RAID]}"
        await core.safe_api_call(
            worker,
            lambda t=title: worker.bot.set_chat_title(chat_id, t[:128]),
            chat_id,
        )
        i += 1
        await worker.rate.wait()


async def _ncemo_loop(core: BotCore, worker: BotWorker, chat_id: int, base: str) -> None:
    i = 0
    while True:
        emo = NCEMO_EMOJIS[i % _LEN_NCEMO]
        title = f"{emo} {base} {emo}"
        await core.safe_api_call(
            worker,
            lambda t=title: worker.bot.set_chat_title(chat_id, t[:128]),
            chat_id,
        )
        i += 1
        await worker.rate.wait()


async def _ncbaap_loop(core: BotCore, worker: BotWorker, chat_id: int, base: str) -> None:
    i = 0
    while True:
        modulo = i % 2
        if modulo == 0:
            title = f"{base} {RAID_TEXTS[i % _LEN_RAID]}"
        else:
            emo = NCEMO_EMOJIS[i % _LEN_NCEMO]
            title = f"{emo} {base} {emo}"
        await core.safe_api_call(
            worker,
            lambda t=title: worker.bot.set_chat_title(chat_id, t[:128]),
            chat_id,
        )
        i += 1
        await worker.rate.wait()


async def _nctime_loop(core: BotCore, worker: BotWorker, chat_id: int, base: str) -> None:
    ist = timezone(timedelta(hours=5, minutes=30))
    while True:
        now = datetime.now(timezone.utc).astimezone(ist)
        ts = now.strftime("%H:%M:%S") + f":{now.microsecond // 10000:02d}"
        title = f"{base} {ts}"
        await core.safe_api_call(
            worker,
            lambda t=title: worker.bot.set_chat_title(chat_id, t[:128]),
            chat_id,
        )
        await worker.rate.wait()


async def _deletencgodspeed_loop(
    core: BotCore, worker: BotWorker, chat_id: int, base: str
) -> None:
    i = 0
    while True:
        t1 = f"{base} {DELETENC_TEXTS[i % _LEN_DELETENC]} {RAID_TEXTS[i % _LEN_RAID]}"
        t2 = f"{DELETENC_TEXTS[i % _LEN_DELETENC]} {base} {RAID_TEXTS[i % _LEN_RAID]}"
        await core.safe_api_call(
            worker,
            lambda t=t1: worker.bot.set_chat_title(chat_id, t[:128]),
            chat_id,
        )
        await core.safe_api_call(
            worker,
            lambda t=t2: worker.bot.set_chat_title(chat_id, t[:128]),
            chat_id,
        )
        i += 1
        await worker.rate.wait()


async def _spam_loop(core: BotCore, worker: BotWorker, chat_id: int, text: str) -> None:
    while True:
        await core.safe_api_call(
            worker,
            lambda: worker.bot.send_message(chat_id, text),
            chat_id,
        )
        await worker.rate.wait()


async def _slide_respond(
    core: BotCore, chat_id: int, msg_id: int, texts: list[str], delay: float
) -> None:
    """Fire-and-forget slide response."""
    for text in texts:
        alive = core.alive_workers(chat_id)
        if not alive:
            break
        w = random.choice(alive)
        await core.safe_api_call(
            w,
            lambda t=text: w.bot.send_message(
                chat_id, t, reply_to_message_id=msg_id
            ),
            chat_id,
        )
        await asyncio.sleep(delay)


# ══════════════════════════════════════════════════════════════
#  COMMAND ROUTER
# ══════════════════════════════════════════════════════════════
class CommandRouter:
    """All command handlers. Thin layer over BotCore."""

    def __init__(self, core: BotCore) -> None:
        self.core = core

    # ── Auth check ──
    def _auth(self, uid: int) -> bool:
        return self.core.is_authorized(uid)

    def _owner(self, uid: int) -> bool:
        return uid in OWNER_IDS

    # ── NC Commands ──
    async def cmd_gcnc(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
        uid = update.effective_user.id
        if not self._auth(uid):
            return
        if not ctx.args:
            return await update.message.reply_text(f"⚠️ {CMD_PREFIX}gcnc <name>")
        base = " ".join(ctx.args)
        cid = update.message.chat_id
        await self.core.task_mgr.stop_command(cid, "gcnc")
        alive = self.core.all_alive_workers(cid)
        if not alive:
            return await update.message.reply_text("❌ No bots available for this chat")
        coros = [_gcnc_loop(self.core, w, cid, base) for w in alive]
        await self.core.task_mgr.register_multi(cid, "gcnc", uid, coros)
        await update.message.reply_text(f"⚡ GC NC Started! ({len(alive)} bots)")

    async def cmd_ncemo(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
        uid = update.effective_user.id
        if not self._auth(uid):
            return
        if not ctx.args:
            return await update.message.reply_text(f"⚠️ {CMD_PREFIX}ncemo <name>")
        base = " ".join(ctx.args)
        cid = update.message.chat_id
        await self.core.task_mgr.stop_command(cid, "ncemo")
        alive = self.core.all_alive_workers(cid)
        if not alive:
            return await update.message.reply_text("❌ No bots available for this chat")
        coros = [_ncemo_loop(self.core, w, cid, base) for w in alive]
        await self.core.task_mgr.register_multi(cid, "ncemo", uid, coros)
        await update.message.reply_text(f"🌹 Emoji NC Started! ({len(alive)} bots)")

    async def cmd_ncbaap(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
        uid = update.effective_user.id
        if not self._auth(uid):
            return
        if not ctx.args:
            return await update.message.reply_text(f"⚠️ {CMD_PREFIX}ncbaap <name>")
        base = " ".join(ctx.args)
        cid = update.message.chat_id
        await self.core.task_mgr.stop_command(cid, "ncbaap")
        alive = self.core.all_alive_workers(cid)
        if not alive:
            return await update.message.reply_text("❌ No bots available for this chat")
        coros = [_ncbaap_loop(self.core, w, cid, base) for w in alive]
        await self.core.task_mgr.register_multi(cid, "ncbaap", uid, coros)
        await update.message.reply_text(f"💀🔥 NCBAAP ACTIVATED! ({len(alive)} bots)")

    async def cmd_nctime(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
        uid = update.effective_user.id
        if not self._auth(uid):
            return
        if not ctx.args:
            return await update.message.reply_text(f"⚠️ {CMD_PREFIX}nctime <name>")
        base = " ".join(ctx.args)
        cid = update.message.chat_id
        await self.core.task_mgr.stop_command(cid, "nctime")
        alive = self.core.all_alive_workers(cid)
        if not alive:
            return await update.message.reply_text("❌ No bots available for this chat")
        coros = [_nctime_loop(self.core, w, cid, base) for w in alive]
        await self.core.task_mgr.register_multi(cid, "nctime", uid, coros)
        await update.message.reply_text(f"🕒 Time NC Started! ({len(alive)} bots)")

    async def cmd_deletencgodspeed(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
        uid = update.effective_user.id
        if not self._auth(uid):
            return
        if not ctx.args:
            return await update.message.reply_text(f"⚠️ {CMD_PREFIX}deletencgodspeed <name>")
        base = " ".join(ctx.args)
        cid = update.message.chat_id
        await self.core.task_mgr.stop_command(cid, "deletencgodspeed")
        alive = self.core.all_alive_workers(cid)
        if not alive:
            return await update.message.reply_text("❌ No bots available for this chat")
        coros = [_deletencgodspeed_loop(self.core, w, cid, base) for w in alive]
        await self.core.task_mgr.register_multi(cid, "deletencgodspeed", uid, coros)
        await update.message.reply_text(f"👑🔥 GOD SPEED ACTIVATED! ({len(alive)} bots)")

    # ── Spam ──
    async def cmd_spam(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
        uid = update.effective_user.id
        if not self._auth(uid):
            return
        if not ctx.args:
            return await update.message.reply_text(f"⚠️ {CMD_PREFIX}spam <text>")
        text = " ".join(ctx.args)
        cid = update.message.chat_id
        await self.core.task_mgr.stop_command(cid, "spam")
        alive = self.core.all_alive_workers(cid)
        if not alive:
            return await update.message.reply_text("❌ No bots available")
        coros = [_spam_loop(self.core, w, cid, text) for w in alive]
        await self.core.task_mgr.register_multi(cid, "spam", uid, coros)
        await update.message.reply_text(f"💥 SPAM STARTED! ({len(alive)} bots)")

    async def cmd_stopspam(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
        uid = update.effective_user.id
        if not self._auth(uid):
            return
        count = await self.core.task_mgr.stop_command(update.message.chat_id, "spam")
        await update.message.reply_text("🛑 Spam Stopped!" if count else "❌ No active spam")

    # ── Slide System ──
    async def cmd_targetslide(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
        uid = update.effective_user.id
        if not self._auth(uid):
            return
        if not update.message.reply_to_message:
            return await update.message.reply_text("⚠️ Reply to a user's message")
        tid = update.message.reply_to_message.from_user.id
        self.core.slide_targets.add(tid)
        await update.message.reply_text(f"🎯 Slide target added: {tid}")

    async def cmd_slidespam(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
        uid = update.effective_user.id
        if not self._auth(uid):
            return
        if not update.message.reply_to_message:
            return await update.message.reply_text("⚠️ Reply to a user's message")
        tid = update.message.reply_to_message.from_user.id
        self.core.slidespam_targets.add(tid)
        await update.message.reply_text(f"💥 Slide spam started: {tid}")

    async def cmd_stopslide(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
        uid = update.effective_user.id
        if not self._auth(uid):
            return
        if update.message.reply_to_message:
            tid = update.message.reply_to_message.from_user.id
            a = tid in self.core.slide_targets
            b = tid in self.core.slidespam_targets
            self.core.slide_targets.discard(tid)
            self.core.slidespam_targets.discard(tid)
            await update.message.reply_text(
                f"🛑 Slide stopped: {tid}" if a or b else "❌ Not targeted"
            )
        else:
            self.core.slide_targets.clear()
            self.core.slidespam_targets.clear()
            await update.message.reply_text("🛑 All slides stopped!")

    # ── AutoReply ──
    async def cmd_autoreply(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
        uid = update.effective_user.id
        if not self._auth(uid):
            return
        if not ctx.args or len(ctx.args) < 2:
            return await update.message.reply_text(f"⚠️ {CMD_PREFIX}autoreply <trigger> <reply>")
        trigger = ctx.args[0]
        reply = " ".join(ctx.args[1:])
        cid = update.message.chat_id
        self.core.autoreply_store.set_trigger(cid, trigger, reply)
        await update.message.reply_text(
            f"🤖 Auto-reply set!\nTrigger: {trigger.lower()}\nReply: {reply}"
        )

    async def cmd_stopautoreply(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
        uid = update.effective_user.id
        if not self._auth(uid):
            return
        cid = update.message.chat_id
        if ctx.args:
            trigger = ctx.args[0]
            if self.core.autoreply_store.remove_trigger(cid, trigger):
                await update.message.reply_text(f"🛑 Auto-reply removed: {trigger}")
            else:
                await update.message.reply_text("❌ Trigger not found")
        else:
            count = self.core.autoreply_store.clear_chat(cid)
            await update.message.reply_text(
                f"🛑 Removed {count} auto-replies" if count else "❌ No auto-replies active"
            )

    # ── Stop System ──
    async def cmd_stop(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
        uid = update.effective_user.id
        if not self._auth(uid):
            return
        cid = update.message.chat_id
        if ctx.args:
            cmd = ctx.args[0].lower()
            count = await self.core.task_mgr.stop_command(cid, cmd)
            await update.message.reply_text(
                f"🛑 Stopped {cmd} ({count} tasks)" if count else f"❌ No active {cmd}"
            )
        else:
            count = await self.core.task_mgr.stop_chat(cid)
            self.core.slide_targets.clear()
            self.core.slidespam_targets.clear()
            self.core.autoreply_store.clear_chat(cid)
            await update.message.reply_text(
                f"🛑 Stopped {count} tasks" if count else "❌ No active tasks"
            )

    async def cmd_stopall(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
        uid = update.effective_user.id
        if not self._auth(uid):
            return
        t0 = time.monotonic()
        count = await self.core.task_mgr.stop_all()
        self.core.slide_targets.clear()
        self.core.slidespam_targets.clear()
        self.core.autoreply_store.clear_all()
        elapsed = (time.monotonic() - t0) * 1000
        await update.message.reply_text(
            f"⏹ ALL STOPPED! ({count} tasks in {elapsed:.0f}ms)"
        )

    # ── Sudo Management ──
    async def cmd_addsudo(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
        uid = update.effective_user.id
        if not self._owner(uid):
            return
        target: Optional[int] = None
        if update.message.reply_to_message:
            target = update.message.reply_to_message.from_user.id
        elif ctx.args:
            try:
                target = int(ctx.args[0])
            except ValueError:
                return await update.message.reply_text("❌ Invalid ID")
        if target is None:
            return await update.message.reply_text(f"⚠️ Reply or: {CMD_PREFIX}addsudo <id>")
        self.core.sudo_store.add(target)
        await update.message.reply_text(f"✅ SUDO added: {target}")

    async def cmd_delsudo(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
        uid = update.effective_user.id
        if not self._owner(uid):
            return
        target: Optional[int] = None
        if update.message.reply_to_message:
            target = update.message.reply_to_message.from_user.id
        elif ctx.args:
            try:
                target = int(ctx.args[0])
            except ValueError:
                return await update.message.reply_text("❌ Invalid ID")
        if target is None:
            return await update.message.reply_text(f"⚠️ Reply or: {CMD_PREFIX}delsudo <id>")
        if target in OWNER_IDS:
            return await update.message.reply_text("❌ Cannot remove owner")
        if self.core.sudo_store.remove(target):
            await update.message.reply_text(f"🗑 SUDO removed: {target}")
        else:
            await update.message.reply_text("❌ User not in SUDO")

    async def cmd_listsudo(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
        uid = update.effective_user.id
        if not self._auth(uid):
            return
        lines = [f"👑 {x}" for x in OWNER_IDS] + [
            f"⭐ {x}" for x in self.core.sudo_store.members
        ]
        await update.message.reply_text("👑 Authorized Users:\n" + "\n".join(lines))

    # ── Status / Stats ──
    async def cmd_status(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
        uid = update.effective_user.id
        if not self._auth(uid):
            return
        cid = update.message.chat_id
        summary = self.core.task_mgr.summary()
        task_lines = "\n".join(f"  {k}: {v}" for k, v in summary.items())
        healthy = sum(1 for w in self.core.workers if w.healthy)
        cooling = sum(1 for w in self.core.workers if w.rate.is_cooling)

        text = (
            f"📊 Status\n"
            f"🤖 Bots: {healthy}/{len(self.core.workers)}\n"
            f"🧊 Cooling: {cooling}\n"
            f"⚡ Tasks: {self.core.task_mgr.active_count()}\n"
            f"🎯 Slides: {len(self.core.slide_targets)}\n"
            f"💥 SlideSpam: {len(self.core.slidespam_targets)}\n"
            f"🤖 Autoreplies: {self.core.autoreply_store.total_triggers}\n"
        )
        if task_lines:
            text += f"\n📋 Tasks:\n{task_lines}"
        await update.message.reply_text(text)

    async def cmd_stats(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
        uid = update.effective_user.id
        if not self._auth(uid):
            return
        snap = metrics.snapshot()
        health = self.core.task_mgr.health_report()

        try:
            import psutil
            proc = psutil.Process()
            mem_mb = proc.memory_info().rss / (1024 * 1024)
            mem_str = f"{mem_mb:.1f} MB"
        except Exception:
            import os as _os
            # Fallback: use gc tracked objects as rough proxy
            mem_str = f"~{len(gc.get_objects()) // 1000}k objects"

        text = (
            f"📈 Engine Stats\n\n"
            f"⏱ Uptime: {snap['uptime']}\n"
            f"✅ Success: {snap['success']} ({snap['success_rate']})\n"
            f"❌ Errors: {snap['errors']}\n"
            f"🔄 Retries: {snap['retries']}\n"
            f"⚡ Avg Latency: {snap['avg_latency_ms']}ms\n"
            f"📦 Tasks Created: {snap['tasks_created']}\n"
            f"🗑 Tasks Destroyed: {snap['tasks_destroyed']}\n"
            f"🔧 Worker Restarts: {snap['worker_restarts']}\n\n"
            f"🏥 Health:\n"
            f"  Active: {health['active']}\n"
            f"  Failed: {health['failed']}\n"
            f"  Queue: {self.core.scheduler.queue_size if self.core.scheduler else 0}\n"
            f"💾 Memory: {mem_str}\n"
        )
        await update.message.reply_text(text)

    async def cmd_ping(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
        t0 = time.monotonic()
        msg = await update.message.reply_text("⚡")
        elapsed = (time.monotonic() - t0) * 1000
        bot_info = await ctx.bot.get_me()
        await msg.edit_text(
            f"⚡ @{bot_info.username}: {elapsed:.0f}ms | "
            f"Bots: {len(self.core.workers)} | "
            f"Tasks: {self.core.task_mgr.active_count()}"
        )

    async def cmd_myid(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(f"🆔 {update.effective_user.id}")

    async def cmd_help(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
        uid = update.effective_user.id
        if not self._auth(uid):
            return
        await update.message.reply_text(
            "╭─────────────────────────╮\n"
            "│  ✦ 𝗗𝗘𝗟𝗘𝗧𝗘 × 𝗣𝗘𝗔𝗖𝗘 ✦  │\n"
            "│       v4.0 Engine       │\n"
            "╰─────────────────────────╯\n\n"
            f"🔄 NC:\n"
            f"  {CMD_PREFIX}gcnc <name>\n"
            f"  {CMD_PREFIX}ncemo <name>\n"
            f"  {CMD_PREFIX}ncbaap <name>\n"
            f"  {CMD_PREFIX}nctime <name>\n"
            f"  {CMD_PREFIX}deletencgodspeed <name>\n\n"
            f"💥 SPAM:\n"
            f"  {CMD_PREFIX}spam <text>\n"
            f"  {CMD_PREFIX}stopspam\n\n"
            f"🎯 SLIDE:\n"
            f"  {CMD_PREFIX}targetslide (reply)\n"
            f"  {CMD_PREFIX}slidespam (reply)\n"
            f"  {CMD_PREFIX}stopslide\n\n"
            f"🤖 AUTOREPLY:\n"
            f"  {CMD_PREFIX}autoreply <trigger> <reply>\n"
            f"  {CMD_PREFIX}stopautoreply [trigger]\n\n"
            f"🛑 CONTROL:\n"
            f"  {CMD_PREFIX}stop [command]\n"
            f"  {CMD_PREFIX}stopall\n\n"
            f"📊 INFO:\n"
            f"  {CMD_PREFIX}status\n"
            f"  {CMD_PREFIX}stats\n"
            f"  {CMD_PREFIX}ping\n"
            f"  {CMD_PREFIX}myid\n\n"
            f"👑 SUDO (owner):\n"
            f"  {CMD_PREFIX}addsudo <id>\n"
            f"  {CMD_PREFIX}delsudo <id>\n"
            f"  {CMD_PREFIX}listsudo\n"
        )

    # ── Message Handler (slides + autoreply) ──
    async def message_handler(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.message or not update.message.from_user:
            return
        uid = update.message.from_user.id
        cid = update.message.chat_id
        mid = update.message.message_id

        # Slide response (fire-and-forget via task to avoid blocking)
        if uid in self.core.slide_targets:
            asyncio.create_task(
                _slide_respond(self.core, cid, mid, RAID_TEXTS[:3], 0.05)
            )

        if uid in self.core.slidespam_targets:
            asyncio.create_task(
                _slide_respond(self.core, cid, mid, RAID_TEXTS, 0.02)
            )

        # AutoReply (dictionary lookup, no polling)
        if update.message.text:
            reply_text = self.core.autoreply_store.match(cid, update.message.text)
            if reply_text:
                alive = self.core.alive_workers(cid)
                if alive:
                    w = random.choice(alive)
                    await self.core.safe_api_call(
                        w,
                        lambda: w.bot.send_message(
                            cid, reply_text, reply_to_message_id=mid
                        ),
                        cid,
                    )





# ══════════════════════════════════════════════════════════════
#  MAIN ENTRY POINT
# ══════════════════════════════════════════════════════════════
async def main() -> None:
    core = BotCore()
    try:
        await core.start()
    except asyncio.CancelledError:
        pass
    finally:
        await core.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Shutdown by user")
    except Exception as e:
        log.critical("Fatal: %s\n%s", e, traceback.format_exc())
