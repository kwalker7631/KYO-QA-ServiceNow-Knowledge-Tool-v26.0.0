# gui_components.py
# Version: 32.3.0
# Last modified: 2025-07-07

import tkinter as tk
from tkinter import ttk
import logging
from branding import KyoceraColors

logging.getLogger(__name__).setLevel(logging.DEBUG)


def setup_high_contrast_styles(app):
    style = ttk.Style(app)
    style.theme_use("clam")
    style.configure(
        ".",
        background=KyoceraColors.BACKGROUND_MAIN,
        foreground=KyoceraColors.TEXT_DARK,
        font=("Segoe UI", 11),
    )
    style.configure("TFrame", background=KyoceraColors.BACKGROUND_MAIN)
    style.configure("TLabel", background=KyoceraColors.BACKGROUND_MAIN)
    style.configure(
        "Card.TFrame",
        background=KyoceraColors.WIDGET_BG,
        relief="solid",
        borderwidth=1,
        bordercolor=KyoceraColors.BORDER_COLOR,
    )
    style.configure("Card.TLabel", background=KyoceraColors.WIDGET_BG)
    style.configure(
        "Card.TLabelframe",
        background=KyoceraColors.WIDGET_BG,
        relief="solid",
        borderwidth=1,
        bordercolor=KyoceraColors.BORDER_COLOR,
    )
    style.configure(
        "Card.TLabelframe.Label",
        background=KyoceraColors.WIDGET_BG,
        foreground=KyoceraColors.TEXT_DARK,
        font=("Segoe UI", 12, "bold"),
    )
    style.configure(
        "TButton",
        font=("Segoe UI", 11),
        padding=10,
        relief="raised",
        borderwidth=1,
        bordercolor=KyoceraColors.BORDER_COLOR,
    )
    style.map(
        "TButton",
        background=[
            ("active", KyoceraColors.PRIMARY_ACTION),
            ("!disabled", KyoceraColors.WIDGET_BG),
        ],
        foreground=[("active", "white")],
    )
    style.configure("Start.TButton", font=("Segoe UI", 12, "bold"), foreground="white")
    style.map(
        "Start.TButton",
        background=[
            ("active", KyoceraColors.PRIMARY_ACTION_HOVER),
            ("!disabled", KyoceraColors.PRIMARY_ACTION),
        ],
    )
    style.configure(
        "Footer.TButton", font=("Segoe UI", 9), padding=(5, 3), relief="flat"
    )
    style.map(
        "Footer.TButton",
        background=[("active", "#e2e6ea")],
        bordercolor=[("!active", KyoceraColors.BACKGROUND_MAIN)],
    )
    style.configure(
        "Exit.TButton",
        background=KyoceraColors.HIGH_CONTRAST_BG,
        foreground=KyoceraColors.HIGH_CONTRAST_TEXT,
        font=("Segoe UI", 10, "bold"),
        padding=(5, 3),
    )
    style.map(
        "Exit.TButton",
        background=[("active", KyoceraColors.HIGH_CONTRAST_BG)],
        foreground=[("active", KyoceraColors.HIGH_CONTRAST_TEXT)],
    )
    style.configure(
        "Exit.TButton",
        background=KyoceraColors.HIGH_CONTRAST_BG,
        foreground=KyoceraColors.HIGH_CONTRAST_TEXT,
    )
    style.configure(
        "Treeview",
        rowheight=28,
        fieldbackground=KyoceraColors.WIDGET_BG,
        font=("Segoe UI", 10),
    )
    style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"), padding=5)
    style.map("Treeview", background=[("selected", KyoceraColors.PRIMARY_ACTION)])
    style.configure(
        "Success.TLabel",
        foreground=KyoceraColors.STATUS_SUCCESS,
        background=KyoceraColors.WIDGET_BG,
        font=("Segoe UI", 14, "bold"),
    )
    style.configure(
        "Review.TLabel",
        foreground=KyoceraColors.STATUS_WARNING,
        background=KyoceraColors.WIDGET_BG,
        font=("Segoe UI", 14, "bold"),
    )
    style.configure(
        "Error.TLabel",
        foreground=KyoceraColors.STATUS_ERROR,
        background=KyoceraColors.WIDGET_BG,
        font=("Segoe UI", 14, "bold"),
    )
    style.configure(
        "Default.TLabel",
        foreground=KyoceraColors.TEXT_DARK,
        background=KyoceraColors.WIDGET_BG,
        font=("Segoe UI", 14),
    )
    style.configure(
        "OCR.TLabel",
        foreground=KyoceraColors.PRIMARY_ACTION,
        background=KyoceraColors.WIDGET_BG,
        font=("Segoe UI", 14, "bold"),
    )
    style.configure("ReviewRow", background=KyoceraColors.STATUS_WARNING)
    style.configure(
        "FailRow", background=KyoceraColors.STATUS_ERROR, foreground="white"
    )
    style.configure(
        "EmptyState.TLabel",
        foreground=KyoceraColors.HIGH_CONTRAST_TEXT,
        background=KyoceraColors.HIGH_CONTRAST_BG,
        font=("Segoe UI", 12, "bold"),
    )


def create_main_header(parent, version):
    header_frame = ttk.Frame(parent, padding=(20, 15))
    header_frame.pack(fill="x", padx=10, pady=(10, 5))
    ttk.Label(
        header_frame,
        text="KYOCERA",
        font=("Arial Black", 32),
        foreground=KyoceraColors.KYOCERA_RED,
    ).pack(side="left")
    title_frame = ttk.Frame(header_frame)
    title_frame.pack(side="left", padx=20)
    ttk.Label(
        title_frame, text="QA ServiceNow Knowledge Tool", font=("Segoe UI", 16, "bold")
    ).pack(anchor="w")
    ttk.Label(
        title_frame, text=f"Version: {version}", foreground=KyoceraColors.TEXT_MUTED
    ).pack(anchor="w")


def create_io_section(parent, app):
    io_frame = ttk.LabelFrame(
        parent, text="1. Select Inputs", style="Card.TLabelframe", padding=20
    )
    io_frame.pack(fill="x", padx=10, pady=10)
    io_frame.columnconfigure(1, weight=1)
    ttk.Label(io_frame, text="Excel Template:", style="Card.TLabel").grid(
        row=0, column=0, sticky="w", pady=8, padx=5
    )
    ttk.Entry(io_frame, textvariable=app.selected_excel, font=("Segoe UI", 10)).grid(
        row=0, column=1, sticky="ew", padx=5
    )
    ttk.Button(io_frame, text="Browse...", command=app.browse_excel).grid(
        row=0, column=2, padx=5
    )
    ttk.Label(io_frame, text="PDF Source:", style="Card.TLabel").grid(
        row=1, column=0, sticky="w", pady=8, padx=5
    )
    ttk.Entry(io_frame, textvariable=app.selected_folder, font=("Segoe UI", 10)).grid(
        row=1, column=1, sticky="ew", padx=5
    )
    btn_frame = ttk.Frame(io_frame, style="Card.TFrame")
    btn_frame.grid(row=1, column=2, padx=5)
    ttk.Button(btn_frame, text="Folder", command=app.browse_folder).pack(side="left")
    ttk.Button(btn_frame, text="Files", command=app.browse_files).pack(
        side="left", padx=5
    )
    ttk.Button(btn_frame, text="ZIP", command=app.browse_zip).pack(side="left")


def create_controls_section(parent, app):
    controls_frame = ttk.LabelFrame(
        parent, text="2. Start Process", style="Card.TLabelframe", padding=20
    )
    controls_frame.pack(fill="x", padx=10, pady=10)
    controls_frame.columnconfigure(0, weight=1)
    app.process_btn = ttk.Button(
        controls_frame,
        text="🚀 START PROCESSING",
        style="Start.TButton",
        command=app.start_processing,
    )
    app.process_btn.grid(row=0, column=0, sticky="ew", ipady=8, pady=(0, 10))

    # Button to manually export cached results to Excel
    app.export_btn = ttk.Button(
        controls_frame,
        text="Export to XLSX",
        command=app.manual_export,
    )
    app.export_btn.grid(row=1, column=0, sticky="ew")


def create_live_status_section(parent, app):
    container = ttk.Frame(parent, padding=10)
    container.pack(fill="both", expand=True)
    container.rowconfigure(1, weight=1)
    container.columnconfigure(0, weight=1)

    top_frame = ttk.Frame(container, style="Card.TFrame", padding=20)
    top_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
    top_frame.columnconfigure(0, weight=1)

    activity_frame = ttk.Frame(top_frame, style="Card.TFrame")
    activity_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
    activity_frame.columnconfigure(1, weight=1)
    ttk.Label(
        activity_frame,
        text="Activity:",
        font=("Segoe UI", 11, "bold"),
        style="Card.TLabel",
    ).grid(row=0, column=0, padx=(0, 10))
    ttk.Label(
        activity_frame,
        textvariable=app.status_current_file,
        style="Card.TLabel",
        foreground=KyoceraColors.TEXT_MUTED,
    ).grid(row=0, column=1, sticky="ew")
    app.spinner_label = ttk.Label(activity_frame, text="", width=2, style="Card.TLabel")
    app.spinner_label.grid(row=0, column=2, padx=(5, 10), sticky="e")
    app.progress_bar = ttk.Progressbar(
        activity_frame, variable=app.progress_value, mode="determinate"
    )
    app.progress_bar.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(5, 0))
    ttk.Label(
        activity_frame,
        textvariable=app.progress_percent_var,
        style="Card.TLabel",
        font=("Segoe UI", 10, "bold"),
    ).grid(row=1, column=3, padx=(10, 0), sticky="w")

    stats_frame = ttk.Frame(top_frame, style="Card.TFrame")
    stats_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
    stats_frame.columnconfigure((0, 1, 2, 3, 4), weight=1)
    stats = [
        ("Processed", app.count_processed, "Default.TLabel"),
        ("Passed", app.count_pass, "Success.TLabel"),
        ("Needs Review", app.count_review, "Review.TLabel"),
        ("Errors", app.count_fail, "Error.TLabel"),
        ("OCR Used", app.count_ocr, "OCR.TLabel"),
    ]  # ADDED OCR
    for i, (text, var, style) in enumerate(stats):
        f = ttk.Frame(stats_frame, style="Card.TFrame")
        f.grid(row=0, column=i, sticky="ew", padx=5)
        ttk.Label(
            f, text=text, font=("Segoe UI", 10, "bold"), style="Card.TLabel"
        ).pack()
        ttk.Label(f, textvariable=var, style=style).pack()

    bottom_pane = ttk.PanedWindow(container, orient=tk.HORIZONTAL)
    bottom_pane.grid(row=1, column=0, sticky="nsew")

    review_pane = ttk.Frame(bottom_pane, style="Card.TFrame", padding=15)
    review_pane.rowconfigure(1, weight=1)
    review_pane.columnconfigure(0, weight=1)
    bottom_pane.add(review_pane, weight=1)
    ttk.Label(
        review_pane,
        text="Files for Review",
        font=("Segoe UI", 12, "bold"),
        style="Card.TLabel",
    ).grid(row=0, column=0, sticky="w", pady=(0, 10))
    app.review_tree = ttk.Treeview(
        review_pane, columns=("file",), show="headings", height=4
    )
    app.review_tree.grid(row=1, column=0, sticky="nsew")
    app.review_tree.heading("file", text="File Name")
    review_scroll = ttk.Scrollbar(
        review_pane, orient="vertical", command=app.review_tree.yview
    )
    review_scroll.grid(row=1, column=1, sticky="ns")
    app.review_tree.configure(yscrollcommand=review_scroll.set)
    app.review_file_btn = ttk.Button(
        review_pane,
        text="🔍 Review Selected File",
        command=app.open_review_for_selected_file,
        state=tk.DISABLED,
    )
    app.review_file_btn.grid(row=2, column=0, columnspan=2, sticky="e", pady=(10, 0))
    app.review_tree.bind(
        "<<TreeviewSelect>>",
        lambda e: app.review_file_btn.config(
            state=tk.NORMAL if app.review_tree.selection() else tk.DISABLED
        ),
    )

    log_pane = ttk.Frame(bottom_pane, style="Card.TFrame", padding=15)
    log_pane.rowconfigure(1, weight=1)
    log_pane.columnconfigure(0, weight=1)
    bottom_pane.add(log_pane, weight=2)
    ttk.Label(
        log_pane,
        text="Processing Log",
        font=("Segoe UI", 12, "bold"),
        style="Card.TLabel",
    ).grid(row=0, column=0, sticky="w", pady=(0, 10))
    app.log_text = tk.Text(
        log_pane,
        wrap=tk.WORD,
        state=tk.DISABLED,
        relief=tk.FLAT,
        font=("Consolas", 10),
        bg=KyoceraColors.WIDGET_BG,
        fg=KyoceraColors.TEXT_DARK,
        borderwidth=0,
        highlightthickness=0,
    )
    app.log_text.grid(row=1, column=0, sticky="nsew")
    log_scroll = ttk.Scrollbar(log_pane, command=app.log_text.yview)
    log_scroll.grid(row=1, column=1, sticky="ns")
    app.log_text.config(yscrollcommand=log_scroll.set)


def create_footer(parent, app):
    footer_frame = ttk.Frame(parent, padding=(10, 5), style="Card.TFrame")
    footer_frame.pack(fill="x", side="bottom")
    app.fullscreen_status_label = ttk.Label(
        footer_frame, textvariable=app.fullscreen_status_var, style="Card.TLabel"
    )
    app.fullscreen_status_label.pack(side="left")
    ttk.Button(
        footer_frame,
        text="Exit Application",
        command=app.on_closing,
        style="Exit.TButton",
    ).pack(side="right")

def create_harvest_tab(parent, app):
    harvest_frame = ttk.Frame(parent, padding=15)
    harvest_frame.pack(fill="both", expand=True)

    select_frame = ttk.Frame(harvest_frame)
    select_frame.pack(fill="x")
    app.harvest_file = tk.StringVar()
    ttk.Entry(
        select_frame,
        textvariable=app.harvest_file,
        font=("Segoe UI", 10),
    ).pack(side="left", fill="x", expand=True, padx=5)
    ttk.Button(select_frame, text="Browse...", command=app.browse_harvest_file).pack(
        side="left", padx=5
    )

    btn_frame = ttk.Frame(harvest_frame)
    btn_frame.pack(fill="x", pady=10)
    app.harvest_run_btn = ttk.Button(
        btn_frame, text="Harvest Data", command=app.harvest_single_file
    )
    app.harvest_run_btn.pack(side="left")
    app.harvest_export_btn = ttk.Button(
        btn_frame,
        text="Export to XLSX",
        command=app.export_harvest_results,
        state=tk.DISABLED,
    )
    app.harvest_export_btn.pack(side="left", padx=5)

    app.harvest_text = tk.Text(
        harvest_frame,
        wrap=tk.WORD,
        state=tk.DISABLED,
        bg=KyoceraColors.HIGH_CONTRAST_BG,
        fg=KyoceraColors.HIGH_CONTRAST_TEXT,
    )
    app.harvest_text.pack(fill="both", expand=True)

    return harvest_frame

def create_review_tab(parent, app):
    review_frame = ttk.Frame(parent, padding=15)
    review_frame.pack(fill="both", expand=True)

    filter_frame = ttk.Frame(review_frame)
    filter_frame.pack(fill="x", pady=(0, 10))

    ttk.Label(filter_frame, text="Status Filter:", style="Card.TLabel").pack(
        side="left"
    )
    app.review_filter = tk.StringVar(value="All")
    status_box = ttk.Combobox(
        filter_frame,
        textvariable=app.review_filter,
        state="readonly",
        values=["All", "Pass", "Needs Review", "Fail"],
        width=15,
    )
    status_box.pack(side="left", padx=5)
    ttk.Button(filter_frame, text="Load", command=app.load_review_data).pack(
        side="left", padx=5
    )

    app.review_table = ttk.Treeview(
        review_frame, columns=("file", "status"), show="headings"
    )
    app.review_table.heading("file", text="File Name")
    app.review_table.heading("status", text="Status")
    app.review_table.pack(fill="both", expand=True)
    
    # --- FIXED ---
    # The 'style' option is not valid for tag_configure.
    # Instead, we directly configure the background and foreground colors.
    app.review_table.tag_configure("review", background=KyoceraColors.STATUS_WARNING)
    app.review_table.tag_configure("fail", background=KyoceraColors.STATUS_ERROR, foreground="white")
    # --- END FIX ---

    app.empty_label = ttk.Label(
        review_frame,
        text="No items to display",
        style="EmptyState.TLabel",
    )
    app.empty_label.pack(pady=10)
    app.empty_label.pack_forget()

    return review_frame


def create_data_harvest_tab(parent, app):
    """Builds the UI for the Data Harvest tab."""
    style = ttk.Style(parent)
    style.configure(
        "Harvest.TFrame",
        background=KyoceraColors.HIGH_CONTRAST_BG,
    )
    style.configure(
        "Harvest.TLabel",
        background=KyoceraColors.HIGH_CONTRAST_BG,
        foreground=KyoceraColors.HIGH_CONTRAST_TEXT,
    )
    style.configure(
        "Harvest.TButton",
        background=KyoceraColors.HIGH_CONTRAST_BG,
        foreground=KyoceraColors.HIGH_CONTRAST_TEXT,
    )

    harvest_frame = ttk.Frame(parent, padding=20, style="Harvest.TFrame")
    harvest_frame.pack(fill="both", expand=True)

    ttk.Label(
        harvest_frame,
        text="Data harvesting tools will appear here.",
        style="Harvest.TLabel",
    ).pack(pady=10)

    ttk.Button(
        harvest_frame,
        text="Start Harvest",
        style="Harvest.TButton",
        command=lambda: None,
    ).pack(pady=5)

    return harvest_frame
