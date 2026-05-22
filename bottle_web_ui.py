#!/usr/bin/env python3
"""
Vector Battleship - Single-File Web UI
A lightweight Bottle-based web interface for the Vector Battleship game.
All HTML, CSS, and JavaScript are embedded in this single file.
"""

from bottle import Bottle, request, response, abort, HTTPResponse
import json
import os
import uuid
from uuid import UUID
from datetime import datetime
from private_stuff import vector_search, destroy_ship, get_max_quadrants, _s
from connect_to_datastore import connect_to_datastore
from vector_battleship_create import make_ship_shape_from_anchorXY

# Initialize Bottle app
app = Bottle()

# Global error handler to return JSON errors instead of HTML
@app.error(404)
def error404(error):
    response.content_type = 'application/json'
    return json.dumps({'error': 'Not found', 'detail': str(error)})

@app.error(500)
def error500(error):
    response.content_type = 'application/json'
    return json.dumps({'error': 'Internal server error', 'detail': str(error)})


# ============================================================================
# EMBEDDED HTML TEMPLATE
# ============================================================================

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vector Battleship</title>
    <style>
/* Vector Battleship Web UI Styles */

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Courier New', monospace;
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    color: #e0e0e0;
    min-height: 100vh;
    padding: 20px;
}

.container {
    max-width: 1400px;
    margin: 0 auto;
}

/* Header */
.game-header {
    background: rgba(15, 52, 96, 0.8);
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border: 2px solid #533483;
}

.game-header h1 {
    font-size: 2em;
    color: #ff6b6b;
    text-shadow: 0 0 10px rgba(255, 107, 107, 0.5);
}

.session-info {
    display: flex;
    gap: 20px;
    font-size: 1.1em;
}

.session-info span {
    background: rgba(83, 52, 131, 0.5);
    padding: 5px 15px;
    border-radius: 5px;
}

/* Main Layout */
.game-layout {
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
}

.left-panel {
    flex: 2;
    min-width: 500px;
}

.right-panel {
    flex: 1;
    min-width: 350px;
    background: rgba(15, 52, 96, 0.6);
    padding: 20px;
    border-radius: 10px;
    border: 2px solid #533483;
}

/* Grid Section */
.grid-section {
    background: rgba(15, 52, 96, 0.6);
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
    border: 2px solid #533483;
}

.grid-section h2 {
    color: #ff6b6b;
    margin-bottom: 15px;
}

.quadrant-selector {
    margin-bottom: 15px;
}

.quadrant-selector label {
    margin-right: 10px;
    font-weight: bold;
}

.quadrant-selector select {
    background: #1a1a2e;
    color: #e0e0e0;
    border: 2px solid #533483;
    padding: 8px 15px;
    border-radius: 5px;
    font-size: 1em;
    cursor: pointer;
}

.quadrant-selector select:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    background: #0d1117;
}

.quadrant-selector input[type="number"] {
    background: #1a1a2e;
    color: #e0e0e0;
    border: 2px solid #533483;
    padding: 8px 15px;
    border-radius: 5px;
    font-size: 1em;
    cursor: pointer;
    width: 100px;
}

.quadrant-selector input[type="number"]:focus {
    outline: none;
    border-color: #ff6b6b;
    box-shadow: 0 0 5px rgba(255, 107, 107, 0.5);
}

.start-game-button {
    margin-left: 15px;
    padding: 8px 20px;
    font-size: 1em;
    font-weight: bold;
    background: linear-gradient(135deg, #533483 0%, #0f3460 100%);
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    transition: all 0.3s;
    box-shadow: 0 2px 4px rgba(83, 52, 131, 0.4);
}

.start-game-button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(83, 52, 131, 0.6);
}

.start-game-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    background: #555;
}

.canvas-container {
    display: flex;
    justify-content: center;
    margin: 20px 0;
}

#grid {
    border: 3px solid #ff6b6b;
    border-radius: 5px;
    cursor: crosshair;
    background: #0f3460;
}

.coordinates-display {
    text-align: center;
    font-size: 1.1em;
    color: #ff6b6b;
}

/* Controls Section */
.controls-section {
    background: rgba(15, 52, 96, 0.6);
    padding: 20px;
    border-radius: 10px;
    border: 2px solid #533483;
}

.ship-type-selector h3 {
    color: #ff6b6b;
    margin-bottom: 10px;
}

.radio-group {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
    margin-bottom: 20px;
}

.radio-group label {
    background: rgba(83, 52, 131, 0.3);
    padding: 10px;
    border-radius: 5px;
    cursor: pointer;
    transition: background 0.3s;
    display: flex;
    align-items: center;
    gap: 8px;
}

.radio-group label:hover {
    background: rgba(83, 52, 131, 0.6);
}

.radio-group input[type="radio"] {
    cursor: pointer;
}

.coordinate-controls {
    margin-bottom: 20px;
}

.slider-control {
    margin-bottom: 15px;
}

.slider-control label {
    display: block;
    margin-bottom: 5px;
    color: #e0e0e0;
}

.slider-control span {
    color: #ff6b6b;
    font-weight: bold;
}

.slider-control input[type="range"] {
    width: 100%;
    height: 8px;
    background: #533483;
    border-radius: 5px;
    outline: none;
}

.slider-control input[type="range"]::-webkit-slider-thumb {
    appearance: none;
    width: 20px;
    height: 20px;
    background: #ff6b6b;
    border-radius: 50%;
    cursor: pointer;
}

.slider-control input[type="range"]::-moz-range-thumb {
    width: 20px;
    height: 20px;
    background: #ff6b6b;
    border-radius: 50%;
    cursor: pointer;
    border: none;
}

/* Fire Button */
.fire-button,
.new-game-button {
    width: 100%;
    padding: 15px;
    font-size: 1.3em;
    font-weight: bold;
    background: linear-gradient(135deg, #e94560 0%, #ff6b6b 100%);
    color: white;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.3s;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    box-shadow: 0 4px 8px rgba(233, 69, 96, 0.4);
}

.fire-button:hover,
.new-game-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(233, 69, 96, 0.6);
}

.fire-button:active,
.new-game-button:active {
    transform: translateY(0);
}

.fire-button:disabled {
    background: #555;
    cursor: not-allowed;
    opacity: 0.5;
}

.new-game-button {
    margin-top: 10px;
    background: linear-gradient(135deg, #533483 0%, #0f3460 100%);
}

/* History Panel */
.right-panel h2 {
    color: #ff6b6b;
    margin-bottom: 15px;
}

.history-container {
    max-height: 600px;
    overflow-y: auto;
}

.no-attempts {
    text-align: center;
    color: #888;
    padding: 20px;
    font-style: italic;
}

.history-item {
    background: rgba(83, 52, 131, 0.3);
    padding: 15px;
    margin-bottom: 10px;
    border-radius: 5px;
    border-left: 5px solid;
    transition: transform 0.3s;
}

.history-item:hover {
    transform: translateX(5px);
}

.history-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
    font-weight: bold;
}

.history-details {
    font-size: 0.9em;
    color: #ccc;
    margin-bottom: 8px;
}

.match-bar-container {
    background: rgba(0, 0, 0, 0.3);
    height: 20px;
    border-radius: 3px;
    overflow: hidden;
    margin-bottom: 5px;
}

.match-bar {
    height: 100%;
    transition: width 0.5s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.8em;
    font-weight: bold;
}

.trend-indicator {
    font-size: 1.2em;
    font-weight: bold;
}

/* Color Scheme for Heat Feedback */
.cold-0 { background-color: #16213e; border-left-color: #16213e; }
.cold-1 { background-color: #0f3460; border-left-color: #0f3460; }
.cool { background-color: #533483; border-left-color: #533483; }
.warm { background-color: #e94560; border-left-color: #e94560; }
.hot { background-color: #ff6b6b; border-left-color: #ff6b6b; }
.very-hot { background-color: #ff4500; border-left-color: #ff4500; }
.burning { background-color: #ff0000; border-left-color: #ff0000; }
.perfect { background-color: #ffd700; border-left-color: #ffd700; color: #000; }

/* Game Messages */
.game-message {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: rgba(0, 0, 0, 0.95);
    padding: 40px;
    border-radius: 15px;
    border: 3px solid #ffd700;
    text-align: center;
    z-index: 1000;
    box-shadow: 0 0 30px rgba(255, 215, 0, 0.5);
}

.game-message h2 {
    font-size: 2.5em;
    margin-bottom: 20px;
    color: #ffd700;
    text-shadow: 0 0 10px rgba(255, 215, 0, 0.8);
}

.game-message p {
    font-size: 1.2em;
    color: #e0e0e0;
}

/* Scrollbar Styling */
.history-container::-webkit-scrollbar {
    width: 8px;
}

.history-container::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.3);
    border-radius: 4px;
}

.history-container::-webkit-scrollbar-thumb {
    background: #533483;
    border-radius: 4px;
}

.history-container::-webkit-scrollbar-thumb:hover {
    background: #e94560;
}

/* Responsive Design */
@media (max-width: 900px) {
    .game-layout {
        flex-direction: column;
    }

    .left-panel,
    .right-panel {
        min-width: 100%;
    }

    .radio-group {
        grid-template-columns: 1fr;
    }

    #grid {
        width: 100%;
        max-width: 400px;
    }
}
    </style>
</head>
<body>
    <div class="container">
        <header class="game-header">
            <h1>VECTOR BATTLESHIP</h1>
            <div class="session-info">
                <span id="session-id">Session: --</span>
                <span id="attempts-counter">Attempts: 0/20</span>
            </div>
        </header>

        <div class="game-layout">
            <!-- Left Panel: Targeting Grid -->
            <div class="left-panel">
                <div class="grid-section">
                    <h2>Targeting Grid</h2>

                    <div class="quadrant-selector">
                        <label for="battleship-table">Vector Table:</label>
                        <select id="battleship-table" name="battleship_table">
                            <option value="vb.battleship" selected>battleship (105 dims)</option>
                            <option value="vb.battle_v21">battle_v21 (21 dims - Goldilocks)</option>
                            <option value="vb.battle_v11">battle_v11 (11 dims)</option>
                        </select>
                        <button id="start-game-button" class="start-game-button">START GAME</button>
                    </div>

                    <!-- <div class="quadrant-selector" id="quadrant-selector-container" style="display: none;">
                        <label for="quadrant">Quadrant:</label>
                        <select id="quadrant" name="quadrant">
                            <option value="1">1</option>
                            <option value="2">2</option>
                            <option value="3">3</option>
                            <option value="4">4</option>
                        </select>
                    </div>
                    -->

                    <div class="quadrant-selector" id="quadrant-selector-container" style="display: none;">
                        <label for="quadrant">Quadrant (1-?):</label>
                        <input type="number" id="quadrant" name="quadrant" min="1" placeholder="Enter quadrant" value="1">
                    </div>

                    <div class="canvas-container">
                        <canvas id="grid" width="400" height="400"></canvas>
                    </div>

                    <div class="coordinates-display">
                        <span>Selected: <strong id="coord-display">X: 5, Y: 5</strong></span>
                    </div>
                </div>

                <div class="controls-section">
                    <div class="ship-type-selector">
                        <h3>Ship Type:</h3>
                        <div class="radio-group">
                            <label>
                                <input type="radio" name="ship_type" value="submarine" checked>
                                Submarine
                            </label>
                            <label>
                                <input type="radio" name="ship_type" value="destroyer">
                                Destroyer
                            </label>
                            <label>
                                <input type="radio" name="ship_type" value="skiff">
                                Skiff
                            </label>
                            <label>
                                <input type="radio" name="ship_type" value="aircraft_carrier">
                                Aircraft Carrier
                            </label>
                        </div>
                    </div>

                    <div class="coordinate-controls">
                        <div class="slider-control">
                            <label for="x-slider">X (Across): <span id="x-value">5</span></label>
                            <input type="range" id="x-slider" min="1" max="10" value="5">
                        </div>
                        <div class="slider-control">
                            <label for="y-slider">Y (Down): <span id="y-value">5</span></label>
                            <input type="range" id="y-slider" min="1" max="10" value="5">
                        </div>
                    </div>

                    <button id="fire-button" class="fire-button">FIRE TORPEDO!</button>
                    <button id="new-game-button" class="new-game-button" style="display: none;">NEW GAME</button>
                </div>
            </div>

            <!-- Right Panel: History -->
            <div class="right-panel">
                <h2>Attempt History</h2>
                <div id="history-container" class="history-container">
                    <p class="no-attempts">No attempts yet. Select coordinates and fire!</p>
                </div>
            </div>
        </div>

        <!-- Game Status Messages -->
        <div id="game-message" class="game-message" style="display: none;"></div>
    </div>

    <script>
/**
 * Vector Battleship - Grid Renderer
 * Handles canvas rendering of the 10x10 targeting grid
 */

class GridRenderer {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.gridSize = 10;
        this.cellSize = this.canvas.width / this.gridSize;
        this.selectedX = 5;
        this.selectedY = 5;
        this.attempts = []; // Store attempts: {x, y, percentage, trend}

        // Set up click handler
        this.canvas.addEventListener('click', (e) => this.handleClick(e));
        this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));

        this.hoverX = null;
        this.hoverY = null;
    }

    handleClick(event) {
        const rect = this.canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        const gridX = Math.floor(x / this.cellSize) + 1;
        const gridY = Math.floor(y / this.cellSize) + 1;

        if (gridX >= 1 && gridX <= 10 && gridY >= 1 && gridY <= 10) {
            this.selectedX = gridX;
            this.selectedY = gridY;

            // Update sliders and display
            document.getElementById('x-slider').value = gridX;
            document.getElementById('y-slider').value = gridY;
            document.getElementById('x-value').textContent = gridX;
            document.getElementById('y-value').textContent = gridY;
            document.getElementById('coord-display').textContent = `X: ${gridX}, Y: ${gridY}`;

            // Update game controller
            if (window.gameController) {
                window.gameController.currentX = gridX;
                window.gameController.currentY = gridY;
            }

            this.render();
        }
    }

    handleMouseMove(event) {
        const rect = this.canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        const gridX = Math.floor(x / this.cellSize) + 1;
        const gridY = Math.floor(y / this.cellSize) + 1;

        if (gridX >= 1 && gridX <= 10 && gridY >= 1 && gridY <= 10) {
            if (this.hoverX !== gridX || this.hoverY !== gridY) {
                this.hoverX = gridX;
                this.hoverY = gridY;
                this.render();
            }
        } else {
            if (this.hoverX !== null) {
                this.hoverX = null;
                this.hoverY = null;
                this.render();
            }
        }
    }

    setSelected(x, y) {
        this.selectedX = x;
        this.selectedY = y;
    }

    addAttempt(x, y, percentage, trend) {
        this.attempts.push({ x, y, percentage, trend });
    }

    clearAttempts() {
        this.attempts = [];
    }

    render() {
        // Clear canvas
        this.ctx.fillStyle = '#0f3460';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw grid
        this.drawGrid();

        // Draw previous attempts
        this.drawAttempts();

        // Draw hover highlight
        if (this.hoverX !== null && this.hoverY !== null) {
            this.drawHoverHighlight(this.hoverX, this.hoverY);
        }

        // Draw selected cell
        this.drawSelectedCell(this.selectedX, this.selectedY);

        // Draw coordinates
        this.drawCoordinates();
    }

    drawGrid() {
        this.ctx.strokeStyle = '#533483';
        this.ctx.lineWidth = 1;

        // Draw vertical lines
        for (let i = 0; i <= this.gridSize; i++) {
            this.ctx.beginPath();
            this.ctx.moveTo(i * this.cellSize, 0);
            this.ctx.lineTo(i * this.cellSize, this.canvas.height);
            this.ctx.stroke();
        }

        // Draw horizontal lines
        for (let i = 0; i <= this.gridSize; i++) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, i * this.cellSize);
            this.ctx.lineTo(this.canvas.width, i * this.cellSize);
            this.ctx.stroke();
        }
    }

    drawAttempts() {
        this.attempts.forEach(attempt => {
            const canvasX = (attempt.x - 1) * this.cellSize;
            const canvasY = (attempt.y - 1) * this.cellSize;

            // Fill cell with heat color
            this.ctx.fillStyle = this.getHeatColor(attempt.percentage);
            this.ctx.globalAlpha = 0.6;
            this.ctx.fillRect(canvasX, canvasY, this.cellSize, this.cellSize);
            this.ctx.globalAlpha = 1.0;

            // Draw marker in center
            const centerX = canvasX + this.cellSize / 2;
            const centerY = canvasY + this.cellSize / 2;
            const radius = this.cellSize / 4;

            // Outer circle
            this.ctx.fillStyle = this.getHeatColor(attempt.percentage);
            this.ctx.beginPath();
            this.ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
            this.ctx.fill();

            // Inner circle
            this.ctx.fillStyle = '#ffffff';
            this.ctx.beginPath();
            this.ctx.arc(centerX, centerY, radius / 2, 0, 2 * Math.PI);
            this.ctx.fill();

            // Draw percentage text
            this.ctx.fillStyle = '#ffffff';
            this.ctx.font = 'bold 12px monospace';
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'bottom';
            this.ctx.fillText(`${attempt.percentage.toFixed(0)}%`, centerX, canvasY + this.cellSize - 5);
        });
    }

    drawHoverHighlight(x, y) {
        const canvasX = (x - 1) * this.cellSize;
        const canvasY = (y - 1) * this.cellSize;

        this.ctx.strokeStyle = '#e94560';
        this.ctx.lineWidth = 2;
        this.ctx.strokeRect(canvasX + 2, canvasY + 2, this.cellSize - 4, this.cellSize - 4);
    }

    drawSelectedCell(x, y) {
        const canvasX = (x - 1) * this.cellSize;
        const canvasY = (y - 1) * this.cellSize;

        // Draw highlighted cell
        this.ctx.fillStyle = 'rgba(255, 107, 107, 0.3)';
        this.ctx.fillRect(canvasX, canvasY, this.cellSize, this.cellSize);

        // Draw border
        this.ctx.strokeStyle = '#ff6b6b';
        this.ctx.lineWidth = 3;
        this.ctx.strokeRect(canvasX + 1.5, canvasY + 1.5, this.cellSize - 3, this.cellSize - 3);

        // Draw crosshair
        const centerX = canvasX + this.cellSize / 2;
        const centerY = canvasY + this.cellSize / 2;
        const crosshairSize = this.cellSize / 3;

        this.ctx.strokeStyle = '#ff6b6b';
        this.ctx.lineWidth = 2;

        // Vertical line
        this.ctx.beginPath();
        this.ctx.moveTo(centerX, centerY - crosshairSize);
        this.ctx.lineTo(centerX, centerY + crosshairSize);
        this.ctx.stroke();

        // Horizontal line
        this.ctx.beginPath();
        this.ctx.moveTo(centerX - crosshairSize, centerY);
        this.ctx.lineTo(centerX + crosshairSize, centerY);
        this.ctx.stroke();
    }

    drawCoordinates() {
        this.ctx.fillStyle = '#e0e0e0';
        this.ctx.font = '14px monospace';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';

        // Draw column numbers (X axis) - top
        for (let i = 1; i <= this.gridSize; i++) {
            const x = (i - 1) * this.cellSize + this.cellSize / 2;
            this.ctx.fillText(i.toString(), x, -10);
        }

        // Draw row numbers (Y axis) - left
        this.ctx.textAlign = 'right';
        for (let i = 1; i <= this.gridSize; i++) {
            const y = (i - 1) * this.cellSize + this.cellSize / 2;
            this.ctx.fillText(i.toString(), -10, y);
        }
    }

    getHeatColor(percentage) {
        if (percentage >= 100) return '#ffd700'; // Gold
        if (percentage >= 96) return '#ff0000';  // Red
        if (percentage >= 86) return '#ff4500';  // Orange
        if (percentage >= 71) return '#ff6b6b';  // Coral
        if (percentage >= 56) return '#e94560';  // Pink
        if (percentage >= 41) return '#533483';  // Purple
        if (percentage >= 26) return '#0f3460';  // Navy
        return '#16213e';                         // Dark Blue
    }
}

/**
 * Vector Battleship - Game Controller
 * Manages game state, API calls, and UI updates
 */

class GameController {
    constructor() {
        this.sessionId = null;
        this.maxQuadrants = 1000000;
        this.currentX = 5;
        this.currentY = 5;
        this.gameActive = false;

        this.init();
    }

    async init() {
        // Set up event listeners
        this.setupEventListeners();

        // Initial grid render
        if (window.gridRenderer) {
            window.gridRenderer.render();
        }
    }

    setupEventListeners() {
        // Start game button
        document.getElementById('start-game-button').addEventListener('click', () => {
            this.startNewSession();
        });

        // Fire button
        document.getElementById('fire-button').addEventListener('click', () => {
            this.fireTorpedo();
        });

        // New game button
        document.getElementById('new-game-button').addEventListener('click', () => {
            window.location.reload();
        });

        // X slider
        const xSlider = document.getElementById('x-slider');
        xSlider.addEventListener('input', (e) => {
            this.currentX = parseInt(e.target.value);
            document.getElementById('x-value').textContent = this.currentX;
            document.getElementById('coord-display').textContent = `X: ${this.currentX}, Y: ${this.currentY}`;
            if (window.gridRenderer) {
                window.gridRenderer.setSelected(this.currentX, this.currentY);
                window.gridRenderer.render();
            }
        });

        // Y slider
        const ySlider = document.getElementById('y-slider');
        ySlider.addEventListener('input', (e) => {
            this.currentY = parseInt(e.target.value);
            document.getElementById('y-value').textContent = this.currentY;
            document.getElementById('coord-display').textContent = `X: ${this.currentX}, Y: ${this.currentY}`;
            if (window.gridRenderer) {
                window.gridRenderer.setSelected(this.currentX, this.currentY);
                window.gridRenderer.render();
            }
        });

        document.getElementById('quadrant').addEventListener('input', () => {
            // We check if the value is not empty to avoid rendering errors while typing
            const val = document.getElementById('quadrant').value;
            
            if (window.gridRenderer && val !== "") {
                window.gridRenderer.clearAttempts();
                window.gridRenderer.render();
            }
        });
    }

    async startNewSession() {
        try {
            const battleshipTable = document.getElementById('battleship-table').value;
            const startButton = document.getElementById('start-game-button');

            // Disable start button during request
            startButton.disabled = true;
            startButton.textContent = 'STARTING...';

            const response = await fetch('/api/sessions/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    player_name: 'Web Player',
                    match_threshold: 55.0,
                    max_attempts: 20,
                    battleship_table: battleshipTable
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || errorData.detail || 'Failed to start session');
            }

            const data = await response.json();
            this.sessionId = data.session_id;
            this.maxQuadrants = data.max_quadrants;
            this.gameActive = true;

            // Update UI
            const tableName = battleshipTable.replace('vb.', '');
            document.getElementById('session-id').textContent = `Session: ${this.sessionId.substring(0, 8)}... | Table: ${tableName} | Max Q: ${this.maxQuadrants}`;

            // Populate quadrant selector
            this.populateQuadrantSelector();

            // Hide start button and table selector, show quadrant selector
            startButton.style.display = 'none';
            document.getElementById('battleship-table').disabled = true;
            document.getElementById('quadrant-selector-container').style.display = 'block';

            console.log('Session started:', this.sessionId);
        } catch (error) {
            console.error('Error starting session:', error);
            alert('Failed to start game session. Please refresh the page.');
            // Re-enable button on error
            const startButton = document.getElementById('start-game-button');
            startButton.disabled = false;
            startButton.textContent = 'START GAME';
        }
    }

    populateQuadrantSelector() {
        const selector = document.getElementById('quadrant');
        // For number input, just set the max attribute
        selector.max = this.maxQuadrants;
        selector.value = 1; // Set default value to 1
        selector.placeholder = `1-${this.maxQuadrants}`;
    }

    async fireTorpedo() {
        if (!this.gameActive) {
            return;
        }

        // Get current selections
        const quadrantValue = document.getElementById('quadrant').value;

        // Validate quadrant input
        if (!quadrantValue || quadrantValue === '') {
            alert('Please enter a quadrant number');
            return;
        }

        const quadrant = parseInt(quadrantValue);

        if (isNaN(quadrant) || quadrant < 1 || quadrant > this.maxQuadrants) {
            alert(`Quadrant must be between 1 and ${this.maxQuadrants}`);
            return;
        }

        const shipType = document.querySelector('input[name="ship_type"]:checked').value;
        const anchorX = this.currentX;
        const anchorY = this.currentY;

        // Disable fire button during request
        const fireButton = document.getElementById('fire-button');
        fireButton.disabled = true;

        try {
            const response = await fetch(`/api/sessions/${this.sessionId}/target`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    quadrant,
                    ship_type: shipType,
                    anchor_x: anchorX,
                    anchor_y: anchorY
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to submit target');
            }

            const data = await response.json();

            // Update attempts counter
            this.updateAttemptsCounter(data.attempt_number);

            // Add to history
            this.addHistoryItem(data, quadrant, shipType, anchorX, anchorY);

            // Add attempt to grid if same quadrant
            const currentQuadrant = parseInt(document.getElementById('quadrant').value);
            if (quadrant === currentQuadrant && window.gridRenderer) {
                window.gridRenderer.addAttempt(anchorX, anchorY, data.match_percentage, data.trend);
                window.gridRenderer.render();
            }

            // Check game status
            if (data.game_status === 'won') {
                this.handleGameWon(data.attempt_number);
            } else if (data.game_status === 'lost') {
                this.handleGameLost(data.attempt_number);
            }

        } catch (error) {
            console.error('Error firing torpedo:', error);
            alert(`Error: ${error.message}`);
        } finally {
            fireButton.disabled = false;
        }
    }

    updateAttemptsCounter(attemptNumber) {
        const status = document.getElementById('attempts-counter');
        status.textContent = `Attempts: ${attemptNumber}/20`;
    }

    addHistoryItem(data, quadrant, shipType, anchorX, anchorY) {
        const container = document.getElementById('history-container');

        // Remove "no attempts" message
        const noAttempts = container.querySelector('.no-attempts');
        if (noAttempts) {
            noAttempts.remove();
        }

        // Create history item
        const item = document.createElement('div');
        item.className = `history-item ${this.getColorClass(data.match_percentage)}`;

        const trendSymbol = this.getTrendSymbol(data.trend);
        const trendClass = data.trend === 'warmer' ? 'trend-warmer' : data.trend === 'cooler' ? 'trend-cooler' : '';

        item.innerHTML = `
            <div class="history-header">
                <span>#${data.attempt_number}</span>
                <span class="trend-indicator ${trendClass}">${trendSymbol}</span>
            </div>
            <div class="history-details">
                <strong>${this.formatShipTypeFull(shipType)}</strong> - Q${quadrant} (${anchorX}, ${anchorY})
            </div>
            <div class="match-bar-container">
                <div class="match-bar" style="width: ${data.match_percentage}%; background-color: ${this.getBarColor(data.match_percentage)}">
                    ${data.match_percentage.toFixed(1)}%
                </div>
            </div>
            <div style="font-size: 0.85em; margin-top: 5px;">
                ${data.perfect_hit ? '🎯 DIRECT HIT!' : this.getTemperatureText(data.match_percentage)}
            </div>
        `;

        // Add to top of history
        container.insertBefore(item, container.firstChild);
    }

    getTrendSymbol(trend) {
        switch (trend) {
            case 'warmer': return '↑ WARMER';
            case 'cooler': return '↓ cooler';
            case 'same': return '→ same';
            case 'first': return '◉ first';
            default: return '';
        }
    }

    formatShipType(shipType) {
        const names = {
            'submarine': 'Sub',
            'destroyer': 'Des',
            'skiff': 'Skf',
            'aircraft_carrier': 'Car'
        };
        return names[shipType] || shipType;
    }

    formatShipTypeFull(shipType) {
        const icons = {
            'submarine': '🔱',
            'destroyer': '⚓',
            'skiff': '⛵',
            'aircraft_carrier': '✈️'
        };
        const names = {
            'submarine': 'Submarine',
            'destroyer': 'Destroyer',
            'skiff': 'Skiff',
            'aircraft_carrier': 'Aircraft Carrier'
        };
        const icon = icons[shipType] || '🚢';
        const name = names[shipType] || shipType;
        return `${icon} ${name}`;
    }

    getColorClass(percentage) {
        if (percentage >= 100) return 'perfect';
        if (percentage >= 96) return 'burning';
        if (percentage >= 86) return 'very-hot';
        if (percentage >= 71) return 'hot';
        if (percentage >= 56) return 'warm';
        if (percentage >= 41) return 'cool';
        if (percentage >= 26) return 'cold-1';
        return 'cold-0';
    }

    getBarColor(percentage) {
        if (percentage >= 100) return '#ffd700';
        if (percentage >= 96) return '#ff0000';
        if (percentage >= 86) return '#ff4500';
        if (percentage >= 71) return '#ff6b6b';
        if (percentage >= 56) return '#e94560';
        if (percentage >= 41) return '#533483';
        if (percentage >= 26) return '#0f3460';
        return '#16213e';
    }

    getTemperatureText(percentage) {
        if (percentage >= 96) return '🔥 BURNING HOT!';
        if (percentage >= 86) return '🔥 Very Hot';
        if (percentage >= 71) return '♨️ Hot';
        if (percentage >= 56) return '🌡️ Warm';
        if (percentage >= 41) return '❄️ Lukewarm';
        if (percentage >= 26) return '🧊 Cool';
        return '🧊 Ice Cold';
    }

    handleGameWon(attempts) {
        this.gameActive = false;
        document.getElementById('fire-button').style.display = 'none';
        document.getElementById('new-game-button').style.display = 'block';

        const message = document.getElementById('game-message');
        message.innerHTML = `
            <h2>🎯 DIRECT HIT!</h2>
            <p>Congratulations! You sunk the battleship in ${attempts} attempts!</p>
            <p style="margin-top: 20px; font-size: 0.9em;">Click "NEW GAME" to play again</p>
        `;
        message.style.display = 'block';
    }

    handleGameLost(attempts) {
        this.gameActive = false;
        document.getElementById('fire-button').style.display = 'none';
        document.getElementById('new-game-button').style.display = 'block';

        const message = document.getElementById('game-message');
        message.innerHTML = `
            <h2>💥 GAME OVER</h2>
            <p>You've used all ${attempts} attempts without finding the target.</p>
            <p style="margin-top: 20px; font-size: 0.9em;">Click "NEW GAME" to try again</p>
        `;
        message.style.display = 'block';
    }
}

// Initialize game when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.gridRenderer = new GridRenderer('grid');
    window.gridRenderer.render();
    window.gameController = new GameController();
});
    </script>
</body>
</html>
"""


# ============================================================================
# DATABASE HELPER FUNCTIONS
# ============================================================================

def execute_target_attempt_db(session_id, quadrant, ship_type, anchor_x, anchor_y, match_threshold, battleship_table):
    """Execute a targeting attempt and return results."""
    vector = make_ship_shape_from_anchorXY(anchor_x, anchor_y, ship_type, battleship_table)
    results = vector_search(battleship_table, quadrant, vector, match_threshold)

    matched_ships = []
    best_match_pct = 0.0
    perfect_hit = False

    for match in results:
        matched_ships.append({
            'ship_class': match['ship_class'],
            'pk': match['uuid'],
            'anchorpoint': match['anchorpoint'],
            'match_percentage': match['match_percentage'],
        })
        if match['match_percentage'] > best_match_pct:
            best_match_pct = match['match_percentage']
        if match['match_percentage'] > 99.99:
            perfect_hit = True
            destroy_ship(battleship_table, match['uuid'])

    return {
        'matched_ships': matched_ships,
        'best_match_percentage': best_match_pct,
        'perfect_hit': perfect_hit,
    }


def create_session_db(player_name, match_threshold, max_attempts, battleship_table):
    """Create a new game session."""
    connection = connect_to_datastore()
    session_id = str(uuid.uuid4())
    connection.hset(f"session:{session_id}", mapping={
        'player_name': player_name or '',
        'battleship_table': battleship_table,
        'started_at': datetime.utcnow().isoformat(),
        'ended_at': '',
        'match_threshold': str(match_threshold),
        'max_attempts': str(max_attempts),
        'attempts_used': '0',
        'status': 'active',
        'best_match_so_far': '0.0',
    })
    connection.expire(f"session:{session_id}", 86400)
    return session_id


def get_session_info_db(session_id):
    """Get current session information."""
    connection = connect_to_datastore()
    raw = connection.hgetall(f"session:{session_id}")
    if not raw:
        raise Exception(f"Session {session_id} not found")
    d = {_s(k): _s(v) for k, v in raw.items()}
    return {
        'session_id': str(session_id),
        'player_name': d.get('player_name', ''),
        'battleship_table': d.get('battleship_table', 'vb.battleship'),
        'started_at': d.get('started_at'),
        'ended_at': d.get('ended_at') or None,
        'match_threshold': float(d.get('match_threshold', 55.0)),
        'max_attempts': int(d.get('max_attempts', 20)),
        'attempts_used': int(d.get('attempts_used', 0)),
        'status': d.get('status', 'active'),
        'best_match_so_far': float(d.get('best_match_so_far', 0.0)),
    }


def record_attempt_db(session_id, attempt_number, quadrant, ship_type, anchor_x, anchor_y,
                      match_percentage, matched_ship_class, previous_best):
    """Record a targeting attempt in the session history list."""
    if attempt_number == 1:
        trend = 'first'
    elif match_percentage > previous_best:
        trend = 'warmer'
    elif match_percentage < previous_best:
        trend = 'cooler'
    else:
        trend = 'same'

    connection = connect_to_datastore()
    connection.rpush(f"session:{session_id}:history", json.dumps({
        'attempt_number': attempt_number,
        'quadrant': quadrant,
        'ship_type': ship_type,
        'anchor_x': anchor_x,
        'anchor_y': anchor_y,
        'match_percentage': match_percentage,
        'matched_ship_class': matched_ship_class,
        'previous_best_match': previous_best,
        'trend': trend,
        'timestamp': datetime.utcnow().isoformat(),
    }))
    return trend


def update_session_db(session_id, attempts_used=None, best_match=None, status=None, ended_at=False):
    """Update session fields."""
    updates = {}
    if attempts_used is not None:
        updates['attempts_used'] = str(attempts_used)
    if best_match is not None:
        updates['best_match_so_far'] = str(best_match)
    if status is not None:
        updates['status'] = status
    if ended_at:
        updates['ended_at'] = datetime.utcnow().isoformat()
    if updates:
        connect_to_datastore().hset(f"session:{session_id}", mapping=updates)


def get_attempt_history_db(session_id):
    """Get all targeting attempts for a session."""
    connection = connect_to_datastore()
    items = connection.lrange(f"session:{session_id}:history", 0, -1)
    return [json.loads(_s(item)) for item in items]


def get_max_quadrants_db(battleship_table):
    """Get the maximum quadrant number."""
    return get_max_quadrants(battleship_table)


# ============================================================================
# INPUT VALIDATION FUNCTIONS
# ============================================================================

def validate_session_start(data):
    """Validate session start request."""
    errors = []

    if data is None:
        data = {}

    player_name = data.get('player_name')
    match_threshold = data.get('match_threshold', 55.0)
    max_attempts = data.get('max_attempts', 20)
    battleship_table = data.get('battleship_table', 'vb.battleship')

    if not isinstance(match_threshold, (int, float)) or not (0 <= match_threshold <= 100):
        errors.append("match_threshold must be between 0 and 100")

    if not isinstance(max_attempts, int) or not (1 <= max_attempts <= 100):
        errors.append("max_attempts must be between 1 and 100")

    if battleship_table not in ['vb.battleship', 'vb.battle_v11', 'vb.battle_v21']:
        errors.append("battleship_table must be one of: vb.battleship, vb.battle_v11, vb.battle_v21")

    if errors:
        error_response = HTTPResponse(status=400, body=json.dumps({'error': '; '.join(errors)}))
        error_response.content_type = 'application/json'
        raise error_response

    return {
        'player_name': player_name,
        'match_threshold': float(match_threshold),
        'max_attempts': int(max_attempts),
        'battleship_table': battleship_table
    }


def validate_target_request(data):
    """Validate target request."""
    errors = []
    required = ['quadrant', 'ship_type', 'anchor_x', 'anchor_y']

    if data is None:
        error_response = HTTPResponse(status=400, body=json.dumps({'error': 'Request body is required'}))
        error_response.content_type = 'application/json'
        raise error_response

    for field in required:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    if errors:
        error_response = HTTPResponse(status=400, body=json.dumps({'error': '; '.join(errors)}))
        error_response.content_type = 'application/json'
        raise error_response

    quadrant = data['quadrant']
    ship_type = data['ship_type']
    anchor_x = data['anchor_x']
    anchor_y = data['anchor_y']

    if not isinstance(quadrant, int) or quadrant < 1:
        errors.append("quadrant must be an integer >= 1")

    if ship_type not in ['submarine', 'destroyer', 'aircraft_carrier', 'skiff']:
        errors.append("Invalid ship_type")

    if not isinstance(anchor_x, int) or not (1 <= anchor_x <= 10):
        errors.append("anchor_x must be between 1 and 10")

    if not isinstance(anchor_y, int) or not (1 <= anchor_y <= 10):
        errors.append("anchor_y must be between 1 and 10")

    if errors:
        error_response = HTTPResponse(status=400, body=json.dumps({'error': '; '.join(errors)}))
        error_response.content_type = 'application/json'
        raise error_response

    return data


# ============================================================================
# ROUTE HANDLERS
# ============================================================================

@app.route('/')
def index():
    """Serve the main HTML page."""
    return HTML_TEMPLATE


@app.route('/health')
def health_check():
    """Health check endpoint."""
    response.content_type = 'application/json'
    return json.dumps({"status": "healthy", "service": "vector-battleship-web"})


@app.route('/api/sessions/start', method='POST')
def create_session_handler():
    """Create a new game session."""
    try:
        data = request.json
        print(f"DEBUG: Received data: {data}")  # Debug logging

        validated = validate_session_start(data)
        print(f"DEBUG: Validated data: {validated}")  # Debug logging

        session_id = create_session_db(
            player_name=validated['player_name'],
            match_threshold=validated['match_threshold'],
            max_attempts=validated['max_attempts'],
            battleship_table=validated['battleship_table']
        )
        print(f"DEBUG: Session created: {session_id}")  # Debug logging

        max_quadrants = get_max_quadrants_db(validated['battleship_table'])
        print(f"DEBUG: Max quadrants: {max_quadrants}")  # Debug logging

        response.content_type = 'application/json'
        return json.dumps({
            'session_id': str(session_id),
            'max_quadrants': max_quadrants
        })
    except HTTPResponse:
        raise
    except Exception as e:
        print(f"ERROR in create_session_handler: {e}")  # Debug logging
        import traceback
        traceback.print_exc()
        error_response = HTTPResponse(status=500, body=json.dumps({'error': str(e)}))
        error_response.content_type = 'application/json'
        raise error_response


@app.route('/api/sessions/<session_id>/target', method='POST')
def submit_target_handler(session_id):
    """Submit a targeting attempt."""
    try:
        # Validate session_id
        try:
            session_uuid = UUID(session_id)
        except ValueError:
            error_response = HTTPResponse(status=400, body=json.dumps({'error': 'Invalid session ID format'}))
            error_response.content_type = 'application/json'
            raise error_response

        # Validate request data
        data = request.json
        validated = validate_target_request(data)

        # Get current session info
        session_info = get_session_info_db(session_uuid)

        # Check if game is still active
        if session_info['status'] != 'active':
            error_response = HTTPResponse(status=400, body=json.dumps({'error': f"Game is already {session_info['status']}"}))
            error_response.content_type = 'application/json'
            raise error_response

        # Check if max attempts exceeded
        if session_info['attempts_used'] >= session_info['max_attempts']:
            error_response = HTTPResponse(status=400, body=json.dumps({'error': 'Maximum attempts reached'}))
            error_response.content_type = 'application/json'
            raise error_response

        # Execute targeting attempt
        result = execute_target_attempt_db(
            session_id=session_uuid,
            quadrant=validated['quadrant'],
            ship_type=validated['ship_type'],
            anchor_x=validated['anchor_x'],
            anchor_y=validated['anchor_y'],
            match_threshold=session_info['match_threshold'],
            battleship_table=session_info['battleship_table']
        )

        # Calculate new attempt number
        new_attempt_number = session_info['attempts_used'] + 1

        # Get previous best match
        previous_best = session_info['best_match_so_far']

        # Determine best match from this attempt
        current_match = result['best_match_percentage']

        # Record the attempt in history
        matched_ship_class = None
        if result['matched_ships']:
            matched_ship_class = result['matched_ships'][0]['ship_class']

        trend = record_attempt_db(
            session_id=session_uuid,
            attempt_number=new_attempt_number,
            quadrant=validated['quadrant'],
            ship_type=validated['ship_type'],
            anchor_x=validated['anchor_x'],
            anchor_y=validated['anchor_y'],
            match_percentage=current_match,
            matched_ship_class=matched_ship_class,
            previous_best=previous_best
        )

        # Update session
        new_best = max(previous_best, current_match)
        new_status = 'active'

        if result['perfect_hit']:
            new_status = 'won'
            update_session_db(
                session_id=session_uuid,
                attempts_used=new_attempt_number,
                best_match=new_best,
                status=new_status,
                ended_at=True
            )
        elif new_attempt_number >= session_info['max_attempts']:
            new_status = 'lost'
            update_session_db(
                session_id=session_uuid,
                attempts_used=new_attempt_number,
                best_match=new_best,
                status=new_status,
                ended_at=True
            )
        else:
            update_session_db(
                session_id=session_uuid,
                attempts_used=new_attempt_number,
                best_match=new_best
            )

        response.content_type = 'application/json'
        return json.dumps({
            'attempt_number': new_attempt_number,
            'match_percentage': current_match,
            'trend': trend,
            'game_status': new_status,
            'matched_ships': result['matched_ships'],
            'perfect_hit': result['perfect_hit']
        })

    except HTTPResponse:
        raise
    except Exception as e:
        print(f"ERROR in submit_target_handler: {e}")
        import traceback
        traceback.print_exc()
        response.content_type = 'application/json'
        error_response = HTTPResponse(status=500, body=json.dumps({'error': str(e)}))
        error_response.content_type = 'application/json'
        raise error_response


@app.route('/api/sessions/<session_id>/history', method='GET')
def get_history_handler(session_id):
    """Get all targeting attempts for a session."""
    try:
        # Validate session_id
        try:
            session_uuid = UUID(session_id)
        except ValueError:
            error_response = HTTPResponse(status=400, body=json.dumps({'error': 'Invalid session ID format'}))
            error_response.content_type = 'application/json'
            raise error_response

        history = get_attempt_history_db(session_uuid)

        response.content_type = 'application/json'
        return json.dumps(history)

    except HTTPResponse:
        raise
    except Exception as e:
        print(f"ERROR in get_history_handler: {e}")
        import traceback
        traceback.print_exc()
        error_response = HTTPResponse(status=500, body=json.dumps({'error': str(e)}))
        error_response.content_type = 'application/json'
        raise error_response


@app.route('/api/sessions/<session_id>/status', method='GET')
def get_status_handler(session_id):
    """Get current game status for a session."""
    try:
        # Validate session_id
        try:
            session_uuid = UUID(session_id)
        except ValueError:
            error_response = HTTPResponse(status=400, body=json.dumps({'error': 'Invalid session ID format'}))
            error_response.content_type = 'application/json'
            raise error_response

        session_info = get_session_info_db(session_uuid)

        response.content_type = 'application/json'
        return json.dumps(session_info)

    except HTTPResponse:
        raise
    except Exception as e:
        print(f"ERROR in get_status_handler: {e}")
        import traceback
        traceback.print_exc()
        error_response = HTTPResponse(status=500, body=json.dumps({'error': str(e)}))
        error_response.content_type = 'application/json'
        raise error_response


# ============================================================================
# SERVER STARTUP
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("VECTOR BATTLESHIP - Web UI")
    print("=" * 60)
    print("Starting Bottle server on http://0.0.0.0:8000")
    print("Open your browser to: http://localhost:8000")
    print("=" * 60)

    app.run(host='0.0.0.0', port=8000, debug=True, reloader=True)
