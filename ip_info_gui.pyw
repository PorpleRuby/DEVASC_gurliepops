"""
IPv4/IPv6 Address Information App - GUI
DEVASC Project Activity 3 - Social Coding (Option 2)
Team: Gurliepops (Alyssa Margarette Abejuela, Ma. Carla Jane Mangao, Shaula J. Ygbuhay)

A Tkinter desktop front end for ip_info_gurliepops.py, for network
technicians who would rather not use a terminal (this was on our BACKLOG
in ip_info_gurliepops.py - this file delivers it).

It reuses the exact same lookup logic as the command-line app (the same
DISPLAY_FIELDS, the same main/backup provider fallback, the same private-IP
check), so anything already covered by test_ip_info_gurliepops.py is
covered here too.

REQUIREMENTS
    Python 3.8+ with Tkinter (bundled with the standard Windows and macOS
    installers; on some Linux distributions install the python3-tk
    package separately), the 'requests' library, and ip_info_gurliepops.py
    in the SAME folder as this file.

USAGE
    python ip_info_gui.py

HOW TO USE
    - Leave the address box empty and click "This computer" to detect
      your own public IPv4 and IPv6 address.
    - Type any IPv4 or IPv6 address and click "Look up" (or press Enter)
      to look up that address instead.
    - Each result appears as its own tab with a Field/Value table.
    - "Copy as JSON" copies the current result to the clipboard.

HOW TO EXTEND
    - New output field: add it to DISPLAY_FIELDS in ip_info_gurliepops.py;
      this GUI picks it up automatically, no changes needed here.
    - A dark theme, a history of past lookups, or a "save to file" button
      are natural next additions (see BACKLOG in ip_info_gurliepops.py).
"""

import ipaddress
import json
import threading
import tkinter as tk
from tkinter import messagebox, ttk

try:
    from ip_info_gurliepops import (
        ApiError,
        DISPLAY_FIELDS,
        IPV4_API,
        IPV6_API,
        get_public_ip,
        lookup_ip,
    )
except ImportError:
    raise SystemExit(
        "Could not find ip_info_gurliepops.py.\n"
        "Put ip_info_gui.py in the SAME folder as ip_info_gurliepops.py "
        "and try again."
    )

# Friendlier tab names for the raw titles our lookup functions use.
TAB_LABELS = {
    "PUBLIC IPv4 INFORMATION": "IPv4",
    "PUBLIC IPv6 INFORMATION": "IPv6",
    "PUBLIC IP INFORMATION": "This Computer",
    "LOOKUP RESULT": "Result",
}

STATUS_COLORS = {
    "info": "#4A5568",
    "error": "#B91C1C",
    "warn": "#B45309",
    "ok": "#166534",
}


class IPInfoApp:
    """The whole GUI: one window, an address box, and a tab per result."""

    def __init__(self, root):
        self.root = root
        self.results = {}

        root.title("IP Address Info — Gurliepops")
        root.geometry("780x560")
        root.minsize(640, 440)

        self._build_widgets()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def _build_widgets(self):
        top = ttk.Frame(self.root)
        top.pack(fill="x", padx=12, pady=10)

        ttk.Label(top, text="IP address:").pack(side="left")

        self.ip_var = tk.StringVar()
        entry = ttk.Entry(top, textvariable=self.ip_var, width=26)
        entry.pack(side="left", padx=(8, 8))
        entry.bind("<Return>", lambda _event: self.on_lookup())
        entry.focus_set()

        self.lookup_btn = ttk.Button(top, text="Look up", command=self.on_lookup)
        self.lookup_btn.pack(side="left")

        self.auto_btn = ttk.Button(
            top, text="This computer", command=self.on_auto
        )
        self.auto_btn.pack(side="left", padx=(8, 0))

        ttk.Label(
            top,
            text='(leave the box empty and click "This computer" for your own IP)',
            foreground="#6B7280",
        ).pack(side="left", padx=(12, 0))

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        self._show_welcome_tab()

        bottom = ttk.Frame(self.root)
        bottom.pack(fill="x", padx=12, pady=(0, 12))

        self.status_var = tk.StringVar(value="Ready.")
        self.status_label = ttk.Label(
            bottom, textvariable=self.status_var, foreground=STATUS_COLORS["info"]
        )
        self.status_label.pack(side="left")

        self.copy_btn = ttk.Button(
            bottom, text="Copy as JSON", command=self.on_copy_json, state="disabled"
        )
        self.copy_btn.pack(side="right")

    def _show_welcome_tab(self):
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)
        frame = ttk.Frame(self.notebook)
        ttk.Label(
            frame,
            text=(
                'Enter an address and click "Look up", or click '
                '"This computer" to detect your own public IPv4/IPv6.'
            ),
            wraplength=640,
            justify="left",
        ).pack(padx=24, pady=24, anchor="w")
        self.notebook.add(frame, text="Welcome")

    # ------------------------------------------------------------------
    # Status / busy state
    # ------------------------------------------------------------------
    def set_status(self, text, kind="info"):
        self.status_var.set(text)
        self.status_label.configure(foreground=STATUS_COLORS.get(kind, STATUS_COLORS["info"]))

    def set_busy(self, busy):
        state = "disabled" if busy else "normal"
        self.lookup_btn.configure(state=state)
        self.auto_btn.configure(state=state)

    # ------------------------------------------------------------------
    # Button handlers
    # ------------------------------------------------------------------
    def on_lookup(self):
        ip_text = self.ip_var.get().strip()
        if not ip_text:
            messagebox.showinfo(
                "No address entered",
                'Type an IPv4 or IPv6 address, or click "This computer" instead.',
            )
            return

        # Validate before calling any API - same rule as the CLI app.
        try:
            address = ipaddress.ip_address(ip_text)
        except ValueError:
            self.set_status(f"'{ip_text}' is not a valid IPv4 or IPv6 address.", "error")
            return
        if not address.is_global:
            self.set_status(
                f"'{ip_text}' is a private or reserved address and has no public information.",
                "error",
            )
            return

        self._run_async(lambda: self._lookup_one(ip_text))

    def on_auto(self):
        self._run_async(self._lookup_auto)

    def on_copy_json(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(json.dumps(self.results, indent=2))
        self.set_status("Copied JSON to clipboard.", "ok")

    # ------------------------------------------------------------------
    # Background work (network calls never run on the GUI thread)
    # ------------------------------------------------------------------
    def _run_async(self, target):
        self.set_busy(True)
        self.set_status("Looking this up…", "info")
        threading.Thread(target=self._worker, args=(target,), daemon=True).start()

    def _worker(self, target):
        try:
            results, warnings = target()
            self.root.after(0, self._on_success, results, warnings)
        except ApiError as err:
            self.root.after(0, self._on_error, str(err))
        except Exception as err:  # keep the GUI alive on anything unexpected
            self.root.after(0, self._on_error, f"Unexpected error: {err}")

    def _lookup_one(self, ip_text):
        return {"LOOKUP RESULT": lookup_ip(ip_text)}, []

    def _lookup_auto(self):
        warnings = []
        ipv4 = get_public_ip(IPV4_API)
        ipv6 = get_public_ip(IPV6_API)
        results = {}
        if ipv4:
            results["PUBLIC IPv4 INFORMATION"] = self._safe(ipv4, warnings)
        if ipv6:
            results["PUBLIC IPv6 INFORMATION"] = self._safe(ipv6, warnings)
        if not results:
            # ipify failed for both; let the details APIs detect the address.
            results["PUBLIC IP INFORMATION"] = lookup_ip()
        return results, warnings

    def _safe(self, address, warnings):
        """Same fallback behavior as safe_lookup(), but keeps the message
        for the GUI instead of only printing it to stderr."""
        try:
            return lookup_ip(address)
        except ApiError as err:
            warnings.append(f"{address}: {err}")
            version = "IPv6" if ":" in address else "IPv4"
            return {"ip": address, "version": version}

    # ------------------------------------------------------------------
    # Result handlers (always run on the GUI thread via root.after)
    # ------------------------------------------------------------------
    def _on_success(self, results, warnings):
        self.results = results
        self._render(results)
        self.copy_btn.configure(state="normal")
        self.set_busy(False)
        if warnings:
            self.set_status(" / ".join(warnings), "warn")
        else:
            self.set_status("Done.", "ok")

    def _on_error(self, message):
        self.set_busy(False)
        self.set_status(message, "error")
        messagebox.showerror("Lookup failed", message)

    def _render(self, results):
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)

        for title, data in results.items():
            frame = ttk.Frame(self.notebook)
            tree = ttk.Treeview(
                frame, columns=("value",), show="tree headings", height=10
            )
            tree.heading("#0", text="Field")
            tree.heading("value", text="Value")
            tree.column("#0", width=160, anchor="w")
            tree.column("value", width=440, anchor="w")

            for label, key in DISPLAY_FIELDS:
                value = data.get(key)
                if value in (None, ""):
                    value = "N/A"
                tree.insert("", "end", text=label, values=(value,))

            tree.pack(fill="both", expand=True, padx=8, pady=8)
            self.notebook.add(frame, text=TAB_LABELS.get(title, title))


def main():
    root = tk.Tk()
    try:
        ttk.Style().theme_use("clam")
    except tk.TclError:
        pass  # fall back to whatever theme is available
    IPInfoApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
