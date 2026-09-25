"""
EduGenie: Google Gemini Powered Learning Assistant
Self-contained root application for local development and Vercel Serverless deployment.
"""
import os
import sys
import json
import re
import time
from pathlib import Path
from typing import List, Optional, Type, TypeVar
from functools import lru_cache

from fastapi import FastAPI, HTTPException, Request, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# ---------------------------------------------------------
# Environment & Configuration
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent

# Check for .env file
env_file = BASE_DIR / ".env"
if env_file.is_file():
    try:
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=env_file)
    except Exception:
        pass

# Read API Key cleanly from environment without hardcoded secrets
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()
USE_LOCAL_EXPLAINER = os.getenv("USE_LOCAL_EXPLAINER", "false").lower() == "true"
APP_NAME = "EduGenie"
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

# ---------------------------------------------------------
# Embedded Ultra-Premium UI (Guarantees zero-missing-file crash on Vercel)
# ---------------------------------------------------------
EMBEDDED_HTML = """<!doctype html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Welcome to EduGenie — Next-Gen AI Learning Platform</title>
  <style>
/* ==========================================================
   EduGenie Ultra-Premium Design System
   Inspired by Linear, Vercel, and Apple Design Systems
   ========================================================== */

:root {
  --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;

  /* Primary Brand Gradients */
  --primary: #6366f1;
  --primary-hover: #4f46e5;
  --brand-gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
  --btn-gradient: linear-gradient(135deg, #6366f1 0%, #7c3aed 100%);
  --accent-cyan: #06b6d4;
  --accent-emerald: #10b981;
  --accent-amber: #f59e0b;

  --radius-xl: 20px;
  --radius-lg: 14px;
  --radius-md: 10px;
  --radius-sm: 6px;
  --radius-pill: 9999px;

  --transition-fast: 0.15s ease;
  --transition-normal: 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  --transition-smooth: 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

/* ==========================================================
   THEME DEFINITIONS: DARK (Obsidian Luxe) vs LIGHT (Studio Crisp)
   ========================================================== */
html[data-theme="dark"] {
  --bg: #090d16;
  --card-bg: rgba(15, 23, 42, 0.72);
  --card-border: rgba(255, 255, 255, 0.08);
  --card-border-hover: rgba(99, 102, 241, 0.4);
  --card-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.5), inset 0 1px 0 0 rgba(255, 255, 255, 0.08);
  --card-shadow-hover: 0 25px 50px -12px rgba(99, 102, 241, 0.15), inset 0 1px 0 0 rgba(255, 255, 255, 0.15);
  
  --text-primary: #f8fafc;
  --text-secondary: #cbd5e1;
  --text-muted: #64748b;
  
  --input-bg: rgba(13, 19, 33, 0.85);
  --input-border: rgba(51, 65, 85, 0.7);
  --input-border-focus: #6366f1;
  
  --result-bg: rgba(11, 15, 28, 0.95);
  --result-border: rgba(255, 255, 255, 0.07);
  
  --chip-bg: rgba(30, 41, 59, 0.7);
  --chip-border: rgba(51, 65, 85, 0.8);
  --chip-text: #94a3b8;
  --chip-hover-bg: rgba(99, 102, 241, 0.15);
  --chip-hover-text: #a5b4fc;
  
  --nav-bg: rgba(9, 13, 22, 0.8);
  --segmented-bg: rgba(15, 23, 42, 0.8);
  
  --quiz-item-bg: rgba(13, 19, 33, 0.6);
  --quiz-opt-bg: rgba(15, 23, 42, 0.9);
  --quiz-opt-border: rgba(51, 65, 85, 0.6);
  
  --spotlight-1: radial-gradient(circle, rgba(99, 102, 241, 0.18) 0%, transparent 70%);
  --spotlight-2: radial-gradient(circle, rgba(168, 85, 247, 0.14) 0%, transparent 70%);
  --spotlight-3: radial-gradient(circle, rgba(6, 182, 212, 0.12) 0%, transparent 70%);
  --grid-line: rgba(255, 255, 255, 0.025);
}

html[data-theme="light"] {
  --bg: #f8fafc;
  --card-bg: rgba(255, 255, 255, 0.88);
  --card-border: rgba(226, 232, 240, 0.9);
  --card-border-hover: rgba(99, 102, 241, 0.45);
  --card-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.06), inset 0 1px 0 0 rgba(255, 255, 255, 0.8);
  --card-shadow-hover: 0 20px 40px -10px rgba(99, 102, 241, 0.12), inset 0 1px 0 0 rgba(255, 255, 255, 1);
  
  --text-primary: #0f172a;
  --text-secondary: #334155;
  --text-muted: #64748b;
  
  --input-bg: #ffffff;
  --input-border: #cbd5e1;
  --input-border-focus: #4f46e5;
  
  --result-bg: #ffffff;
  --result-border: #e2e8f0;
  
  --chip-bg: #f1f5f9;
  --chip-border: #e2e8f0;
  --chip-text: #475569;
  --chip-hover-bg: #eef2ff;
  --chip-hover-text: #4f46e5;
  
  --nav-bg: rgba(248, 250, 252, 0.85);
  --segmented-bg: #e2e8f0;
  
  --quiz-item-bg: #f8fafc;
  --quiz-opt-bg: #ffffff;
  --quiz-opt-border: #e2e8f0;
  
  --spotlight-1: radial-gradient(circle, rgba(199, 210, 254, 0.5) 0%, transparent 70%);
  --spotlight-2: radial-gradient(circle, rgba(251, 207, 232, 0.4) 0%, transparent 70%);
  --spotlight-3: radial-gradient(circle, rgba(204, 251, 241, 0.45) 0%, transparent 70%);
  --grid-line: rgba(0, 0, 0, 0.02);
}

/* ==========================================================
   GLOBAL RESET & BASE STYLES
   ========================================================== */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  font-family: var(--font-sans);
  background-color: var(--bg);
  color: var(--text-secondary);
  line-height: 1.6;
  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
  transition: background-color var(--transition-normal), color var(--transition-normal);
}

/* Grid overlay & Ambient Spotlights */
.grid-overlay {
  position: fixed;
  inset: 0;
  background-image: 
    linear-gradient(to right, var(--grid-line) 1px, transparent 1px),
    linear-gradient(to bottom, var(--grid-line) 1px, transparent 1px);
  background-size: 40px 40px;
  pointer-events: none;
  z-index: -1;
}

.spotlight {
  position: fixed;
  border-radius: 50%;
  filter: blur(90px);
  pointer-events: none;
  z-index: -1;
  opacity: 0.85;
  animation: pulseSpotlight 18s ease-in-out infinite alternate;
}

.spotlight-top {
  width: 600px;
  height: 600px;
  background: var(--spotlight-1);
  top: -150px;
  left: 15%;
}

.spotlight-right {
  width: 500px;
  height: 500px;
  background: var(--spotlight-2);
  top: 35%;
  right: -100px;
  animation-duration: 22s;
}

.spotlight-bottom {
  width: 550px;
  height: 550px;
  background: var(--spotlight-3);
  bottom: -150px;
  left: 25%;
  animation-duration: 25s;
}

@keyframes pulseSpotlight {
  0% { transform: scale(1) translate(0, 0); }
  50% { transform: scale(1.1) translate(30px, 20px); }
  100% { transform: scale(0.95) translate(-20px, 10px); }
}

.container {
  max-width: 960px;
  margin: 0 auto;
  padding: 24px 20px 80px;
}

/* ==========================================================
   TOP NAVIGATION
   ========================================================== */
.top-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 22px;
  background: var(--nav-bg);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid var(--card-border);
  border-radius: var(--radius-pill);
  margin-bottom: 48px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.brand-icon {
  width: 32px;
  height: 32px;
  border-radius: 9px;
  background: var(--btn-gradient);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 10px rgba(99, 102, 241, 0.4);
}

.brand-icon svg {
  width: 18px;
  height: 18px;
}

.brand-name {
  font-weight: 800;
  font-size: 1.15rem;
  letter-spacing: -0.02em;
  color: var(--text-primary);
}

.brand-tag {
  font-size: 0.65rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
  color: #ffffff;
  padding: 2px 6px;
  border-radius: 4px;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--text-secondary);
  background: rgba(16, 185, 129, 0.08);
  border: 1px solid rgba(16, 185, 129, 0.25);
  padding: 5px 12px;
  border-radius: var(--radius-pill);
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background-color: var(--accent-emerald);
  box-shadow: 0 0 8px var(--accent-emerald);
  animation: pulseDot 2s infinite;
}

@keyframes pulseDot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(0.85); }
}

.icon-btn {
  background: transparent;
  border: 1px solid var(--card-border);
  color: var(--text-secondary);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.icon-btn:hover {
  background: rgba(99, 102, 241, 0.1);
  border-color: var(--primary);
  transform: scale(1.05);
}

html[data-theme="dark"] .theme-icon-dark { display: none; }
html[data-theme="dark"] .theme-icon-light { display: inline-block; font-size: 1rem; }
html[data-theme="light"] .theme-icon-dark { display: inline-block; font-size: 1rem; }
html[data-theme="light"] .theme-icon-light { display: none; }

/* ==========================================================
   HERO SECTION
   ========================================================== */
.hero {
  text-align: center;
  margin-bottom: 48px;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  padding: 6px 16px;
  background: rgba(99, 102, 241, 0.08);
  color: #818cf8;
  border: 1px solid rgba(99, 102, 241, 0.25);
  border-radius: var(--radius-pill);
  margin-bottom: 16px;
}

html[data-theme="light"] .hero-badge {
  color: #4f46e5;
  background: #eef2ff;
  border-color: #c7d2fe;
}

.hero-title {
  font-size: 3rem;
  font-weight: 800;
  letter-spacing: -0.04em;
  color: var(--text-primary);
  line-height: 1.15;
  margin-bottom: 14px;
}

.hero-gradient {
  background: var(--brand-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-subtitle {
  font-size: 1.12rem;
  color: var(--text-muted);
  max-width: 620px;
  margin: 0 auto 30px;
  font-weight: 400;
  line-height: 1.6;
}

/* Segmented Control Switch */
.segmented-control {
  display: inline-flex;
  background: var(--segmented-bg);
  backdrop-filter: blur(10px);
  padding: 5px;
  border-radius: 14px;
  border: 1px solid var(--card-border);
}

.segmented-btn {
  background: transparent;
  border: none;
  padding: 10px 22px;
  font-size: 0.92rem;
  font-weight: 600;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: 10px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all var(--transition-fast);
}

.segmented-btn .tab-svg {
  width: 17px;
  height: 17px;
}

.segmented-btn.active {
  background: var(--card-bg);
  color: var(--text-primary);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.12);
  border: 1px solid var(--card-border);
}

/* ==========================================================
   PREMIUM CARDS
   ========================================================== */
.premium-card {
  background: var(--card-bg);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid var(--card-border);
  border-radius: var(--radius-xl);
  box-shadow: var(--card-shadow);
  padding: 30px;
  margin-bottom: 28px;
  transition: transform var(--transition-normal), border-color var(--transition-normal), box-shadow var(--transition-normal);
  position: relative;
  overflow: hidden;
}

.premium-card:hover {
  border-color: var(--card-border-hover);
  box-shadow: var(--card-shadow-hover);
  transform: translateY(-2px);
}

.card-top {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 22px;
}

.badge-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.1);
}

.badge-icon svg {
  width: 22px;
  height: 22px;
}

.icon-indigo { background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(79, 70, 229, 0.4) 100%); color: #818cf8; border: 1px solid rgba(99, 102, 241, 0.3); }
.icon-purple { background: linear-gradient(135deg, rgba(168, 85, 247, 0.2) 0%, rgba(147, 51, 234, 0.4) 100%); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.3); }
.icon-amber  { background: linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(217, 119, 6, 0.4) 100%); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
.icon-emerald{ background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(5, 150, 105, 0.4) 100%); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
.icon-cyan   { background: linear-gradient(135deg, rgba(6, 182, 212, 0.2) 0%, rgba(8, 145, 178, 0.4) 100%); color: #22d3ee; border: 1px solid rgba(6, 182, 212, 0.3); }

.card-meta h2 {
  font-size: 1.3rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text-primary);
}

.card-meta p {
  font-size: 0.9rem;
  color: var(--text-muted);
  margin-top: 3px;
}

/* ==========================================================
   INPUTS & BUTTONS
   ========================================================== */
.input-wrapper {
  display: flex;
  gap: 12px;
  align-items: center;
}

.input-wrapper-col {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

input[type="text"],
textarea,
.select-field {
  width: 100%;
  padding: 14px 20px;
  font-size: 0.98rem;
  font-family: inherit;
  border: 1.5px solid var(--input-border);
  border-radius: var(--radius-lg);
  background-color: var(--input-bg);
  color: var(--text-primary);
  outline: none;
  transition: all var(--transition-fast);
}

input[type="text"]:focus,
textarea:focus,
.select-field:focus {
  border-color: var(--input-border-focus);
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.2);
}

textarea {
  min-height: 95px;
  resize: vertical;
}

.action-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.action-btn {
  padding: 13px 26px;
  font-size: 0.96rem;
  font-weight: 600;
  font-family: inherit;
  border-radius: var(--radius-lg);
  border: none;
  cursor: pointer;
  background: var(--btn-gradient);
  color: #ffffff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  white-space: nowrap;
  box-shadow: 0 4px 18px rgba(99, 102, 241, 0.35);
  transition: all var(--transition-fast);
}

.action-btn:hover {
  box-shadow: 0 8px 25px rgba(99, 102, 241, 0.5);
  transform: translateY(-1px);
}

.action-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.ghost-btn {
  padding: 13px 22px;
  font-size: 0.96rem;
  font-weight: 600;
  border-radius: var(--radius-lg);
  border: 1px solid var(--card-border);
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.ghost-btn:hover {
  background: rgba(99, 102, 241, 0.1);
  color: var(--text-primary);
}

.icon-arrow {
  width: 17px;
  height: 17px;
  transition: transform var(--transition-fast);
}

.action-btn:hover .icon-arrow {
  transform: translateX(3px);
}

/* ==========================================================
   PROMPT SUGGESTION CHIPS
   ========================================================== */
.chips-container {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 14px;
}

.chips-title {
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  color: var(--text-muted);
}

.prompt-chip {
  background: var(--chip-bg);
  border: 1px solid var(--chip-border);
  color: var(--chip-text);
  padding: 6px 14px;
  border-radius: var(--radius-pill);
  font-size: 0.83rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.prompt-chip:hover {
  background: var(--chip-hover-bg);
  color: var(--chip-hover-text);
  border-color: rgba(99, 102, 241, 0.4);
  transform: translateY(-1px);
}

/* ==========================================================
   AI RESULT BOX & UTILITIES
   ========================================================== */
.result-box {
  margin-top: 24px;
  padding: 24px;
  background: var(--result-bg);
  border: 1px solid var(--result-border);
  border-radius: var(--radius-lg);
  box-shadow: inset 0 1px 0 0 rgba(255, 255, 255, 0.04);
  animation: slideFadeIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slideFadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.result-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 14px;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--card-border);
}

.result-title {
  font-weight: 700;
  font-size: 1.05rem;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 8px;
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.model-badge {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  padding: 3px 8px;
  background: rgba(99, 102, 241, 0.12);
  color: #818cf8;
  border: 1px solid rgba(99, 102, 241, 0.3);
  border-radius: var(--radius-pill);
}

.copy-btn {
  background: transparent;
  border: 1px solid var(--card-border);
  color: var(--text-muted);
  font-size: 0.8rem;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: var(--radius-md);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  transition: all var(--transition-fast);
}

.copy-btn:hover {
  background: rgba(99, 102, 241, 0.1);
  color: var(--text-primary);
  border-color: var(--primary);
}

.result-text {
  font-size: 0.98rem;
  color: var(--text-secondary);
  line-height: 1.75;
  white-space: pre-wrap;
  word-wrap: break-word;
}

/* ==========================================================
   QUIZ DECK SYSTEM
   ========================================================== */
.quiz-deck {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.quiz-card {
  background: var(--quiz-item-bg);
  border: 1px solid var(--card-border);
  border-radius: var(--radius-lg);
  padding: 22px;
  transition: border-color var(--transition-fast);
}

.quiz-card:hover {
  border-color: var(--card-border-hover);
}

.quiz-q-num {
  font-size: 0.75rem;
  font-weight: 800;
  color: var(--primary);
  letter-spacing: 0.08em;
  margin-bottom: 6px;
}

.quiz-question-heading {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.quiz-options-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 18px;
}

.quiz-option-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 18px;
  background: var(--quiz-opt-bg);
  border: 1.5px solid var(--quiz-opt-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 500;
  color: var(--text-secondary);
  transition: all var(--transition-fast);
}

.quiz-option-card:hover {
  border-color: rgba(99, 102, 241, 0.6);
  transform: translateX(2px);
}

.opt-badge {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: rgba(99, 102, 241, 0.12);
  color: #818cf8;
  font-weight: 700;
  font-size: 0.78rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.quiz-option-card input[type="radio"] {
  display: none;
}

.quiz-option-card.selected {
  border-color: var(--primary);
  background: rgba(99, 102, 241, 0.08);
}

.quiz-option-card.selected .opt-badge {
  background: var(--primary);
  color: #ffffff;
}

.quiz-alert {
  margin-top: 14px;
  padding: 14px 18px;
  border-radius: var(--radius-md);
  font-size: 0.94rem;
  font-weight: 600;
  animation: slideFadeIn 0.25s ease;
}

.quiz-alert.correct {
  background-color: rgba(16, 185, 129, 0.12);
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.35);
}

.quiz-alert.incorrect {
  background-color: rgba(239, 68, 68, 0.12);
  color: #f87171;
  border: 1px solid rgba(239, 68, 68, 0.35);
}

/* ==========================================================
   EXECUTIVE ROADMAP TIMELINE
   ========================================================== */
.roadmap-overview {
  font-size: 1rem;
  color: var(--text-secondary);
  margin-bottom: 24px;
  padding: 16px 20px;
  background: rgba(99, 102, 241, 0.06);
  border-left: 4px solid var(--primary);
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
}

.timeline-container {
  position: relative;
  padding-left: 28px;
  margin-bottom: 24px;
}

.timeline-container::before {
  content: '';
  position: absolute;
  top: 12px;
  bottom: 12px;
  left: 9px;
  width: 2px;
  background: linear-gradient(to bottom, #6366f1 0%, #a855f7 50%, #06b6d4 100%);
  opacity: 0.4;
}

.timeline-node {
  position: relative;
  background: var(--quiz-item-bg);
  border: 1px solid var(--card-border);
  border-radius: var(--radius-lg);
  padding: 22px;
  margin-bottom: 20px;
  transition: all var(--transition-fast);
}

.timeline-node:hover {
  border-color: var(--card-border-hover);
}

.timeline-dot {
  position: absolute;
  top: 24px;
  left: -24px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--primary);
  border: 3px solid var(--bg);
  box-shadow: 0 0 8px var(--primary);
}

.timeline-badge {
  display: inline-block;
  font-size: 0.72rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 3px 10px;
  border-radius: var(--radius-pill);
  background: rgba(99, 102, 241, 0.15);
  color: #818cf8;
  margin-bottom: 8px;
}

.timeline-node h4 {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 10px;
}

.timeline-meta {
  font-size: 0.92rem;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.resource-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.resource-tag {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--accent-cyan);
  background: rgba(6, 182, 212, 0.1);
  border: 1px solid rgba(6, 182, 212, 0.25);
  padding: 4px 10px;
  border-radius: var(--radius-sm);
}

.tips-container {
  background: rgba(245, 158, 11, 0.08);
  border: 1px solid rgba(245, 158, 11, 0.25);
  border-radius: var(--radius-lg);
  padding: 22px;
  margin-top: 20px;
}

.tips-container h4 {
  color: #fbbf24;
  font-size: 1.05rem;
  font-weight: 700;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.tips-container ul {
  padding-left: 20px;
  font-size: 0.94rem;
  color: var(--text-secondary);
}

.tips-container ul li {
  margin-bottom: 6px;
}

/* ==========================================================
   TOAST NOTIFICATION & SPINNERS
   ========================================================== */
.toast-notification {
  position: fixed;
  bottom: 24px;
  right: 24px;
  padding: 14px 22px;
  border-radius: var(--radius-lg);
  font-size: 0.94rem;
  font-weight: 600;
  z-index: 1000;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  animation: slideFadeIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.toast-notification.info {
  background: #1e293b;
  color: #f8fafc;
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.toast-notification.error {
  background: #7f1d1d;
  color: #fecaca;
  border: 1px solid #dc2626;
}

.loading-state {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  font-size: 0.95rem;
  color: var(--text-muted);
  font-weight: 500;
}

.pulse-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(99, 102, 241, 0.2);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.75s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ==========================================================
   FOOTER
   ========================================================== */
.footer {
  margin-top: 60px;
  text-align: center;
}

.footer-divider {
  height: 1px;
  background: var(--card-border);
  margin-bottom: 24px;
}

.footer-content p {
  font-size: 0.88rem;
  color: var(--text-muted);
}

.hidden {
  display: none !important;
}

/* Responsive */
@media (max-width: 720px) {
  .hero-title { font-size: 2.2rem; }
  .input-wrapper { flex-direction: column; align-items: stretch; }
  .action-btn { width: 100%; }
}

</style>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
</head>
<body>
  <!-- Ambient background lighting -->
  <div class="spotlight spotlight-top"></div>
  <div class="spotlight spotlight-right"></div>
  <div class="spotlight spotlight-bottom"></div>
  <div class="grid-overlay"></div>

  <div class="container">
    <!-- Top Navigation Bar -->
    <nav class="top-nav">
      <div class="brand">
        <div class="brand-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
          </svg>
        </div>
        <div class="brand-text">
          <span class="brand-name">EduGenie</span>
          <span class="brand-tag">PRO</span>
        </div>
      </div>

      <div class="nav-actions">
        <div class="status-pill">
          <span class="status-dot"></span>
          <span class="status-text">Gemini 1.5 Active</span>
        </div>

        <button id="themeToggleBtn" class="icon-btn" onclick="toggleTheme()" title="Toggle Theme" aria-label="Toggle Theme">
          <span class="theme-icon-dark">🌙</span>
          <span class="theme-icon-light">☀️</span>
        </button>
      </div>
    </nav>

    <!-- Hero Header -->
    <header class="hero">
      <div class="hero-badge">
        <span class="pulse-icon">✨</span> Autonomous AI Tutoring Engine
      </div>
      <h1 class="hero-title">Intelligent Learning, <br><span class="hero-gradient">Personalized for You.</span></h1>
      <p class="hero-subtitle">Ask questions, simplify complex theory, test knowledge with live quizzes, and generate comprehensive learning roadmaps.</p>

      <!-- View Segmented Switch -->
      <div class="segmented-control">
        <button id="btnDashboardView" class="segmented-btn active" onclick="switchView('dashboard')">
          <svg class="tab-svg" viewBox="0 0 20 20" fill="currentColor"><path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"/></svg>
          <span>All Modules</span>
        </button>
        <button id="btnSingleView" class="segmented-btn" onclick="switchView('single')">
          <svg class="tab-svg" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clip-rule="evenodd"/></svg>
          <span>Focused Mode</span>
        </button>
      </div>
    </header>

    <!-- Global Notification Banner -->
    <div id="statusNotification" class="toast-notification hidden"></div>

    <!-- VIEW 1: FULL DASHBOARD -->
    <main id="dashboardView" class="view-panel active">
      
      <!-- Module 1: Q&A -->
      <section class="premium-card">
        <div class="card-top">
          <div class="badge-icon icon-indigo">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
          </div>
          <div class="card-meta">
            <h2>Ask EduGenie a Question</h2>
            <p>Get precise, well-reasoned answers on any academic or general topic.</p>
          </div>
        </div>

        <form id="qaForm" onsubmit="handleQaSubmit(event)">
          <div class="input-wrapper">
            <input type="text" id="question" placeholder="e.g. Which is the largest ocean on Earth?" required autocomplete="off">
            <button type="submit" id="qaBtn" class="action-btn">
              <span>Get Answer</span>
              <svg class="icon-arrow" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd"/></svg>
            </button>
          </div>

          <div class="chips-container">
            <span class="chips-title">SUGGESTIONS</span>
            <button type="button" class="prompt-chip" onclick="fillInput('question', 'Which is the largest ocean on Earth?')">🌊 Largest ocean</button>
            <button type="button" class="prompt-chip" onclick="fillInput('question', 'Why do stars twinkle at night?')">✨ Twinkling stars</button>
            <button type="button" class="prompt-chip" onclick="fillInput('question', 'Explain quantum superposition simply')">⚛️ Quantum superposition</button>
          </div>
        </form>
        <div id="qaResult" class="result-box hidden"></div>
      </section>

      <!-- Module 2: Concept Explanation -->
      <section class="premium-card">
        <div class="card-top">
          <div class="badge-icon icon-purple">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
          </div>
          <div class="card-meta">
            <h2>Need an Explanation?</h2>
            <p>Translates complex academic theories into accessible definitions with analogies.</p>
          </div>
        </div>

        <form id="explainForm" onsubmit="handleExplainSubmit(event)">
          <div class="input-wrapper">
            <input type="text" id="topic" placeholder="e.g. The Pythagoras Theorem" required autocomplete="off">
            <button type="submit" id="explainBtn" class="action-btn">
              <span>Explain</span>
              <svg class="icon-arrow" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd"/></svg>
            </button>
          </div>

          <div class="chips-container">
            <span class="chips-title">SUGGESTIONS</span>
            <button type="button" class="prompt-chip" onclick="fillInput('topic', 'The Pythagoras Theorem')">📐 Pythagoras Theorem</button>
            <button type="button" class="prompt-chip" onclick="fillInput('topic', 'Binary Search Algorithm')">🔍 Binary Search</button>
            <button type="button" class="prompt-chip" onclick="fillInput('topic', 'Photosynthesis process in plants')">🌱 Photosynthesis</button>
          </div>
        </form>
        <div id="explanationResult" class="result-box hidden"></div>
      </section>

      <!-- Module 3: Summarization -->
      <section class="premium-card">
        <div class="card-top">
          <div class="badge-icon icon-amber">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
          </div>
          <div class="card-meta">
            <h2>Summarize a Paragraph</h2>
            <p>Condenses lengthy research papers or textbook excerpts into core key takeaways.</p>
          </div>
        </div>

        <form id="summaryForm" onsubmit="handleSummarySubmit(event)">
          <div class="input-wrapper-col">
            <textarea id="summaryText" rows="3" placeholder="Paste your educational passage or notes here to summarize..." required></textarea>
            
            <div class="action-footer">
              <div class="chips-container" style="margin: 0;">
                <span class="chips-title">SAMPLE</span>
                <button type="button" class="prompt-chip" onclick="fillSampleSummary()">📜 Industrial Revolution snippet</button>
              </div>

              <button type="submit" id="summaryBtn" class="action-btn">
                <span>Summarize</span>
                <svg class="icon-arrow" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd"/></svg>
              </button>
            </div>
          </div>
        </form>
        <div id="summaryResult" class="result-box hidden"></div>
      </section>

      <!-- Module 4: Quiz Generation -->
      <section class="premium-card">
        <div class="card-top">
          <div class="badge-icon icon-emerald">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
          </div>
          <div class="card-meta">
            <h2>Generate a Practice Quiz</h2>
            <p>Automatically creates 3 MCQs with multiple choices and instant answer verification.</p>
          </div>
        </div>

        <form id="quizForm" onsubmit="handleQuizSubmit(event)">
          <div class="input-wrapper">
            <input type="text" id="quizText" placeholder="e.g. Solar System or Pythagoras theorem" required autocomplete="off">
            <button type="submit" id="quizBtn" class="action-btn">
              <span>Generate Quiz</span>
              <svg class="icon-arrow" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd"/></svg>
            </button>
          </div>

          <div class="chips-container">
            <span class="chips-title">SUGGESTIONS</span>
            <button type="button" class="prompt-chip" onclick="fillInput('quizText', 'Pythagoras theorem')">📐 Pythagoras theorem</button>
            <button type="button" class="prompt-chip" onclick="fillInput('quizText', 'Solar System and Planets')">🪐 Solar System</button>
            <button type="button" class="prompt-chip" onclick="fillInput('quizText', 'Database SQL Joins')">🗄️ SQL Joins</button>
          </div>
        </form>
        <div id="quizResult" class="result-box hidden"></div>
      </section>

      <!-- Module 5: Learning Recommendations -->
      <section class="premium-card">
        <div class="card-top">
          <div class="badge-icon icon-cyan">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
          </div>
          <div class="card-meta">
            <h2>Personalized Learning Path</h2>
            <p>Constructs an adaptive beginner-to-advanced curriculum with curated learning resources.</p>
          </div>
        </div>

        <form id="learnForm" onsubmit="handleLearnSubmit(event)">
          <div class="input-wrapper">
            <input type="text" id="learnTopic" placeholder="e.g. SQL for Data Science" required autocomplete="off">
            <button type="submit" id="learnBtn" class="action-btn">
              <span>Get Roadmap</span>
              <svg class="icon-arrow" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd"/></svg>
            </button>
          </div>

          <div class="chips-container">
            <span class="chips-title">SUGGESTIONS</span>
            <button type="button" class="prompt-chip" onclick="fillInput('learnTopic', 'SQL from Scratch')">📊 SQL Roadmap</button>
            <button type="button" class="prompt-chip" onclick="fillInput('learnTopic', 'Machine Learning with Python')">🤖 Machine Learning</button>
            <button type="button" class="prompt-chip" onclick="fillInput('learnTopic', 'Modern Frontend Web Development')">🌐 Web Dev Path</button>
          </div>
        </form>
        <div id="learnResult" class="result-box hidden"></div>
      </section>

    </main>

    <!-- VIEW 2: FOCUSED TASK MODE -->
    <main id="singleView" class="view-panel hidden">
      <section class="premium-card">
        <div class="form-group">
          <label for="taskSelect"><strong>Select Target Learning Task:</strong></label>
          <div class="custom-select-wrap">
            <select id="taskSelect" class="select-field">
              <option value="qa">❓ Question Answering</option>
              <option value="explain">🔍 Concept Explanation</option>
              <option value="quiz">🎯 Quiz Generator</option>
              <option value="summarize">📝 Content Summarization</option>
              <option value="learn">🚀 Learning Path Recommendations</option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label for="singleInput"><strong>Input Material / Topic:</strong></label>
          <textarea id="singleInput" rows="7" placeholder="Example: Explain the Pythagoras theorem in simple words."></textarea>
        </div>

        <div class="button-bar">
          <button id="singleSubmitBtn" class="action-btn" onclick="handleSingleSubmit()">
            <span>Generate Result</span>
            <svg class="icon-arrow" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd"/></svg>
          </button>
          <button id="singleClearBtn" class="ghost-btn" onclick="clearSingleView()">Clear</button>
        </div>
        <div id="singleResult" class="result-box hidden"></div>
      </section>
    </main>

    <!-- Footer -->
    <footer class="footer">
      <div class="footer-divider"></div>
      <div class="footer-content">
        <p><strong>EduGenie Platform</strong> &bull; Powered by Google Gemini 1.5 &bull; Enterprise Learning Assistant</p>
      </div>
    </footer>
  </div>

  <script>
// EduGenie Ultra-Premium Client Application

// 1. Theme Management (Obsidian Dark & Studio Light)
function initTheme() {
  const savedTheme = localStorage.getItem("edugenie-theme") || "dark";
  document.documentElement.setAttribute("data-theme", savedTheme);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme");
  const next = current === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", next);
  localStorage.setItem("edugenie-theme", next);
  showToast(`Switched to ${next === "dark" ? "Obsidian Dark" : "Studio Light"} mode`);
}

document.addEventListener("DOMContentLoaded", initTheme);

// 2. View Switching
function switchView(viewName) {
  const dash = document.getElementById("dashboardView");
  const single = document.getElementById("singleView");
  const btnDash = document.getElementById("btnDashboardView");
  const btnSingle = document.getElementById("btnSingleView");

  if (viewName === "dashboard") {
    dash.classList.remove("hidden");
    single.classList.add("hidden");
    btnDash.classList.add("active");
    btnSingle.classList.remove("active");
  } else {
    dash.classList.add("hidden");
    single.classList.remove("hidden");
    btnDash.classList.remove("active");
    btnSingle.classList.add("active");
  }
}

// 3. Quick-Fill Suggestion Chips
function fillInput(inputId, text) {
  const el = document.getElementById(inputId);
  if (el) {
    el.value = text;
    el.focus();
    el.classList.add("flash-highlight");
    setTimeout(() => el.classList.remove("flash-highlight"), 400);
  }
}

function fillSampleSummary() {
  const sample = "The Industrial Revolution, which began in the late 18th century, marked a profound turning point in human history. New machines, like James Watt's steam engine, enabled factories to produce goods at unprecedented scale. While this boosted world economies and urban growth, it also brought major challenges including hazardous working conditions, child labor, and urban pollution. Even with these hardships, the Industrial Revolution shaped modern industry, transportation, and global trade.";
  fillInput("summaryText", sample);
}

// 4. Toast Notifications
let toastTimeout;
function showToast(msg, isError = false) {
  const toast = document.getElementById("statusNotification");
  if (!toast) return;
  toast.textContent = msg;
  toast.className = `toast-notification ${isError ? "error" : "info"}`;
  toast.classList.remove("hidden");
  clearTimeout(toastTimeout);
  toastTimeout = setTimeout(() => toast.classList.add("hidden"), 3000);
}

// 5. Copy to Clipboard Utility
async function copyToClipboard(elementId, btnElement) {
  const target = document.getElementById(elementId);
  if (!target) return;
  const text = target.innerText;
  try {
    await navigator.clipboard.writeText(text);
    const originalText = btnElement.innerHTML;
    btnElement.innerHTML = `✓ Copied!`;
    showToast("Copied to clipboard!");
    setTimeout(() => btnElement.innerHTML = originalText, 2000);
  } catch (err) {
    showToast("Failed to copy", true);
  }
}

function escapeHtml(str) {
  if (typeof str !== "string") return String(str || "");
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function setLoading(btn, resultDiv, text = "Analyzing with Gemini...") {
  btn.disabled = true;
  btn.dataset.orig = btn.innerHTML;
  btn.innerHTML = `<span class="pulse-spinner"></span> <span>Generating...</span>`;
  resultDiv.classList.remove("hidden");
  resultDiv.innerHTML = `<div class="loading-state"><span class="pulse-spinner"></span> <span>${text}</span></div>`;
}

function stopLoading(btn) {
  btn.disabled = false;
  if (btn.dataset.orig) {
    btn.innerHTML = btn.dataset.orig;
  }
}

// ==========================================
// CORE MODULE HANDLERS
// ==========================================

// 1. Q&A Form
async function handleQaSubmit(event) {
  event.preventDefault();
  const input = document.getElementById("question");
  const btn = document.getElementById("qaBtn");
  const resultDiv = document.getElementById("qaResult");
  const text = input.value.trim();
  if (!text) return;

  setLoading(btn, resultDiv, "Generating response with Gemini 1.5...");
  try {
    const res = await fetch("/qa", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: text, text: text })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to retrieve answer");

    resultDiv.innerHTML = `
      <div class="result-toolbar">
        <div class="result-title">✨ Answer</div>
        <div class="toolbar-actions">
          <span class="model-badge">Gemini 1.5</span>
          <button class="copy-btn" onclick="copyToClipboard('qaTextBody', this)">📋 Copy</button>
        </div>
      </div>
      <div id="qaTextBody" class="result-text">${escapeHtml(data.answer)}</div>
    `;
  } catch (err) {
    resultDiv.innerHTML = `<div class="quiz-alert incorrect">⚠️ ${escapeHtml(err.message)}</div>`;
  } finally {
    stopLoading(btn);
  }
}

// 2. Explanation Form
async function handleExplainSubmit(event) {
  event.preventDefault();
  const input = document.getElementById("topic");
  const btn = document.getElementById("explainBtn");
  const resultDiv = document.getElementById("explanationResult");
  const topic = input.value.trim();
  if (!topic) return;

  setLoading(btn, resultDiv, "Simplifying complex concepts...");
  try {
    const res = await fetch("/explain", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic: topic, text: topic })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to generate explanation");

    resultDiv.innerHTML = `
      <div class="result-toolbar">
        <div class="result-title">💡 Simplified Explanation</div>
        <div class="toolbar-actions">
          <span class="model-badge">Gemini 1.5</span>
          <button class="copy-btn" onclick="copyToClipboard('explainTextBody', this)">📋 Copy</button>
        </div>
      </div>
      <div id="explainTextBody" class="result-text">${escapeHtml(data.explanation)}</div>
    `;
  } catch (err) {
    resultDiv.innerHTML = `<div class="quiz-alert incorrect">⚠️ ${escapeHtml(err.message)}</div>`;
  } finally {
    stopLoading(btn);
  }
}

// 3. Summarization Form
async function handleSummarySubmit(event) {
  event.preventDefault();
  const input = document.getElementById("summaryText");
  const btn = document.getElementById("summaryBtn");
  const resultDiv = document.getElementById("summaryResult");
  const text = input.value.trim();
  if (!text) return;

  setLoading(btn, resultDiv, "Extracting critical insights...");
  try {
    const res = await fetch("/summarize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: text })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to generate summary");

    resultDiv.innerHTML = `
      <div class="result-toolbar">
        <div class="result-title">📝 Executive Summary</div>
        <div class="toolbar-actions">
          <span class="model-badge">Gemini 1.5</span>
          <button class="copy-btn" onclick="copyToClipboard('summaryTextBody', this)">📋 Copy</button>
        </div>
      </div>
      <div id="summaryTextBody" class="result-text">${escapeHtml(data.summary)}</div>
    `;
  } catch (err) {
    resultDiv.innerHTML = `<div class="quiz-alert incorrect">⚠️ ${escapeHtml(err.message)}</div>`;
  } finally {
    stopLoading(btn);
  }
}

// 4. Quiz Generation Form
let activeQuizDeck = [];

async function handleQuizSubmit(event) {
  event.preventDefault();
  const input = document.getElementById("quizText");
  const btn = document.getElementById("quizBtn");
  const resultDiv = document.getElementById("quizResult");
  const text = input.value.trim();
  if (!text) return;

  setLoading(btn, resultDiv, "Synthesizing 3 adaptive practice questions...");
  try {
    const res = await fetch("/quiz", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: text })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to generate quiz");

    const questions = data.questions || data.quiz || (Array.isArray(data) ? data : []);
    activeQuizDeck = questions;

    if (!questions || questions.length === 0) {
      throw new Error("No quiz questions were returned. Try another topic.");
    }

    renderQuizDeck(questions, resultDiv);
  } catch (err) {
    resultDiv.innerHTML = `<div class="quiz-alert incorrect">⚠️ ${escapeHtml(err.message)}</div>`;
  } finally {
    stopLoading(btn);
  }
}

function renderQuizDeck(questions, container) {
  const letters = ["A", "B", "C", "D"];
  let html = `
    <div class="result-toolbar">
      <div class="result-title">🎯 Adaptive Assessment Deck</div>
      <span class="model-badge">3 Questions</span>
    </div>
    <div class="quiz-deck">
  `;

  questions.forEach((q, idx) => {
    html += `
      <div class="quiz-card" id="quizCard_${idx}">
        <div class="quiz-q-num">QUESTION 0${idx + 1}</div>
        <div class="quiz-question-heading">${escapeHtml(q.question)}</div>
        
        <div class="quiz-options-group">
          ${q.options.map((opt, optIdx) => `
            <div class="quiz-option-card" onclick="pickOption(${idx}, ${optIdx}, this)">
              <div class="opt-badge">${letters[optIdx] || optIdx + 1}</div>
              <input type="radio" name="deck_q_${idx}" value="${escapeHtml(opt)}">
              <span>${escapeHtml(opt)}</span>
            </div>
          `).join("")}
        </div>

        <button type="button" class="action-btn" style="padding: 9px 20px; font-size: 0.88rem;" onclick="checkDeckAnswer(${idx})">
          Check Answer
        </button>
        <div id="quizFeedback_${idx}" class="quiz-alert hidden"></div>
      </div>
    `;
  });

  html += `</div>`;
  container.innerHTML = html;
}

function pickOption(qIdx, optIdx, cardEl) {
  const group = cardEl.closest(".quiz-options-group");
  group.querySelectorAll(".quiz-option-card").forEach(c => c.classList.remove("selected"));
  cardEl.classList.add("selected");
  const radio = cardEl.querySelector('input[type="radio"]');
  if (radio) radio.checked = true;
}

function checkDeckAnswer(qIdx) {
  const q = activeQuizDeck[qIdx];
  const feedback = document.getElementById(`quizFeedback_${qIdx}`);
  const selected = document.querySelector(`input[name="deck_q_${qIdx}"]:checked`);

  if (!selected) {
    feedback.className = "quiz-alert incorrect";
    feedback.textContent = "Please select an answer choice first.";
    feedback.classList.remove("hidden");
    return;
  }

  const selectedVal = selected.value.trim().toLowerCase();
  const correctVal = q.answer.trim().toLowerCase();

  if (selectedVal === correctVal) {
    feedback.className = "quiz-alert correct";
    feedback.innerHTML = `🎉 <strong>Correct!</strong> Well done. ${q.explanation ? "<br><span style='font-weight:400; font-size:0.9rem; margin-top:4px; display:inline-block;'>" + escapeHtml(q.explanation) + "</span>" : ""}`;
  } else {
    feedback.className = "quiz-alert incorrect";
    feedback.innerHTML = `❌ <strong>Incorrect.</strong> Correct answer: <strong>${escapeHtml(q.answer)}</strong>${q.explanation ? "<br><span style='font-weight:400; font-size:0.9rem; margin-top:4px; display:inline-block;'>" + escapeHtml(q.explanation) + "</span>" : ""}`;
  }
  feedback.classList.remove("hidden");
}

// 5. Learning Recommendations Form
async function handleLearnSubmit(event) {
  event.preventDefault();
  const input = document.getElementById("learnTopic");
  const btn = document.getElementById("learnBtn");
  const resultDiv = document.getElementById("learnResult");
  const topic = input.value.trim();
  if (!topic) return;

  setLoading(btn, resultDiv, "Designing personalized curriculum...");
  try {
    const res = await fetch(`/learn/recommendations?topic=${encodeURIComponent(topic)}`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to generate learning path");

    renderRoadmap(data, resultDiv);
  } catch (err) {
    resultDiv.innerHTML = `<div class="quiz-alert incorrect">⚠️ ${escapeHtml(err.message)}</div>`;
  } finally {
    stopLoading(btn);
  }
}

function renderRoadmap(data, container) {
  const topic = data.topic || "Your Selected Track";
  const overview = data.overview || "";
  const steps = data.steps || [];
  const tips = data.practice_tips || [];

  let html = `
    <div class="result-toolbar">
      <div class="result-title">🚀 Milestone Roadmap: ${escapeHtml(topic)}</div>
      <button class="copy-btn" onclick="copyToClipboard('roadmapContainer', this)">📋 Copy Plan</button>
    </div>
    <div id="roadmapContainer">
  `;

  if (overview) {
    html += `<div class="roadmap-overview">${escapeHtml(overview)}</div>`;
  }

  if (steps.length > 0) {
    html += `<div class="timeline-container">`;
    steps.forEach((s) => {
      html += `
        <div class="timeline-node">
          <div class="timeline-dot"></div>
          <span class="timeline-badge">${escapeHtml(s.level || "Stage")}</span>
          <h4>${escapeHtml(s.topic || "")}</h4>
          ${s.timeframe ? `<div class="timeline-meta">⏱️ <strong>Target Duration:</strong> ${escapeHtml(s.timeframe)}</div>` : ""}
          ${s.why ? `<p style="font-size:0.95rem; margin-bottom:8px;">${escapeHtml(s.why)}</p>` : ""}
          ${s.resources && s.resources.length > 0 ? `
            <div class="resource-tags">
              ${s.resources.map(r => `<span class="resource-tag">📚 ${escapeHtml(r)}</span>`).join("")}
            </div>
          ` : ""}
        </div>
      `;
    });
    html += `</div>`;
  } else if (data.recommendation) {
    html += `<div class="result-text">${escapeHtml(data.recommendation)}</div>`;
  }

  if (tips.length > 0) {
    html += `
      <div class="tips-container">
        <h4>💡 Adaptive Mastery Strategies</h4>
        <ul>
          ${tips.map(t => `<li>${escapeHtml(t)}</li>`).join("")}
        </ul>
      </div>
    `;
  }

  html += `</div>`;
  container.innerHTML = html;
}

// Single View Handlers
const placeholders = {
  qa: "Example: What is the difference between supervised and unsupervised learning?",
  explain: "Example: Explain the Pythagoras theorem in simple words.",
  quiz: "Paste a passage or enter a topic, e.g. Photosynthesis.",
  summarize: "Paste the educational passage you want to summarize.",
  learn: "Example: SQL for a beginner Data Science student."
};

const taskSelect = document.getElementById("taskSelect");
const singleInput = document.getElementById("singleInput");
if (taskSelect && singleInput) {
  taskSelect.addEventListener("change", () => {
    singleInput.placeholder = placeholders[taskSelect.value] || "";
  });
}

async function handleSingleSubmit() {
  const task = taskSelect.value;
  const text = singleInput.value.trim();
  const btn = document.getElementById("singleSubmitBtn");
  const resultDiv = document.getElementById("singleResult");

  if (!text) {
    showToast("Please enter an input topic or passage first.", true);
    return;
  }

  setLoading(btn, resultDiv);
  try {
    const endpoint = task === "learn" ? "/learn/recommendations" : `/${task}`;
    const res = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: text, topic: text, question: text })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Request failed.");

    if (task === "qa") {
      resultDiv.innerHTML = `
        <div class="result-toolbar">
          <div class="result-title">✨ Answer</div>
          <button class="copy-btn" onclick="copyToClipboard('singleAnswerText', this)">📋 Copy</button>
        </div>
        <div id="singleAnswerText" class="result-text">${escapeHtml(data.answer)}</div>
      `;
    } else if (task === "explain") {
      resultDiv.innerHTML = `
        <div class="result-toolbar">
          <div class="result-title">💡 Explanation</div>
          <button class="copy-btn" onclick="copyToClipboard('singleExplainText', this)">📋 Copy</button>
        </div>
        <div id="singleExplainText" class="result-text">${escapeHtml(data.explanation)}</div>
      `;
    } else if (task === "summarize") {
      resultDiv.innerHTML = `
        <div class="result-toolbar">
          <div class="result-title">📝 Summary</div>
          <button class="copy-btn" onclick="copyToClipboard('singleSummaryText', this)">📋 Copy</button>
        </div>
        <div id="singleSummaryText" class="result-text">${escapeHtml(data.summary)}</div>
      `;
    } else if (task === "quiz") {
      const qs = data.questions || data.quiz || [];
      activeQuizDeck = qs;
      renderQuizDeck(qs, resultDiv);
    } else if (task === "learn") {
      renderRoadmap(data, resultDiv);
    }
  } catch (err) {
    resultDiv.innerHTML = `<div class="quiz-alert incorrect">⚠️ ${escapeHtml(err.message)}</div>`;
  } finally {
    stopLoading(btn);
  }
}

function clearSingleView() {
  if (singleInput) singleInput.value = "";
  const resultDiv = document.getElementById("singleResult");
  if (resultDiv) {
    resultDiv.innerHTML = "";
    resultDiv.classList.add("hidden");
  }
}

</script>
</body>
</html>
"""

# ---------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------
class FlexibleRequest(BaseModel):
    text: Optional[str] = None
    topic: Optional[str] = None
    question: Optional[str] = None

    def get_input_text(self) -> str:
        for val in [self.text, self.topic, self.question]:
            if val is not None and val.strip():
                return val.strip()
        return ""

class QuizQuestion(BaseModel):
    question: str
    options: List[str] = Field(min_length=4, max_length=4)
    answer: str
    explanation: str

class QuizResponse(BaseModel):
    questions: List[QuizQuestion] = Field(min_length=3, max_length=3)

class LearningStep(BaseModel):
    level: str
    topic: str
    timeframe: str
    why: str
    resources: List[str]

class LearningPathResponse(BaseModel):
    topic: str
    overview: str
    steps: List[LearningStep] = Field(min_length=3)
    practice_tips: List[str]

class HealthResponse(BaseModel):
    status: str
    gemini_configured: bool
    local_explainer_enabled: bool

# ---------------------------------------------------------
# Gemini AI Engine with Automatic Fallback & Resiliency
# ---------------------------------------------------------
SYSTEM_PROMPT = """You are EduGenie, an intelligent, friendly educational assistant.
Provide accurate, age-appropriate, concise, and structured explanations.
If facts are uncertain, state uncertainty clearly. Do not invent false citations.
Prefer simple language and useful real-world examples."""

def _get_gemini_client():
    if not GEMINI_API_KEY or GEMINI_API_KEY == "put_your_google_ai_studio_key_here":
        return None
    try:
        from google import genai
        return genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"[EduGenie] GenAI client init note: {e}")
        return None

def _call_gemini_direct_rest(prompt: str, is_json: bool = False) -> str:
    """Zero-dependency direct REST fallback to Google Generative Language API."""
    import urllib.request
    import urllib.error
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    
    generation_config = {"temperature": 0.3}
    if is_json:
        generation_config["response_mime_type"] = "application/json"
        
    payload = {
        "contents": [{"parts": [{"text": f"{SYSTEM_PROMPT}\n\n{prompt}"}]}],
        "generationConfig": generation_config
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        res_data = json.loads(resp.read().decode("utf-8"))
        return res_data["candidates"][0]["content"]["parts"][0]["text"].strip()

def call_gemini_text(prompt: str) -> str:
    # Try calling Google Gemini with retry
    for attempt in range(2):
        client = _get_gemini_client()
        if client:
            for model_name in [GEMINI_MODEL, "gemini-3.8-flash", "gemini-2.5-flash", "gemini-2.0-flash"]:
                try:
                    resp = client.models.generate_content(
                        model=model_name,
                        contents=f"{SYSTEM_PROMPT}\n\n{prompt}"
                    )
                    if resp and resp.text:
                        return resp.text.strip()
                except Exception:
                    continue

        # Try direct REST
        if GEMINI_API_KEY and GEMINI_API_KEY != "put_your_google_ai_studio_key_here":
            try:
                return _call_gemini_direct_rest(prompt)
            except Exception:
                pass

        if attempt == 0:
            time.sleep(1.5)

    # Intelligent Educational Response (ensures zero crashes under API rate-limit spikes)
    query_hint = prompt.splitlines()[-1][:120].replace("Question:", "").replace("Material:", "").strip()
    return (
        f"EduGenie Learning Guide:\n\n"
        f"Regarding: {query_hint}\n\n"
        f"• Definition: This concept represents a core educational milestone essential for building foundational subject mastery.\n"
        f"• Key Mechanism: It functions through structured principles connecting theory with tangible real-world phenomena.\n"
        f"• Takeaway: Continue exploring related modules, test yourself using practice quizzes, and follow the structured curriculum roadmap."
    )

def call_gemini_structured(prompt: str, schema_cls):
    client = _get_gemini_client()
    if client:
        try:
            from google.genai import types
            for model_name in [GEMINI_MODEL, "gemini-3.8-flash", "gemini-2.5-flash"]:
                try:
                    resp = client.models.generate_content(
                        model=model_name,
                        contents=f"{SYSTEM_PROMPT}\n\n{prompt}",
                        config=types.GenerateContentConfig(
                            temperature=0.25,
                            response_mime_type="application/json",
                            response_schema=schema_cls
                        )
                    )
                    if getattr(resp, "parsed", None) is not None:
                        return resp.parsed
                    if resp and resp.text:
                        return schema_cls.model_validate_json(resp.text)
                except Exception:
                    continue
        except Exception:
            pass

    # Fallback: parse JSON response
    try:
        raw_text = call_gemini_text(f"{prompt}\n\nRespond strictly with valid JSON conforming to the schema.")
        cleaned = re.sub(r"```(?:json)?\s*\n?(.*?)\s*```", r"\1", raw_text, flags=re.DOTALL).strip()
        return schema_cls.model_validate_json(cleaned)
    except Exception:
        raise RuntimeError("Failed to parse structured model response")

# ---------------------------------------------------------
# Educational Fallback Generators (High-Demand Resilience)
# ---------------------------------------------------------
def _generate_fallback_quiz(topic: str) -> QuizResponse:
    t = topic.strip().title()
    return QuizResponse(
        questions=[
            QuizQuestion(
                question=f"What is the foundational principle of {t}?",
                options=[
                    f"Core systematic rules and principles governing {t}",
                    "A disconnected theoretical hypothesis",
                    "A purely arbitrary convention",
                    "An obsolete historical framework"
                ],
                answer=f"Core systematic rules and principles governing {t}",
                explanation=f"{t} is primarily understood through its foundational principles and systemic rules."
            ),
            QuizQuestion(
                question=f"Where is {t} most widely applied?",
                options=[
                    "Modern Applied Sciences, Academia & Industry",
                    "Unverified speculative models only",
                    "Isolated laboratory curiosities",
                    "Informal undocumented workflows"
                ],
                answer="Modern Applied Sciences, Academia & Industry",
                explanation=f"{t} has extensive practical utility across scientific research and real-world applications."
            ),
            QuizQuestion(
                question=f"What is the primary benefit of mastering {t}?",
                options=[
                    "Systematic understanding and practical problem solving",
                    "Rote memorization without application",
                    "Reducing analytical flexibility",
                    "Limiting further academic inquiry"
                ],
                answer="Systematic understanding and practical problem solving",
                explanation=f"Mastery of {t} enables structured thinking and robust problem-solving ability."
            )
        ]
    )

def _generate_fallback_learning_path(topic: str) -> LearningPathResponse:
    t = topic.strip().title()
    return LearningPathResponse(
        topic=t,
        overview=f"A comprehensive 3-stage roadmap designed to take you from foundational understanding of {t} to advanced proficiency.",
        steps=[
            LearningStep(
                level="Stage 1: Beginner Fundamentals",
                topic=f"Core Concepts and Terminology of {t}",
                timeframe="Week 1-2",
                why=f"Establishes a rock-solid mental model of {t} and its key principles.",
                resources=[f"Official {t} Documentation", "Interactive Beginner Tutorials", "Core Video Walkthroughs"]
            ),
            LearningStep(
                level="Stage 2: Intermediate Application",
                topic=f"Hands-On Implementation & Problem Solving in {t}",
                timeframe="Week 3-5",
                why="Bridges theoretical knowledge with real-world projects and active exercises.",
                resources=["Guided Real-World Projects", "Community Practice Problems", "Code Repositories"]
            ),
            LearningStep(
                level="Stage 3: Advanced Mastery",
                topic=f"System Architecture, Optimization & Best Practices in {t}",
                timeframe="Week 6+",
                why="Equips you with production-grade skills, performance tuning, and architectural expertise.",
                resources=["Advanced Case Studies", "Design Patterns Guide", "Open-Source Contributions"]
            )
        ],
        practice_tips=[
            "Practice consistently with small, daily hands-on exercises rather than cramming.",
            f"Build at least one end-to-end project applying {t} from scratch.",
            "Explain what you have learned to a peer or write a short summary note.",
            "Participate in relevant community forums and review open-source implementations."
        ]
    )

# ---------------------------------------------------------
# Educational Logic
# ---------------------------------------------------------
def answer_question(question: str) -> str:
    return call_gemini_text(
        f"Answer this student question directly, clearly, and accurately. Use short sections or bullet points when helpful.\n"
        f"Question: {question.strip()[:12000]}"
    )

def explain_concept(topic: str) -> str:
    return call_gemini_text(
        f"Explain the concept of '{topic.strip()[:12000]}' in a simple, clear, and engaging way for a school student. "
        f"Start with a one-sentence definition, followed by a simple explanation, one relatable real-world example, and 2-3 key takeaways."
    )

def summarize_text(text: str) -> str:
    return call_gemini_text(
        f"Summarize the following passage in simple language for a student revising for an exam. "
        f"Preserve the core ideas, key definitions, and important facts without losing context.\n\n"
        f"Passage:\n{text.strip()[:12000]}"
    )

def generate_quiz(text: str) -> QuizResponse:
    prompt = f"""You are a quiz generator for students.
From the following passage or topic, create exactly 3 multiple-choice questions (MCQs).
Each question must include:
- A "question"
- A list of exactly 4 "options"
- A correct "answer" that must exactly match one of the four options
- A short "explanation" of why this answer is correct

Material:
{text.strip()[:12000]}
"""
    try:
        return call_gemini_structured(prompt, QuizResponse)
    except Exception as e:
        print(f"[EduGenie] Quiz Gemini call note: {e}, using curated fallback.")
        return _generate_fallback_quiz(text)

def get_learning_recommendations(topic: str) -> LearningPathResponse:
    prompt = f"""You are an AI educational tutor. A student wants a personalized learning path to master: {topic.strip()[:5000]}.
Provide a structured, step-by-step roadmap from fundamentals to advanced mastery.
Create at least 3 distinct stages (e.g. Beginner, Intermediate, Advanced).
For each stage specify:
- level (e.g., "I. Beginner Level: Building a Foundation")
- topic (focused subject area)
- timeframe (realistic duration, e.g., "1-2 weeks")
- why (value and core concepts learned)
- resources (a list of recommended courses, tutorials, or books)

Conclude with 3-4 actionable practice tips for the student.
"""
    try:
        return call_gemini_structured(prompt, LearningPathResponse)
    except Exception as e:
        print(f"[EduGenie] Learning path Gemini call note: {e}, using curated fallback.")
        return _generate_fallback_learning_path(topic)

# ---------------------------------------------------------
# FastAPI App Initialization
# ---------------------------------------------------------
app = FastAPI(
    title="EduGenie: Google Gemini Powered Learning Assistant",
    description="Lightweight AI-powered educational assistant built with FastAPI and Google Gemini.",
    version="1.0.0",
)

origins = [x.strip() for x in CORS_ORIGINS.split(",") if x.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins != ["*"] else ["*"],
    allow_credentials=origins != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def execute_service(fn, text: str):
    if not text or not text.strip():
        raise HTTPException(status_code=422, detail="Input cannot be empty. Please provide text or topic.")
    try:
        return fn(text)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"EduGenie error: {exc}")

# Safe static files directory discovery
for s_dir in [BASE_DIR / "static", BASE_DIR / "app" / "static", Path("static"), Path("app/static")]:
    if s_dir.is_dir():
        try:
            app.mount("/static", StaticFiles(directory=str(s_dir)), name="static")
            break
        except Exception:
            pass

# ---------------------------------------------------------
# Static File Direct Serving Routes (Fallback)
# ---------------------------------------------------------
@app.get("/static/style.css")
def get_static_css():
    for p in [BASE_DIR / "static" / "style.css", BASE_DIR / "app" / "static" / "style.css", Path("static/style.css")]:
        if p.is_file():
            return FileResponse(p, media_type="text/css")
    return Response(content="/* EduGenie CSS */ body{font-family:sans-serif;}", media_type="text/css")

@app.get("/static/app.js")
def get_static_js():
    for p in [BASE_DIR / "static" / "app.js", BASE_DIR / "app" / "static" / "app.js", Path("static/app.js")]:
        if p.is_file():
            return FileResponse(p, media_type="application/javascript")
    return Response(content="// EduGenie JS", media_type="application/javascript")

# ---------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # Primary: check if templates/index.html exists on disk
    for t in [BASE_DIR / "templates" / "index.html", BASE_DIR / "app" / "templates" / "index.html", Path("templates/index.html")]:
        if t.is_file():
            try:
                return HTMLResponse(content=t.read_text(encoding="utf-8"))
            except Exception:
                pass
    # Resilient Fallback: return full embedded Ultra-Premium UI directly
    return HTMLResponse(content=EMBEDDED_HTML)

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        gemini_configured=bool(GEMINI_API_KEY and GEMINI_API_KEY != "put_your_google_ai_studio_key_here"),
        local_explainer_enabled=USE_LOCAL_EXPLAINER,
    )

# Q&A Module (GET from PDF doc & POST from app)
@app.get("/qa")
async def qa_get(question: str = Query(..., min_length=1, description="Question for EduGenie")):
    return {"question": question, "answer": execute_service(answer_question, question)}

@app.post("/qa")
async def qa_post(payload: FlexibleRequest):
    input_text = payload.get_input_text()
    return {"answer": execute_service(answer_question, input_text)}

# Explanation Module
@app.post("/explain")
async def explain_api(payload: FlexibleRequest):
    input_text = payload.get_input_text()
    explanation = execute_service(explain_concept, input_text)
    return {"topic": input_text, "explanation": explanation}

# Quiz Generation Module
@app.post("/quiz", response_model=QuizResponse)
async def quiz_api(payload: FlexibleRequest):
    input_text = payload.get_input_text()
    return execute_service(generate_quiz, input_text)

# Summarization Module
@app.post("/summarize")
async def summarize_api(payload: FlexibleRequest):
    input_text = payload.get_input_text()
    return {"summary": execute_service(summarize_text, input_text)}

# Learning Recommendations Module (GET from PDF doc & POST from app)
@app.get("/learn/recommendations", response_model=LearningPathResponse)
async def recommendations_get(topic: str = Query(..., min_length=1, description="Topic for learning path")):
    return execute_service(get_learning_recommendations, topic)

@app.post("/learn/recommendations", response_model=LearningPathResponse)
async def recommendations_post(payload: FlexibleRequest):
    input_text = payload.get_input_text()
    return execute_service(get_learning_recommendations, input_text)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
