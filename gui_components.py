# gui_components.py
import tkinter as tk
from tkinter import ttk

def create_main_header(parent, version, colors):
    header = ttk.Frame(parent, style="Header.TFrame", padding=(10, 10))
    header.grid(row=0, column=0, sticky="ew")
    ttk.Separator(header, orient='horizontal').pack(side="bottom", fill="x")
    ttk.Label(header, text="KYOCERA", foreground=colors["kyocera_red"], font=("Arial Black", 22)).pack(side=tk.LEFT, padx=(10, 0))
    ttk.Label(header, text=f"QA Knowledge Tool v{version}", font=("Segoe UI", 16, "bold")).pack(side=tk.LEFT, padx=(15, 0))

def create_io_section(parent, app):
    io = ttk.LabelFrame(parent, text="1. Select Inputs", padding=10)
    io.grid(row=0, column=0, sticky="ew", pady=5)
    io.columnconfigure(1, weight=1)

    ttk.Label(io, text="Excel to Clone:").grid(row=0, column=0, sticky="w", pady=2, padx=5)
    ttk.Entry(io, textvariable=app.selected_excel).grid(row=0, column=1, sticky="ew", padx=5)
    ttk.Button(io, image=app.browse_icon, text=" Browse...", compound="left", command=app.browse_excel).grid(row=0, column=2, padx=5)

    ttk.Label(io, text="PDFs Folder:").grid(row=1, column=0, sticky="w", pady=2, padx=5)
    ttk.Entry(io, textvariable=app.selected_folder).grid(row=1, column=1, sticky="ew", padx=5)
    ttk.Button(io, image=app.browse_icon, text=" Browse...", compound="left", command=app.browse_folder).grid(row=1, column=2, padx=5)

    app.files_label = ttk.Label(io, text="Or select individual files -->")
    app.files_label.grid(row=2, column=1, sticky="e", padx=5, pady=(5,0))
    ttk.Button(io, image=app.browse_icon, text=" Browse Files...", compound="left", command=app.browse_files).grid(row=2, column=2, padx=5, pady=(5,0))

def create_process_controls(parent, app):
    ctrl = ttk.LabelFrame(parent, text="2. Process & Manage", padding=10)
    ctrl.grid(row=1, column=0, sticky="ew", pady=5)
    # --- FIX: Reconfigured the grid to have 4 columns ---
    ctrl.columnconfigure((0, 1, 2, 3), weight=1)

    app.process_btn = ttk.Button(ctrl, text=" START", image=app.start_icon, compound="left", command=app.start_processing, style="Red.TButton")
    app.process_btn.grid(row=0, column=0, columnspan=4, sticky="ew", pady=2)

    app.pause_btn = ttk.Button(ctrl, text=" Pause", image=app.pause_icon, compound="left", command=app.toggle_pause, state=tk.DISABLED)
    app.pause_btn.grid(row=1, column=0, sticky="ew", pady=2)
    app.stop_btn = ttk.Button(ctrl, text=" Stop", image=app.stop_icon, compound="left", command=app.stop_processing, state=tk.DISABLED)
    app.stop_btn.grid(row=1, column=1, sticky="ew", pady=2)
    app.rerun_btn = ttk.Button(ctrl, text=" Re-run Flagged", image=app.rerun_icon, compound="left", command=app.rerun_flagged_job, state=tk.DISABLED)
    app.rerun_btn.grid(row=1, column=2, sticky="ew", pady=2)
    app.open_result_btn = ttk.Button(ctrl, text=" Open Result", image=app.open_icon, compound="left", command=app.open_result, state=tk.DISABLED)
    app.open_result_btn.grid(row=1, column=3, sticky="ew", pady=2)
    
    # --- FIX: Placed each button in its own grid cell for proper layout ---
    app.review_btn = ttk.Button(ctrl, text=" Patterns", image=app.patterns_icon, compound="left", command=app.open_pattern_manager)
    app.review_btn.grid(row=2, column=0, sticky="ew", pady=2)
    
    app.fullscreen_btn = ttk.Button(ctrl, text=" Fullscreen", image=app.fullscreen_icon, compound="left", command=app.toggle_fullscreen)
    app.fullscreen_btn.grid(row=2, column=1, sticky="ew", pady=2)
    
    app.exit_btn = ttk.Button(ctrl, text=" Exit", image=app.exit_icon, compound="left", command=app.on_closing)
    app.exit_btn.grid(row=2, column=3, sticky="ew", pady=2)

def create_controls_section(parent, app):
    """Creates the main control panel section with action buttons and options."""
    controls_frame = ttk.LabelFrame(parent, text="Controls", padding=10)
    controls_frame.grid(row=1, column=0, sticky="ew", pady=5)
    controls_frame.columnconfigure(tuple(range(4)), weight=1)  # 4 equal columns
    
    # Main action buttons
    action_frame = ttk.Frame(controls_frame)
    action_frame.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 10))
    action_frame.columnconfigure(0, weight=1)
    
    # Create the primary action button (START/STOP)
    app.primary_action_btn = ttk.Button(
        action_frame, 
        text=" START PROCESSING", 
        image=app.start_icon, 
        compound="left", 
        command=app.toggle_processing, 
        style="Primary.TButton"
    )
    app.primary_action_btn.grid(row=0, column=0, sticky="ew")
    
    # Secondary action buttons
    btn_configs = [
        # Row 1
        (0, "Pause/Resume", app.pause_icon, app.toggle_pause, tk.DISABLED),
        (1, "Reset", app.reset_icon, app.reset_processing, tk.NORMAL),
        (2, "Verify", app.verify_icon, app.verify_files, tk.NORMAL),
        (3, "Settings", app.settings_icon, app.open_settings, tk.NORMAL),
        # Row 2
        (4, "Patterns", app.patterns_icon, app.open_pattern_manager, tk.NORMAL),
        (5, "Open Output", app.open_icon, app.open_result, tk.DISABLED),
        (6, "Re-run Flagged", app.rerun_icon, app.rerun_flagged_job, tk.DISABLED),
        (7, "Exit", app.exit_icon, app.on_closing, tk.NORMAL),
    ]
    
    # Create buttons in a 2x4 grid
    for i, (idx, text, icon, command, state) in enumerate(btn_configs):
        row, col = divmod(i, 4)
        btn = ttk.Button(
            controls_frame,
            text=f" {text}",
            image=icon,
            compound="left",
            command=command,
            state=state
        )
        btn.grid(row=row+1, column=col, sticky="ew", padx=2, pady=2)
        
        # Store references to buttons we need to control later
        if text == "Pause/Resume":
            app.pause_btn = btn
        elif text == "Open Output":
            app.open_result_btn = btn
        elif text == "Re-run Flagged":
            app.rerun_btn = btn
        elif text == "Exit":
            app.exit_btn = btn
    
    # Advanced options section
    options_frame = ttk.LabelFrame(controls_frame, text="Options", padding=5)
    options_frame.grid(row=3, column=0, columnspan=4, sticky="ew", pady=(10, 0))
    options_frame.columnconfigure(1, weight=1)
    
    # Create checkboxes for options
    app.use_ocr_var = tk.BooleanVar(value=True)
    app.use_ai_var = tk.BooleanVar(value=True)
    app.skip_cached_var = tk.BooleanVar(value=True)
    
    ttk.Checkbutton(
        options_frame, 
        text="Use OCR for scanned documents", 
        variable=app.use_ocr_var
    ).grid(row=0, column=0, sticky="w", padx=5)
    
    ttk.Checkbutton(
        options_frame, 
        text="Use AI extraction", 
        variable=app.use_ai_var
    ).grid(row=0, column=1, sticky="w", padx=5)
    
    ttk.Checkbutton(
        options_frame, 
        text="Skip previously cached files", 
        variable=app.skip_cached_var
    ).grid(row=1, column=0, sticky="w", padx=5)
    
    return controls_frame

def create_status_and_log_section(parent, app):
    stat = ttk.LabelFrame(parent, text="3. Status & Logs", padding=10)
    stat.grid(row=2, column=0, sticky="nsew", pady=5)
    stat.columnconfigure(0, weight=1)
    stat.rowconfigure(4, weight=1)

    app.status_frame = ttk.Frame(stat, style="Status.TFrame", padding=5)
    app.status_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=2)
    app.status_frame.columnconfigure(1, weight=1)
    app.led_label = ttk.Label(app.status_frame, textvariable=app.led_status_var, style="LED.TLabel")
    app.led_label.grid(row=0, column=0, sticky="w")
    ttk.Label(app.status_frame, textvariable=app.status_current_file, style="Status.TLabel").grid(row=0, column=1, sticky="ew", padx=5)

    prog_frame = ttk.Frame(stat)
    prog_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=(5,10))
    prog_frame.columnconfigure(0, weight=1)
    app.progress_bar = ttk.Progressbar(prog_frame, variable=app.progress_value, style="Blue.Horizontal.TProgressbar")
    app.progress_bar.grid(row=0, column=0, sticky="ew")
    ttk.Label(prog_frame, textvariable=app.time_remaining_var).grid(row=0, column=1, sticky="e", padx=10)

    sum_frame = ttk.Frame(stat)
    sum_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=2)
    counters = [("Pass:", app.count_pass, "Green"), ("Fail:", app.count_fail, "Red"), ("Review:", app.count_review, "Orange"), ("OCR:", app.count_ocr, "Blue")]
    for i, (text, var, color) in enumerate(counters):
        ttk.Label(sum_frame, text=text, style="Status.Header.TLabel").pack(side="left", padx=(15, 2))
        ttk.Label(sum_frame, textvariable=var, style=f"Count.{color}.TLabel").pack(side="left")

    rev_frame = ttk.Frame(stat)
    rev_frame.grid(row=3, column=0, sticky="nsew", padx=5, pady=2)
    rev_frame.rowconfigure(1, weight=1)
    rev_frame.columnconfigure(0, weight=1)
    ttk.Label(rev_frame, text="Files to Review:", style="Status.Header.TLabel").grid(row=0, column=0, sticky="w")
    app.review_file_btn = ttk.Button(rev_frame, text="Review Selected", command=app.open_review_for_selected_file, state=tk.DISABLED)
    app.review_file_btn.grid(row=0, column=1, sticky="e")
    app.review_tree = ttk.Treeview(rev_frame, columns=('file'), show='headings', height=4)
    app.review_tree.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=2)
    app.review_tree.heading('file', text='File Name')
    app.review_tree.bind("<<TreeviewSelect>>", lambda e: app.review_file_btn.config(state=tk.NORMAL))

    log_frame = ttk.Frame(stat)
    log_frame.grid(row=4, column=0, sticky="nsew", padx=5, pady=(10,2))
    log_frame.rowconfigure(0, weight=1)
    log_frame.columnconfigure(0, weight=1)
    app.log_text = tk.Text(log_frame, height=8, wrap=tk.WORD, state=tk.DISABLED, relief="solid", borderwidth=1, font=("Consolas", 9))
    app.log_text.grid(row=0, column=0, sticky="nsew")
    log_scroll = ttk.Scrollbar(log_frame, command=app.log_text.yview)
    log_scroll.grid(row=0, column=1, sticky="ns")
    app.log_text.config(yscrollcommand=log_scroll.set)

def create_live_status_section(parent, app):
    """Creates a real-time status display panel for monitoring processing."""
    status_frame = ttk.LabelFrame(parent, text="Live Status", padding=10)
    status_frame.grid(row=0, column=1, rowspan=3, sticky="nsew", padx=(10, 0))
    status_frame.columnconfigure(0, weight=1)
    status_frame.rowconfigure(3, weight=1)
    
    # Current operation display
    op_frame = ttk.Frame(status_frame, padding=5)
    op_frame.grid(row=0, column=0, sticky="ew", pady=5)
    op_frame.columnconfigure(1, weight=1)
    
    ttk.Label(op_frame, text="Operation:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w")
    app.live_operation = tk.StringVar(value="Idle")
    ttk.Label(op_frame, textvariable=app.live_operation, foreground="#0078D4").grid(row=0, column=1, sticky="w", padx=5)
    
    # Current file display
    file_frame = ttk.Frame(status_frame, padding=5)
    file_frame.grid(row=1, column=0, sticky="ew", pady=5)
    file_frame.columnconfigure(1, weight=1)
    
    ttk.Label(file_frame, text="Processing:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w")
    app.live_filename = tk.StringVar(value="No file selected")
    ttk.Label(file_frame, textvariable=app.live_filename).grid(row=0, column=1, sticky="w", padx=5)
    
    # Performance metrics
    perf_frame = ttk.LabelFrame(status_frame, text="Performance", padding=5)
    perf_frame.grid(row=2, column=0, sticky="ew", pady=5)
    perf_frame.columnconfigure(1, weight=1)
    
    # Create StringVars for metrics first (fixed the syntax error)
    app.live_rate_var = tk.StringVar(value="0")
    app.live_avg_time = tk.StringVar(value="0 sec")
    app.live_memory = tk.StringVar(value="0 MB")
    
    metrics = [
        ("Files/min:", app.live_rate_var),
        ("Avg time/file:", app.live_avg_time),
        ("Memory usage:", app.live_memory)
    ]
    
    for i, (label, var) in enumerate(metrics):
        ttk.Label(perf_frame, text=label, font=("Segoe UI", 9, "bold")).grid(row=i, column=0, sticky="w", pady=2)
        ttk.Label(perf_frame, textvariable=var).grid(row=i, column=1, sticky="w", padx=5, pady=2)
    
    # Mini log display - shows last few operations
    mini_log_frame = ttk.LabelFrame(status_frame, text="Recent Activity", padding=5)
    mini_log_frame.grid(row=3, column=0, sticky="nsew", pady=5)
    mini_log_frame.columnconfigure(0, weight=1)
    mini_log_frame.rowconfigure(0, weight=1)
    
    app.mini_log = tk.Text(mini_log_frame, height=8, width=30, wrap=tk.WORD, font=("Consolas", 8))
    app.mini_log.grid(row=0, column=0, sticky="nsew")
    mini_scroll = ttk.Scrollbar(mini_log_frame, command=app.mini_log.yview)
    mini_scroll.grid(row=0, column=1, sticky="ns")
    app.mini_log.config(yscrollcommand=mini_scroll.set, state=tk.DISABLED)
    
    # Configure tag for timestamps
    app.mini_log.tag_configure("timestamp", foreground="gray")
    
    return status_frame

# ADD THIS NEW FUNCTION
def create_review_tab(parent, app):
    """Creates a tab for reviewing and editing files that need attention."""
    review_frame = ttk.Frame(parent)
    
    # Split frame into left and right panels
    paned_window = ttk.PanedWindow(review_frame, orient=tk.HORIZONTAL)
    paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Left panel - File list with filters
    left_panel = ttk.Frame(paned_window)
    left_panel.columnconfigure(0, weight=1)
    left_panel.rowconfigure(2, weight=1)
    paned_window.add(left_panel, weight=1)
    
    # Search and filter controls
    filter_frame = ttk.Frame(left_panel)
    filter_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
    filter_frame.columnconfigure(1, weight=1)
    
    ttk.Label(filter_frame, text="Search:").grid(row=0, column=0, sticky="w", padx=(0, 5))
    app.review_search_var = tk.StringVar()
    search_entry = ttk.Entry(filter_frame, textvariable=app.review_search_var)
    search_entry.grid(row=0, column=1, sticky="ew")
    search_entry.bind("<KeyRelease>", app.filter_review_files)
    
    # Filter options
    filter_options_frame = ttk.Frame(left_panel)
    filter_options_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
    
    # Create filter variables if they don't exist
    app.show_all_files_var = tk.BooleanVar(value=True)
    app.show_needs_review_var = tk.BooleanVar(value=True)
    app.show_ocr_files_var = tk.BooleanVar(value=True)
    app.show_failed_var = tk.BooleanVar(value=True)
    
    filters = [
        ("Show all files", app.show_all_files_var, app.toggle_all_files),
        ("Needs review", app.show_needs_review_var, app.filter_review_files),
        ("OCR processed", app.show_ocr_files_var, app.filter_review_files),
        ("Failed", app.show_failed_var, app.filter_review_files)
    ]
    
    for i, (text, var, command) in enumerate(filters):
        ttk.Checkbutton(
            filter_options_frame, 
            text=text,
            variable=var,
            command=command
        ).grid(row=i//2, column=i%2, sticky="w", padx=5, pady=2)
    
    # File list with columns for status, filename, and reason
    columns = ("status", "filename", "reason")
    app.review_files_tree = ttk.Treeview(left_panel, columns=columns, show="headings", selectmode="browse")
    app.review_files_tree.grid(row=2, column=0, sticky="nsew")
    
    # Configure columns and headings
    app.review_files_tree.column("status", width=30, anchor="center")
    app.review_files_tree.column("filename", width=200)
    app.review_files_tree.column("reason", width=100)
    
    app.review_files_tree.heading("status", text="")
    app.review_files_tree.heading("filename", text="Filename")
    app.review_files_tree.heading("reason", text="Status")
    
    # Scrollbar for file list
    files_scroll = ttk.Scrollbar(left_panel, orient="vertical", command=app.review_files_tree.yview)
    files_scroll.grid(row=2, column=1, sticky="ns")
    app.review_files_tree.configure(yscrollcommand=files_scroll.set)
    
    # Action buttons under file list
    action_frame = ttk.Frame(left_panel)
    action_frame.grid(row=3, column=0, sticky="ew", pady=(10, 0))
    
    ttk.Button(
        action_frame,
        text="Open File",
        command=app.open_selected_review_file
    ).pack(side="left", padx=(0, 5))
    
    ttk.Button(
        action_frame,
        text="Process Selected",
        command=app.process_selected_review_file
    ).pack(side="left", padx=5)
    
    ttk.Button(
        action_frame,
        text="Process All",
        command=app.process_all_review_files
    ).pack(side="left", padx=5)
    
    # Right panel - File content and editing
    right_panel = ttk.Frame(paned_window)
    right_panel.columnconfigure(0, weight=1)
    right_panel.rowconfigure(1, weight=1)
    paned_window.add(right_panel, weight=2)
    
    # File details header
    details_header = ttk.Frame(right_panel)
    details_header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
    details_header.columnconfigure(1, weight=1)
    
    ttk.Label(details_header, text="File Details", font=("Segoe UI", 12, "bold")).grid(
        row=0, column=0, sticky="w"
    )
    
    app.review_current_file_var = tk.StringVar(value="No file selected")
    ttk.Label(details_header, textvariable=app.review_current_file_var).grid(
        row=0, column=1, sticky="e"
    )
    
    # Notebook for different views of the file
    app.review_notebook = ttk.Notebook(right_panel)
    app.review_notebook.grid(row=1, column=0, sticky="nsew")
    
    # Text view tab
    text_frame = ttk.Frame(app.review_notebook)
    app.review_notebook.add(text_frame, text="Text View")
    text_frame.columnconfigure(0, weight=1)
    text_frame.rowconfigure(0, weight=1)
    
    app.review_text = tk.Text(text_frame, wrap="word", font=("Consolas", 10))
    app.review_text.grid(row=0, column=0, sticky="nsew")
    text_scroll = ttk.Scrollbar(text_frame, orient="vertical", command=app.review_text.yview)
    text_scroll.grid(row=0, column=1, sticky="ns")
    app.review_text.config(yscrollcommand=text_scroll.set)
    
    # Patterns tab
    patterns_frame = ttk.Frame(app.review_notebook)
    app.review_notebook.add(patterns_frame, text="Patterns")
    patterns_frame.columnconfigure(0, weight=1)
    patterns_frame.rowconfigure(1, weight=1)
    
    patterns_header = ttk.Frame(patterns_frame)
    patterns_header.grid(row=0, column=0, sticky="ew", pady=(5, 10))
    patterns_header.columnconfigure(2, weight=1)
    
    ttk.Label(patterns_header, text="Pattern Type:").grid(row=0, column=0, sticky="w", padx=(0, 5))
    
    app.pattern_type_var = tk.StringVar(value="Model Patterns")
    pattern_types = ["Model Patterns", "QA Number Patterns"]
    pattern_combo = ttk.Combobox(patterns_header, textvariable=app.pattern_type_var, values=pattern_types, state="readonly")
    pattern_combo.grid(row=0, column=1, sticky="w", padx=5)
    pattern_combo.bind("<<ComboboxSelected>>", app.load_patterns)
    
    ttk.Button(
        patterns_header, 
        text="Test Selected Pattern",
        command=app.test_selected_pattern
    ).grid(row=0, column=2, sticky="e")
    
    # Pattern list on the left, preview on the right
    patterns_paned = ttk.PanedWindow(patterns_frame, orient=tk.HORIZONTAL)
    patterns_paned.grid(row=1, column=0, sticky="nsew")
    
    # Left side - pattern list
    pattern_list_frame = ttk.Frame(patterns_paned)
    pattern_list_frame.columnconfigure(0, weight=1)
    pattern_list_frame.rowconfigure(0, weight=1)
    patterns_paned.add(pattern_list_frame, weight=1)
    
    app.patterns_listbox = tk.Listbox(pattern_list_frame, font=("Consolas", 10))
    app.patterns_listbox.grid(row=0, column=0, sticky="nsew")
    patterns_scroll = ttk.Scrollbar(pattern_list_frame, orient="vertical", command=app.patterns_listbox.yview)
    patterns_scroll.grid(row=0, column=1, sticky="ns")
    app.patterns_listbox.config(yscrollcommand=patterns_scroll.set)
    
    pattern_button_frame = ttk.Frame(pattern_list_frame)
    pattern_button_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5, 0))
    
    ttk.Button(
        pattern_button_frame,
        text="Add New",
        command=app.add_new_pattern
    ).pack(side="left", padx=(0, 5))
    
    ttk.Button(
        pattern_button_frame,
        text="Edit",
        command=app.edit_pattern
    ).pack(side="left", padx=5)
    
    ttk.Button(
        pattern_button_frame,
        text="Remove",
        command=app.remove_pattern
    ).pack(side="left", padx=5)
    
    # Right side - pattern test area
    pattern_test_frame = ttk.Frame(patterns_paned)
    pattern_test_frame.columnconfigure(0, weight=1)
    pattern_test_frame.rowconfigure(1, weight=1)
    patterns_paned.add(pattern_test_frame, weight=2)
    
    ttk.Label(pattern_test_frame, text="Pattern Test Area").grid(row=0, column=0, sticky="w", pady=(0, 5))
    
    app.pattern_test_text = tk.Text(pattern_test_frame, wrap="word", font=("Consolas", 10))
    app.pattern_test_text.grid(row=1, column=0, sticky="nsew")
    test_scroll = ttk.Scrollbar(pattern_test_frame, orient="vertical", command=app.pattern_test_text.yview)
    test_scroll.grid(row=1, column=1, sticky="ns")
    app.pattern_test_text.config(yscrollcommand=test_scroll.set)
    
    # Configure highlighting tags
    app.pattern_test_text.tag_configure("match", background="yellow")
    
    # Metadata tab
    metadata_frame = ttk.Frame(app.review_notebook)
    app.review_notebook.add(metadata_frame, text="Metadata")
    metadata_frame.columnconfigure(1, weight=1)
    
    # File information fields
    metadata_fields = [
        ("Filename:", app.meta_filename_var := tk.StringVar()),
        ("File Size:", app.meta_size_var := tk.StringVar()),
        ("Last Modified:", app.meta_modified_var := tk.StringVar()),
        ("Status:", app.meta_status_var := tk.StringVar()),
        ("Processed On:", app.meta_processed_var := tk.StringVar()),
        ("OCR Used:", app.meta_ocr_var := tk.StringVar()),
        ("Model Number:", app.meta_model_var := tk.StringVar()),
        ("QA Number:", app.meta_qa_var := tk.StringVar()),
        ("Author:", app.meta_author_var := tk.StringVar())
    ]
    
    for i, (label_text, var) in enumerate(metadata_fields):
        ttk.Label(metadata_frame, text=label_text, font=("Segoe UI", 10, "bold")).grid(
            row=i, column=0, sticky="w", padx=(10, 5), pady=5
        )
        ttk.Label(metadata_frame, textvariable=var).grid(
            row=i, column=1, sticky="w", padx=5, pady=5
        )
    
    # Actions at the bottom of the metadata tab
    meta_actions_frame = ttk.Frame(metadata_frame)
    meta_actions_frame.grid(row=len(metadata_fields), column=0, columnspan=2, sticky="ew", pady=(15, 0))
    
    ttk.Button(
        meta_actions_frame,
        text="Edit Metadata",
        command=app.edit_metadata
    ).pack(side="left", padx=(0, 5))
    
    ttk.Button(
        meta_actions_frame,
        text="Apply Changes",
        command=app.apply_metadata_changes
    ).pack(side="left", padx=5)
    
    ttk.Button(
        meta_actions_frame,
        text="Revert Changes",
        command=app.revert_metadata_changes
    ).pack(side="left", padx=5)
    
    # Bind events
    app.review_files_tree.bind("<<TreeviewSelect>>", app.on_review_file_select)
    app.patterns_listbox.bind("<<ListboxSelect>>", app.on_pattern_select)
    
    return review_frame

def create_footer(parent, app, version, colors):
    """Creates the footer section with app info and status."""
    footer_frame = ttk.Frame(parent, style="Footer.TFrame")
    footer_frame.grid(row=99, column=0, columnspan=2, sticky="ew", pady=(10, 0))
    
    # Add separator line above footer
    ttk.Separator(footer_frame, orient="horizontal").pack(fill="x", pady=2)
    
    # Create main footer content area
    content_frame = ttk.Frame(footer_frame)
    content_frame.pack(fill="x", expand=True, padx=10, pady=5)
    content_frame.columnconfigure(1, weight=1)
    
    # Version and copyright info on the left
    info_frame = ttk.Frame(content_frame)
    info_frame.grid(row=0, column=0, sticky="w")
    
    version_label = ttk.Label(
        info_frame, 
        text=f"KYO QA Tool v{version}", 
        font=("Segoe UI", 8)
    )
    version_label.pack(side="left", padx=(0, 15))
    
    copyright_label = ttk.Label(
        info_frame, 
        text="© 2024-2025 Kyocera - All Rights Reserved", 
        font=("Segoe UI", 8)
    )
    copyright_label.pack(side="left")
    
    # Status info on the right
    status_frame = ttk.Frame(content_frame)
    status_frame.grid(row=0, column=1, sticky="e")
    
    # Create status variables if they don't exist yet
    if not hasattr(app, "footer_status_var"):
        app.footer_status_var = tk.StringVar(value="Ready")
    
    if not hasattr(app, "footer_memory_var"):
        app.footer_memory_var = tk.StringVar(value="Memory: 0 MB")
    
    # Status indicators
    ttk.Label(status_frame, text="Status:", font=("Segoe UI", 8, "bold")).pack(side="left")
    ttk.Label(status_frame, textvariable=app.footer_status_var).pack(side="left", padx=(2, 15))
    
    ttk.Label(status_frame, textvariable=app.footer_memory_var, font=("Segoe UI", 8)).pack(side="left")
    
    return footer_frame

def setup_high_contrast_styles(style, colors=None):
    """
    Configure high-contrast theme styles for accessibility.
    
    Args:
        style: ttk.Style object to configure
        colors: Optional dictionary of colors to use, if None uses default high contrast
    """
    # Default high contrast color scheme
    high_contrast = {
        "background": "#000000",
        "foreground": "#FFFFFF",
        "accent": "#FFFF00",  # Yellow for highlights
        "button": "#000080",  # Navy for buttons
        "button_fg": "#FFFFFF",
        "success": "#00FF00",  # Bright green
        "warning": "#FFFF00",  # Yellow
        "error": "#FF0000",   # Bright red
        "highlight": "#FFFF00" # Yellow for selections
    }
    
    # Override with any colors provided
    if colors:
        for key, value in colors.items():
            if key in high_contrast:
                high_contrast[key] = value
    
    # Configure base styles
    style.configure("HighContrast.TFrame", background=high_contrast["background"])
    style.configure("HighContrast.TLabel", 
                    background=high_contrast["background"], 
                    foreground=high_contrast["foreground"])
    
    # Buttons
    style.configure("HighContrast.TButton", 
                    background=high_contrast["button"],
                    foreground=high_contrast["button_fg"],
                    focuscolor=high_contrast["accent"])
    
    # Entry fields
    style.configure("HighContrast.TEntry",
                    fieldbackground=high_contrast["background"],
                    foreground=high_contrast["foreground"],
                    insertcolor=high_contrast["foreground"])
    
    # Progress bar
    style.configure("HighContrast.Horizontal.TProgressbar",
                    background=high_contrast["accent"],
                    troughcolor=high_contrast["background"])
    
    # Treeview
    style.configure("HighContrast.Treeview",
                    background=high_contrast["background"],
                    foreground=high_contrast["foreground"],
                    fieldbackground=high_contrast["background"])
    
    style.configure("HighContrast.Treeview.Heading",
                    background=high_contrast["button"],
                    foreground=high_contrast["button_fg"])
    
    # LabelFrame
    style.configure("HighContrast.TLabelframe",
                    background=high_contrast["background"],
                    foreground=high_contrast["foreground"],
                    labeloutside=True)
    
    style.configure("HighContrast.TLabelframe.Label",
                    background=high_contrast["background"],
                    foreground=high_contrast["foreground"],
                    font=("Segoe UI", 11, "bold"))
    
    # Status indicators
    style.configure("HighContrast.Success.TLabel",
                    background=high_contrast["background"],
                    foreground=high_contrast["success"])
    
    style.configure("HighContrast.Warning.TLabel",
                    background=high_contrast["background"],
                    foreground=high_contrast["warning"])
    
    style.configure("HighContrast.Error.TLabel",
                    background=high_contrast["background"],
                    foreground=high_contrast["error"])
    
    # Status frame
    style.configure("HighContrast.Status.TFrame",
                    background=high_contrast["button"],
                    relief="sunken")
    
    style.configure("HighContrast.Status.TLabel",
                    background=high_contrast["button"],
                    foreground=high_contrast["button_fg"])
    
    return style