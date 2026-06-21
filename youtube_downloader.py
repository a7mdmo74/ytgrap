import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import yt_dlp
import threading
import os
import sys
import time

# ── Frozen (exe) support ─────────────────────────────────────────────────────
if getattr(sys, 'frozen', False):
    APP_DIR = os.path.dirname(sys.executable)
    # PyInstaller puts --add-binary files in _internal/
    _internal = os.path.join(APP_DIR, "_internal")
    FFMPEG_DIR = os.path.join(_internal, "ffmpeg_bin") if os.path.isdir(os.path.join(_internal, "ffmpeg_bin")) else os.path.join(APP_DIR, "ffmpeg_bin")
    ICO_PATH = os.path.join(_internal, "ytgrab_icon.ico") if os.path.exists(os.path.join(_internal, "ytgrab_icon.ico")) else os.path.join(APP_DIR, "ytgrab_icon.ico")
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
    FFMPEG_DIR = r"C:\Users\dev\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin"
    ICO_PATH = os.path.join(APP_DIR, "ytgrab_icon.ico")

# ── Palette (IDM-inspired: dark steel, amber accent, clean chrome) ──────────
BG          = "#1c1f26"       # deep charcoal body
SIDEBAR_BG  = "#141720"       # slightly darker left rail
PANEL_BG    = "#22262f"       # card / panel surface
TOOLBAR_BG  = "#191d24"       # top toolbar strip
INPUT_BG    = "#0f1117"       # input fields
BORDER      = "#2e3340"       # subtle border
BORDER_LT   = "#3a3f50"       # lighter border / separator

ACCENT      = "#f5a623"       # IDM amber / orange
ACCENT_DK   = "#d4891a"       # pressed amber
ACCENT_GLOW = "#f5a62340"     # semi-transparent glow

BLUE        = "#3b82f6"       # info / progress fill
BLUE_LT     = "#60a5fa"

GREEN       = "#22c55e"
GREEN_DK    = "#16a34a"
RED         = "#ef4444"
RED_DK      = "#dc2626"

TEXT        = "#e8eaf0"       # primary text
TEXT_DIM    = "#8890a4"       # secondary / muted
TEXT_TINY   = "#555d72"       # very dim labels

MONO        = "Consolas"
UI_FONT     = "Segoe UI"


class IDMButton(tk.Canvas):
    """Flat button with gradient-style highlight bar on top (IDM look)."""
    def __init__(self, parent, text, color, hover, command=None,
                 width=110, height=32, text_color="#ffffff", **kw):
        super().__init__(parent, width=width, height=height,
                         bg=parent.cget("bg"), highlightthickness=0,
                         cursor="hand2", **kw)
        self._color  = color
        self._hover  = hover
        self._text   = text
        self._cmd    = command
        self._tc     = text_color
        self._bw     = width
        self._bh     = height
        self._active = True
        self._draw(color)
        self.bind("<Enter>",    self._on_enter)
        self.bind("<Leave>",    self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def _draw(self, color):
        self.delete("all")
        r = 4
        w, h = self._bw, self._bh
        # body
        self._rounded_rect(2, 2, w-2, h-2, r, fill=color, outline="")
        # top shine strip
        self._rounded_rect(2, 2, w-2, h//2, r, fill=self._lighten(color, 30), outline="")
        # bottom border shade
        self.create_rectangle(2, h-3, w-2, h-2, fill=self._darken(color, 40), outline="")
        # text
        self.create_text(w//2, h//2, text=self._text,
                         font=(UI_FONT, 9, "bold"), fill=self._tc)

    def _rounded_rect(self, x1, y1, x2, y2, r, **kw):
        pts = [x1+r,y1, x2-r,y1, x2,y1, x2,y1+r,
               x2,y2-r, x2,y2, x2-r,y2, x1+r,y2,
               x1,y2, x1,y2-r, x1,y1+r, x1,y1]
        self.create_polygon(pts, smooth=True, **kw)

    @staticmethod
    def _lighten(hex_color, amt):
        r,g,b = int(hex_color[1:3],16), int(hex_color[3:5],16), int(hex_color[5:7],16)
        return "#{:02x}{:02x}{:02x}".format(min(r+amt,255), min(g+amt,255), min(b+amt,255))

    @staticmethod
    def _darken(hex_color, amt):
        r,g,b = int(hex_color[1:3],16), int(hex_color[3:5],16), int(hex_color[5:7],16)
        return "#{:02x}{:02x}{:02x}".format(max(r-amt,0), max(g-amt,0), max(b-amt,0))

    def _on_enter(self, _):
        if self._active: self._draw(self._hover)

    def _on_leave(self, _):
        if self._active: self._draw(self._color)

    def _on_click(self, _):
        if self._active and self._cmd:
            self._cmd()

    def config_state(self, enabled: bool, text: str = None):
        self._active = enabled
        if text: self._text = text
        col = self._color if enabled else "#3a3f50"
        self._tc = "#ffffff" if enabled else "#b0b8cc"
        self._draw(col)


class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text   = text
        self.tw     = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, _=None):
        x, y = self.widget.winfo_rootx()+20, self.widget.winfo_rooty()+28
        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        self.tw.geometry(f"+{x}+{y}")
        tk.Label(self.tw, text=self.text, font=(UI_FONT, 8),
                 bg="#2a2d38", fg=TEXT, relief="flat",
                 padx=6, pady=3).pack()

    def hide(self, _=None):
        if self.tw:
            self.tw.destroy()
            self.tw = None


class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YTGrab  —  Download Manager  ·  by Ahmed Amer")
        self.root.geometry("820x640")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        # Set window icon
        if os.path.exists(ICO_PATH):
            self.root.iconbitmap(ICO_PATH)

        # apply ttk theme early
        self._setup_ttk_styles()

        self.output_dir      = os.path.join(os.path.expanduser("~"), "Downloads")
        self.formats         = []
        self.is_playlist     = False
        self.playlist_entries= []
        self._dl_start_time  = None
        self._speed_samples  = []
        self._build_ui()

    # ── TTK styles ────────────────────────────────────────────────────────────
    def _setup_ttk_styles(self):
        st = ttk.Style()
        st.theme_use("clam")
        # Progress bar — amber fill, dark trough
        st.configure("IDM.Horizontal.TProgressbar",
                     troughcolor=INPUT_BG, background=ACCENT,
                     lightcolor=ACCENT, darkcolor=ACCENT_DK,
                     bordercolor=BORDER, thickness=18)
        # Combobox
        st.configure("IDM.TCombobox",
                     fieldbackground=INPUT_BG, background=PANEL_BG,
                     foreground=TEXT, selectbackground=ACCENT,
                     selectforeground=BG, arrowcolor=ACCENT,
                     bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER)
        st.map("IDM.TCombobox",
               fieldbackground=[("readonly", INPUT_BG)],
               foreground=[("readonly", TEXT)],
               selectbackground=[("readonly", ACCENT)])
        # Scrollbar
        st.configure("Dark.Vertical.TScrollbar",
                     background=PANEL_BG, troughcolor=INPUT_BG,
                     arrowcolor=TEXT_DIM, bordercolor=BORDER,
                     darkcolor=PANEL_BG, lightcolor=PANEL_BG)

    # ── Main UI ───────────────────────────────────────────────────────────────
    def _build_ui(self):
        root = self.root

        # ── Top toolbar ──────────────────────────────────────────────
        toolbar = tk.Frame(root, bg=TOOLBAR_BG, height=52)
        toolbar.pack(fill="x")
        toolbar.pack_propagate(False)

        # Logo zone
        logo_frame = tk.Frame(toolbar, bg=TOOLBAR_BG)
        logo_frame.pack(side="left", padx=(16, 0))
        tk.Label(logo_frame, text="YT", font=(UI_FONT, 16, "bold"),
                 fg=RED, bg=TOOLBAR_BG).pack(side="left")
        tk.Label(logo_frame, text="Grab", font=(UI_FONT, 16, "bold"),
                 fg=ACCENT, bg=TOOLBAR_BG).pack(side="left")
        tk.Label(logo_frame, text="  Download Manager",
                 font=(UI_FONT, 9), fg=TEXT_DIM, bg=TOOLBAR_BG).pack(side="left", pady=(4,0))

        # Toolbar buttons (right side)
        btn_frame = tk.Frame(toolbar, bg=TOOLBAR_BG)
        btn_frame.pack(side="right", padx=16)
        for label, tip, cmd in [
            ("⚙ Settings", "Download settings", self._open_settings),
            ("? Help",     "How to use",         self._open_help),
        ]:
            b = tk.Label(btn_frame, text=label, font=(UI_FONT, 9),
                         fg=TEXT_DIM, bg=TOOLBAR_BG, cursor="hand2", padx=8)
            b.pack(side="left")
            b.bind("<Button-1>", lambda e, c=cmd: c())
            b.bind("<Enter>",    lambda e, w=b: w.config(fg=ACCENT))
            b.bind("<Leave>",    lambda e, w=b: w.config(fg=TEXT_DIM))
            Tooltip(b, tip)

        # Separator
        tk.Frame(root, bg=BORDER, height=1).pack(fill="x")

        # ── URL bar (IDM-style add-download row) ──────────────────────
        url_panel = tk.Frame(root, bg=PANEL_BG, pady=10)
        url_panel.pack(fill="x", padx=0)

        inner = tk.Frame(url_panel, bg=PANEL_BG)
        inner.pack(fill="x", padx=16)

        tk.Label(inner, text="Video / Playlist URL", font=(UI_FONT, 8, "bold"),
                 fg=ACCENT, bg=PANEL_BG).pack(anchor="w", pady=(0,4))

        url_row = tk.Frame(inner, bg=PANEL_BG)
        url_row.pack(fill="x")

        # URL entry with left icon
        entry_frame = tk.Frame(url_row, bg=INPUT_BG,
                               highlightthickness=1, highlightbackground=BORDER)
        entry_frame.pack(side="left", fill="x", expand=True)

        tk.Label(entry_frame, text=" 🔗", font=(UI_FONT, 10),
                 fg=TEXT_DIM, bg=INPUT_BG).pack(side="left")

        self.url_entry = tk.Entry(entry_frame, font=(UI_FONT, 10),
                                  bg=INPUT_BG, fg=TEXT, insertbackground=ACCENT,
                                  relief="flat", bd=0)
        self.url_entry.pack(side="left", fill="x", expand=True, ipady=7, padx=(0,8))
        self.url_entry.bind("<FocusIn>",  lambda e: entry_frame.config(highlightbackground=ACCENT))
        self.url_entry.bind("<FocusOut>", lambda e: entry_frame.config(highlightbackground=BORDER))
        self.url_entry.bind("<Return>",   lambda e: self.fetch_formats())

        self.fetch_btn = IDMButton(url_row, "  🔍 FETCH  ", GREEN, GREEN_DK,
                                   command=self.fetch_formats, width=120, height=36)
        self.fetch_btn.pack(side="right", padx=(10,0))

        # Video info label
        self.info_var = tk.StringVar(value="Paste a URL and press Fetch  ·  Supports videos and playlists")
        info_row = tk.Frame(inner, bg=PANEL_BG)
        info_row.pack(fill="x", pady=(6,0))
        self.info_icon = tk.Label(info_row, text="●", font=(UI_FONT, 8),
                                   fg=TEXT_TINY, bg=PANEL_BG)
        self.info_icon.pack(side="left")
        tk.Label(info_row, textvariable=self.info_var, font=(UI_FONT, 9),
                 fg=TEXT_DIM, bg=PANEL_BG, anchor="w").pack(side="left", padx=(4,0))

        tk.Frame(root, bg=BORDER, height=1).pack(fill="x")

        # ── Middle section: Quality + Save-to side by side ────────────
        mid = tk.Frame(root, bg=BG)
        mid.pack(fill="x", padx=16, pady=10)

        # Quality block
        q_block = self._panel(mid, "QUALITY / FORMAT")
        q_block.pack(side="left", fill="x", expand=True, padx=(0,8))

        q_inner = tk.Frame(q_block, bg=PANEL_BG)
        q_inner.pack(fill="x", padx=10, pady=(0,10))

        # small icon + combobox
        tk.Label(q_inner, text="🎬", font=(UI_FONT, 11), bg=PANEL_BG, fg=ACCENT).pack(side="left")
        self.quality_cb   = tk.StringVar()
        self.quality_menu = ttk.Combobox(q_inner, textvariable=self.quality_cb,
                                          state="readonly", font=(UI_FONT, 10),
                                          style="IDM.TCombobox")
        self.quality_menu.pack(side="left", fill="x", expand=True, ipady=5, padx=(8,0))
        self.quality_menu.bind("<<ComboboxSelected>>", lambda e: self._on_quality_change())

        # Save-to block
        s_block = self._panel(mid, "SAVE TO")
        s_block.pack(side="right", fill="x", expand=True, padx=(8,0))

        s_inner = tk.Frame(s_block, bg=PANEL_BG)
        s_inner.pack(fill="x", padx=10, pady=(0,10))

        self.dir_var = tk.StringVar(value=self.output_dir)
        dir_entry_frame = tk.Frame(s_inner, bg=INPUT_BG,
                                   highlightthickness=1, highlightbackground=BORDER)
        dir_entry_frame.pack(side="left", fill="x", expand=True)
        tk.Label(dir_entry_frame, text=" 📁", font=(UI_FONT, 10),
                 fg=TEXT_DIM, bg=INPUT_BG).pack(side="left")
        tk.Entry(dir_entry_frame, textvariable=self.dir_var, font=(UI_FONT, 9),
                 bg=INPUT_BG, fg=TEXT_DIM, relief="flat", bd=0,
                 state="readonly", readonlybackground=INPUT_BG,
                 insertbackground=ACCENT).pack(side="left", fill="x", expand=True,
                                              ipady=7, padx=(0,4))
        IDMButton(s_inner, " Browse ", BLUE, BLUE_LT,
                  command=self.browse_dir, width=88, height=36).pack(side="right", padx=(8,0))

        tk.Frame(root, bg=BORDER, height=1).pack(fill="x")

        # ── Progress / Status panel (IDM-style chunked info) ──────────
        prog_panel = tk.Frame(root, bg=PANEL_BG, pady=12)
        prog_panel.pack(fill="x")

        # Status row
        stat_top = tk.Frame(prog_panel, bg=PANEL_BG)
        stat_top.pack(fill="x", padx=16, pady=(0,6))

        # Status dot + label
        self.dot_canvas = tk.Canvas(stat_top, width=12, height=12,
                                    bg=PANEL_BG, highlightthickness=0)
        self.dot_canvas.pack(side="left", pady=(2,0))
        self._set_dot(TEXT_TINY)

        self.status_var = tk.StringVar(value="Ready")
        tk.Label(stat_top, textvariable=self.status_var,
                 font=(UI_FONT, 9, "bold"), fg=TEXT, bg=PANEL_BG).pack(side="left", padx=(6,0))

        # Speed / Size / ETA info chips (right side)
        chips_frame = tk.Frame(stat_top, bg=PANEL_BG)
        chips_frame.pack(side="right")

        self.speed_var = tk.StringVar(value="—")
        self.size_var  = tk.StringVar(value="—")
        self.eta_var   = tk.StringVar(value="—")
        self.pct_var   = tk.StringVar(value="0%")

        for label, var, icon in [
            ("SPEED", self.speed_var, "⚡"),
            ("SIZE",  self.size_var,  "💾"),
            ("ETA",   self.eta_var,   "⏱"),
            ("DONE",  self.pct_var,   "📊"),
        ]:
            chip = tk.Frame(chips_frame, bg=INPUT_BG,
                            highlightthickness=1, highlightbackground=BORDER)
            chip.pack(side="left", padx=4)
            tk.Label(chip, text=f" {icon} {label} ", font=(UI_FONT, 7, "bold"),
                     fg=TEXT_TINY, bg=INPUT_BG).pack(anchor="w", padx=4, pady=(3,0))
            tk.Label(chip, textvariable=var, font=(MONO, 9, "bold"),
                     fg=ACCENT, bg=INPUT_BG, width=9).pack(padx=4, pady=(0,3))

        # Progress bar  — IDM shows a SEGMENTED bar with % label inside
        prog_wrap = tk.Frame(prog_panel, bg=PANEL_BG)
        prog_wrap.pack(fill="x", padx=16, pady=(0,4))

        self.progress = ttk.Progressbar(prog_wrap, mode="determinate",
                                         style="IDM.Horizontal.TProgressbar")
        self.progress.pack(fill="x", ipady=2)

        # ── Download button row ────────────────────────────────────────
        tk.Frame(root, bg=BORDER, height=1).pack(fill="x")
        dl_row = tk.Frame(root, bg=BG, pady=10)
        dl_row.pack(fill="x", padx=16)

        self.dl_btn = IDMButton(dl_row, "  ⬇  START DOWNLOAD  ", ACCENT, ACCENT_DK,
                                command=self.start_download, width=220, height=40,
                                text_color=BG)
        self.dl_btn.pack(side="left")

        self.cancel_btn = IDMButton(dl_row, " ✖ Cancel ", RED, RED_DK,
                                    command=self._cancel, width=100, height=40)
        self.cancel_btn.pack(side="left", padx=(10,0))

        tk.Label(dl_row, text="Select quality, pick destination, then click Start Download",
                 font=(UI_FONT, 8), fg=TEXT_TINY, bg=BG).pack(side="right")

        # ── Log panel ─────────────────────────────────────────────────
        tk.Frame(root, bg=BORDER, height=1).pack(fill="x")
        log_header = tk.Frame(root, bg=SIDEBAR_BG, pady=4)
        log_header.pack(fill="x")
        tk.Label(log_header, text="  📋  ACTIVITY LOG",
                 font=(UI_FONT, 8, "bold"), fg=TEXT_DIM, bg=SIDEBAR_BG).pack(side="left")
        self._clear_btn = tk.Label(log_header, text="Clear  ", font=(UI_FONT, 8),
                                    fg=ACCENT, bg=SIDEBAR_BG, cursor="hand2")
        self._clear_btn.pack(side="right")
        self._clear_btn.bind("<Button-1>", lambda e: self._clear_log())

        log_body = tk.Frame(root, bg=SIDEBAR_BG)
        log_body.pack(fill="both", expand=True, padx=0, pady=0)

        self.log_text = tk.Text(log_body, bg=SIDEBAR_BG, fg=TEXT_DIM,
                                font=(MONO, 8), wrap="word", state="disabled",
                                relief="flat", bd=0, padx=14, pady=8,
                                selectbackground=ACCENT, selectforeground=BG,
                                insertbackground=ACCENT)
        sb = ttk.Scrollbar(log_body, command=self.log_text.yview,
                           style="Dark.Vertical.TScrollbar")
        self.log_text.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.log_text.pack(fill="both", expand=True)

        # colour tags for log
        self.log_text.tag_configure("ok",    foreground=GREEN)
        self.log_text.tag_configure("err",   foreground=RED)
        self.log_text.tag_configure("info",  foreground=ACCENT)
        self.log_text.tag_configure("dim",   foreground=TEXT_TINY)

    # ── Helper widgets ────────────────────────────────────────────────────────
    def _panel(self, parent, title):
        wrap = tk.Frame(parent, bg=PANEL_BG,
                        highlightthickness=1, highlightbackground=BORDER)
        # title bar strip
        title_bar = tk.Frame(wrap, bg=BORDER, height=24)
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)
        # amber left accent bar
        tk.Frame(title_bar, bg=ACCENT, width=3).pack(side="left", fill="y")
        tk.Label(title_bar, text=f"  {title}", font=(UI_FONT, 7, "bold"),
                 fg=TEXT_DIM, bg=BORDER).pack(side="left", pady=2)
        return wrap

    def _set_dot(self, color):
        self.dot_canvas.delete("all")
        self.dot_canvas.create_oval(1, 1, 11, 11, fill=color, outline=color)

    def _clear_log(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

    # ── Logging ───────────────────────────────────────────────────────────────
    def log(self, msg, tag=""):
        ts  = time.strftime("%H:%M:%S")
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"[{ts}]  ", "dim")
        self.log_text.insert("end", msg + "\n", tag or "")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    # ── Actions ───────────────────────────────────────────────────────────────
    def browse_dir(self):
        d = filedialog.askdirectory(initialdir=self.output_dir)
        if d:
            self.output_dir = d
            self.dir_var.set(d)

    def _open_settings(self):
        win = tk.Toplevel(self.root)
        win.title("Settings")
        win.geometry("480x360")
        win.configure(bg=PANEL_BG)
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text="⚙  Settings", font=(UI_FONT, 14, "bold"),
                 fg=ACCENT, bg=PANEL_BG).pack(pady=(16, 12))

        # Output format
        fmt_frame = tk.Frame(win, bg=PANEL_BG)
        fmt_frame.pack(fill="x", padx=20, pady=4)
        tk.Label(fmt_frame, text="Output format:", font=(UI_FONT, 10),
                 fg=TEXT, bg=PANEL_BG).pack(side="left")
        self._fmt_var = tk.StringVar(value="mp4")
        for val in ["mp4", "mkv", "webm"]:
            tk.Radiobutton(fmt_frame, text=val.upper(), variable=self._fmt_var,
                           value=val, font=(UI_FONT, 10), fg=TEXT, bg=PANEL_BG,
                           selectcolor=INPUT_BG, activebackground=PANEL_BG,
                           activeforeground=ACCENT).pack(side="left", padx=8)

        # Concurrent fragments
        cf_frame = tk.Frame(win, bg=PANEL_BG)
        cf_frame.pack(fill="x", padx=20, pady=8)
        tk.Label(cf_frame, text="Parallel fragments:", font=(UI_FONT, 10),
                 fg=TEXT, bg=PANEL_BG).pack(side="left")
        self._cf_var = tk.IntVar(value=3)
        tk.Spinbox(cf_frame, from_=1, to=8, textvariable=self._cf_var,
                   width=4, font=(UI_FONT, 10), bg=INPUT_BG, fg=TEXT,
                   buttonbackground=PANEL_BG, relief="flat").pack(side="left", padx=8)

        # Retries
        rt_frame = tk.Frame(win, bg=PANEL_BG)
        rt_frame.pack(fill="x", padx=20, pady=8)
        tk.Label(rt_frame, text="Max retries:", font=(UI_FONT, 10),
                 fg=TEXT, bg=PANEL_BG).pack(side="left")
        self._rt_var = tk.IntVar(value=10)
        tk.Spinbox(rt_frame, from_=1, to=30, textvariable=self._rt_var,
                   width=4, font=(UI_FONT, 10), bg=INPUT_BG, fg=TEXT,
                   buttonbackground=PANEL_BG, relief="flat").pack(side="left", padx=8)

        # Auto-clean
        self._clean_var = tk.BooleanVar(value=True)
        tk.Checkbutton(win, text="Auto-clean leftover .part / .temp files",
                       variable=self._clean_var, font=(UI_FONT, 10),
                       fg=TEXT, bg=PANEL_BG, selectcolor=INPUT_BG,
                       activebackground=PANEL_BG).pack(anchor="w", padx=20, pady=8)

        def apply_settings():
            self.log(f"Settings updated — format={self._fmt_var.get()}, "
                     f"fragments={self._cf_var.get()}, retries={self._rt_var.get()}", "info")
            win.destroy()

        btn_row = tk.Frame(win, bg=PANEL_BG)
        btn_row.pack(pady=16)
        tk.Button(btn_row, text="Apply", font=(UI_FONT, 10, "bold"),
                  bg=ACCENT, fg=BG, relief="flat", padx=24, pady=4,
                  cursor="hand2", command=apply_settings).pack(side="left", padx=6)
        tk.Button(btn_row, text="Cancel", font=(UI_FONT, 10),
                  bg=BORDER, fg=TEXT, relief="flat", padx=24, pady=4,
                  cursor="hand2", command=win.destroy).pack(side="left", padx=6)

    def _open_help(self):
        win = tk.Toplevel(self.root)
        win.title("Help")
        win.geometry("520x440")
        win.configure(bg=PANEL_BG)
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text="?  How to Use", font=(UI_FONT, 14, "bold"),
                 fg=ACCENT, bg=PANEL_BG).pack(pady=(16, 8))

        help_text = """1.  Paste a YouTube video or playlist URL
     into the URL field at the top.

2.  Click "Fetch" to load available qualities.
     Wait for the info to appear.

3.  Pick a quality from the dropdown.
     "Best quality" auto-selects the highest.

4.  (Optional) Click "Browse" to change
     the save location.

5.  Click "Start Download" and wait.
     Progress, speed, and ETA show live.

6.  A popup will confirm when done.
     The merged mp4 is saved to your folder.

TIPS:
 •  Playlists are auto-detected and
     downloaded one by one.
 •  If a download fails, it retries
     automatically.
 •  Use Settings (⚙) to change output
     format to MKV or WebM.

By Ahmed Amer"""

        text = tk.Text(win, bg=PANEL_BG, fg=TEXT_DIM, font=(UI_FONT, 10),
                       wrap="word", relief="flat", bd=0, padx=20, pady=8,
                       state="normal")
        text.insert("1.0", help_text)
        text.config(state="disabled")
        text.pack(fill="both", expand=True)

        tk.Button(win, text="Close", font=(UI_FONT, 10, "bold"),
                  bg=ACCENT, fg=BG, relief="flat", padx=24, pady=4,
                  cursor="hand2", command=win.destroy).pack(pady=(8, 16))

    def _show_done_dialog(self):
        import subprocess
        win = tk.Toplevel(self.root)
        win.title("Done")
        win.geometry("400x200")
        win.configure(bg=PANEL_BG)
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text="✔  Download Complete", font=(UI_FONT, 14, "bold"),
                 fg=GREEN, bg=PANEL_BG).pack(pady=(24, 8))
        tk.Label(win, text=f"Saved to:\n{self.output_dir}",
                 font=(UI_FONT, 9), fg=TEXT_DIM, bg=PANEL_BG,
                 justify="center").pack(pady=(0, 16))

        btn_row = tk.Frame(win, bg=PANEL_BG)
        btn_row.pack()
        tk.Button(btn_row, text="📂  Open Folder", font=(UI_FONT, 10, "bold"),
                  bg=ACCENT, fg=BG, relief="flat", padx=20, pady=6,
                  cursor="hand2",
                  command=lambda: (subprocess.Popen(["explorer", self.output_dir]),
                                   win.destroy())).pack(side="left", padx=6)
        tk.Button(btn_row, text="Close", font=(UI_FONT, 10),
                  bg=BORDER, fg=TEXT, relief="flat", padx=20, pady=6,
                  cursor="hand2", command=win.destroy).pack(side="left", padx=6)

    def _cancel(self):
        # minimal cancel: just reset UI (yt-dlp thread is daemon, will die)
        self.status_var.set("Cancelled")
        self._set_dot(RED)
        self.log("Download cancelled by user.", "err")
        self.dl_btn.config_state(True, "  ⬇  START DOWNLOAD  ")
        self.fetch_btn.config_state(True, "  🔍 FETCH  ")
        self.progress["value"] = 0
        self._reset_chips()

    def _reset_chips(self):
        self.speed_var.set("—")
        self.size_var.set("—")
        self.eta_var.set("—")
        self.pct_var.set("0%")

    def _on_quality_change(self):
        idx = self.quality_menu.current()
        if idx >= 0 and self.formats:
            fmt = self.formats[idx]
            fid, res, fps, ext = fmt
            if res:
                self.log(f"Quality selected: {res}p{fps}  [{ext.upper()}]", "info")

    # ── Fetch ─────────────────────────────────────────────────────────────────
    def fetch_formats(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("No URL", "Please enter a YouTube URL.")
            return
        self.fetch_btn.config_state(False, "  ⏳ Fetching…  ")
        self.info_var.set("Contacting server…")
        self.info_icon.config(fg="#facc15")
        self._set_dot("#facc15")
        self.status_var.set("Fetching video information…")
        self.log(f"Fetching: {url}", "info")
        threading.Thread(target=self._fetch_formats, args=(url,), daemon=True).start()

    def _fetch_formats(self, url):
        try:
            ydl_opts = {"quiet": True, "no_warnings": True, "skip_download": True,
                        "ffmpeg_location": FFMPEG_DIR,
                        "extract_flat": False,
                        "ignoreerrors": True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

            self.is_playlist      = info.get("_type") == "playlist" or "entries" in info
            entries               = [e for e in info.get("entries", []) if e] if self.is_playlist else [info]
            self.playlist_entries = entries

            title = info.get("title", "Unknown")
            if self.is_playlist:
                count = len(entries)
                label = f"Playlist  ·  {title}  ·  {count} videos"
                self.root.after(0, lambda l=label: self.info_var.set(l))
                self.log(f"Playlist detected: {title} — {count} videos", "info")
            else:
                dur  = info.get("duration", 0)
                dstr = f"{dur//60}:{dur%60:02d}" if dur else "—"
                label = f"Video  ·  {title}  ·  {dstr}"
                self.root.after(0, lambda l=label: self.info_var.set(l))
                self.log(f"Video: {title}  [{dstr}]", "info")

            self.formats = []
            seen = set()
            sample = next((e for e in entries if e and e.get("formats")), None)
            if sample:
                for f in sample.get("formats", []):
                    res    = f.get("height")
                    fps    = f.get("fps", 30)
                    ext    = f.get("ext", "")
                    vcodec = f.get("vcodec", "none")
                    if vcodec == "none" or not res:
                        continue
                    key = f"{res}_{fps}_{ext}"
                    if key not in seen:
                        seen.add(key)
                        self.formats.append((f.get("format_id", ""), res, fps, ext))

            self.formats.sort(key=lambda x: x[1], reverse=True)
            self.formats.insert(0, ("bestvideo+bestaudio/best", 0, 0, ""))

            if self.is_playlist:
                self.log(f"Playlist: {len(entries)} videos, {len(self.formats)-1} quality options", "ok")
            else:
                self.log(f"Video: {len(self.formats)-1} quality options", "ok")

            if self.is_playlist and len(self.formats) <= 1:
                self.log("Playlist detected — using best quality for all videos", "info")

            self.root.after(0, self._update_quality_dropdown)
            self.root.after(0, lambda: self.fetch_btn.config_state(True, "  🔍 FETCH  "))
            self.root.after(0, lambda: self._set_dot(GREEN))
            self.root.after(0, lambda: self.info_icon.config(fg=GREEN))
            self.root.after(0, lambda: self.status_var.set("Ready  —  Select quality and start download"))

        except Exception as e:
            self.root.after(0, lambda: self.info_var.set(f"Error: {str(e)[:60]}"))
            self.root.after(0, lambda: self._set_dot(RED))
            self.root.after(0, lambda: self.info_icon.config(fg=RED))
            self.root.after(0, lambda: self.status_var.set("Error"))
            self.root.after(0, lambda err=e: self.log(f"ERROR: {err}", "err"))
            self.root.after(0, lambda: self.fetch_btn.config_state(True, "  🔍 FETCH  "))

    def _update_quality_dropdown(self):
        labels = []
        for fmt in self.formats:
            fid, res, fps, ext = fmt
            if res == 0:
                labels.append("✦  Best quality  (auto-select)")
            else:
                labels.append(f"  {res}p  ·  {fps}fps  ·  {ext.upper()}")
        self.quality_menu["values"] = labels
        if labels:
            self.quality_menu.current(0)
        self.log(f"{len(labels)-1} quality options available.", "ok")

    # ── Download ──────────────────────────────────────────────────────────────
    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("No URL", "Please enter a YouTube URL.")
            return
        if not self.formats:
            messagebox.showwarning("Fetch first", "Click Fetch to load video info first.")
            return
        sel_idx = self.quality_menu.current()
        if sel_idx < 0:
            messagebox.showwarning("No quality", "Select a quality option.")
            return

        self.dl_btn.config_state(False, "  ⏳ Downloading…  ")
        self.fetch_btn.config_state(False, "  🔍 FETCH  ")
        self._set_dot("#facc15")
        self.status_var.set("Preparing download…")
        self.progress["value"] = 0
        self._reset_chips()
        self._dl_start_time = time.time()

        threading.Thread(target=self._download, args=(url, sel_idx), daemon=True).start()

    def _download(self, url, sel_idx):
        try:
            fmt      = self.formats[sel_idx]
            fmt_id   = fmt[0]
            is_best  = fmt_id == "bestvideo+bestaudio/best"
            fmt_str  = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best" if is_best else f"{fmt_id}+bestaudio"

            total = len(self.playlist_entries) if self.is_playlist else 1
            self.root.after(0, lambda: self.progress.configure(maximum=max(total*100, 100)))

            # Clean leftover .part / .temp files in output dir
            if getattr(self, '_clean_var', None) is None or self._clean_var.get():
                for f in os.listdir(self.output_dir):
                    if f.endswith(".part") or f.endswith(".temp.mp4"):
                        try: os.remove(os.path.join(self.output_dir, f))
                        except: pass

            download_count = [0]

            def progress_hook(d):
                if d["status"] == "downloading":
                    pct_raw = d.get("_percent_str", "0%").strip()
                    speed   = d.get("_speed_str", "—").strip()
                    eta     = d.get("_eta_str", "—").strip()
                    down    = d.get("_downloaded_bytes_str", "—").strip()
                    # strip ANSI codes if any
                    import re
                    pct_raw = re.sub(r'\x1b\[[0-9;]*m', '', pct_raw)
                    speed   = re.sub(r'\x1b\[[0-9;]*m', '', speed)
                    eta     = re.sub(r'\x1b\[[0-9;]*m', '', eta)
                    try:
                        pct_f = float(pct_raw.replace("%","").strip())
                    except Exception:
                        pct_f = 0.0

                    fn = os.path.basename(d.get("filename", ""))
                    if fn.endswith((".m4a", ".opus", ".mp3", ".ogg", ".wav")):
                        status = f"Downloading audio…  {pct_raw}"
                    else:
                        status = f"Downloading…  {pct_raw}"
                    self.root.after(0, lambda s=status: self.status_var.set(s))
                    self.root.after(0, lambda p=pct_raw, s=speed, e=eta, pf=pct_f, sz=down:
                                    self._update_progress(p, s, e, pf, sz))
                elif d["status"] == "finished":
                    fn = os.path.basename(d.get("filename", ""))
                    if fn.endswith((".m4a", ".opus", ".mp3", ".ogg", ".wav", ".webm", ".mp4", ".mkv")):
                        self.root.after(0, lambda f=fn: self.log(f"✔  Saved: {f}", "ok"))
                        download_count[0] += 1
                        self.root.after(0, lambda: self.status_var.set("Merging files…"))
                    else:
                        self.root.after(0, lambda f=fn: self.log(f"✔  Saved: {f}", "ok"))

            ydl_opts = {
                "format":             fmt_str,
                "merge_output_format": getattr(self, '_fmt_var', None) and self._fmt_var.get() or "mp4",
                "outtmpl":            os.path.join(self.output_dir, "%(title)s.%(ext)s"),
                "progress_hooks":     [progress_hook],
                "quiet":              True,
                "no_warnings":        True,
                "noplaylist":         not self.is_playlist,
                "ffmpeg_location":    FFMPEG_DIR,
                "retries":            getattr(self, '_rt_var', None) and self._rt_var.get() or 10,
                "fragment_retries":   getattr(self, '_rt_var', None) and self._rt_var.get() or 10,
                "concurrent_fragment_downloads": getattr(self, '_cf_var', None) and self._cf_var.get() or 3,
                "keepvideo":          False,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                if self.is_playlist:
                    for i, entry in enumerate(self.playlist_entries):
                        vid_url = entry.get("url") or entry.get("webpage_url") or entry.get("id")
                        title   = entry.get("title", f"Video {i+1}")
                        self.root.after(0, lambda t=title, n=i+1, tt=total:
                                        self.log(f"[{n}/{tt}] {t}", "info"))
                        ydl.download([str(vid_url)])
                else:
                    ydl.download([url])

            self.root.after(0, lambda: self.status_var.set("Download Complete  ✔"))
            self.root.after(0, lambda: self._set_dot(GREEN))
            self.root.after(0, lambda: self.progress.configure(value=self.progress["maximum"]))
            self.root.after(0, lambda: self.pct_var.set("100%"))
            self.root.after(0, lambda: self.log("All downloads finished successfully.", "ok"))
            self.root.after(0, self._show_done_dialog)

        except Exception as e:
            self.root.after(0, lambda: self._set_dot(RED))
            self.root.after(0, lambda: self.status_var.set("Error during download"))
            self.root.after(0, lambda err=e: self.log(f"ERROR: {err}", "err"))
        finally:
            self.root.after(0, lambda: self.dl_btn.config_state(True, "  ⬇  START DOWNLOAD  "))
            self.root.after(0, lambda: self.fetch_btn.config_state(True, "  🔍 FETCH  "))

    def _update_progress(self, pct_str, speed, eta, pct_float, size):
        self.speed_var.set(speed[:12])
        self.eta_var.set(eta[:10])
        self.pct_var.set(pct_str[:8])
        self.size_var.set(size[:10] if size != "—" else "—")
        try:
            self.progress["value"] = pct_float
        except Exception:
            pass


if __name__ == "__main__":
    root = tk.Tk()
    app  = YouTubeDownloader(root)
    root.mainloop()
