"""
Dashboard Components
====================
Reusable Streamlit UI components for the Automotive Data Platform.
All icons use inline SVG (Lucide-style) and modern Material Symbols — zero emojis.
Includes modern glassmorphic loading popups and overlays.
"""

from __future__ import annotations

import contextlib
import io
from typing import Any, Iterator

import pandas as pd
import streamlit as st


# ---------------------------------------------------------------------------
# SVG Icon Library  (Lucide-compatible, 24 × 24 viewBox, stroke-based)
# ---------------------------------------------------------------------------

_ICONS: dict[str, str] = {
    "car": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M5 17H3a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2h1"/>'
        '<path d="M19 17h2a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-1"/>'
        '<path d="M14 17H9"/>'
        '<circle cx="6.5" cy="17.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/>'
        '<path d="M3 9h18l-2-5H5L3 9Z"/>'
        "</svg>"
    ),
    "package": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M12 22V12"/><path d="m2 7 10 5 10-5"/>'
        '<path d="M2 12l10 5 10-5"/>'
        '<path d="M2 7l10-5 10 5v10l-10 5L2 17Z"/>'
        "</svg>"
    ),
    "dollar": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<line x1="12" y1="2" x2="12" y2="22"/>'
        '<path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>'
        "</svg>"
    ),
    "tag": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="m15 5 6.3 6.3a2.4 2.4 0 0 1 0 3.4L17 19"/>'
        '<path d="M9.586 5.586A2 2 0 0 0 8.172 5H3a1 1 0 0 0-1 1v5.172a2 2 0 0 0 .586 1.414L8.29 18.29a2.426 2.426 0 0 0 3.42 0l4.58-4.58a2.426 2.426 0 0 0 0-3.42z"/>'
        '<circle cx="6.5" cy="9.5" r="1.5"/>'
        "</svg>"
    ),
    "fuel": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M3 22V8"/><path d="M3 8h12v14H3z"/>'
        '<path d="M15 8h2a2 2 0 0 1 2 2v4a2 2 0 0 0 2 2h0V6l-3-3"/>'
        '<line x1="3" y1="13" x2="15" y2="13"/>'
        "</svg>"
    ),
    "wrench": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>'
        "</svg>"
    ),
    "layout-dashboard": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<rect width="7" height="9" x="3" y="3" rx="1"/>'
        '<rect width="7" height="5" x="14" y="3" rx="1"/>'
        '<rect width="7" height="9" x="14" y="12" rx="1"/>'
        '<rect width="7" height="5" x="3" y="16" rx="1"/>'
        "</svg>"
    ),
    "table": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M12 3v18"/><rect width="18" height="18" x="3" y="3" rx="2"/>'
        '<path d="M3 9h18"/><path d="M3 15h18"/>'
        "</svg>"
    ),
    "shield-check": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10"/>'
        '<path d="m9 12 2 2 4-4"/>'
        "</svg>"
    ),
    "trending-up": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/>'
        '<polyline points="16 7 22 7 22 13"/>'
        "</svg>"
    ),
    "gauge": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="m12 14 4-4"/>'
        '<path d="M3.34 19a10 10 0 1 1 17.32 0"/>'
        "</svg>"
    ),
    "settings": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/>'
        '<circle cx="12" cy="12" r="3"/>'
        "</svg>"
    ),
    "file-text": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/>'
        '<path d="M14 2v4a2 2 0 0 0 2 2h4"/>'
        '<line x1="10" y1="13" x2="16" y2="13"/>'
        '<line x1="10" y1="17" x2="14" y2="17"/>'
        '<line x1="10" y1="9" x2="12" y2="9"/>'
        "</svg>"
    ),
    "filter": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>'
        "</svg>"
    ),
    "refresh": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/>'
        '<path d="M21 3v5h-5"/>'
        '<path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/>'
        '<path d="M8 16H3v5"/>'
        "</svg>"
    ),
    "download": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>'
        '<polyline points="7 10 12 15 17 10"/>'
        '<line x1="12" y1="15" x2="12" y2="3"/>'
        "</svg>"
    ),
    "search": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>'
        "</svg>"
    ),
    "list": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/>'
        '<line x1="8" y1="18" x2="21" y2="18"/>'
        '<line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/>'
        '<line x1="3" y1="18" x2="3.01" y2="18"/>'
        "</svg>"
    ),
    "play": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<polygon points="5 3 19 12 5 21 5 3"/>'
        "</svg>"
    ),
    "alert-triangle": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/>'
        '<path d="M12 9v4"/><path d="M12 17h.01"/>'
        "</svg>"
    ),
    "check-circle": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>'
        '<polyline points="22 4 12 14.01 9 11.01"/>'
        "</svg>"
    ),
    "database": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<ellipse cx="12" cy="5" rx="9" ry="3"/>'
        '<path d="M3 5V19A9 3 0 0 0 21 19V5"/>'
        '<path d="M3 12A9 3 0 0 0 21 12"/>'
        "</svg>"
    ),
    "cpu": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<rect width="16" height="16" x="4" y="4" rx="2"/>'
        '<rect width="6" height="6" x="9" y="9" rx="1"/>'
        '<path d="M15 2v2"/><path d="M15 20v2"/><path d="M2 15h2"/><path d="M2 9h2"/>'
        '<path d="M20 15h2"/><path d="M20 9h2"/><path d="M9 2v2"/><path d="M9 20v2"/>'
        "</svg>"
    ),
    "sparkles": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z"/>'
        "</svg>"
    ),
    "arrow-up": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">'
        '<line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/>'
        "</svg>"
    ),
}


def icon(name: str, color: str = "currentColor", size: int = 18) -> str:
    """Return an inline SVG string for the given icon name."""
    svg = _ICONS.get(name, _ICONS["car"])
    svg = svg.replace('stroke="currentColor"', f'stroke="{color}"')
    for sz in ("14", "16", "18", "20", "22", "24"):
        svg = svg.replace(f'width="{sz}"', f'width="{size}"').replace(f'height="{sz}"', f'height="{size}"')
    return svg


def icon_label(icon_name: str, text: str, color: str = "#7EB3FF") -> str:
    """Return an HTML snippet: SVG icon + text side-by-side."""
    return (
        f'<span style="display:inline-flex;align-items:center;gap:8px;color:{color};font-weight:500;">'
        f'{icon(icon_name, color)}'
        f'<span>{text}</span>'
        f'</span>'
    )


# ---------------------------------------------------------------------------
# Modern Loading Popup & Global Loader Styling
# ---------------------------------------------------------------------------

LOADING_POPUP_CSS = """
<style>
/* ── Modern Glassmorphic Loading Popup Overlay ── */
#ag-loader-overlay {
    position: fixed;
    inset: 0;
    z-index: 999999;
    background: rgba(6, 8, 16, 0.82);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    display: flex;
    align-items: center;
    justify-content: center;
    animation: ag-overlay-fade 0.25s ease-out;
}

@keyframes ag-overlay-fade {
    from { opacity: 0; }
    to { opacity: 1; }
}

.ag-modal-card {
    background: linear-gradient(145deg, rgba(22, 26, 46, 0.95), rgba(12, 14, 28, 0.98));
    border: 1px solid rgba(126, 179, 255, 0.28);
    border-radius: 20px;
    padding: 2.2rem 2.6rem;
    box-shadow: 0 24px 70px rgba(0, 0, 0, 0.75), 0 0 35px rgba(99, 102, 241, 0.2);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 18px;
    max-width: 440px;
    width: 90%;
    text-align: center;
    animation: ag-modal-pop 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes ag-modal-pop {
    from { transform: scale(0.92); opacity: 0; }
    to { transform: scale(1); opacity: 1; }
}

/* ── Modern Orbit Ring Spinner ── */
.ag-spinner-box {
    position: relative;
    width: 72px;
    height: 72px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.ag-spinner-outer {
    position: absolute;
    inset: 0;
    border-radius: 50%;
    border: 3px solid transparent;
    border-top-color: #38bdf8;
    border-right-color: #818cf8;
    animation: ag-spin-cw 1s cubic-bezier(0.55, 0.15, 0.45, 0.85) infinite;
}

.ag-spinner-inner {
    position: absolute;
    inset: 9px;
    border-radius: 50%;
    border: 2px solid transparent;
    border-bottom-color: #c084fc;
    border-left-color: #60a5fa;
    animation: ag-spin-ccw 0.7s linear infinite;
}

.ag-spinner-glow {
    position: absolute;
    width: 42px;
    height: 42px;
    background: radial-gradient(circle, rgba(126, 179, 255, 0.35) 0%, transparent 70%);
    border-radius: 50%;
    animation: ag-pulse 1.6s ease-in-out infinite;
}

@keyframes ag-spin-cw {
    to { transform: rotate(360deg); }
}

@keyframes ag-spin-ccw {
    to { transform: rotate(-360deg); }
}

@keyframes ag-pulse {
    0%, 100% { transform: scale(0.9); opacity: 0.6; }
    50% { transform: scale(1.3); opacity: 1; }
}

.ag-modal-title {
    font-family: 'Inter', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: #e2e8f0;
    letter-spacing: -0.01em;
    margin: 0;
}

.ag-modal-sub {
    font-family: 'Inter', sans-serif;
    font-size: 0.84rem;
    color: #94a3b8;
    line-height: 1.45;
    margin: 0;
}

/* ── Progress Shimmer Bar ── */
.ag-modal-progress {
    width: 100%;
    height: 5px;
    background: rgba(255, 255, 255, 0.08);
    border-radius: 99px;
    overflow: hidden;
    position: relative;
    margin-top: 4px;
}

.ag-modal-progress-bar {
    position: absolute;
    top: 0;
    bottom: 0;
    left: -40%;
    width: 40%;
    background: linear-gradient(90deg, transparent, #38bdf8, #818cf8, transparent);
    border-radius: 99px;
    animation: ag-shimmer 1.4s ease-in-out infinite;
}

@keyframes ag-shimmer {
    0% { left: -40%; width: 40%; }
    50% { left: 40%; width: 60%; }
    100% { left: 100%; width: 40%; }
}

.ag-modal-dots {
    display: flex;
    gap: 8px;
    align-items: center;
    justify-content: center;
}

.ag-modal-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #475569;
    animation: ag-dot-glow 1.2s ease-in-out infinite;
}
.ag-modal-dot:nth-child(2) { animation-delay: 0.2s; }
.ag-modal-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes ag-dot-glow {
    0%, 80%, 100% { background: #475569; transform: scale(1); }
    40% { background: #38bdf8; transform: scale(1.35); box-shadow: 0 0 10px #38bdf8; }
}

/* ── Modern Styling for Native Streamlit Spinners & Status Widgets ── */
[data-testid="stSpinner"] {
    background: linear-gradient(135deg, rgba(22, 26, 46, 0.92), rgba(15, 17, 32, 0.95)) !important;
    border: 1px solid rgba(126, 179, 255, 0.3) !important;
    border-radius: 12px !important;
    padding: 0.9rem 1.4rem !important;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.45) !important;
    backdrop-filter: blur(10px) !important;
    color: #cbd5e1 !important;
    font-weight: 500 !important;
    margin: 10px 0 !important;
}

[data-testid="stStatusWidget"] {
    background: linear-gradient(135deg, rgba(20, 24, 44, 0.9), rgba(12, 14, 26, 0.95)) !important;
    border: 1px solid rgba(126, 179, 255, 0.25) !important;
    border-radius: 14px !important;
    box-shadow: 0 10px 32px rgba(0, 0, 0, 0.4) !important;
    backdrop-filter: blur(10px) !important;
}
</style>
"""

LOADING_HIDE_JS = """
<script>
(function() {
    var el = document.getElementById('ag-loader-overlay');
    if (el) {
        el.style.opacity = '0';
        setTimeout(function() { el.style.display = 'none'; }, 200);
    }
})();
</script>
"""


def show_loading_overlay(
    message: str = "Initialising Analytics Pipeline",
    sub: str = "Loading dataset, running validation, and compiling metrics…",
    placeholder: Any = None,
) -> None:
    """Inject a modern glassmorphic loading popup modal into the page or placeholder."""
    renderer = placeholder if placeholder is not None else st
    renderer.markdown(LOADING_POPUP_CSS, unsafe_allow_html=True)
    overlay_html = (
        f'<div id="ag-loader-overlay">'
        f'<div class="ag-modal-card">'
        f'<div class="ag-spinner-box">'
        f'<div class="ag-spinner-outer"></div>'
        f'<div class="ag-spinner-inner"></div>'
        f'<div class="ag-spinner-glow"></div>'
        f'</div>'
        f'<div class="ag-modal-title">{message}</div>'
        f'<div class="ag-modal-sub">{sub}</div>'
        f'<div class="ag-modal-progress">'
        f'<div class="ag-modal-progress-bar"></div>'
        f'</div>'
        f'<div class="ag-modal-dots">'
        f'<div class="ag-modal-dot"></div>'
        f'<div class="ag-modal-dot"></div>'
        f'<div class="ag-modal-dot"></div>'
        f'</div>'
        f'</div>'
        f'</div>'
    )
    renderer.markdown(overlay_html, unsafe_allow_html=True)


def hide_loading_overlay(placeholder: Any = None) -> None:
    """Hide the loading overlay modal via placeholder clearing and CSS override."""
    if placeholder is not None:
        placeholder.empty()
    st.markdown(
        "<style>#ag-loader-overlay { display: none !important; opacity: 0 !important; visibility: hidden !important; pointer-events: none !important; }</style>",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# KPI card — icon-based, zero emojis
# ---------------------------------------------------------------------------

_KPI_CARD_CSS = """
<style>
.ag-kpi-card {
    background: linear-gradient(135deg, #181b30 0%, #222644 100%);
    border: 1px solid #363b63;
    border-radius: 14px;
    padding: 1.15rem 1.35rem;
    display: flex;
    align-items: center;
    gap: 15px;
    box-shadow: 0 4px 22px rgba(0, 0, 0, 0.35);
    transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
    margin-bottom: 0.6rem;
}
.ag-kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(126, 179, 255, 0.16);
    border-color: #6366f1;
}
.ag-kpi-icon {
    width: 46px; height: 46px;
    background: rgba(126, 179, 255, 0.12);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}
.ag-kpi-body { flex: 1; min-width: 0; }
.ag-kpi-label {
    font-size: 0.74rem;
    font-weight: 600;
    color: #8892b0;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-bottom: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.ag-kpi-value {
    font-size: 1.55rem;
    font-weight: 700;
    color: #7EB3FF;
    line-height: 1.1;
    white-space: nowrap;
}
.ag-kpi-delta {
    font-size: 0.78rem;
    font-weight: 600;
    color: #34d399;
    margin-top: 3px;
    display: inline-flex;
    align-items: center;
    gap: 3px;
}
</style>
"""

_kpi_css_injected = False


def kpi_card(label: str, value: str, icon_name: str = "gauge", delta: str | None = None) -> None:
    """Render a single icon-based KPI card with clean SVG icon."""
    global _kpi_css_injected
    if not _kpi_css_injected:
        st.markdown(_KPI_CARD_CSS, unsafe_allow_html=True)
        _kpi_css_injected = True

    delta_html = ""
    if delta:
        up_svg = icon("arrow-up", "#34d399", 12)
        delta_html = f'<div class="ag-kpi-delta">{up_svg}<span>{delta}</span></div>'

    svg = icon(icon_name, "#7EB3FF", 22)

    card_html = (
        f'<div class="ag-kpi-card">'
        f'<div class="ag-kpi-icon">{svg}</div>'
        f'<div class="ag-kpi-body">'
        f'<div class="ag-kpi-label">{label}</div>'
        f'<div class="ag-kpi-value">{value}</div>'
        f'{delta_html}'
        f'</div>'
        f'</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)


def kpi_row(kpis: list[dict[str, Any]], cols: int = 3) -> None:
    """Render a row of icon-based KPI cards.

    Args:
        kpis: List of dicts with keys: label, value, icon, (optional) delta.
        cols: Number of columns.
    """
    columns = st.columns(cols)
    for i, kpi in enumerate(kpis):
        with columns[i % cols]:
            kpi_card(
                label=kpi.get("label", ""),
                value=str(kpi.get("value", "")),
                icon_name=kpi.get("icon", "gauge"),
                delta=kpi.get("delta"),
            )


# ---------------------------------------------------------------------------
# Sidebar filter builder
# ---------------------------------------------------------------------------

def build_sidebar_filters(df: pd.DataFrame) -> dict[str, Any]:
    """Render sidebar filters and return filter dict."""
    with st.sidebar:
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:10px;padding:4px 0 2px;">'
            f'{icon("filter", "#7EB3FF", 16)}'
            f'<span style="font-weight:600;font-size:0.95rem;color:#7EB3FF;">Filters</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        manufacturers = sorted(df["manufacturer"].dropna().unique().tolist())
        sel_mfr = st.multiselect("Manufacturer", manufacturers, key="filter_mfr")

        if sel_mfr:
            model_options = sorted(df[df["manufacturer"].isin(sel_mfr)]["model"].dropna().unique())
        else:
            model_options = sorted(df["model"].dropna().unique().tolist())
        sel_model = st.multiselect("Model", model_options, key="filter_model")

        fuel_types = sorted(df["fuel_type"].dropna().unique().tolist())
        sel_fuel = st.multiselect("Fuel Type", fuel_types, key="filter_fuel")

        vtypes = sorted(df["vehicle_type"].dropna().unique().tolist())
        sel_vtype = st.multiselect("Vehicle Type", vtypes, key="filter_vtype")

        trans = sorted(df["transmission"].dropna().unique().tolist())
        sel_trans = st.multiselect("Transmission", trans, key="filter_trans")

        min_yr = int(df["vehicle_year"].min())
        max_yr = int(df["vehicle_year"].max())
        sel_yr = st.slider(
            "Model Year Range", min_yr, max_yr, (min_yr, max_yr), key="filter_year"
        )

        st.divider()
        if st.button("Reset Filters", use_container_width=True, icon=":material/refresh:"):
            for k in ["filter_mfr", "filter_model", "filter_fuel",
                      "filter_vtype", "filter_trans", "filter_year"]:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()

    return {
        "manufacturers": sel_mfr,
        "models":        sel_model,
        "fuel_types":    sel_fuel,
        "vehicle_types": sel_vtype,
        "transmissions": sel_trans,
        "year_range":    sel_yr,
    }


def apply_filters(df: pd.DataFrame, filters: dict[str, Any]) -> pd.DataFrame:
    """Apply sidebar filters to *df*."""
    mask = pd.Series([True] * len(df), index=df.index)

    if filters.get("manufacturers"):
        mask &= df["manufacturer"].isin(filters["manufacturers"])
    if filters.get("models"):
        mask &= df["model"].isin(filters["models"])
    if filters.get("fuel_types"):
        mask &= df["fuel_type"].isin(filters["fuel_types"])
    if filters.get("vehicle_types"):
        mask &= df["vehicle_type"].isin(filters["vehicle_types"])
    if filters.get("transmissions"):
        mask &= df["transmission"].isin(filters["transmissions"])

    yr = filters.get("year_range")
    if yr:
        mask &= df["vehicle_year"].between(yr[0], yr[1])

    return df[mask].copy()


# ---------------------------------------------------------------------------
# Section header — icon-based
# ---------------------------------------------------------------------------

_SECTION_HEADER_CSS = """
<style>
.ag-section-header {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 3px;
}
.ag-section-icon {
    width: 40px; height: 40px;
    background: linear-gradient(135deg, rgba(126, 179, 255, 0.18), rgba(99, 102, 241, 0.22));
    border: 1px solid rgba(126, 179, 255, 0.25);
    border-radius: 11px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}
.ag-section-title {
    font-size: 1.48rem;
    font-weight: 700;
    color: #c0d8ff;
    margin: 0;
    letter-spacing: -0.01em;
}
.ag-section-sub {
    font-size: 0.83rem;
    color: #718096;
    margin: 2px 0 0 54px;
}
</style>
"""

_section_css_injected = False


def section_header(title: str, subtitle: str = "", icon_name: str = "layout-dashboard") -> None:
    """Render a styled section header with an SVG icon."""
    global _section_css_injected
    if not _section_css_injected:
        st.markdown(_SECTION_HEADER_CSS, unsafe_allow_html=True)
        _section_css_injected = True

    svg = icon(icon_name, "#7EB3FF", 20)
    sub_html = f'<div class="ag-section-sub">{subtitle}</div>' if subtitle else ""

    header_html = (
        f'<div class="ag-section-header">'
        f'<div class="ag-section-icon">{svg}</div>'
        f'<h1 class="ag-section-title">{title}</h1>'
        f'</div>'
        f'{sub_html}'
    )
    st.markdown(header_html, unsafe_allow_html=True)
    st.markdown("<div style='margin-top:6px'></div>", unsafe_allow_html=True)
    st.divider()


# ---------------------------------------------------------------------------
# Download helpers
# ---------------------------------------------------------------------------

def download_csv_button(df: pd.DataFrame, filename: str, label: str = "Download CSV") -> None:
    """Render a CSV download button with a Material icon."""
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=label,
        data=csv,
        file_name=filename,
        mime="text/csv",
        icon=":material/download:",
    )


def download_text_button(content: str, filename: str, label: str = "Download Report") -> None:
    """Render a plain-text download button with a Material icon."""
    st.download_button(
        label=label,
        data=content.encode("utf-8"),
        file_name=filename,
        mime="text/plain",
        icon=":material/download:",
    )


def download_excel_button(df: pd.DataFrame, filename: str, label: str = "Download Excel") -> None:
    """Render an Excel (.xlsx) download button with a Material icon."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Cleaned_Data")
    st.download_button(
        label=label,
        data=buffer.getvalue(),
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        icon=":material/table_view:",
    )


def active_dataset_banner(
    source_name: str,
    raw_count: int,
    cleaned_count: int,
    cleaned_df: pd.DataFrame,
) -> None:
    """Render a top action banner showing current dataset status and download buttons."""
    col1, col2, col3 = st.columns([2.5, 1, 1])
    with col1:
        banner_html = (
            f'<div style="display:flex;align-items:center;gap:12px;padding:9px 14px;background:rgba(126,179,255,0.07);border:1px solid rgba(126,179,255,0.22);border-radius:10px;">'
            f'{icon("database", "#7EB3FF", 20)}'
            f'<div>'
            f'<div style="font-size:0.72rem;color:#8892b0;text-transform:uppercase;font-weight:600;letter-spacing:0.06em;">Active Curated Dataset</div>'
            f'<div style="font-size:0.95rem;color:#e2e8f0;font-weight:600;">{source_name} <span style="font-size:0.8rem;color:#34d399;font-weight:500;margin-left:8px;">({cleaned_count:,} records curated)</span></div>'
            f'</div>'
            f'</div>'
        )
        st.markdown(banner_html, unsafe_allow_html=True)
    with col2:
        download_csv_button(cleaned_df, f"{source_name.lower().replace(' ', '_')}_cleaned.csv", "Export CSV")
    with col3:
        download_excel_button(cleaned_df, f"{source_name.lower().replace(' ', '_')}_cleaned.xlsx", "Export Excel")
    st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)

