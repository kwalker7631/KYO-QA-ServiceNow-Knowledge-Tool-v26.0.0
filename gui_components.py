# gui_components.py - Improved UI with consistent colors and processing indicator
import tkinter as tk
from tkinter import ttk

def create_processing_indicator(parent, app):
    """Creates a processing status crawler at the top of the interface."""
    # Processing frame at the very top
    proc_frame = ttk.Frame(parent, style="Processing.TFrame", padding=(10, 5))
    proc_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
    proc_frame.columnconfigure(1, weight=1)
    
    # Processing status indicator
    app.proc_status_label = ttk.Label(proc_frame, text="● Ready", 
                                     style="ProcessingStatus.TLabel", 
                                     font=("Segoe UI", 10, "bold"))
    app.proc_status_label.grid(row=0, column=0, sticky="w")
    
    # Processing crawler/progress text
    app.proc_crawler = ttk.Label(proc_frame, text="Waiting for input...", 
                                style="ProcessingCrawler.TLabel")
    app.proc_crawler.grid(row=0, column=1, sticky="ew", padx=(10, 0))
    
    # Processing speed indicator
    app.proc_speed = ttk.Label(proc_frame, text="", 
                              style="ProcessingSpeed.TLabel")
    app.proc_speed.grid(row=0, column=2, sticky="e")
    
    return proc_frame

def create_main_header(parent, version, colors):
    """Creates the main application header with consistent styling."""
    header = ttk.Frame(parent, style="Header.TFrame", padding=(15, 12))
    header.grid(row=1, column=0, sticky="ew")
    header.columnconfigure(1, weight=1)
    
    # App branding
    brand_frame = ttk.Frame(header, style="Header.TFrame")
    brand_frame.pack(side=tk.LEFT, fill="y")
    
    ttk.Label(brand_frame, text="KYOCERA", 
             foreground=colors.get("kyocera_red", "#CC0000"), 
             font=("Arial Black", 24)).pack(side=tk.TOP, anchor="w")
    ttk.Label(brand_frame, text=f"QA Knowledge Tool v{version}", 
             font=("Segoe UI", 12), 
             foreground=colors.get("header_text", "#666666")).pack(side=tk.TOP, anchor="w")
    
    # Status indicators on the right
    status_frame = ttk.Frame(header, style="Header.TFrame")
    status_frame.pack(side=tk.RIGHT, fill="y", padx=(20, 0))
    
    # Connection status
    ttk.Label(status_frame, text="System Status:", 
             font=("Segoe UI", 9), 
             foreground=colors.get("label_text", "#666666")).pack(anchor="e")
    
    # Add separator
    ttk.Separator(header, orient='horizontal').pack(side="bottom", fill="x", pady=(10, 0))

def create_io_section(parent, app):
    """Creates the input/output section with improved styling."""
    io = ttk.LabelFrame(parent, text="📁 Input Selection", 
                       padding=15, style="Card.TLabelframe")
    io.grid(row=2, column=0, sticky="ew", pady=(5, 10))
    io.columnconfigure(1, weight=1)

    # Excel input
    ttk.Label(io, text="Excel Template:", style="Label.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 8), padx=(0, 10))
    ttk.Entry(io, textvariable=app.selected_excel, style="Input.TEntry").grid(row=0, column=1, sticky="ew", padx=(0, 8))
    ttk.Button(io, text="📄 Browse", command=app.browse_excel, style="Browse.TButton").grid(row=0, column=2)

    # PDF folder input
    ttk.Label(io, text="PDFs Folder:", style="Label.TLabel").grid(row=1, column=0, sticky="w", pady=(0, 8), padx=(0, 10))
    ttk.Entry(io, textvariable=app.selected_folder, style="Input.TEntry").grid(row=1, column=1, sticky="ew", padx=(0, 8))
    ttk.Button(io, text="📂 Browse", command=app.browse_folder, style="Browse.TButton").grid(row=1, column=2)

    # Individual files option
    files_frame = ttk.Frame(io)
    files_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(10, 0))
    files_frame.columnconfigure(0, weight=1)
    
    ttk.Label(files_frame, text="OR select individual files:", 
             style="Label.Secondary.TLabel").pack(side=tk.LEFT)
    ttk.Button(files_frame, text="📎 Select Files", command=app.browse_files, 
              style="Browse.Secondary.TButton").pack(side=tk.RIGHT)

def create_process_controls(parent, app):
    """Creates the process control section with improved button layout."""
    ctrl = ttk.LabelFrame(parent, text="⚙️ Process Controls", 
                         padding=15, style="Card.TLabelframe")
    ctrl.grid(row=3, column=0, sticky="ew", pady=(0, 10))
    ctrl.columnconfigure((0, 1, 2, 3), weight=1)

    # Main START button (prominent)
    app.process_btn = ttk.Button(ctrl, text="🚀 START PROCESSING", 
                                command=app.start_processing, 
                                style="Start.TButton")
    app.process_btn.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 10))

    # Control buttons row
    app.pause_btn = ttk.Button(ctrl, text="⏸️ Pause", command=app.toggle_pause, 
                              state=tk.DISABLED, style="Control.TButton")
    app.pause_btn.grid(row=1, column=0, sticky="ew", padx=(0, 5))
    
    app.stop_btn = ttk.Button(ctrl, text="⏹️ Stop", command=app.stop_processing, 
                             state=tk.DISABLED, style="Control.TButton")
    app.stop_btn.grid(row=1, column=1, sticky="ew", padx=5)
    
    app.rerun_btn = ttk.Button(ctrl, text="🔄 Re-run Flagged", command=app.rerun_flagged_job, 
                              state=tk.DISABLED, style="Control.TButton")
    app.rerun_btn.grid(row=1, column=2, sticky="ew", padx=5)
    
    app.open_result_btn = ttk.Button(ctrl, text="📊 Open Result", command=app.open_result, 
                                    state=tk.DISABLED, style="Success.TButton")
    app.open_result_btn.grid(row=1, column=3, sticky="ew", padx=(5, 0))
    
    # Utility buttons row
    app.review_btn = ttk.Button(ctrl, text="🔍 Patterns", command=app.open_pattern_manager,
                               style="Utility.TButton")
    app.review_btn.grid(row=2, column=0, sticky="ew", padx=(0, 5), pady=(10, 0))
    
    app.locked_files_btn = ttk.Button(ctrl, text="🔒 Locked Files", command=app.handle_locked_files,
                                     style="Warning.TButton")
    app.locked_files_btn.grid(row=2, column=1, sticky="ew", padx=5, pady=(10, 0))
    
    app.fullscreen_btn = ttk.Button(ctrl, text="⛶ Fullscreen", command=app.toggle_fullscreen,
                                   style="Utility.TButton")
    app.fullscreen_btn.grid(row=2, column=2, sticky="ew", padx=5, pady=(10, 0))
    
    app.exit_btn = ttk.Button(ctrl, text="❌ Exit", command=app.on_closing,
                             style="Exit.TButton")
    app.exit_btn.grid(row=2, column=3, sticky="ew", padx=(5, 0), pady=(10, 0))

def create_status_and_log_section(parent, app):
    """Creates the status monitoring section with better organization."""
    stat = ttk.LabelFrame(parent, text="📊 Status Monitor", 
                         padding=15, style="Card.TLabelframe")
    stat.grid(row=4, column=0, sticky="nsew", pady=(0, 10))
    stat.columnconfigure(0, weight=1)
    stat.rowconfigure(5, weight=1)

    # Current file status
    current_frame = ttk.Frame(stat, style="Status.TFrame", padding=(10, 8))
    current_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
    current_frame.columnconfigure(1, weight=1)
    
    app.led_label = ttk.Label(current_frame, text="●", style="LED.TLabel", font=("Arial", 12))
    app.led_label.grid(row=0, column=0, sticky="w")
    
    ttk.Label(current_frame, text="Processing:", style="Status.Label.TLabel").grid(row=0, column=1, sticky="w", padx=(8, 5))
    
    app.status_current_file = tk.StringVar(value="Ready to start...")
    ttk.Label(current_frame, textvariable=app.status_current_file, 
             style="Status.File.TLabel").grid(row=0, column=2, sticky="ew")

    # Progress bar with time remaining
    prog_frame = ttk.Frame(stat)
    prog_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
    prog_frame.columnconfigure(0, weight=1)
    
    app.progress_bar = ttk.Progressbar(prog_frame, style="Progress.Horizontal.TProgressbar")
    app.progress_bar.grid(row=0, column=0, sticky="ew", padx=(0, 10))
    
    app.time_remaining_var = tk.StringVar(value="")
    ttk.Label(prog_frame, textvariable=app.time_remaining_var, 
             style="Time.TLabel").grid(row=0, column=1, sticky="e")

    # Statistics summary
    stats_frame = ttk.Frame(stat, style="Stats.TFrame", padding=(10, 8))
    stats_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
    
    ttk.Label(stats_frame, text="Results:", style="Stats.Header.TLabel").pack(side="left")
    
    # Initialize count variables if they don't exist
    if not hasattr(app, 'count_pass'):
        app.count_pass = tk.StringVar(value="0")
        app.count_fail = tk.StringVar(value="0") 
        app.count_review = tk.StringVar(value="0")
        app.count_ocr = tk.StringVar(value="0")
        app.count_locked = tk.StringVar(value="0")
    
    stats = [
        ("✅ Pass:", app.count_pass, "Success"),
        ("❌ Fail:", app.count_fail, "Error"), 
        ("⚠️ Review:", app.count_review, "Warning"),
        ("👁️ OCR:", app.count_ocr, "Info"),
        ("🔒 Locked:", app.count_locked, "Locked")
    ]
    
    for text, var, style in stats:
        ttk.Label(stats_frame, text=text, style="Stats.Label.TLabel").pack(side="left", padx=(20, 5))
        ttk.Label(stats_frame, textvariable=var, style=f"Count.{style}.TLabel").pack(side="left")

    # Files requiring review/attention
    review_frame = ttk.LabelFrame(stat, text="⚠️ Files Requiring Attention", padding=10)
    review_frame.grid(row=3, column=0, sticky="nsew", pady=(0, 10))
    review_frame.rowconfigure(1, weight=1)
    review_frame.columnconfigure(0, weight=1)
    
    # Review controls
    review_controls = ttk.Frame(review_frame)
    review_controls.grid(row=0, column=0, sticky="ew", pady=(0, 5))
    review_controls.columnconfigure(0, weight=1)
    
    app.review_file_btn = ttk.Button(review_controls, text="🔍 Review Selected", 
                                    command=app.open_review_for_selected_file, 
                                    state=tk.DISABLED, style="Review.TButton")
    app.review_file_btn.pack(side=tk.RIGHT)
    
    # Tabbed view for different file types
    review_notebook = ttk.Notebook(review_frame)
    review_notebook.grid(row=1, column=0, sticky="nsew")
    
    # Review files tab
    review_tab = ttk.Frame(review_notebook)
    review_notebook.add(review_tab, text="Review")
    
    app.review_tree = ttk.Treeview(review_tab, columns=('file', 'reason'), show='headings', height=3)
    app.review_tree.pack(fill="both", expand=True)
    app.review_tree.heading('file', text='File Name')
    app.review_tree.heading('reason', text='Reason')
    app.review_tree.column('reason', width=150)
    
    # Locked files tab
    locked_tab = ttk.Frame(review_notebook)
    review_notebook.add(locked_tab, text="Locked Files")
    
    app.locked_tree = ttk.Treeview(locked_tab, columns=('file', 'status'), show='headings', height=3)
    app.locked_tree.pack(fill="both", expand=True)
    app.locked_tree.heading('file', text='File Name')
    app.locked_tree.heading('status', text='Status')
    app.locked_tree.column('status', width=100)
    
    # Bind selection events
    app.review_tree.bind("<<TreeviewSelect>>", 
                        lambda e: app.review_file_btn.config(state=tk.NORMAL if app.review_tree.selection() else tk.DISABLED))

    # Log section
    log_frame = ttk.LabelFrame(stat, text="📋 Processing Log", padding=10)
    log_frame.grid(row=5, column=0, sticky="nsew")
    log_frame.rowconfigure(0, weight=1)
    log_frame.columnconfigure(0, weight=1)
    
    app.log_text = tk.Text(log_frame, height=6, wrap=tk.WORD, state=tk.DISABLED, 
                          relief="flat", borderwidth=0, font=("Consolas", 9),
                          bg="#f8f9fa", fg="#212529")
    app.log_text.grid(row=0, column=0, sticky="nsew")
    
    log_scroll = ttk.Scrollbar(log_frame, command=app.log_text.yview)
    log_scroll.grid(row=0, column=1, sticky="ns")
    app.log_text.config(yscrollcommand=log_scroll.set)

def setup_modern_styles(app):
    """Sets up modern, consistent styling for the application."""
    style = ttk.Style()
    
    # Configure modern color scheme
    colors = {
        'primary': '#2563eb',      # Blue
        'primary_hover': '#1d4ed8',
        'success': '#059669',      # Green  
        'warning': '#d97706',      # Orange
        'error': '#dc2626',        # Red
        'info': '#0891b2',         # Cyan
        'background': '#ffffff',   # White
        'surface': '#f8fafc',      # Light gray
        'border': '#e2e8f0',       # Gray border
        'text': '#1e293b',         # Dark gray text
        'text_secondary': '#64748b' # Medium gray text
    }
    
    # Frame styles
    style.configure('Card.TLabelframe', background=colors['surface'], borderwidth=1, relief='solid')
    style.configure('Card.TLabelframe.Label', background=colors['surface'], foreground=colors['text'], font=('Segoe UI', 10, 'bold'))
    
    # Processing indicator styles
    style.configure('Processing.TFrame', background=colors['primary'], relief='flat')
    style.configure('ProcessingStatus.TLabel', background=colors['primary'], foreground='white')
    style.configure('ProcessingCrawler.TLabel', background=colors['primary'], foreground='white')
    style.configure('ProcessingSpeed.TLabel', background=colors['primary'], foreground='white', font=('Segoe UI', 9))
    
    # Header styles
    style.configure('Header.TFrame', background=colors['background'])
    
    # Button styles
    style.configure('Start.TButton', font=('Segoe UI', 11, 'bold'))
    style.map('Start.TButton', background=[('active', colors['primary_hover']), ('!active', colors['primary'])])
    
    style.configure('Success.TButton', foreground='white')
    style.map('Success.TButton', background=[('active', colors['success']), ('!active', colors['success'])])
    
    style.configure('Warning.TButton', foreground='white')
    style.map('Warning.TButton', background=[('active', colors['warning']), ('!active', colors['warning'])])
    
    style.configure('Control.TButton', foreground=colors['text'])
    style.configure('Utility.TButton', foreground=colors['text'])
    style.configure('Review.TButton', foreground=colors['text'])
    
    style.configure('Exit.TButton', foreground='white')
    style.map('Exit.TButton', background=[('active', colors['error']), ('!active', colors['error'])])
    
    # Entry styles
    style.configure('Input.TEntry', borderwidth=1, relief='solid', fieldbackground='white')
    
    # Label styles
    style.configure('Label.TLabel', foreground=colors['text'], font=('Segoe UI', 9))
    style.configure('Label.Secondary.TLabel', foreground=colors['text_secondary'], font=('Segoe UI', 9))
    
    # Status styles
    style.configure('LED.TLabel', foreground=colors['success'])
    style.configure('Status.TFrame', background=colors['surface'])
    style.configure('Status.Label.TLabel', foreground=colors['text'], font=('Segoe UI', 9, 'bold'))
    style.configure('Status.File.TLabel', foreground=colors['text'])
    
    # Count styles for statistics
    style.configure('Count.Success.TLabel', foreground=colors['success'], font=('Segoe UI', 9, 'bold'))
    style.configure('Count.Error.TLabel', foreground=colors['error'], font=('Segoe UI', 9, 'bold'))
    style.configure('Count.Warning.TLabel', foreground=colors['warning'], font=('Segoe UI', 9, 'bold'))
    style.configure('Count.Info.TLabel', foreground=colors['info'], font=('Segoe UI', 9, 'bold'))
    style.configure('Count.Locked.TLabel', foreground=colors['text_secondary'], font=('Segoe UI', 9, 'bold'))
    
    # Progress bar
    style.configure('Progress.Horizontal.TProgressbar', troughcolor=colors['border'], 
                   background=colors['primary'], borderwidth=0, lightcolor=colors['primary'], 
                   darkcolor=colors['primary'])