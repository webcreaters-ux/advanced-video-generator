/**
 * Advanced Video Generator - Web App
 * Interactive functionality for the landing page
 */

// ========================================
// DOM Elements
// ========================================
const navbar = document.querySelector('.navbar');
const navToggle = document.querySelector('.nav-toggle');
const navMenu = document.querySelector('.nav-menu');
const tabButtons = document.querySelectorAll('.tab-btn');
const tabPanes = document.querySelectorAll('.tab-pane');
const copyButtons = document.querySelectorAll('.copy-btn');
const generateBtn = document.getElementById('generate-btn');
const scriptInput = document.getElementById('script-input');
const qualitySelect = document.getElementById('quality-select');
const ttsSelect = document.getElementById('tts-select');
const imagesCheckbox = document.getElementById('images-checkbox');
const subtitlesCheckbox = document.getElementById('subtitles-checkbox');
const transitionsCheckbox = document.getElementById('transitions-checkbox');
const outputArea = document.getElementById('output-area');
const progressContainer = document.getElementById('progress-container');
const progressFill = document.getElementById('progress-fill');
const progressText = document.getElementById('progress-text');

// ========================================
// Navigation
// ========================================

// Mobile menu toggle
navToggle?.addEventListener('click', () => {
    navMenu?.classList.toggle('active');
});

// Navbar scroll effect
window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
        navbar?.classList.add('scrolled');
    } else {
        navbar?.classList.remove('scrolled');
    }
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
            // Close mobile menu if open
            navMenu?.classList.remove('active');
        }
    });
});

// ========================================
// Tab Switching
// ========================================
tabButtons.forEach(button => {
    button.addEventListener('click', () => {
        const tabId = button.dataset.tab;
        
        // Update button states
        tabButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        
        // Update pane visibility
        tabPanes.forEach(pane => {
            pane.classList.remove('active');
            if (pane.id === `${tabId}-tab`) {
                pane.classList.add('active');
            }
        });
    });
});

// ========================================
// Copy to Clipboard
// ========================================
copyButtons.forEach(button => {
    button.addEventListener('click', async () => {
        const codeId = button.dataset.code;
        const codeElement = document.getElementById(codeId);
        
        if (codeElement) {
            const code = codeElement.textContent;
            
            try {
                await navigator.clipboard.writeText(code);
                
                // Update button text temporarily
                const originalHTML = button.innerHTML;
                button.innerHTML = '<i class="fas fa-check"></i> Copied!';
                button.classList.add('success');
                
                setTimeout(() => {
                    button.innerHTML = originalHTML;
                    button.classList.remove('success');
                }, 2000);
            } catch (err) {
                console.error('Failed to copy:', err);
            }
        }
    });
});

// ========================================
// Demo Generation Simulation
// ========================================
if (generateBtn) {
    generateBtn.addEventListener('click', async () => {
        const script = scriptInput?.value.trim();
        
        if (!script) {
            showNotification('Please enter a script first!', 'error');
            return;
        }
        
        // Disable button and show progress
        generateBtn.disabled = true;
        generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
        
        progressContainer?.classList.remove('hidden');
        outputArea.innerHTML = '<div class="output-placeholder"><i class="fas fa-hourglass-half"></i><p>Processing your script...</p></div>';
        
        // Simulate generation steps
        const steps = [
            { progress: 10, text: 'Parsing script into scenes...' },
            { progress: 20, text: 'Initializing TTS engine...' },
            { progress: 35, text: 'Generating audio narration...' },
            { progress: 50, text: 'Processing AI image prompts...' },
            { progress: 65, text: 'Generating AI images...' },
            { progress: 75, text: 'Creating video frames...' },
            { progress: 85, text: 'Adding transitions...' },
            { progress: 90, text: 'Generating subtitles...' },
            { progress: 95, text: 'Rendering final video...' },
            { progress: 100, text: 'Complete!' }
        ];
        
        for (const step of steps) {
            await delay(800);
            if (progressFill) progressFill.style.width = `${step.progress}%`;
            if (progressText) progressText.textContent = step.text;
        }
        
        // Show completion
        await delay(500);
        
        const quality = qualitySelect?.value || 'medium';
        const tts = ttsSelect?.value || 'google';
        const hasImages = imagesCheckbox?.checked;
        const hasSubtitles = subtitlesCheckbox?.checked;
        const hasTransitions = transitionsCheckbox?.checked;
        
        // Calculate estimated duration based on script
        const wordCount = script.split(/\s+/).length;
        const estimatedDuration = Math.round(wordCount / 2.5); // ~2.5 words per second
        
        outputArea.innerHTML = `
            <div class="video-result">
                <div class="result-icon">
                    <i class="fas fa-check-circle"></i>
                </div>
                <h3>Video Generated Successfully!</h3>
                <div class="result-stats">
                    <div class="result-stat">
                        <span class="stat-value">${estimatedDuration}s</span>
                        <span class="stat-label">Duration</span>
                    </div>
                    <div class="result-stat">
                        <span class="stat-value">${quality.toUpperCase()}</span>
                        <span class="stat-label">Quality</span>
                    </div>
                    <div class="result-stat">
                        <span class="stat-value">${wordCount}</span>
                        <span class="stat-label">Words</span>
                    </div>
                </div>
                <div class="result-options">
                    <span class="result-option ${hasImages ? 'active' : ''}">
                        <i class="fas fa-image"></i> AI Images
                    </span>
                    <span class="result-option ${hasSubtitles ? 'active' : ''}">
                        <i class="fas fa-closed-captioning"></i> Subtitles
                    </span>
                    <span class="result-option ${hasTransitions ? 'active' : ''}">
                        <i class="fas fa-film"></i> Transitions
                    </span>
                </div>
                <p class="result-note">
                    <i class="fas fa-info-circle"></i>
                    This is a demo simulation. To generate actual videos, run the Python application locally or in Google Colab.
                </p>
                <div class="result-actions">
                    <a href="https://colab.research.google.com/github/yourusername/advanced-video-generator" 
                       class="btn btn-primary" target="_blank">
                        <i class="fas fa-rocket"></i> Open in Colab
                    </a>
                    <a href="https://github.com/yourusername/advanced-video-generator" 
                       class="btn btn-secondary" target="_blank">
                        <i class="fab fa-github"></i> View Source
                    </a>
                </div>
            </div>
        `;
        
        // Add styles for result
        addResultStyles();
        
        // Reset button
        generateBtn.disabled = false;
        generateBtn.innerHTML = '<i class="fas fa-rocket"></i> Generate Video';
    });
}

// ========================================
// Particles Animation
// ========================================
function createParticles() {
    const particlesContainer = document.getElementById('particles');
    if (!particlesContainer) return;
    
    const particleCount = 50;
    
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = `${Math.random() * 100}%`;
        particle.style.top = `${Math.random() * 100}%`;
        particle.style.animationDelay = `${Math.random() * 20}s`;
        particle.style.animationDuration = `${15 + Math.random() * 10}s`;
        particlesContainer.appendChild(particle);
    }
}

// ========================================
// Notification System
// ========================================
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    // Add styles if not exists
    if (!document.getElementById('notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            .notification {
                position: fixed;
                top: 80px;
                right: 20px;
                padding: 1rem 1.5rem;
                background: var(--bg-card);
                border: 1px solid var(--border);
                border-radius: var(--radius-lg);
                display: flex;
                align-items: center;
                gap: 0.75rem;
                z-index: 9999;
                animation: slideIn 0.3s ease;
                box-shadow: var(--shadow-lg);
            }
            .notification-error {
                border-color: #ef4444;
                color: #ef4444;
            }
            .notification-success {
                border-color: #10b981;
                color: #10b981;
            }
            @keyframes slideIn {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    // Remove after delay
    setTimeout(() => {
        notification.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// ========================================
// Result Styles
// ========================================
function addResultStyles() {
    if (document.getElementById('result-styles')) return;
    
    const style = document.createElement('style');
    style.id = 'result-styles';
    style.textContent = `
        .video-result {
            text-align: center;
            padding: 2rem;
        }
        .result-icon {
            font-size: 4rem;
            color: #10b981;
            margin-bottom: 1rem;
        }
        .video-result h3 {
            font-size: 1.5rem;
            margin-bottom: 1.5rem;
        }
        .result-stats {
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin-bottom: 1.5rem;
        }
        .result-stat {
            text-align: center;
        }
        .result-stat .stat-value {
            display: block;
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--primary-light);
        }
        .result-stat .stat-label {
            font-size: 0.875rem;
            color: var(--text-muted);
        }
        .result-options {
            display: flex;
            justify-content: center;
            gap: 1rem;
            margin-bottom: 1.5rem;
            flex-wrap: wrap;
        }
        .result-option {
            padding: 0.5rem 1rem;
            background: var(--bg-card);
            border-radius: var(--radius-md);
            font-size: 0.875rem;
            color: var(--text-muted);
        }
        .result-option.active {
            background: rgba(99, 102, 241, 0.1);
            color: var(--primary-light);
        }
        .result-option i {
            margin-right: 0.5rem;
        }
        .result-note {
            font-size: 0.875rem;
            color: var(--text-muted);
            margin-bottom: 1.5rem;
            padding: 1rem;
            background: rgba(245, 158, 11, 0.1);
            border-radius: var(--radius-lg);
        }
        .result-note i {
            margin-right: 0.5rem;
            color: var(--accent);
        }
        .result-actions {
            display: flex;
            justify-content: center;
            gap: 1rem;
            flex-wrap: wrap;
        }
    `;
    document.head.appendChild(style);
}

// ========================================
// Utility Functions
// ========================================
function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// ========================================
// Intersection Observer for Animations
// ========================================
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate-in');
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Observe elements for animation
document.querySelectorAll('.feature-card, .extension-card, .demo-panel').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    observer.observe(el);
});

// Add animation class styles
const animationStyles = document.createElement('style');
animationStyles.textContent = `
    .animate-in {
        opacity: 1 !important;
        transform: translateY(0) !important;
    }
`;
document.head.appendChild(animationStyles);

// ========================================
// Typing Effect for Hero
// ========================================
function typeWriter(element, text, speed = 50) {
    let i = 0;
    element.textContent = '';
    
    function type() {
        if (i < text.length) {
            element.textContent += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }
    
    type();
}

// ========================================
// Initialize
// ========================================
document.addEventListener('DOMContentLoaded', () => {
    createParticles();
    
    // Add loaded class to body for animations
    document.body.classList.add('loaded');
    
    console.log('🎬 Advanced Video Generator - Web App Loaded');
});

// ========================================
// Service Worker Registration (for PWA)
// ========================================
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // Service worker can be added later for offline support
        // navigator.serviceWorker.register('/sw.js');
    });
}

// ========================================
// Keyboard Navigation
// ========================================
document.addEventListener('keydown', (e) => {
    // ESC to close mobile menu
    if (e.key === 'Escape') {
        navMenu?.classList.remove('active');
    }
    
    // Ctrl/Cmd + K to focus script input
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        scriptInput?.focus();
    }
});

// ========================================
// Export for module usage
// ========================================
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        showNotification,
        delay
    };
}
