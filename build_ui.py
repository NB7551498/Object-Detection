html_content = r'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VisionAI — Intelligent Object Detection</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-base: #0B0F14;
            --bg-surface: #111820;
            --bg-surface-secondary: #151D26;
            --border: #202934;
            --accent: #7C3AED;
            --accent-hover: #6D28D9;
            --text-primary: #F5F7FA;
            --text-secondary: #8B95A5;
            --success: #22C55E;
            --warning: #F59E0B;
            --danger: #EF4444;
            
            --sidebar-width: 260px;
            --header-height: 64px;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Inter', sans-serif;
        }

        body {
            background-color: var(--bg-base);
            color: var(--text-primary);
            height: 100vh;
            display: flex;
            overflow: hidden;
            font-size: 14px;
        }

        /* ── Typography & Globals ── */
        h1 { font-size: 24px; font-weight: 600; letter-spacing: -0.02em; }
        h2 { font-size: 18px; font-weight: 500; letter-spacing: -0.01em; color: var(--text-primary); }
        p { color: var(--text-secondary); line-height: 1.5; }
        
        button {
            cursor: pointer;
            border: none;
            outline: none;
            font-family: 'Inter', sans-serif;
            font-size: 14px;
            font-weight: 500;
            transition: background 0.15s ease, border-color 0.15s ease, color 0.15s ease;
        }

        .btn-primary {
            background-color: var(--accent);
            color: #fff;
            padding: 10px 18px;
            border-radius: 6px;
        }
        .btn-primary:hover { background-color: var(--accent-hover); }
        .btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

        .btn-secondary {
            background-color: transparent;
            color: var(--text-primary);
            border: 1px solid var(--border);
            padding: 9px 17px;
            border-radius: 6px;
        }
        .btn-secondary:hover {
            background-color: var(--bg-surface-secondary);
            border-color: #313D4C;
        }

        /* ── Layout ── */
        .sidebar {
            width: var(--sidebar-width);
            background-color: var(--bg-surface);
            border-right: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            z-index: 20;
        }

        .brand {
            height: var(--header-height);
            display: flex;
            align-items: center;
            padding: 0 24px;
            border-bottom: 1px solid var(--border);
            font-weight: 700;
            font-size: 16px;
            letter-spacing: 0.5px;
            gap: 10px;
        }

        .brand-icon {
            width: 20px;
            height: 20px;
            border-radius: 4px;
            background: var(--accent);
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .nav-section {
            padding: 24px 12px;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }

        .nav-label {
            font-size: 11px;
            font-weight: 600;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            padding: 0 12px;
            margin-bottom: 8px;
        }

        .nav-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 12px;
            border-radius: 6px;
            color: var(--text-secondary);
            text-decoration: none;
            transition: all 0.15s;
            cursor: pointer;
        }

        .nav-item:hover {
            background-color: var(--bg-surface-secondary);
            color: var(--text-primary);
        }

        .nav-item.active {
            background-color: rgba(124, 58, 237, 0.1);
            color: var(--accent);
            font-weight: 500;
        }

        .main-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            min-width: 0;
        }

        .header {
            height: var(--header-height);
            border-bottom: 1px solid var(--border);
            background-color: var(--bg-base);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 32px;
        }

        .header-title {
            font-size: 16px;
            font-weight: 500;
        }

        .header-actions {
            display: flex;
            gap: 12px;
        }

        .content-area {
            flex: 1;
            overflow-y: auto;
            padding: 32px;
            position: relative;
        }

        .view { display: none; flex-direction: column; gap: 32px; max-width: 1200px; margin: 0 auto; width: 100%; }
        .view.active { display: flex; }

        /* ── Cards & UI Elements ── */
        .card {
            background-color: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 24px;
        }

        .card-header {
            margin-bottom: 20px;
        }

        .card-title {
            font-size: 15px;
            font-weight: 500;
            margin-bottom: 4px;
        }

        .card-desc {
            font-size: 13px;
        }

        /* ── Dashboard Stats ── */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 16px;
        }

        .stat-card {
            background-color: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .stat-label {
            font-size: 13px;
            color: var(--text-secondary);
            font-weight: 500;
        }

        .stat-value {
            font-size: 28px;
            font-weight: 600;
            color: var(--text-primary);
        }

        /* ── Workspace / Upload ── */
        .workspace-tabs {
            display: flex;
            gap: 4px;
            background-color: var(--bg-surface);
            padding: 4px;
            border-radius: 8px;
            border: 1px solid var(--border);
            width: fit-content;
            margin-bottom: 24px;
        }

        .ws-tab {
            padding: 8px 16px;
            border-radius: 4px;
            background: transparent;
            color: var(--text-secondary);
            font-size: 13px;
        }
        .ws-tab.active {
            background-color: var(--bg-surface-secondary);
            color: var(--text-primary);
            font-weight: 500;
        }

        .upload-zone {
            border: 1px dashed var(--border);
            border-radius: 8px;
            padding: 60px 24px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            background-color: rgba(17, 24, 32, 0.3);
            transition: all 0.2s;
            cursor: pointer;
        }

        .upload-zone:hover, .upload-zone.dragover {
            background-color: rgba(124, 58, 237, 0.05);
            border-color: var(--accent);
        }

        .upload-icon {
            color: var(--text-secondary);
            margin-bottom: 16px;
        }

        .upload-text-main {
            font-size: 15px;
            font-weight: 500;
            color: var(--text-primary);
            margin-bottom: 8px;
        }

        .upload-text-sub {
            font-size: 13px;
            color: var(--text-secondary);
            margin-bottom: 24px;
        }

        /* ── Workspace / Results ── */
        .results-layout {
            display: none;
            grid-template-columns: 1fr 340px;
            gap: 24px;
            align-items: start;
        }

        .image-preview-container {
            background-color: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 400px;
            position: relative;
        }

        .image-preview-container img {
            max-width: 100%;
            max-height: 70vh;
            display: block;
        }

        /* ── Table ── */
        .data-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }

        .data-table th {
            text-align: left;
            padding: 12px 16px;
            border-bottom: 1px solid var(--border);
            color: var(--text-secondary);
            font-weight: 500;
            background-color: var(--bg-surface);
        }

        .data-table td {
            padding: 12px 16px;
            border-bottom: 1px solid var(--border);
            color: var(--text-primary);
        }

        .data-table tr:last-child td { border-bottom: none; }

        .badge {
            display: inline-flex;
            align-items: center;
            padding: 2px 8px;
            border-radius: 100px;
            font-size: 11px;
            font-weight: 500;
            letter-spacing: 0.3px;
        }

        .badge-success { background: rgba(34, 197, 94, 0.1); color: var(--success); }
        .badge-warning { background: rgba(245, 158, 11, 0.1); color: var(--warning); }

        /* ── Live Camera ── */
        .live-container {
            display: none;
            flex-direction: column;
            gap: 16px;
        }

        .live-viewport {
            position: relative;
            background: #000;
            border-radius: 8px;
            border: 1px solid var(--border);
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 480px;
            aspect-ratio: 4/3;
        }

        #webcam-video { display: none; }
        #live-canvas { width: 100%; height: 100%; object-fit: contain; }

        .live-hud {
            position: absolute;
            top: 16px;
            left: 16px;
            right: 16px;
            display: flex;
            justify-content: space-between;
            pointer-events: none;
        }

        .hud-left { display: flex; gap: 8px; }
        .hud-right { display: flex; gap: 8px; }

        .hud-badge {
            background: rgba(17, 24, 32, 0.8);
            border: 1px solid rgba(255,255,255,0.1);
            color: #fff;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
            backdrop-filter: blur(4px);
        }

        .live-indicator {
            background: rgba(239, 68, 68, 0.9);
            border: none;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .dot-pulse {
            width: 6px;
            height: 6px;
            background: #fff;
            border-radius: 50%;
            animation: pulse 1.5s infinite;
        }

        @keyframes pulse {
            0% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(1.2); }
            100% { opacity: 1; transform: scale(1); }
        }

        /* ── States ── */
        .empty-state {
            padding: 60px 24px;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            color: var(--text-secondary);
        }
        
        .empty-icon { margin-bottom: 16px; opacity: 0.5; }
        .empty-title { font-size: 15px; font-weight: 500; color: var(--text-primary); margin-bottom: 8px; }

        .loading-state {
            display: none;
            flex-direction: column;
            align-items: center;
            padding: 60px 24px;
            gap: 16px;
        }

        .spinner {
            width: 24px;
            height: 24px;
            border: 2px solid var(--border);
            border-top-color: var(--accent);
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }

        @keyframes spin { to { transform: rotate(360deg); } }
        
        .error-message {
            display: none;
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.2);
            color: var(--danger);
            padding: 12px 16px;
            border-radius: 6px;
            margin-bottom: 24px;
            font-size: 13px;
        }
        
        /* ── Toasts ── */
        .toast-container {
            position: fixed;
            bottom: 24px;
            right: 24px;
            display: flex;
            flex-direction: column;
            gap: 10px;
            z-index: 100;
        }
        
        .toast {
            background: var(--bg-surface);
            border: 1px solid var(--border);
            color: var(--text-primary);
            padding: 12px 16px;
            border-radius: 6px;
            font-size: 13px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            display: flex;
            align-items: center;
            gap: 10px;
            opacity: 0;
            transform: translateY(10px);
            animation: slideIn 0.2s forwards;
        }
        
        @keyframes slideIn {
            to { opacity: 1; transform: translateY(0); }
        }

    </style>
</head>
<body>

    <!-- Sidebar -->
    <aside class="sidebar">
        <div class="brand">
            <div class="brand-icon">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M2 12A10 10 0 0 1 22 12"></path>
                    <circle cx="12" cy="12" r="3"></circle>
                </svg>
            </div>
            VisionAI
        </div>
        
        <div class="nav-section">
            <div class="nav-label">Workspace</div>
            <a class="nav-item active" data-view="dashboard">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
                Dashboard
            </a>
            <a class="nav-item" data-view="detect">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path><circle cx="12" cy="13" r="4"></circle></svg>
                Detect
            </a>
            <a class="nav-item" data-view="history">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                History
            </a>
        </div>

        <div class="nav-section" style="margin-top: auto;">
            <div class="nav-label">System</div>
            <a class="nav-item" data-view="settings">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
                Settings
            </a>
        </div>
    </aside>

    <!-- Main Content -->
    <main class="main-container">
        <header class="header">
            <div class="header-title" id="header-title">Dashboard</div>
            <div class="header-actions">
                <a href="/docs" target="_blank" class="btn-secondary" style="text-decoration: none; font-size: 13px;">API Docs</a>
                <a href="https://github.com/NB7551498/Object-Detection" target="_blank" class="btn-secondary" style="text-decoration: none; font-size: 13px; display: flex; align-items: center; gap: 6px;">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"></path></svg>
                    GitHub
                </a>
            </div>
        </header>

        <div class="content-area">
            
            <!-- Dashboard View -->
            <div id="view-dashboard" class="view active">
                <div>
                    <h1>Welcome to VisionAI</h1>
                    <p>Analyze images and identify objects using computer vision.</p>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <span class="stat-label">Total Detections</span>
                        <span class="stat-value" id="stat-total">0</span>
                    </div>
                    <div class="stat-card">
                        <span class="stat-label">Objects Found</span>
                        <span class="stat-value" id="stat-objects">0</span>
                    </div>
                    <div class="stat-card">
                        <span class="stat-label">Avg Confidence</span>
                        <span class="stat-value" id="stat-conf">0%</span>
                    </div>
                    <div class="stat-card">
                        <span class="stat-label">Active Model</span>
                        <span class="stat-value" style="font-size: 18px; line-height: 32px;" id="stat-model">YOLOv8 Nano</span>
                    </div>
                </div>

                <div class="card" style="flex: 1;">
                    <div class="card-header">
                        <h3 class="card-title">Recent Activity</h3>
                        <p class="card-desc">Overview of your latest detection tasks.</p>
                    </div>
                    <div id="dash-recent-list">
                        <div class="empty-state" style="padding: 30px;">
                            <span class="empty-title">No activity yet</span>
                            <p style="font-size: 13px;">Go to the Detect workspace to analyze your first image.</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Detect View -->
            <div id="view-detect" class="view">
                
                <div class="workspace-tabs">
                    <button class="ws-tab active" onclick="switchWsTab('image')">Image Upload</button>
                    <button class="ws-tab" onclick="switchWsTab('live')">Live Camera</button>
                </div>

                <div id="error-alert" class="error-message"></div>

                <!-- Image Upload Mode -->
                <div id="ws-mode-image">
                    
                    <div id="upload-container" class="upload-zone" onclick="document.getElementById('file-input').click()">
                        <svg class="upload-icon" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>
                        <div class="upload-text-main">Click or drag image here</div>
                        <div class="upload-text-sub">Supports JPG, PNG, WEBP (Max 15MB)</div>
                        <button class="btn-secondary" style="pointer-events: none;">Browse Files</button>
                    </div>
                    <input type="file" id="file-input" accept="image/*" style="display: none;" onchange="handleFileSelect(event)">

                    <div id="processing-state" class="loading-state">
                        <div class="spinner"></div>
                        <div style="font-weight: 500;">Analyzing image...</div>
                        <div style="font-size: 13px; color: var(--text-secondary);">Running YOLO object detection</div>
                    </div>

                    <div id="results-container" class="results-layout">
                        <div class="image-preview-container">
                            <img id="result-image" alt="Detection result">
                        </div>
                        <div class="card" style="padding: 16px;">
                            <div class="card-header" style="margin-bottom: 12px;">
                                <h3 class="card-title">Detection Results</h3>
                                <div style="display: flex; gap: 12px; font-size: 12px; color: var(--text-secondary); margin-top: 8px;">
                                    <span><span id="res-count" style="color: var(--text-primary); font-weight: 500;">0</span> Objects</span>
                                    <span>•</span>
                                    <span><span id="res-time" style="color: var(--text-primary); font-weight: 500;">0</span> ms</span>
                                </div>
                            </div>
                            <div style="overflow-y: auto; max-height: 400px; border: 1px solid var(--border); border-radius: 6px;">
                                <table class="data-table">
                                    <thead>
                                        <tr>
                                            <th>Object</th>
                                            <th>Confidence</th>
                                        </tr>
                                    </thead>
                                    <tbody id="res-table-body">
                                        <!-- populated dynamically -->
                                    </tbody>
                                </table>
                            </div>
                            <div style="margin-top: 16px; display: flex; gap: 10px;">
                                <button class="btn-secondary" style="flex: 1;" onclick="resetWorkspace()">New Image</button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Live Camera Mode -->
                <div id="ws-mode-live" class="live-container">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h2 style="font-size: 16px; margin-bottom: 4px;">Real-time Analysis</h2>
                            <p style="font-size: 13px;">Local frame rendering decoupled from inference latency.</p>
                        </div>
                        <button id="btn-camera" class="btn-primary" onclick="toggleCamera()">Start Camera</button>
                    </div>

                    <div class="live-viewport">
                        <video id="webcam-video" autoplay playsinline muted></video>
                        <canvas id="live-canvas"></canvas>
                        
                        <div id="cam-placeholder" class="empty-state">
                            <svg class="empty-icon" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path><circle cx="12" cy="13" r="4"></circle></svg>
                            <span class="empty-title">Camera Idle</span>
                            <span style="font-size: 13px;">Start camera to begin real-time detection.</span>
                        </div>

                        <div id="cam-hud" class="live-hud" style="display: none;">
                            <div class="hud-left">
                                <div class="hud-badge live-indicator">
                                    <div class="dot-pulse"></div> LIVE
                                </div>
                                <div class="hud-badge" id="hud-fps">0 FPS</div>
                            </div>
                            <div class="hud-right">
                                <div class="hud-badge" id="hud-latency">-- ms</div>
                                <div class="hud-badge"><span id="hud-obj" style="color: var(--accent);">0</span> objects</div>
                            </div>
                        </div>
                    </div>
                </div>

            </div>

            <!-- History View -->
            <div id="view-history" class="view">
                <div>
                    <h1>Detection History</h1>
                    <p>Review your recent image analysis results.</p>
                </div>

                <div class="card" style="padding: 0; overflow: hidden;">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Date & Time</th>
                                <th>Model</th>
                                <th>Objects Found</th>
                                <th>Avg Confidence</th>
                            </tr>
                        </thead>
                        <tbody id="history-table-body">
                            <!-- populated dynamically -->
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Settings View -->
            <div id="view-settings" class="view">
                <div>
                    <h1>System Settings</h1>
                    <p>Manage application preferences and model configuration.</p>
                </div>

                <div class="card">
                    <h3 class="card-title">Model Configuration</h3>
                    <p class="card-desc" style="margin-bottom: 24px;">Current backend parameters running on the server.</p>
                    
                    <div style="display: flex; flex-direction: column; gap: 16px; max-width: 400px;">
                        <div>
                            <label style="display: block; font-size: 12px; color: var(--text-secondary); margin-bottom: 6px;">Active Model Weights</label>
                            <input type="text" id="setting-model" readonly value="Loading..." style="width: 100%; background: var(--bg-surface-secondary); border: 1px solid var(--border); color: var(--text-primary); padding: 10px; border-radius: 6px; outline: none; font-family: monospace;">
                        </div>
                        <div>
                            <label style="display: block; font-size: 12px; color: var(--text-secondary); margin-bottom: 6px;">Compute Device</label>
                            <input type="text" id="setting-device" readonly value="Loading..." style="width: 100%; background: var(--bg-surface-secondary); border: 1px solid var(--border); color: var(--text-primary); padding: 10px; border-radius: 6px; outline: none; font-family: monospace;">
                        </div>
                        <div>
                            <label style="display: block; font-size: 12px; color: var(--text-secondary); margin-bottom: 6px;">Confidence Threshold</label>
                            <input type="text" id="setting-conf" readonly value="Loading..." style="width: 100%; background: var(--bg-surface-secondary); border: 1px solid var(--border); color: var(--text-primary); padding: 10px; border-radius: 6px; outline: none; font-family: monospace;">
                        </div>
                    </div>
                </div>
            </div>

        </div>
    </main>

    <div class="toast-container" id="toast-container"></div>

    <script>
        // ── View Routing ──
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', () => {
                document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
                item.classList.add('active');
                
                const targetId = 'view-' + item.dataset.view;
                document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
                document.getElementById(targetId).classList.add('active');
                
                document.getElementById('header-title').textContent = item.textContent.trim();
                
                if (item.dataset.view === 'dashboard') updateDashboard();
                if (item.dataset.view === 'history') updateHistory();
            });
        });

        // ── Toast Notifications ──
        function showToast(message) {
            const container = document.getElementById('toast-container');
            const toast = document.createElement('div');
            toast.className = 'toast';
            toast.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--success)" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg> ${message}`;
            container.appendChild(toast);
            setTimeout(() => {
                toast.style.opacity = '0';
                setTimeout(() => toast.remove(), 200);
            }, 3000);
        }

        function showError(msg) {
            const err = document.getElementById('error-alert');
            err.textContent = msg;
            err.style.display = 'block';
            setTimeout(() => err.style.display = 'none', 5000);
        }

        // ── Local Storage DB ──
        const DB = {
            getStats: () => JSON.parse(localStorage.getItem('visionai_stats') || '{"runs":0,"objects":0,"sumConf":0}'),
            saveRun: (count, avgConf) => {
                const stats = DB.getStats();
                stats.runs += 1;
                stats.objects += count;
                stats.sumConf += avgConf;
                localStorage.setItem('visionai_stats', JSON.stringify(stats));

                const history = JSON.parse(localStorage.getItem('visionai_history') || '[]');
                history.unshift({
                    date: new Date().toLocaleString(),
                    count: count,
                    avgConf: avgConf
                });
                if(history.length > 50) history.pop();
                localStorage.setItem('visionai_history', JSON.stringify(history));
            },
            getHistory: () => JSON.parse(localStorage.getItem('visionai_history') || '[]')
        };

        function updateDashboard() {
            const stats = DB.getStats();
            document.getElementById('stat-total').textContent = stats.runs;
            document.getElementById('stat-objects').textContent = stats.objects;
            document.getElementById('stat-conf').textContent = stats.runs > 0 ? Math.round((stats.sumConf / stats.runs)*100) + '%' : '0%';
            
            const hist = DB.getHistory().slice(0, 5);
            const list = document.getElementById('dash-recent-list');
            if (hist.length > 0) {
                list.innerHTML = hist.map(h => `
                    <div style="padding: 12px 24px; border-top: 1px solid var(--border); display: flex; justify-content: space-between; font-size: 13px;">
                        <span style="color: var(--text-secondary);">${h.date}</span>
                        <span><strong style="color: var(--text-primary);">${h.count}</strong> objects found</span>
                    </div>
                `).join('');
            }
        }

        function updateHistory() {
            const hist = DB.getHistory();
            const tbody = document.getElementById('history-table-body');
            if (hist.length === 0) {
                tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: var(--text-secondary);">No history available.</td></tr>';
                return;
            }
            tbody.innerHTML = hist.map(h => `
                <tr>
                    <td>${h.date}</td>
                    <td>YOLOv8 Nano</td>
                    <td>${h.count}</td>
                    <td><span class="badge ${h.avgConf >= 0.7 ? 'badge-success' : 'badge-warning'}">${Math.round(h.avgConf * 100)}%</span></td>
                </tr>
            `).join('');
        }

        // ── Fetch Settings ──
        fetch('/model-info')
            .then(r => r.json())
            .then(data => {
                document.getElementById('setting-model').value = data.model;
                document.getElementById('setting-device').value = data.device.toUpperCase();
                document.getElementById('setting-conf').value = data.confidence_threshold;
                document.getElementById('stat-model').textContent = data.model;
            })
            .catch(() => {});

        // ── Workspace: Image Upload ──
        function switchWsTab(tab) {
            document.querySelectorAll('.ws-tab').forEach(b => b.classList.remove('active'));
            document.querySelector(`.ws-tab[onclick*="${tab}"]`).classList.add('active');
            
            if (tab === 'image') {
                document.getElementById('ws-mode-image').style.display = 'block';
                document.getElementById('ws-mode-live').style.display = 'none';
                if(isStreaming) toggleCamera();
            } else {
                document.getElementById('ws-mode-image').style.display = 'none';
                document.getElementById('ws-mode-live').style.display = 'flex';
            }
        }

        const dropzone = document.getElementById('upload-container');
        dropzone.addEventListener('dragover', (e) => { e.preventDefault(); dropzone.classList.add('dragover'); });
        dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));
        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('dragover');
            if (e.dataTransfer.files.length) processFile(e.dataTransfer.files[0]);
        });

        function handleFileSelect(e) {
            if (e.target.files.length) processFile(e.target.files[0]);
        }

        async function processFile(file) {
            document.getElementById('upload-container').style.display = 'none';
            document.getElementById('processing-state').style.display = 'flex';
            document.getElementById('results-container').style.display = 'none';
            document.getElementById('error-alert').style.display = 'none';

            const formData = new FormData();
            formData.append('file', file);

            try {
                const res = await fetch('/predict', { method: 'POST', body: formData });
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                const data = await res.json();
                
                document.getElementById('processing-state').style.display = 'none';
                document.getElementById('results-container').style.display = 'grid';
                document.getElementById('result-image').src = data.annotated_image;
                
                document.getElementById('res-count').textContent = data.detections.length;
                document.getElementById('res-time').textContent = data.inference_time_ms || '--';
                
                const tbody = document.getElementById('res-table-body');
                if (data.detections.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="2" style="text-align: center; color: var(--text-secondary);">No objects detected.</td></tr>';
                } else {
                    let sumConf = 0;
                    tbody.innerHTML = data.detections.map(d => {
                        sumConf += d.confidence;
                        return `<tr>
                            <td><span style="text-transform: capitalize; font-weight: 500;">${d.label}</span></td>
                            <td><span class="badge ${d.confidence >= 0.7 ? 'badge-success' : 'badge-warning'}">${Math.round(d.confidence*100)}%</span></td>
                        </tr>`;
                    }).join('');
                    
                    const avgConf = sumConf / data.detections.length;
                    DB.saveRun(data.detections.length, avgConf);
                }
                showToast("Detection completed successfully");
                
            } catch(e) {
                document.getElementById('processing-state').style.display = 'none';
                resetWorkspace();
                showError("Detection failed. Please ensure the file is a valid image.");
            }
        }

        function resetWorkspace() {
            document.getElementById('upload-container').style.display = 'flex';
            document.getElementById('processing-state').style.display = 'none';
            document.getElementById('results-container').style.display = 'none';
            document.getElementById('file-input').value = '';
        }

        // ── Workspace: Live Camera ──
        let cameraStream = null;
        let isStreaming = false;
        let ws = null;
        let frameCount = 0;
        let fpsTimer = performance.now();
        let latestDetections = [];
        let renderLoop = null;

        const videoElem = document.getElementById('webcam-video');
        const liveCanvas = document.getElementById('live-canvas');
        const canvasCtx = liveCanvas.getContext('2d');
        const offscreenCanvas = document.createElement('canvas');
        const offscreenCtx = offscreenCanvas.getContext('2d');

        async function toggleCamera() {
            if (isStreaming) { stopCamera(); return; }
            try {
                cameraStream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 }, audio: false });
                videoElem.srcObject = cameraStream;
                await videoElem.play();

                liveCanvas.width = videoElem.videoWidth || 640;
                liveCanvas.height = videoElem.videoHeight || 480;
                offscreenCanvas.width = 640;
                offscreenCanvas.height = 480;

                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                ws = new WebSocket(`${protocol}//${window.location.host}/ws/live`);
                ws.onopen = () => { streamNextFrame(); renderLoop = requestAnimationFrame(renderLiveFeed); };
                ws.onmessage = (e) => {
                    if (!isStreaming) return;
                    const data = JSON.parse(e.data);
                    if (data.inference_time_ms) document.getElementById('hud-latency').textContent = `${data.inference_time_ms} ms`;
                    frameCount++;
                    const now = performance.now();
                    if (now - fpsTimer >= 1000) { document.getElementById('hud-fps').textContent = `${frameCount} FPS`; frameCount = 0; fpsTimer = now; }
                    if (data.detections) {
                        latestDetections = data.detections;
                        document.getElementById('hud-obj').textContent = data.detections.length;
                    }
                    streamNextFrame();
                };

                isStreaming = true;
                document.getElementById('cam-placeholder').style.display = 'none';
                document.getElementById('cam-hud').style.display = 'flex';
                const btn = document.getElementById('btn-camera');
                btn.textContent = 'Stop Camera';
                btn.style.backgroundColor = 'var(--bg-surface-secondary)';
                btn.style.border = '1px solid var(--border)';
                btn.style.color = 'var(--danger)';
            } catch (err) {
                showError("Camera access denied.");
            }
        }

        function stopCamera() {
            isStreaming = false;
            if (renderLoop) cancelAnimationFrame(renderLoop);
            if (ws) ws.close();
            if (cameraStream) cameraStream.getTracks().forEach(t => t.stop());
            videoElem.srcObject = null;
            canvasCtx.clearRect(0, 0, liveCanvas.width, liveCanvas.height);
            document.getElementById('cam-placeholder').style.display = 'flex';
            document.getElementById('cam-hud').style.display = 'none';
            const btn = document.getElementById('btn-camera');
            btn.textContent = 'Start Camera';
            btn.style = '';
        }

        function renderLiveFeed() {
            if (!isStreaming) return;
            canvasCtx.drawImage(videoElem, 0, 0, liveCanvas.width, liveCanvas.height);
            latestDetections.forEach(det => {
                const b = det.box;
                const x = b.xmin * (liveCanvas.width / offscreenCanvas.width);
                const y = b.ymin * (liveCanvas.height / offscreenCanvas.height);
                const w = (b.xmax - b.xmin) * (liveCanvas.width / offscreenCanvas.width);
                const h = (b.ymax - b.ymin) * (liveCanvas.height / offscreenCanvas.height);

                canvasCtx.strokeStyle = 'var(--accent)';
                canvasCtx.lineWidth = 2;
                canvasCtx.strokeRect(x, y, w, h);
                
                const txt = `${det.label.toUpperCase()} ${Math.round(det.confidence*100)}%`;
                canvasCtx.font = '11px Inter, sans-serif';
                canvasCtx.fontWeight = '600';
                const tw = canvasCtx.measureText(txt).width;
                canvasCtx.fillStyle = 'var(--accent)';
                canvasCtx.fillRect(x, y - 20, tw + 8, 20);
                canvasCtx.fillStyle = '#fff';
                canvasCtx.fillText(txt, x + 4, y - 6);
            });
            renderLoop = requestAnimationFrame(renderLiveFeed);
        }

        function streamNextFrame() {
            if (!isStreaming || !ws || ws.readyState !== WebSocket.OPEN) return;
            offscreenCtx.drawImage(videoElem, 0, 0, offscreenCanvas.width, offscreenCanvas.height);
            offscreenCanvas.toBlob((blob) => { if (blob && ws.readyState === WebSocket.OPEN) ws.send(blob); }, 'image/jpeg', 0.5);
        }

        // Init
        updateDashboard();
    </script>
</body>
</html>'''

with open('app/templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("UI successfully built.")
