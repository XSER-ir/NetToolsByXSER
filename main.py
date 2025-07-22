
import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
import ctypes
import sys
import threading
import requests
import time
import os
import json

# Save/load settings
SETTINGS_FILE = "net_tools_settings.json"
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"language": "English", "buttons": {"renew": True, "flush": True, "release": True, "check": True}}

def save_settings():
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump({"language": current_lang, "buttons": visible_buttons}, f)

# Languages and translations
LANGUAGES = {
    "English": {
        "title": "Net Tools By XSER",
        "renew": "Renew IP",
        "flush": "Flush DNS",
        "release": "Release IP",
        "check": "Check IP Info",
        "settings": "Settings",
        "about": "About Us",
        "log": "Log (resets on close):",
        "location": "Location",
        "ping": "Ping",
        "connected": "🟢 Connected",
        "disconnected": "🔴 Disconnected",
        "tooltip": {
            "renew": "Renews your computer's IP address.",
            "flush": "Clears the DNS cache.",
            "release": "Releases the current IP address.",
            "check": "Shows your IP configuration.",
            "settings": "Change language and button visibility.",
            "about": "Project info and social links."
        }
    },
    "فارسی": {
        "title": "ابزار شبکه XSER",
        "renew": "تجدید IP",
        "flush": "پاک‌سازی DNS",
        "release": "رهاسازی IP",
        "check": "اطلاعات IP",
        "settings": "تنظیمات",
        "about": "درباره ما",
        "log": "گزارش (با بستن حذف می‌شود):",
        "location": "موقعیت",
        "ping": "پینگ",
        "connected": "🟢 متصل",
        "disconnected": "🔴 قطع",
        "tooltip": {
            "renew": "دریافت مجدد آدرس IP از سرور.",
            "flush": "پاک‌سازی کش DNS.",
            "release": "رهاسازی آدرس IP فعلی.",
            "check": "نمایش اطلاعات شبکه.",
            "settings": "تغییر زبان و نمایش دکمه‌ها.",
            "about": "اطلاعات پروژه و لینک‌ها"
        }
    },
    "日本語": {
        "title": "ネットツール by XSER",
        "renew": "IPを更新",
        "flush": "DNSを消去",
        "release": "IPを解放",
        "check": "IP情報表示",
        "settings": "設定",
        "about": "このアプリについて",
        "log": "ログ（終了時にリセット）:",
        "location": "位置情報",
        "ping": "Ping",
        "connected": "🟢 接続中",
        "disconnected": "🔴 未接続",
        "tooltip": {
            "renew": "IPアドレスを再取得します。",
            "flush": "DNSキャッシュをクリアします。",
            "release": "現在のIPを解放します。",
            "check": "IP設定を表示します。",
            "settings": "言語と表示設定を変更します。",
            "about": "プロジェクト情報とリンク"
        }
    }
}

settings = load_settings()
current_lang = settings.get("language", "English")
visible_buttons = settings.get("buttons", {"renew": True, "flush": True, "release": True, "check": True})

def get_text(key): return LANGUAGES[current_lang][key]
def get_tip(key): return LANGUAGES[current_lang]["tooltip"][key]

# GUI Setup
root = tk.Tk()
root.title(get_text("title"))
root.geometry("480x640")
root.configure(bg="black")
root.resizable(False, False)

font_style = ("Segoe UI", 10, "bold")

# Network status widgets
status_frame = tk.Frame(root, bg="black"); status_frame.pack(pady=10)
net_icon = tk.Label(status_frame, text="...", bg="black", font=font_style)
net_icon.pack()
ping_label = tk.Label(status_frame, text="...", bg="black", font=font_style)
ping_label.pack()
ip_location = tk.Label(status_frame, text="...", bg="black", font=font_style)
ip_location.pack()

# Log box
log_label = tk.Label(root, text=get_text("log"), bg="black", fg="white", font=font_style)
log_label.pack()
log_text = tk.Text(root, height=6, width=56, bg="#111", fg="lime", font=("Consolas", 9), borderwidth=0)
log_text.pack(pady=5)
def log_action(text):
    import time
    timestamp = time.strftime("%H:%M:%S")
    log_text.insert(tk.END, f"[{timestamp}] {text}\n")
    log_text.see(tk.END)

# Tooltip fix (status bar tooltip instead of overlay)
tooltip_var = tk.StringVar()
tooltip_label = tk.Label(root, textvariable=tooltip_var, bg="black", fg="gray", font=("Segoe UI", 9))
tooltip_label.pack()

def bind_tooltip(widget, key):
    widget.bind("<Enter>", lambda e: tooltip_var.set(get_tip(key)))
    widget.bind("<Leave>", lambda e: tooltip_var.set(""))

# Buttons
buttons = {}
button_frame = tk.Frame(root, bg="black"); button_frame.pack()

def run_command(command, label):
    try:
        subprocess.run(command, shell=True, check=True)
        messagebox.showinfo(get_text("title"), f"{label} ✔")
        log_action(f"{label} ✔")
    except:
        messagebox.showerror(get_text("title"), f"{label} ❌")
        log_action(f"{label} ❌")

def renew(): run_command("ipconfig /renew", get_text("renew"))
def flush(): run_command("ipconfig /flushdns", get_text("flush"))
def release(): run_command("ipconfig /release", get_text("release"))
def check():
    try:
        result = subprocess.run("ipconfig", shell=True, capture_output=True, text=True)
        log_action(get_text("check") + " ✔")

        # Create new window
        win = tk.Toplevel(root)
        win.title(get_text("check"))
        win.geometry("500x400")
        win.configure(bg="black")

        # Scrollable text box
        text_frame = tk.Frame(win, bg="black")
        text_frame.pack(expand=True, fill="both", padx=10, pady=10)

        text_box = tk.Text(text_frame, wrap="word", bg="#111", fg="lime", font=("Consolas", 9), borderwidth=0)
        text_box.insert("1.0", result.stdout)
        text_box.config(state="disabled")
        text_box.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(text_frame, command=text_box.yview, bg="black")
        scrollbar.pack(side="right", fill="y")
        text_box.config(yscrollcommand=scrollbar.set)

    except Exception as e:
        messagebox.showerror(get_text("title"), f"{get_text('check')} ❌")
        log_action(f"{get_text('check')} ❌ {e}")

def add_button(key, command_func):
    btn = tk.Button(button_frame, text=get_text(key), command=command_func,
                    font=font_style, bg="red", fg="white", activebackground="#990000",
                    width=25, height=2, relief="flat", bd=0)
    btn.pack(pady=5)
    bind_tooltip(btn, key)
    buttons[key] = btn

def refresh_buttons():
    for key, btn in buttons.items():
        if visible_buttons.get(key, True):
            btn.pack(pady=5)
        else:
            btn.pack_forget()

add_button("renew", renew)
add_button("flush", flush)
add_button("release", release)
add_button("check", check)
refresh_buttons()

# Ping + flag emoji
def country_flag_emoji(country_code):
    if not country_code: return ""
    return chr(127397 + ord(country_code[0])) + chr(127397 + ord(country_code[1]))

def update_status():
    while True:
        try:
            res = subprocess.run("ping -n 1 8.8.8.8", shell=True, capture_output=True, text=True)
            if "TTL=" in res.stdout:
                ping_time = "?"
                for line in res.stdout.splitlines():
                    if "time=" in line:
                        ping_time = line.split("time=")[-1].split()[0]
                        break
                ping_label.config(text=f"{get_text('ping')}: {ping_time}", fg="lime")
                net_icon.config(text=get_text("connected"), fg="lime")
            else:
                ping_label.config(text=f"{get_text('ping')}: Fail", fg="red")
                net_icon.config(text=get_text("disconnected"), fg="red")
        except:
            ping_label.config(text=f"{get_text('ping')}: Error", fg="red")
            net_icon.config(text=get_text("disconnected"), fg="red")

        try:
            loc = requests.get("https://ipinfo.io", timeout=5).json()
            city = loc.get("city", "Unknown")
            country = loc.get("country", "")
            flag = country_flag_emoji(country)
            ip_location.config(text=f"{get_text('location')}: {flag} {city}, {country}")
        except:
            ip_location.config(text=f"{get_text('location')}: ---")
        time.sleep(10)

threading.Thread(target=update_status, daemon=True).start()

# Settings
def show_settings():
    win = tk.Toplevel(root)
    win.title(get_text("settings"))
    win.geometry("300x280")
    win.configure(bg="black")

    def on_lang_change(e):
        global current_lang
        current_lang = lang_var.get()
        save_settings()
        root.title(get_text("title"))
        log_label.config(text=get_text("log"))
        for k in buttons: buttons[k].config(text=get_text(k))
        refresh_buttons()

    lang_var = tk.StringVar(value=current_lang)
    combo = ttk.Combobox(win, values=list(LANGUAGES.keys()), textvariable=lang_var)
    combo.pack(pady=10)
    combo.bind("<<ComboboxSelected>>", on_lang_change)

    for key in buttons:
        var = tk.BooleanVar(value=visible_buttons[key])
        def toggle(k=key, v=var):
            visible_buttons[k] = v.get()
            refresh_buttons()
            save_settings()
        chk = tk.Checkbutton(win, text=get_text(key), variable=var, command=toggle,
                             bg="black", fg="white", selectcolor="black")
        chk.pack(anchor="w", padx=20)

tk.Button(root, text=get_text("settings"), command=show_settings,
          font=font_style, bg="gray20", fg="white",
          activebackground="gray30", width=25, height=2, relief="flat", bd=0).pack(pady=5)

def show_about():
    win = tk.Toplevel(root)
    win.title(get_text("about"))
    win.geometry("440x360")
    win.configure(bg="black")
    text = tk.Text(win, wrap="word", height=20, width=58, bg="black", fg="white", font=("Segoe UI", 9), borderwidth=0)
    info = (
        "This project was made by XSER and powered by ChatGPT.\n\n"
        "🔗 Social Links:\n"
        "• Aparat: https://www.aparat.com/XSER007\n"
        "• GitHub: https://github.com/XSER-ir\n"
        "• YouTube: https://www.youtube.com/channel/UCdmjY8rQ32W9E-oniegV3vw?sub_confirmation=1\n"
        "• Twitch: https://www.twitch.tv/xser_tv\n"
        "• Instagram: https://www.instagram.com/xser.uchiha/"
    )
    text.insert("1.0", info)
    text.config(state="disabled")
    text.pack(padx=10, pady=10)

tk.Button(root, text=get_text("about"), command=show_about,
          font=font_style, bg="gray20", fg="white",
          activebackground="gray30", width=25, height=2, relief="flat", bd=0).pack(pady=5)

root.protocol("WM_DELETE_WINDOW", lambda: (save_settings(), root.destroy()))
root.mainloop()
