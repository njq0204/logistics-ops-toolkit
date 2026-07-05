"""预警通知模块 — 企业微信 / 邮件 / 本地日志"""

import json
import os
import smtplib
import ssl
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import List, Optional


LEVEL_ORDER = {"info": 0, "warning": 1, "danger": 2}


def _should_notify(alerts: List[dict], config: dict) -> List[dict]:
    """按最低级别过滤预警"""
    notify_cfg = config.get("notifications", {})
    min_level = notify_cfg.get("min_level", "warning")
    min_ord = LEVEL_ORDER.get(min_level, 1)
    return [a for a in alerts if LEVEL_ORDER.get(a.get("level", "warning"), 1) >= min_ord]


def _check_cooldown(state_path: Path, cooldown_minutes: int) -> bool:
    """是否在冷却期内（避免重复推送）"""
    if not state_path.exists() or cooldown_minutes <= 0:
        return False
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
        last = datetime.fromisoformat(state.get("last_sent", "2000-01-01"))
        return datetime.now() - last < timedelta(minutes=cooldown_minutes)
    except (json.JSONDecodeError, ValueError):
        return False


def _save_notify_state(state_path: Path, results: dict) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps({"last_sent": datetime.now().isoformat(), "results": results}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _build_message(project_name: str, alerts: List[dict], goals: List[dict], run_at: str) -> str:
    lines = [
        f"【{project_name}】经营预警通知",
        f"时间: {run_at}",
        f"预警数量: {len(alerts)}",
        "",
        "—— 预警详情 ——",
    ]
    for a in alerts:
        tag = "🔴" if a.get("level") == "danger" else "🟡"
        lines.append(f"{tag} [{a.get('category', '')}] {a.get('message', '')}")

    if goals:
        lines.extend(["", "—— 目标进度 ——"])
        for g in goals:
            icon = "✅" if g["status"] == "achieved" else "⚠️" if g["status"] in ("at_risk", "behind") else "📊"
            lines.append(
                f"{icon} {g['name']}: {g['actual']}/{g['target']} ({g['progress_pct']}%) [{g['status_label']}]"
            )

    return "\n".join(lines)


def _build_markdown(project_name: str, alerts: List[dict], goals: List[dict], run_at: str) -> str:
    lines = [
        f"## {project_name} 经营预警",
        f"> 时间: {run_at}",
        "",
    ]
    for a in alerts:
        color = "warning" if a.get("level") == "danger" else "info"
        lines.append(f"**[{a.get('category', '')}]** {a.get('message', '')}")

    if goals:
        lines.extend(["", "### 目标进度"])
        for g in goals:
            lines.append(f"- {g['name']}: **{g['progress_pct']}%** ({g['status_label']})")

    return "\n".join(lines)


def send_webhook(url: str, content: str, markdown: str) -> dict:
    """发送企业微信 / 通用 Webhook"""
    payload = json.dumps({
        "msgtype": "markdown",
        "markdown": {"content": markdown},
    }).encode("utf-8")

    req = urllib.request.Request(
        url, data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            return {"ok": True, "channel": "webhook", "response": body}
    except urllib.error.URLError as e:
        return {"ok": False, "channel": "webhook", "error": str(e)}


def send_email(
    smtp_host: str,
    smtp_port: int,
    sender: str,
    password: str,
    receivers: List[str],
    subject: str,
    body: str,
) -> dict:
    """发送邮件通知"""
    if not receivers:
        return {"ok": False, "channel": "email", "error": "未配置收件人"}

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = ", ".join(receivers)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as server:
            server.login(sender, password)
            server.sendmail(sender, receivers, msg.as_string())
        return {"ok": True, "channel": "email", "receivers": receivers}
    except Exception as e:
        return {"ok": False, "channel": "email", "error": str(e)}


def write_notify_log(log_path: Path, message: str, results: dict) -> None:
    """写入本地通知日志"""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n{'='*50}\n[{ts}]\n{message}\n")
        f.write(f"发送结果: {json.dumps(results, ensure_ascii=False)}\n")


def send_alert_notifications(
    alerts: List[dict],
    config: dict,
    output_dir: Path,
    goals: Optional[List[dict]] = None,
    run_at: str = "",
) -> dict:
    """
    发送预警通知。
    支持: 企业微信 Webhook、邮件、本地日志。
    """
    notify_cfg = config.get("notifications", {})
    if not notify_cfg.get("enabled", False):
        return {"skipped": True, "reason": "notifications.enabled = false"}

    filtered = _should_notify(alerts, config)
    if not filtered:
        return {"skipped": True, "reason": "no alerts above min_level"}

    state_path = output_dir / ".notify_state.json"
    cooldown = notify_cfg.get("cooldown_minutes", 60)
    if _check_cooldown(state_path, cooldown):
        return {"skipped": True, "reason": f"cooldown ({cooldown}min)"}

    project_name = config.get("project", {}).get("name", "物流经营数据分析平台")
    goals = goals or []
    text = _build_message(project_name, filtered, goals, run_at)
    markdown = _build_markdown(project_name, filtered, goals, run_at)

    results = {"channels": []}
    channels = notify_cfg.get("channels", {})

    # 企业微信 / Webhook
    webhook_cfg = channels.get("webhook", {})
    if webhook_cfg.get("enabled") and webhook_cfg.get("url"):
        r = send_webhook(webhook_cfg["url"], text, markdown)
        results["channels"].append(r)

    # 邮件
    email_cfg = channels.get("email", {})
    if email_cfg.get("enabled"):
        password = os.environ.get("NOTIFY_EMAIL_PASSWORD", email_cfg.get("password", ""))
        r = send_email(
            smtp_host=email_cfg.get("smtp_host", "smtp.qq.com"),
            smtp_port=email_cfg.get("smtp_port", 465),
            sender=email_cfg.get("sender", ""),
            password=password,
            receivers=email_cfg.get("receivers", []),
            subject=f"[经营预警] {project_name} - {len(filtered)}条预警",
            body=text,
        )
        results["channels"].append(r)

    # 始终写本地日志
    log_cfg = notify_cfg.get("log", {})
    if log_cfg.get("enabled", True):
        log_path = output_dir / log_cfg.get("path", "logs/notifications.log")
        write_notify_log(log_path, text, results)
        results["channels"].append({"ok": True, "channel": "log", "path": str(log_path)})

    _save_notify_state(state_path, results)
    results["sent"] = any(c.get("ok") for c in results["channels"])
    return results
