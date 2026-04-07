#!/usr/bin/env python3
"""
OrthoConnect v1.0 — Interfaz Gráfica (customtkinter)
Ejecutar desde la raíz del proyecto: PYTHONPATH=. python -m src.gui_main
"""
from __future__ import annotations

import sys
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Optional

import customtkinter as ctk
import psycopg2

from src.db import connect, set_application_name
from src.db_errors import format_db_error, is_business_rule_violation
from src import repo as repo_pg
from src import repo_demo

# ── Paleta ─────────────────────────────────────────────────────────────────────
BG       = "#0D1117"
SURF     = "#161B27"
SURF2    = "#1E2535"
BORDER   = "#252D40"
AMBER    = "#E8A838"
AMBER_DK = "#B07820"
TEXT     = "#F0EDE8"
TEXT_MU  = "#7A8297"
GREEN    = "#4CAF84"
RED      = "#E05858"
AMBER_BG = "#1E1A0D"
GREEN_BG = "#0D1E14"
RED_BG   = "#1E0D0D"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

_APP_USER = "gui"
_REPO     = repo_pg


def effective_repo_for_connection(conn, repo_mod):
    """DemoConnection debe ir siempre con repo_demo (el cursor demo no ejecuta SQL)."""
    if isinstance(conn, repo_demo.DemoConnection):
        return repo_demo
    return repo_mod


# ── Helpers ────────────────────────────────────────────────────────────────────
def _dark_treeview_style(name: str = "Dark") -> str:
    """Configura un estilo ttk.Treeview oscuro y devuelve su nombre."""
    s = ttk.Style()
    s.theme_use("default")
    style_name = f"{name}.Treeview"
    s.configure(style_name,
        background=SURF2,
        foreground=TEXT,
        fieldbackground=SURF2,
        bordercolor=BORDER,
        rowheight=30,
        font=("Menlo", 11) if sys.platform == "darwin" else ("Consolas", 10),
    )
    s.configure(f"{name}.Treeview.Heading",
        background=SURF,
        foreground=TEXT_MU,
        font=("Helvetica Neue", 10, "bold") if sys.platform == "darwin" else ("Segoe UI", 9, "bold"),
        bordercolor=BORDER,
        relief="flat",
    )
    s.map(style_name,
        background=[("selected", "#2D3553")],
        foreground=[("selected", AMBER)],
    )
    s.configure("Vertical.TScrollbar",
        background=SURF2, troughcolor=SURF, arrowcolor=TEXT_MU, bordercolor=BORDER,
    )
    return style_name


def _build_tree(parent, columns: list[tuple[str, int]], height: int = 14) -> ttk.Treeview:
    """(col_id, width) pairs → Treeview inside a scrollable container."""
    style_name = _dark_treeview_style()
    frame = ctk.CTkFrame(parent, fg_color=SURF2, corner_radius=8,
                         border_color=BORDER, border_width=1)
    frame.pack(fill="both", expand=True, padx=0, pady=0)

    col_ids = [c[0] for c in columns]
    tv = ttk.Treeview(frame, columns=col_ids, show="headings",
                      style=style_name, height=height)
    for cid, w in columns:
        label = cid.replace("_", " ").title()
        tv.heading(cid, text=label, anchor="w")
        tv.column(cid, width=w, minwidth=40, anchor="w")

    vsb = ttk.Scrollbar(frame, orient="vertical", command=tv.yview)
    tv.configure(yscrollcommand=vsb.set)
    tv.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    return tv


def _label(parent, text: str, size: int = 12, bold: bool = False,
           color: str = TEXT, anchor: str = "w") -> ctk.CTkLabel:
    weight = "bold" if bold else "normal"
    font_family = "Helvetica Neue" if sys.platform == "darwin" else "Segoe UI"
    return ctk.CTkLabel(parent, text=text, anchor=anchor,
                        font=(font_family, size, weight), text_color=color)


def _entry(parent, placeholder: str = "", width: int = 280) -> ctk.CTkEntry:
    return ctk.CTkEntry(parent, placeholder_text=placeholder,
                        fg_color=SURF2, border_color=BORDER, text_color=TEXT,
                        placeholder_text_color=TEXT_MU, corner_radius=6,
                        width=width)


def _btn(parent, text: str, command=None, color: str = AMBER,
         hover: str = AMBER_DK, width: int = 160) -> ctk.CTkButton:
    return ctk.CTkButton(parent, text=text, command=command,
                         fg_color=color, hover_color=hover,
                         text_color="#0D0D0D" if color == AMBER else TEXT,
                         corner_radius=6, width=width, height=34,
                         font=("Helvetica Neue", 12, "bold")
                         if sys.platform == "darwin" else ("Segoe UI", 10, "bold"))


def _ghost_btn(parent, text: str, command=None, width: int = 140) -> ctk.CTkButton:
    return ctk.CTkButton(parent, text=text, command=command,
                         fg_color="transparent", hover_color=SURF2,
                         border_color=BORDER, border_width=1,
                         text_color=TEXT_MU, corner_radius=6,
                         width=width, height=34)


def _combobox(parent, values: list[str], width: int = 280) -> ctk.CTkComboBox:
    return ctk.CTkComboBox(parent, values=values,
                           fg_color=SURF2, border_color=BORDER,
                           button_color=BORDER, button_hover_color=SURF,
                           text_color=TEXT, dropdown_fg_color=SURF2,
                           dropdown_text_color=TEXT, width=width, corner_radius=6)


def _show_success(msg: str) -> None:
    messagebox.showinfo("✓  Éxito", msg)


def _show_error(msg: str) -> None:
    messagebox.showerror("Error", msg)


def _page_header(parent, title: str, breadcrumb: str = "") -> None:
    hdr = ctk.CTkFrame(parent, fg_color=SURF, corner_radius=0)
    hdr.pack(fill="x", padx=0, pady=(0, 0))
    inner = ctk.CTkFrame(hdr, fg_color="transparent")
    inner.pack(fill="x", padx=28, pady=16)
    if breadcrumb:
        _label(inner, breadcrumb, size=10, color=AMBER).pack(anchor="w")
    ff = "Georgia" if sys.platform == "darwin" else "Georgia"
    ctk.CTkLabel(inner, text=title, anchor="w",
                 font=(ff, 22, "bold"), text_color=TEXT).pack(anchor="w", pady=(2, 0))


# ── Cada "página" como CTkScrollableFrame ──────────────────────────────────────
class BasePage(ctk.CTkScrollableFrame):
    def __init__(self, master, app: "App", **kw):
        super().__init__(master, fg_color=BG, **kw)
        self.app = app

    def _get_conn(self):
        return self.app.conn

    def _get_repo(self):
        # DemoConnection solo puede usar repo_demo (DemoCursor no tiene execute SQL).
        if isinstance(self.app.conn, repo_demo.DemoConnection):
            return repo_demo
        return self.app.repo

    def refresh(self):
        pass


class DashboardPage(BasePage):
    def __init__(self, master, app):
        super().__init__(master, app)
        _page_header(self, "Panel General", "Inicio")
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=28, pady=20)

        # stat cards
        cards_frame = ctk.CTkFrame(body, fg_color="transparent")
        cards_frame.pack(fill="x", pady=(0, 24))
        stats = [
            ("Pacientes registrados", "—", AMBER),
            ("Citas pendientes de pago", "—", RED),
            ("Tratamientos activos", "—", GREEN),
            ("Eficacia promedio", "—", AMBER),
        ]
        for i, (lbl, val, col) in enumerate(stats):
            c = ctk.CTkFrame(cards_frame, fg_color=SURF, corner_radius=10,
                             border_color=BORDER, border_width=1)
            c.grid(row=0, column=i, padx=(0, 12) if i < 3 else 0, sticky="nsew")
            cards_frame.grid_columnconfigure(i, weight=1)
            _label(c, lbl, size=10, color=TEXT_MU).pack(anchor="w", padx=16, pady=(14, 2))
            ctk.CTkLabel(c, text=val, anchor="w",
                         font=("Georgia", 28, "bold"), text_color=col).pack(
                anchor="w", padx=16, pady=(0, 14))

        _label(body,
               "Selecciona un módulo en la barra lateral para comenzar.",
               size=13, color=TEXT_MU).pack(anchor="w", pady=8)

        info = ctk.CTkFrame(body, fg_color=AMBER_BG, corner_radius=8,
                            border_color=AMBER_DK, border_width=1)
        info.pack(fill="x", pady=(16, 0))
        _label(info, "  Regla de negocio activa",
               size=11, bold=True, color=AMBER).pack(anchor="w", padx=16, pady=(10, 2))
        _label(info,
               "  El trigger de morosidad bloqueará el agendamiento si el paciente acumula ≥ 2 citas sin pagar.",
               size=11, color=TEXT_MU).pack(anchor="w", padx=16, pady=(0, 10))

    def refresh(self):
        pass


class PacientesPage(BasePage):
    def __init__(self, master, app):
        super().__init__(master, app)
        _page_header(self, "Pacientes", "Administrativo")
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=28, pady=20)

        bar = ctk.CTkFrame(body, fg_color="transparent")
        bar.pack(fill="x", pady=(0, 12))
        _btn(bar, "+ Nuevo Paciente", self._nuevo_dialog, width=170).pack(side="left")
        _ghost_btn(bar, "↺  Actualizar", self.refresh, width=120).pack(side="left", padx=10)

        self.tv = _build_tree(body, [
            ("id", 50), ("nombre", 200), ("nacimiento", 110),
            ("contacto", 130), ("referido_por", 180),
        ], height=16)
        self.refresh()

    def refresh(self):
        for row in self.tv.get_children():
            self.tv.delete(row)
        try:
            with self.app.conn.cursor() as cur:
                rows = self._get_repo().listar_pacientes(cur)
            for r in rows:
                self.tv.insert("", "end", values=r)
        except Exception as e:
            _show_error(str(e))

    def _nuevo_dialog(self):
        dlg = _Dialog(self.app, "Nuevo Paciente", width=480)

        _label(dlg.body, "Nombre completo *").grid(row=0, column=0, sticky="w", pady=4)
        e_nom = _entry(dlg.body, "ej. Laura Martínez", 420)
        e_nom.grid(row=0, column=1, pady=4, padx=(12, 0))

        _label(dlg.body, "Fecha de nacimiento *").grid(row=1, column=0, sticky="w", pady=4)
        e_fn = _entry(dlg.body, "YYYY-MM-DD", 420)
        e_fn.grid(row=1, column=1, pady=4, padx=(12, 0))

        _label(dlg.body, "Contacto *").grid(row=2, column=0, sticky="w", pady=4)
        e_cont = _entry(dlg.body, "ej. 3001234567", 420)
        e_cont.grid(row=2, column=1, pady=4, padx=(12, 0))

        _label(dlg.body, "Referido por (ID)").grid(row=3, column=0, sticky="w", pady=4)
        e_ref = _entry(dlg.body, "dejar vacío = Directo", 420)
        e_ref.grid(row=3, column=1, pady=4, padx=(12, 0))

        def save():
            nom = e_nom.get().strip()
            fn  = e_fn.get().strip()
            cont = e_cont.get().strip()
            if not nom or not fn or not cont:
                _show_error("Nombre, fecha y contacto son obligatorios.")
                return
            ref = int(e_ref.get()) if e_ref.get().strip() else None
            try:
                with self.app.conn.cursor() as cur:
                    nid = self._get_repo().insertar_paciente(cur, nom, fn, cont, ref)
                self.app.conn.commit()
                dlg.destroy()
                _show_success(f"Paciente registrado  ·  ID asignado: {nid}")
                self.refresh()
            except psycopg2.Error as e:
                self.app.conn.rollback()
                _show_error(format_db_error(e))
            except Exception as e:
                self.app.conn.rollback()
                _show_error(str(e))

        _btn(dlg.footer, "Registrar", save).pack(side="right")
        _ghost_btn(dlg.footer, "Cancelar", dlg.destroy).pack(side="right", padx=8)
        dlg.mainloop()


class TratamientosPage(BasePage):
    def __init__(self, master, app):
        super().__init__(master, app)
        _page_header(self, "Tratamientos", "Administrativo")
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=28, pady=20)

        bar = ctk.CTkFrame(body, fg_color="transparent")
        bar.pack(fill="x", pady=(0, 12))
        _btn(bar, "+ Abrir Tratamiento", self._nuevo_dialog, width=180).pack(side="left")
        _ghost_btn(bar, "↺  Actualizar", self.refresh, width=120).pack(side="left", padx=10)

        self.tv = _build_tree(body, [
            ("id", 40), ("paciente", 160), ("médico", 170), ("diagnóstico", 180),
            ("ses_est", 80), ("estado", 90), ("eficacia", 90),
        ], height=16)
        self.refresh()

    def refresh(self):
        for row in self.tv.get_children():
            self.tv.delete(row)
        try:
            with self.app.conn.cursor() as cur:
                for r in self._get_repo().listar_tratamientos(cur):
                    self.tv.insert("", "end", values=r)
        except Exception as e:
            _show_error(str(e))

    def _nuevo_dialog(self):
        dlg = _Dialog(self.app, "Abrir Tratamiento", width=500)

        # pacientes
        pacs = []
        meds = []
        try:
            with self.app.conn.cursor() as cur:
                pacs = self._get_repo().listar_pacientes(cur)
                meds = self._get_repo().listar_medicos_tratantes(cur)
        except Exception:
            pass
        pac_opts = [f"{p[0]} · {p[1]}" for p in pacs]
        med_opts = [f"{m[0]} · {m[1]}" for m in meds]

        _label(dlg.body, "Paciente *").grid(row=0, column=0, sticky="w", pady=4)
        cb_pac = _combobox(dlg.body, pac_opts or ["(sin datos)"], 360)
        cb_pac.grid(row=0, column=1, pady=4, padx=(12, 0))

        _label(dlg.body, "Médico tratante *").grid(row=1, column=0, sticky="w", pady=4)
        cb_med = _combobox(dlg.body, med_opts or ["(sin datos)"], 360)
        cb_med.grid(row=1, column=1, pady=4, padx=(12, 0))

        _label(dlg.body, "Diagnóstico *").grid(row=2, column=0, sticky="w", pady=4)
        e_diag = _entry(dlg.body, "ej. Fractura de fémur", 360)
        e_diag.grid(row=2, column=1, pady=4, padx=(12, 0))

        _label(dlg.body, "Sesiones estimadas *").grid(row=3, column=0, sticky="w", pady=4)
        e_ses = _entry(dlg.body, "ej. 10", 360)
        e_ses.grid(row=3, column=1, pady=4, padx=(12, 0))

        def save():
            try:
                pid = int(cb_pac.get().split(" · ")[0])
                mid = int(cb_med.get().split(" · ")[0])
                diag = e_diag.get().strip()
                ses  = int(e_ses.get().strip())
            except Exception:
                _show_error("Revisa los datos ingresados.")
                return
            if not diag:
                _show_error("Diagnóstico obligatorio.")
                return
            try:
                with self.app.conn.cursor() as cur:
                    tid = self._get_repo().insertar_tratamiento(cur, pid, mid, diag, ses)
                self.app.conn.commit()
                dlg.destroy()
                _show_success(f"Tratamiento abierto  ·  ID: {tid}")
                self.refresh()
            except Exception as e:
                self.app.conn.rollback()
                _show_error(str(e))

        _btn(dlg.footer, "Abrir", save).pack(side="right")
        _ghost_btn(dlg.footer, "Cancelar", dlg.destroy).pack(side="right", padx=8)
        dlg.mainloop()


class CitasPage(BasePage):
    def __init__(self, master, app):
        super().__init__(master, app)
        _page_header(self, "Agendar Cita", "Administrativo · Control de Morosidad")
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", padx=28, pady=20)

        form = ctk.CTkFrame(body, fg_color=SURF, corner_radius=10,
                            border_color=BORDER, border_width=1)
        form.pack(fill="x", pady=(0, 16))
        fi = ctk.CTkFrame(form, fg_color="transparent")
        fi.pack(fill="x", padx=24, pady=20)

        fields = [
            ("ID Tratamiento *", "ej. 1"),
            ("Fecha y Hora *", "YYYY-MM-DD HH:MM"),
            ("Tipo de atención *", "ej. Fisioterapia"),
            ("Monto *", "ej. 50000"),
            ("ID Profesional", "dejar vacío = sin asignar"),
        ]
        self._entries: list[ctk.CTkEntry] = []
        for i, (lbl, ph) in enumerate(fields):
            _label(fi, lbl).grid(row=i, column=0, sticky="w", pady=6)
            e = _entry(fi, ph, 360)
            e.grid(row=i, column=1, pady=6, padx=(16, 0))
            self._entries.append(e)

        self._err_lbl = _label(body, "", size=12, color=RED)
        self._err_lbl.pack(anchor="w", pady=(0, 8))

        btn_row = ctk.CTkFrame(body, fg_color="transparent")
        btn_row.pack(anchor="w")
        _btn(btn_row, "Confirmar Agendamiento", self._agendar, width=220).pack(side="left")
        _ghost_btn(btn_row, "Limpiar", self._clear, width=100).pack(side="left", padx=10)

    def _clear(self):
        for e in self._entries:
            e.delete(0, "end")
        self._err_lbl.configure(text="")

    def _agendar(self):
        self._err_lbl.configure(text="")
        try:
            tid  = int(self._entries[0].get().strip())
            fh   = datetime.strptime(self._entries[1].get().strip(), "%Y-%m-%d %H:%M")
            tipo = self._entries[2].get().strip()
            mont = Decimal(self._entries[3].get().strip())
            prof_raw = self._entries[4].get().strip()
            prof = int(prof_raw) if prof_raw else None
        except Exception:
            self._err_lbl.configure(text="  ✗  Revisa los datos (formato fecha: YYYY-MM-DD HH:MM)")
            return
        try:
            with self.app.conn.cursor() as cur:
                if not self._get_repo().tratamiento_existe(cur, tid):
                    self._err_lbl.configure(text="  ✗  Tratamiento no encontrado.")
                    self.app.conn.rollback()
                    return
                cid = self._get_repo().insertar_cita(cur, tid, fh, tipo, mont, prof)
            self.app.conn.commit()
            self._clear()
            _show_success(f"Cita agendada con éxito  ·  ID cita: {cid}")
        except psycopg2.Error as e:
            self.app.conn.rollback()
            msg = format_db_error(e)
            self._err_lbl.configure(text=f"  ✗  {msg}")
        except ValueError as ve:
            self.app.conn.rollback()
            self._err_lbl.configure(text=f"  ✗  {ve}")


class PagosPage(BasePage):
    def __init__(self, master, app):
        super().__init__(master, app)
        _page_header(self, "Registrar Pago", "Administrativo · FIFO — cita pendiente más antigua")
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", padx=28, pady=20)

        form = ctk.CTkFrame(body, fg_color=SURF, corner_radius=10,
                            border_color=BORDER, border_width=1)
        form.pack(fill="x", ipadx=0, pady=(0, 16), anchor="nw")
        fi = ctk.CTkFrame(form, fg_color="transparent")
        fi.pack(padx=24, pady=20, anchor="w")

        _label(fi, "ID del Tratamiento *").grid(row=0, column=0, sticky="w", pady=8)
        self._e_tid = _entry(fi, "ej. 1", 280)
        self._e_tid.grid(row=0, column=1, pady=8, padx=(16, 0))

        _btn(fi, "Procesar Pago", self._pagar).grid(row=1, column=1, sticky="w", pady=8, padx=(16, 0))

        self._result = ctk.CTkTextbox(body, fg_color=SURF2, text_color=TEXT,
                                      corner_radius=8, height=160,
                                      font=("Menlo", 12) if sys.platform == "darwin" else ("Consolas", 11))
        self._result.pack(fill="x")
        self._result.configure(state="disabled")

    def _pagar(self):
        try:
            tid = int(self._e_tid.get().strip())
        except ValueError:
            _show_error("ID de tratamiento inválido.")
            return
        try:
            with self.app.conn.cursor() as cur:
                row = self._get_repo().aplicar_pago(cur, tid)
            self.app.conn.commit()
            cid, fecha, concepto, monto = row
            txt = (
                f"✓  ¡PAGO PROCESADO EXITOSAMENTE!\n\n"
                f"   ID Cita:   {cid}\n"
                f"   Fecha:     {fecha}\n"
                f"   Concepto:  {concepto}\n"
                f"   Monto:     ${monto}\n"
            )
            self._result.configure(state="normal")
            self._result.delete("0.0", "end")
            self._result.insert("0.0", txt)
            self._result.configure(state="disabled")
        except psycopg2.Error as e:
            self.app.conn.rollback()
            msg = format_db_error(e)
            self._result.configure(state="normal")
            self._result.delete("0.0", "end")
            self._result.insert("0.0", f"✗  {msg}")
            self._result.configure(state="disabled")
        except ValueError as ve:
            self.app.conn.rollback()
            _show_error(str(ve))


class EvolucionPage(BasePage):
    def __init__(self, master, app):
        super().__init__(master, app)
        _page_header(self, "Registrar Evolución", "Médico")
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", padx=28, pady=20)

        form = ctk.CTkFrame(body, fg_color=SURF, corner_radius=10,
                            border_color=BORDER, border_width=1)
        form.pack(fill="x", pady=(0, 16))
        fi = ctk.CTkFrame(form, fg_color="transparent")
        fi.pack(fill="x", padx=24, pady=20)

        _label(fi, "ID de la Cita *").grid(row=0, column=0, sticky="w", pady=8)
        self._e_cid = _entry(fi, "ej. 2", 340)
        self._e_cid.grid(row=0, column=1, pady=8, padx=(16, 0))

        _label(fi, "Nota de Evolución *").grid(row=1, column=0, sticky="nw", pady=8)
        self._txt = ctk.CTkTextbox(fi, fg_color=SURF2, text_color=TEXT,
                                   corner_radius=6, height=100, width=340)
        self._txt.grid(row=1, column=1, pady=8, padx=(16, 0))

        hint = ctk.CTkLabel(fi, text="La nota anterior quedará registrada en la tabla de auditoría.",
                            text_color=TEXT_MU, font=("Helvetica Neue", 10), anchor="w")
        hint.grid(row=2, column=1, sticky="w", padx=(16, 0))

        btn_r = ctk.CTkFrame(body, fg_color="transparent")
        btn_r.pack(anchor="w")
        _btn(btn_r, "Guardar Evolución", self._guardar, width=180).pack(side="left")
        _ghost_btn(btn_r, "Limpiar", self._clear, width=100).pack(side="left", padx=10)

    def _clear(self):
        self._e_cid.delete(0, "end")
        self._txt.delete("0.0", "end")

    def _guardar(self):
        try:
            cid = int(self._e_cid.get().strip())
        except ValueError:
            _show_error("ID de cita inválido.")
            return
        nota = self._txt.get("0.0", "end").strip()
        if not nota:
            _show_error("La nota de evolución no puede estar vacía.")
            return
        try:
            with self.app.conn.cursor() as cur:
                if not self._get_repo().cita_existe(cur, cid):
                    _show_error("Cita no encontrada.")
                    self.app.conn.rollback()
                    return
                self._get_repo().actualizar_evolucion(cur, cid, nota)
            self.app.conn.commit()
            self._clear()
            _show_success("Evolución registrada  ·  Auditoría guardada en base de datos.")
        except Exception as e:
            self.app.conn.rollback()
            _show_error(str(e))


class CierrePage(BasePage):
    def __init__(self, master, app):
        super().__init__(master, app)
        _page_header(self, "Finalizar Tratamiento", "Médico · Trigger de Eficacia")
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", padx=28, pady=20)

        warn = ctk.CTkFrame(body, fg_color=AMBER_BG, corner_radius=8,
                            border_color=AMBER_DK, border_width=1)
        warn.pack(fill="x", pady=(0, 16))
        _label(warn,
               "  Esta acción es irreversible. El tratamiento pasará a FINALIZADO y se calculará la eficacia.",
               size=11, color=TEXT_MU).pack(anchor="w", padx=16, pady=10)

        form = ctk.CTkFrame(body, fg_color=SURF, corner_radius=10,
                            border_color=BORDER, border_width=1)
        form.pack(fill="x")
        fi = ctk.CTkFrame(form, fg_color="transparent")
        fi.pack(padx=24, pady=20, anchor="w")

        _label(fi, "ID del Tratamiento *").grid(row=0, column=0, sticky="w", pady=8)
        self._e_tid = _entry(fi, "ej. 1", 280)
        self._e_tid.grid(row=0, column=1, pady=8, padx=(16, 0))

        self._result_lbl = _label(body, "", size=13, color=GREEN)
        self._result_lbl.pack(anchor="w", pady=(16, 0))

        _btn(fi, "Finalizar y Calcular", self._finalizar, width=200).grid(
            row=1, column=1, sticky="w", pady=8, padx=(16, 0)
        )

    def _finalizar(self):
        self._result_lbl.configure(text="")
        try:
            tid = int(self._e_tid.get().strip())
        except ValueError:
            _show_error("ID inválido.")
            return
        try:
            with self.app.conn.cursor() as cur:
                if not self._get_repo().tratamiento_existe(cur, tid):
                    _show_error("Tratamiento no encontrado.")
                    self.app.conn.rollback()
                    return
                row = self._get_repo().finalizar_tratamiento(cur, tid)
            self.app.conn.commit()
            _, _est, efic, _se = row
            efic_s = f"{efic}%" if efic is not None else "N/D"
            self._result_lbl.configure(
                text=f"  ✓  Tratamiento #{tid} cerrado  ·  Eficacia: {efic_s}")
        except Exception as e:
            self.app.conn.rollback()
            _show_error(str(e))


class OrganigramaPage(BasePage):
    def __init__(self, master, app):
        super().__init__(master, app)
        _page_header(self, "Organigrama", "Gerencia · CTE Recursiva")
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=28, pady=20)

        bar = ctk.CTkFrame(body, fg_color="transparent")
        bar.pack(fill="x", pady=(0, 12))
        _ghost_btn(bar, "↺  Actualizar", self.refresh, width=120).pack(side="left")

        self.tv = _build_tree(body, [
            ("nivel", 60), ("nombre", 220), ("rol", 130), ("especialidad", 200), ("supervisor_id", 100),
        ], height=16)
        self.refresh()

    def refresh(self):
        for row in self.tv.get_children():
            self.tv.delete(row)
        try:
            with self.app.conn.cursor() as cur:
                rows = self._get_repo().organigrama_empleados(cur)
            # build tree
            from collections import defaultdict
            by_sup: dict = defaultdict(list)
            for eid, nom, esp, sup, rol in rows:
                by_sup[sup].append((eid, nom, esp, sup, rol))

            def walk(parent_id, nivel, tv_parent=""):
                for eid, nom, esp, sup, rol in sorted(by_sup.get(parent_id, []), key=lambda x: x[1]):
                    indent = "  " * nivel
                    iid = self.tv.insert(tv_parent, "end",
                                        values=(nivel, f"{indent}└─ {nom}", rol, esp, sup or "—"))
                    walk(eid, nivel + 1, iid)

            walk(None, 0)
            # expand all
            def expand_all(item):
                self.tv.item(item, open=True)
                for child in self.tv.get_children(item):
                    expand_all(child)
            for item in self.tv.get_children():
                expand_all(item)
        except Exception as e:
            _show_error(str(e))


class AdherenciaPage(BasePage):
    def __init__(self, master, app):
        super().__init__(master, app)
        _page_header(self, "Reporte de Adherencia", "Gerencia · Window Functions")
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=28, pady=20)

        bar = ctk.CTkFrame(body, fg_color="transparent")
        bar.pack(fill="x", pady=(0, 12))
        _ghost_btn(bar, "↺  Actualizar", self.refresh, width=120).pack(side="left")
        _label(bar, "  ≤ 7d = ALTA   ≤ 15d = MEDIA   > 15d = BAJA",
               size=10, color=TEXT_MU).pack(side="left", padx=12)

        self.tv = _build_tree(body, [
            ("paciente", 220), ("promedio_días", 120), ("estado", 240),
        ], height=16)
        self.refresh()

    def refresh(self):
        for row in self.tv.get_children():
            self.tv.delete(row)
        try:
            with self.app.conn.cursor() as cur:
                rows = self._get_repo().reporte_adherencia(cur)
            for nom, prom, estado in rows:
                self.tv.insert("", "end", values=(nom, prom, estado))
        except Exception as e:
            _show_error(str(e))


class ReferidosPage(BasePage):
    def __init__(self, master, app):
        super().__init__(master, app)
        _page_header(self, "Red de Referidos", "Gerencia · CTE Recursiva")
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=28, pady=20)

        bar = ctk.CTkFrame(body, fg_color="transparent")
        bar.pack(fill="x", pady=(0, 12))
        _ghost_btn(bar, "↺  Actualizar", self.refresh, width=120).pack(side="left")

        self.tv = _build_tree(body, [
            ("nivel", 60), ("paciente", 200), ("cadena", 400),
        ], height=16)
        self.refresh()

    def refresh(self):
        for row in self.tv.get_children():
            self.tv.delete(row)
        try:
            with self.app.conn.cursor() as cur:
                rows = self._get_repo().cadena_referidos(cur)
            for pid, nom, nivel, cadena in rows:
                self.tv.insert("", "end", values=(nivel, nom, cadena))
        except Exception as e:
            _show_error(str(e))


# ── Diálogo modal reutilizable ─────────────────────────────────────────────────
class _Dialog(ctk.CTkToplevel):
    def __init__(self, master, title: str, width: int = 460):
        super().__init__(master)
        self.title(title)
        self.geometry(f"{width}x500")
        self.configure(fg_color=BG)
        self.resizable(False, False)
        self.grab_set()

        hdr = ctk.CTkFrame(self, fg_color=SURF, corner_radius=0)
        hdr.pack(fill="x")
        ctk.CTkLabel(hdr, text=title, anchor="w",
                     font=("Georgia", 18, "bold"), text_color=TEXT).pack(
            anchor="w", padx=24, pady=14)

        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.pack(fill="both", expand=True, padx=24, pady=16)

        sep = ctk.CTkFrame(self, fg_color=BORDER, height=1)
        sep.pack(fill="x")

        self.footer = ctk.CTkFrame(self, fg_color=SURF, corner_radius=0)
        self.footer.pack(fill="x")
        ctk.CTkFrame(self.footer, fg_color="transparent", height=12).pack()


# ── Sidebar ────────────────────────────────────────────────────────────────────
class Sidebar(ctk.CTkFrame):
    _ITEMS = [
        ("dashboard",    "  ⊞  Panel General",      None),
        (None,           None,                       "Administrativo"),
        ("pacientes",    "  ◎  Pacientes",           None),
        ("tratamientos", "  ☰  Tratamientos",        None),
        ("citas",        "  ◈  Agendar Cita",        None),
        ("pagos",        "  ◷  Registrar Pago",      None),
        (None,           None,                       "Médico"),
        ("evolucion",    "  ✎  Evolución",           None),
        ("cierre",       "  ✓  Finalizar Trat.",     None),
        (None,           None,                       "Gerencia"),
        ("organigrama",  "  ⊾  Organigrama",         None),
        ("adherencia",   "  ▦  Adherencia",          None),
        ("referidos",    "  ⊹  Red Referidos",       None),
    ]

    def __init__(self, master, navigate_cb):
        super().__init__(master, fg_color=SURF, corner_radius=0,
                         border_color=BORDER, border_width=0,
                         width=210)
        self.pack_propagate(False)
        self._cb = navigate_cb
        self._btns: dict[str, ctk.CTkButton] = {}
        self._active = "dashboard"

        # Logo
        logo_f = ctk.CTkFrame(self, fg_color="transparent")
        logo_f.pack(fill="x", padx=18, pady=(20, 10))
        ctk.CTkLabel(logo_f, text="OrthoConnect",
                     font=("Georgia", 16, "bold"), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(logo_f, text="v1.0  ·  Sistema Clínico",
                     font=("Helvetica Neue", 9), text_color=TEXT_MU).pack(anchor="w")

        ctk.CTkFrame(self, fg_color=BORDER, height=1).pack(fill="x", pady=8)

        # Nav items
        ff = "Helvetica Neue" if sys.platform == "darwin" else "Segoe UI"
        for key, label, section in self._ITEMS:
            if section:
                ctk.CTkLabel(self, text=f"  {section.upper()}",
                             anchor="w", text_color=TEXT_MU,
                             font=(ff, 9, "bold")).pack(fill="x", padx=8, pady=(10, 2))
                continue
            btn = ctk.CTkButton(self, text=label, anchor="w",
                                command=lambda k=key: self._nav(k),
                                fg_color="transparent",
                                hover_color=SURF2,
                                text_color=TEXT_MU,
                                corner_radius=6, height=32,
                                font=(ff, 12))
            btn.pack(fill="x", padx=8, pady=1)
            self._btns[key] = btn
        self._set_active("dashboard")

    def _nav(self, key: str) -> None:
        self._set_active(key)
        self._cb(key)

    def _set_active(self, key: str) -> None:
        if self._active in self._btns:
            self._btns[self._active].configure(fg_color="transparent", text_color=TEXT_MU)
        self._active = key
        if key in self._btns:
            self._btns[key].configure(fg_color=AMBER_BG, text_color=AMBER)


# ── App principal ──────────────────────────────────────────────────────────────
class App(ctk.CTk):
    def __init__(self, conn, repo_mod):
        super().__init__()
        repo_mod = effective_repo_for_connection(conn, repo_mod)
        self.conn = conn
        self.repo = repo_mod

        self.title("OrthoConnect v1.0")
        self.geometry("1100x700")
        self.minsize(900, 600)
        self.configure(fg_color=BG)

        # Layout: sidebar + content
        self.sidebar = Sidebar(self, self._navigate)
        self.sidebar.pack(side="left", fill="y")

        # Thin amber accent border
        sep = ctk.CTkFrame(self, fg_color=BORDER, width=1)
        sep.pack(side="left", fill="y")

        self.content = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        self.content.pack(side="left", fill="both", expand=True)

        # Build all pages
        self._pages: dict[str, BasePage] = {}
        page_classes = {
            "dashboard":    DashboardPage,
            "pacientes":    PacientesPage,
            "tratamientos": TratamientosPage,
            "citas":        CitasPage,
            "pagos":        PagosPage,
            "evolucion":    EvolucionPage,
            "cierre":       CierrePage,
            "organigrama":  OrganigramaPage,
            "adherencia":   AdherenciaPage,
            "referidos":    ReferidosPage,
        }
        for key, cls in page_classes.items():
            page = cls(self.content, self)
            page.place(relx=0, rely=0, relwidth=1, relheight=1)
            self._pages[key] = page

        self._navigate("dashboard")

    def _navigate(self, key: str) -> None:
        for page in self._pages.values():
            page.place_forget()
        page = self._pages.get(key)
        if page:
            page.place(relx=0, rely=0, relwidth=1, relheight=1)
            page.refresh()
        self.sidebar._set_active(key)

    def on_close(self):
        try:
            self.conn.close()
        except Exception:
            pass
        self.destroy()


# ── Ventana de inicio ──────────────────────────────────────────────────────────
class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("OrthoConnect — Iniciar sesión")
        self.geometry("460x420")
        self.resizable(False, False)
        self.configure(fg_color=BG)

        self.result: Optional[tuple] = None  # (conn, repo_mod)

        # Card
        card = ctk.CTkFrame(self, fg_color=SURF, corner_radius=14,
                            border_color=BORDER, border_width=1)
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.88)

        # Logo area
        ctk.CTkLabel(card, text="OrthoConnect",
                     font=("Georgia", 26, "bold"), text_color=TEXT).pack(pady=(28, 2))
        ctk.CTkLabel(card, text="Sistema Clínico · v1.0",
                     font=("Helvetica Neue", 11), text_color=TEXT_MU).pack()

        ctk.CTkFrame(card, fg_color=BORDER, height=1).pack(fill="x", pady=16)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=28, fill="x")

        _label(inner, "Modo de conexión").pack(anchor="w", pady=(0, 4))
        self._mode = ctk.CTkSegmentedButton(
            inner, values=["Demo (sin BD)", "PostgreSQL"],
            fg_color=SURF2, selected_color=AMBER, selected_hover_color=AMBER_DK,
            unselected_color=SURF2, unselected_hover_color=SURF,
            text_color=TEXT, font=("Helvetica Neue", 11),
        )
        self._mode.set("PostgreSQL")
        self._mode.pack(fill="x", pady=(0, 14))

        _label(inner, "Nombre del operador").pack(anchor="w", pady=(0, 4))
        self._e_user = _entry(inner, "ej. admin", width=380)
        self._e_user.pack(fill="x", pady=(0, 14))

        self._err = _label(inner, "", size=11, color=RED)
        self._err.pack(anchor="w", pady=(0, 4))

        _btn(inner, "Ingresar", self._login, width=380).pack(fill="x", pady=(4, 0))

        ctk.CTkLabel(card, text="", height=16).pack()  # spacing

    def _login(self):
        self._err.configure(text="")
        mode = self._mode.get()
        user = self._e_user.get().strip() or "gui"

        if "Demo" in mode:
            conn = repo_demo.DemoConnection()
            conn.data.app_user = user
            self.result = (conn, repo_demo)
            self.destroy()
            return

        try:
            conn = connect()
            set_application_name(conn, user)
            conn.commit()
            self.result = (conn, repo_pg)
            self.destroy()
        except psycopg2.Error as e:
            self._err.configure(text=f"  ✗  {e}")


# ── Entry point ────────────────────────────────────────────────────────────────
def main() -> None:
    login = LoginWindow()
    login.mainloop()

    if login.result is None:
        sys.exit(0)

    conn, repo_mod = login.result
    app = App(conn, repo_mod)
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()


if __name__ == "__main__":
    main()
