# gui_components.py
# Version: 31.0.0
# Last modified: 2025-07-06

import tkinter as tk
from tkinter import ttk
from branding import KyoceraColors

def setup_high_contrast_styles(app):
    """Sets up a modern, high-contrast style for all ttk widgets."""
    style = ttk.Style(app)
    style.theme_use('clam')

    # --- General Widget Styling ---
    style.configure('.',
                    background=KyoceraColors.BACKGROUND_MAIN,
                    foreground=KyoceraColors.TEXT_DARK,
                    font=('Segoe UI', 11))
    style.configure('TFrame', background=KyoceraColors.BACKGROUND_MAIN)
    style.configure('TLabel', background=KyoceraColors.BACKGROUND_MAIN)

    # --- Card Styling (for widgets on a white background) ---
    style.configure('Card.TLabelframe', 
                    background=KyoceraColors.WIDGET_BG,
                    relief='solid',
                    borderwidth=1,
                    bordercolor=KyoceraColors.BORDER_COLOR)
    style.configure('Card.TLabelframe.Label', 
                    background=KyoceraColors.WIDGET_BG,
                    foreground=KyoceraColors.TEXT_DARK,
                    font=('Segoe UI', 12, 'bold'))
    
    # Styles for widgets inside a "Card" to ensure they have a white background
    style.configure('Card.TLabel', background=KyoceraColors.WIDGET_BG)
    style.configure('Card.TFrame', background=KyoceraColors.WIDGET_BG)

    # --- Button Styling for Visibility ---
    style.configure('TButton', 
                    font=('Segoe UI', 11), 
                    padding=10, 
                    relief='raised', 
                    borderwidth=1,
                    bordercolor=KyoceraColors.BORDER_COLOR)
    style.map('TButton',
              background=[('active', KyoceraColors.PRIMARY_ACTION), ('!disabled', KyoceraColors.WIDGET_BG)],
              foreground=[('active', 'white')])

    style.configure('Start.TButton', font=('Segoe UI', 12, 'bold'), foreground='white')
    style.map('Start.TButton', background=[('active', KyoceraColors.PRIMARY_ACTION_HOVER), ('!disabled', KyoceraColors.PRIMARY_ACTION)])
    
    # --- Treeview ---
    style.configure("Treeview", rowheight=28, fieldbackground=KyoceraColors.WIDGET_BG, font=('Segoe UI', 10))
    style.configure("Treeview.Heading", font=('Segoe UI', 11, 'bold'), padding=5)
    style.map("Treeview", background=[('selected', KyoceraColors.PRIMARY_ACTION)])

def create_main_header(parent, version):
    """Creates the main application header."""
    header_frame = ttk.Frame(parent, padding=(20, 15))
    header_frame.pack(fill='x', padx=10, pady=(10, 5))
    
    ttk.Label(header_frame, text="KYOCERA", font=('Arial Black', 32), foreground=KyoceraColors.KYOCERA_RED).pack(side='left')
    title_frame = ttk.Frame(header_frame)
    title_frame.pack(side='left', padx=20)
    ttk.Label(title_frame, text="QA ServiceNow Knowledge Tool", font=('Segoe UI', 16, 'bold')).pack(anchor='w')
    ttk.Label(title_frame, text=f"Version: {version}", foreground=KyoceraColors.TEXT_MUTED).pack(anchor='w')

def create_io_section(parent, app):
    """Creates the input/output selection section."""
    io_frame = ttk.LabelFrame(parent, text="1. Select Inputs", style='Card.TLabelframe', padding=20)
    io_frame.pack(fill='x', padx=10, pady=10)
    io_frame.columnconfigure(1, weight=1)

    ttk.Label(io_frame, text="Excel Template:", style='Card.TLabel').grid(row=0, column=0, sticky='w', pady=8, padx=5)
    ttk.Entry(io_frame, textvariable=app.selected_excel, font=('Segoe UI', 10)).grid(row=0, column=1, sticky='ew', padx=5)
    ttk.Button(io_frame, text="Browse...", command=app.browse_excel).grid(row=0, column=2, padx=5)

    ttk.Label(io_frame, text="PDF Source:", style='Card.TLabel').grid(row=1, column=0, sticky='w', pady=8, padx=5)
    ttk.Entry(io_frame, textvariable=app.selected_folder, font=('Segoe UI', 10)).grid(row=1, column=1, sticky='ew', padx=5)
    
    btn_frame = ttk.Frame(io_frame, style='Card.TFrame')
    btn_frame.grid(row=1, column=2, padx=5)
    ttk.Button(btn_frame, text="Folder", command=app.browse_folder).pack(side='left')
    ttk.Button(btn_frame, text="Files", command=app.browse_files).pack(side='left', padx=5)
    ttk.Button(btn_frame, text="ZIP", command=app.browse_zip).pack(side='left')

def create_controls_section(parent, app):
    """Creates the main process control buttons."""
    controls_frame = ttk.LabelFrame(parent, text="2. Start Process", style='Card.TLabelframe', padding=20)
    controls_frame.pack(fill='x', padx=10, pady=10)
    controls_frame.columnconfigure(0, weight=1)
    
    app.process_btn = ttk.Button(controls_frame, text="🚀 START PROCESSING", style='Start.TButton', command=app.start_processing)
    app.process_btn.grid(row=0, column=0, sticky='ew', ipady=8, pady=(0, 10))

def create_live_status_section(parent, app):
    """Creates the live status, progress, and feedback section."""
    container = ttk.LabelFrame(parent, text="3. Live Status", style='Card.TLabelframe', padding=20)
    container.pack(fill='both', expand=True, padx=10, pady=10)
    container.columnconfigure(0, weight=1)
    container.rowconfigure(2, weight=1) 

    # --- Activity and Progress Bar ---
    activity_frame = ttk.Frame(container, style='Card.TFrame')
    activity_frame.grid(row=0, column=0, sticky='ew', pady=(0, 15))
    activity_frame.columnconfigure(1, weight=1)
    activity_frame.columnconfigure(2, weight=0)
    
    ttk.Label(activity_frame, text="Activity:", font=('Segoe UI', 11, 'bold'), style='Card.TLabel').grid(row=0, column=0, padx=10, pady=5)
    app.status_current_file = tk.StringVar(value="Waiting to start...")
    ttk.Label(activity_frame, textvariable=app.status_current_file, style='Card.TLabel', foreground=KyoceraColors.TEXT_MUTED).grid(row=0, column=1, sticky='ew')
    app.spinner_label = ttk.Label(activity_frame, text="", width=2, style='Card.TLabel')
    app.spinner_label.grid(row=0, column=2, padx=(5,0), sticky='w')
    
    app.progress_bar = ttk.Progressbar(activity_frame, variable=app.progress_value, mode='determinate')
    app.progress_bar.grid(row=1, column=0, columnspan=2, sticky='ew', padx=10, pady=(5,10))

    # --- Statistics Counters ---
    stats_frame = ttk.Frame(container, style='Card.TFrame')
    stats_frame.grid(row=1, column=0, sticky='ew', pady=(0, 15))
    stats_frame.columnconfigure((0,1,2,3), weight=1)

    stats = [("Processed", app.count_processed), ("Passed", app.count_pass), 
             ("Needs Review", app.count_review), ("Errors", app.count_fail)]
    
    for i, (text, var) in enumerate(stats):
        f = ttk.Frame(stats_frame, style='Card.TFrame')
        f.grid(row=0, column=i, sticky='ew', padx=5)
        ttk.Label(f, text=text, font=('Segoe UI', 10, 'bold'), style='Card.TLabel').pack(pady=(5,0))
        ttk.Label(f, textvariable=var, font=('Segoe UI', 14), style='Card.TLabel').pack(pady=(0,5))

    # --- Review & Log Tabs ---
    notebook = ttk.Notebook(container)
    notebook.grid(row=2, column=0, sticky='nsew', pady=(5,0))
    
    # Review Tab
    review_tab = ttk.Frame(notebook, padding=10)
    notebook.add(review_tab, text='Files for Review')
    review_tab.columnconfigure(0, weight=1)
    review_tab.rowconfigure(0, weight=1)
    
    app.review_tree = ttk.Treeview(review_tab, columns=('file',), show='headings', height=4)
    app.review_tree.grid(row=0, column=0, sticky='nsew')
    app.review_tree.heading('file', text='File Name')
    
    review_scroll = ttk.Scrollbar(review_tab, orient="vertical", command=app.review_tree.yview)
    review_scroll.grid(row=0, column=1, sticky='ns')
    app.review_tree.configure(yscrollcommand=review_scroll.set)
    
    app.review_file_btn = ttk.Button(review_tab, text="🔍 Review Selected File", 
                                     command=app.open_review_for_selected_file, state=tk.DISABLED)
    app.review_file_btn.grid(row=1, column=0, columnspan=2, sticky='e', pady=(10,0))
    app.review_tree.bind("<<TreeviewSelect>>", lambda e: app.review_file_btn.config(state=tk.NORMAL if app.review_tree.selection() else tk.DISABLED))
    
    # Log Tab
    log_tab = ttk.Frame(notebook, padding=10)
    notebook.add(log_tab, text='Processing Log')
    log_tab.columnconfigure(0, weight=1)
    log_tab.rowconfigure(0, weight=1)

    app.log_text = tk.Text(log_tab, wrap=tk.WORD, state=tk.DISABLED, relief="flat", 
                          font=("Consolas", 10), bg=KyoceraColors.WIDGET_BG, fg=KyoceraColors.TEXT_DARK)
    app.log_text.grid(row=0, column=0, sticky="nsew")
    
    log_scroll_main = ttk.Scrollbar(log_tab, command=app.log_text.yview)
    log_scroll_main.grid(row=0, column=1, sticky="ns")
    app.log_text.config(yscrollcommand=log_scroll_main.set)
