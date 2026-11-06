"""
IPv4/IPv6 Address Information App - GUI
DEVASC Project Activity 3 - Social Coding (Option 2)
Team: Gurliepops (Alyssa Margarette Abejuela, Ma. Carla Jane Mangao, Shaula J. Ygbuhay)

A Tkinter desktop front end for ip_info_gurliepops.py, for network
technicians who would rather not use a terminal (this was on our BACKLOG
in ip_info_gurliepops.py - this file delivers it).

When the window opens it automatically detects THIS computer's public IPv4
and IPv6 addresses and shows each one on its own card with its location,
ISP/organization, ASN, country and time zone.

It reuses the exact same lookup logic as the command-line app (the same
DISPLAY_FIELDS, the same main/backup provider fallback), so anything already
covered by test_ip_info_gurliepops.py is covered here too.

REQUIREMENTS
    Python 3.8+ with Tkinter (bundled with the standard Windows and macOS
    installers; on some Linux distributions install the python3-tk
    package separately), the 'requests' library, and ip_info_gurliepops.py
    in the SAME folder as this file.

USAGE
    python ip_info_gui.py          (or rename to ip_info_gui.pyw and
                                    double-click it - no console window)

BUTTONS
    - Refresh        detect this computer's addresses again
    - Copy (on card) copy that one IP address to the clipboard
    - Copy as JSON   copy both results to the clipboard

HOW TO EXTEND
    - New output field: add it to DISPLAY_FIELDS in ip_info_gurliepops.py;
      each card picks it up automatically, no changes needed here.
    - Colors and fonts are all in the THEME block just below.
"""

import ipaddress
import json
import threading
import tkinter as tk

try:
    from ip_info_gurliepops import (
        ApiError,
        DISPLAY_FIELDS,
        IPV4_API,
        IPV6_API,
        fetch_url,
        lookup_ip,
    )
except ImportError:
    raise SystemExit(
        "Could not find ip_info_gurliepops.py.\n"
        "Put ip_info_gui.py in the SAME folder as ip_info_gurliepops.py "
        "and try again."
    )

# ----------------------------------------------------------------------
# THEME
# ----------------------------------------------------------------------
BG = "#EEF2F7"            # window background
HEADER_BG = "#0B1526"     # dark navy banner
HEADER_FG = "#FFFFFF"
HEADER_SUB = "#93A9C4"
CARD_BG = "#FFFFFF"
CARD_BORDER = "#D9E1EC"
TEXT = "#13213B"
MUTED = "#64748B"
ROW_ALT = "#F6F8FB"

V4_COLOR = "#0369A1"      # IPv4 accent (blue)
V6_COLOR = "#6D28D9"      # IPv6 accent (purple)

STATUS_COLORS = {
    "info": "#64748B",
    "ok": "#15803D",
    "warn": "#B45309",
    "error": "#B91C1C",
}

FONT = "Segoe UI"
MONO = "Consolas"

# Fields shown as rows under the big IP address (IP + Version are shown above).
DETAIL_FIELDS = [(label, key) for label, key in DISPLAY_FIELDS
                 if key not in ("ip", "version")]


class HoverButton(tk.Button):
    """Flat colored button that brightens when the mouse is over it."""

    def __init__(self, parent, text, command, bg, fg="#FFFFFF", hover=None, **kw):
        super().__init__(
            parent, text=text, command=command, bg=bg, fg=fg,
            activebackground=hover or bg, activeforeground=fg,
            relief="flat", bd=0, cursor="hand2",
            font=(FONT, 10, "bold"), padx=16, pady=7, **kw
        )
        self._bg = bg
        self._hover = hover or bg
        self.bind("<Enter>", lambda _e: self._on_enter())
        self.bind("<Leave>", lambda _e: self._on_leave())

    def _on_enter(self):
        if str(self["state"]) != "disabled":
            self.configure(bg=self._hover)

    def _on_leave(self):
        self.configure(bg=self._bg)


class IPCard(tk.Frame):
    """One card: colored strip, version badge, big IP, then detail rows."""

    def __init__(self, parent, version_label, accent, on_copy_ip):
        super().__init__(parent, bg=CARD_BG, highlightthickness=1,
                         highlightbackground=CARD_BORDER)
        self.version_label = version_label
        self.accent = accent
        self.on_copy_ip = on_copy_ip
        self.current_ip = None

        # Colored strip across the top of the card.
        tk.Frame(self, bg=accent, height=6).pack(fill="x")

        body = tk.Frame(self, bg=CARD_BG)
        body.pack(fill="both", expand=True, padx=22, pady=(16, 18))

        # Badge row: [ IPv4 ]                     (Copy)
        top = tk.Frame(body, bg=CARD_BG)
        top.pack(fill="x")
        tk.Label(top, text=f" {version_label} ", bg=accent, fg="#FFFFFF",
                 font=(FONT, 10, "bold")).pack(side="left")
        self.copy_btn = HoverButton(
            top, "Copy", self._copy, bg="#E2E8F0", fg=TEXT, hover="#CBD5E1")
        self.copy_btn.configure(padx=12, pady=3, font=(FONT, 9, "bold"),
                                state="disabled")
        self.copy_btn.pack(side="right")

        # Big IP address.
        self.ip_var = tk.StringVar(value="…")
        self.ip_label = tk.Label(body, textvariable=self.ip_var, bg=CARD_BG,
                                 fg=TEXT, font=(MONO, 20, "bold"), anchor="w")
        self.ip_label.pack(fill="x", pady=(14, 2))

        self.sub_var = tk.StringVar(value="Detecting…")
        self.sub_label = tk.Label(body, textvariable=self.sub_var, bg=CARD_BG,
                                  fg=MUTED, font=(FONT, 10), anchor="w",
                                  wraplength=360, justify="left")
        self.sub_label.pack(fill="x", pady=(0, 12))

        tk.Frame(body, bg=CARD_BORDER, height=1).pack(fill="x", pady=(0, 6))

        # Detail rows.
        self.value_vars = {}
        for i, (label, key) in enumerate(DETAIL_FIELDS):
            row_bg = ROW_ALT if i % 2 == 0 else CARD_BG
            row = tk.Frame(body, bg=row_bg)
            row.pack(fill="x")
            tk.Label(row, text=label, bg=row_bg, fg=MUTED, width=10,
                     anchor="w", font=(FONT, 10)).pack(side="left", padx=(8, 0), pady=6)
            var = tk.StringVar(value="—")
            tk.Label(row, textvariable=var, bg=row_bg, fg=TEXT, anchor="w",
                     font=(FONT, 11, "bold"), wraplength=250,
                     justify="left").pack(side="left", fill="x", expand=True, padx=(6, 8))
            self.value_vars[key] = var

    # -- states --------------------------------------------------------
    def show_loading(self):
        self.current_ip = None
        self.ip_label.configure(font=(MONO, 20, "bold"))
        self.ip_var.set("…")
        self.sub_var.set("Detecting…")
        self.sub_label.configure(fg=MUTED)
        self.copy_btn.configure(state="disabled")
        for var in self.value_vars.values():
            var.set("—")

    def show_data(self, data):
        self.current_ip = data.get("ip")
        self.ip_var.set(self.current_ip or "N/A")
        # Long IPv6 addresses shrink so they always fit on one line.
        n = len(self.current_ip or "")
        size = 20 if n <= 15 else 13 if n <= 26 else 11
        self.ip_label.configure(font=(MONO, size, "bold"))
        self.sub_var.set("Public address detected")
        self.sub_label.configure(fg=STATUS_COLORS["ok"])
        self.copy_btn.configure(state="normal" if self.current_ip else "disabled")
        for key, var in self.value_vars.items():
            value = data.get(key)
            var.set("N/A" if value in (None, "") else str(value))

    def show_unavailable(self, message):
        self.current_ip = None
        self.ip_label.configure(font=(MONO, 20, "bold"))
        self.ip_var.set("Not available")
        self.sub_var.set(message)
        self.sub_label.configure(fg=STATUS_COLORS["warn"])
        self.copy_btn.configure(state="disabled")
        for var in self.value_vars.values():
            var.set("—")

    def _copy(self):
        if self.current_ip:
            self.on_copy_ip(self.current_ip, self.version_label)


class IPInfoApp:
    """The whole GUI: banner, two cards (IPv4 + IPv6), and a footer."""

    def __init__(self, root):
        self.root = root
        self.results = {}
        self.pending = 0
        self.detected = {"IPv4": None, "IPv6": None}

        root.title("My IP Address — Gurliepops")
        root.configure(bg=BG)
        root.geometry("960x640")
        root.minsize(860, 600)

        self._build_widgets()
        self.refresh()  # detect automatically as soon as the window opens

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def _build_widgets(self):
        # Banner
        header = tk.Frame(self.root, bg=HEADER_BG)
        header.pack(fill="x")
        inner = tk.Frame(header, bg=HEADER_BG)
        inner.pack(fill="x", padx=28, pady=20)
        tk.Label(inner, text="THIS COMPUTER", bg=HEADER_BG, fg="#38BDF8",
                 font=(FONT, 10, "bold")).pack(anchor="w")
        tk.Label(inner, text="Your public IP addresses", bg=HEADER_BG,
                 fg=HEADER_FG, font=(FONT, 22, "bold")).pack(anchor="w")
        tk.Label(inner,
                 text="IPv4 and IPv6, with location, ISP, ASN and time zone",
                 bg=HEADER_BG, fg=HEADER_SUB, font=(FONT, 11)).pack(anchor="w")

        # Footer first (packed to the bottom so it is always visible).
        footer = tk.Frame(self.root, bg=BG)
        footer.pack(side="bottom", fill="x", padx=28, pady=(0, 18))

        self.status_dot = tk.Label(footer, text="●", bg=BG,
                                   fg=STATUS_COLORS["info"], font=(FONT, 12))
        self.status_dot.pack(side="left")
        self.status_var = tk.StringVar(value="Starting…")
        self.status_label = tk.Label(footer, textvariable=self.status_var,
                                     bg=BG, fg=STATUS_COLORS["info"],
                                     font=(FONT, 10), anchor="w",
                                     wraplength=420, justify="left")
        self.status_label.pack(side="left", padx=(6, 0))

        self.json_btn = HoverButton(footer, "Copy as JSON", self.on_copy_json,
                                    bg="#E2E8F0", fg=TEXT, hover="#CBD5E1",
                                    state="disabled")
        self.json_btn.pack(side="right")
        self.refresh_btn = HoverButton(footer, "↻  Refresh", self.refresh,
                                       bg=V4_COLOR, hover="#0284C7")
        self.refresh_btn.pack(side="right", padx=(0, 10))

        # Cards
        cards = tk.Frame(self.root, bg=BG)
        cards.pack(fill="both", expand=True, padx=28, pady=22)
        cards.columnconfigure(0, weight=1, uniform="cards")
        cards.columnconfigure(1, weight=1, uniform="cards")
        cards.rowconfigure(0, weight=1)

        self.cards = {
            "IPv4": IPCard(cards, "IPv4", V4_COLOR, self.on_copy_ip),
            "IPv6": IPCard(cards, "IPv6", V6_COLOR, self.on_copy_ip),
        }
        self.cards["IPv4"].grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.cards["IPv6"].grid(row=0, column=1, sticky="nsew", padx=(10, 0))

    # ------------------------------------------------------------------
    # Status helpers
    # ------------------------------------------------------------------
    def set_status(self, text, kind="info"):
        color = STATUS_COLORS.get(kind, STATUS_COLORS["info"])
        self.status_var.set(text)
        self.status_label.configure(fg=color)
        self.status_dot.configure(fg=color)

    # ------------------------------------------------------------------
    # Button handlers
    # ------------------------------------------------------------------
    def on_copy_ip(self, ip, label):
        self.root.clipboard_clear()
        self.root.clipboard_append(ip)
        self.set_status(f"Copied {label} address {ip} to the clipboard.", "ok")

    def on_copy_json(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(json.dumps(self.results, indent=2))
        self.set_status("Copied both results as JSON to the clipboard.", "ok")

    # ------------------------------------------------------------------
    # Detection (network calls never run on the GUI thread)
    # ------------------------------------------------------------------
    def refresh(self):
        self.refresh_btn.configure(state="disabled")
        self.json_btn.configure(state="disabled")
        self.results = {}
        self.detected = {"IPv4": None, "IPv6": None}
        self.warnings = []
        self.reasons = {}
        self.pending = 2
        for card in self.cards.values():
            card.show_loading()
        self.set_status("Detecting your public IPv4 and IPv6 addresses…", "info")

        threading.Thread(target=self._worker, args=("IPv4", IPV4_API),
                         daemon=True).start()
        threading.Thread(target=self._worker, args=("IPv6", IPV6_API),
                         daemon=True).start()

    def _detect(self, api_url):
        """Ask ipify for this computer's address. Returns (address, reason).

        Unlike get_public_ip() this keeps the real error text so the card can
        explain WHY an address is missing, and it retries once because
        api6.ipify.org occasionally times out on the first try.
        """
        reason = "Unknown problem."
        for _attempt in range(2):
            try:
                address = fetch_url(api_url)
                ipaddress.ip_address(address)  # must be a real address
                return address, None
            except ApiError as err:
                reason = str(err)
            except ValueError:
                reason = "The detection service returned something unexpected."
        return None, reason

    def _worker(self, label, api_url):
        """Find one address family, then look up its details."""
        try:
            address, reason = self._detect(api_url)
            if not address:
                self.reasons[label] = reason
                self.root.after(0, self._on_family_done, label, None, None)
                return
            try:
                data = lookup_ip(address)
                warning = None
            except ApiError as err:
                # Same idea as safe_lookup(): keep the address, details = N/A.
                data = {"ip": address, "version": label}
                warning = f"{address}: {err}"
            self.root.after(0, self._on_family_done, label, data, warning)
        except Exception as err:  # keep the GUI alive on anything unexpected
            self.root.after(0, self._on_family_done, label, None,
                            f"Unexpected error: {err}")

    def _on_family_done(self, label, data, warning):
        if warning:
            self.warnings.append(warning)
        self.detected[label] = data
        self.pending -= 1
        if self.pending == 0:
            self._finish()

    def _finish(self):
        # If neither ipify call worked, ask the details APIs to detect the
        # address themselves (same last-resort step as the CLI app).
        if not any(self.detected.values()):
            self.set_status("Trying the backup detection method…", "info")
            threading.Thread(target=self._fallback_worker, daemon=True).start()
            return
        self._render()

    def _fallback_worker(self):
        try:
            data = lookup_ip()
            self.root.after(0, self._on_fallback, data, None)
        except ApiError as err:
            self.root.after(0, self._on_fallback, None, str(err))
        except Exception as err:
            self.root.after(0, self._on_fallback, None, f"Unexpected error: {err}")

    def _on_fallback(self, data, error):
        if data:
            label = "IPv6" if ":" in str(data.get("ip", "")) else "IPv4"
            self.detected[label] = data
        elif error:
            self.warnings.append(error)
        self._render()

    # ------------------------------------------------------------------
    # Show results (always on the GUI thread)
    # ------------------------------------------------------------------
    def _render(self):
        missing_msgs = {
            "IPv4": "No IPv4 address could be detected.",
            "IPv6": "No IPv6 route found on this connection.",
        }
        for label, card in self.cards.items():
            data = self.detected.get(label)
            if data:
                card.show_data(data)
                self.results[label] = data
            else:
                reason = self.reasons.get(label)
                msg = missing_msgs[label]
                if reason:
                    msg += f"\nReason: {reason}"
                card.show_unavailable(msg)

        self.refresh_btn.configure(state="normal")
        self.json_btn.configure(state="normal" if self.results else "disabled")

        if not self.results:
            detail = f" ({self.warnings[-1]})" if self.warnings else ""
            self.set_status("Could not detect any address. Check your "
                            f"internet connection and click Refresh.{detail}", "error")
        elif self.warnings:
            self.set_status("Some details are missing: " + " / ".join(self.warnings),
                            "warn")
        else:
            self.set_status("Done — both addresses detected." if len(self.results) == 2
                            else "Done — detected what this network provides.", "ok")


def main():
    root = tk.Tk()
    IPInfoApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()