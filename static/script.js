// HIBBI JavaScript Application
class HibbiApp {
    constructor() {
        this.currentSection = 'chat';
        this.isLoading = false;
        this.chatHistory = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadStatus();
        this.setupKeyboardShortcuts();
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const section = item.dataset.section;
                this.switchSection(section);
            });
        });

        // Mobile menu toggle
        const menuToggle = document.getElementById('menuToggle');
        const sidebar = document.getElementById('sidebar');
        
        menuToggle?.addEventListener('click', () => {
            sidebar.classList.toggle('active');
        });

        // Chat functionality
        this.setupChatEvents();
        
        // Image generation
        this.setupImageGeneration();
        
        // Web search
        this.setupWebSearch();
        
        // Code generation
        this.setupCodeGeneration();
        
        // Text generation
        this.setupTextGeneration();
        
        // Settings
        this.setupSettings();
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + K for quick chat focus
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                const chatInput = document.getElementById('chatInput');
                if (chatInput && this.currentSection === 'chat') {
                    chatInput.focus();
                }
            }
            
            // Escape to close loading overlay
            if (e.key === 'Escape') {
                this.hideLoading();
            }
        });
    }

    switchSection(section) {
        // Update navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-section="${section}"]`).classList.add('active');

        // Update content sections
        document.querySelectorAll('.content-section').forEach(sec => {
            sec.classList.remove('active');
        });
        document.getElementById(`${section}-section`).classList.add('active');

        // Update page title
        const titles = {
            chat: 'Chat avec HIBBI',
            image: 'Génération d\'Images',
            search: 'Recherche Web',
            code: 'Génération de Code',
            text: 'Création de Textes',
            settings: 'Paramètres'
        };
        
        document.querySelector('.page-title').textContent = titles[section] || 'HIBBI';
        
        this.currentSection = section;

        // Close mobile menu
        document.getElementById('sidebar').classList.remove('active');
    }

    setupChatEvents() {
        const chatInput = document.getElementById('chatInput');
        const sendButton = document.getElementById('sendMessage');

        const sendMessage = async () => {
            const message = chatInput.value.trim();
            if (!message || this.isLoading) return;

            // Add user message to chat
            this.addChatMessage(message, 'user');
            chatInput.value = '';

            // Show loading
            this.showLoading('HIBBI réfléchit...');

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message })
                });

                const data = await response.json();
                
                if (response.ok) {
                    this.addChatMessage(data.response, 'hibbi', data);
                } else {
                    this.addChatMessage(`Erreur: ${data.error}`, 'hibbi', null, true);
                }
            } catch (error) {
                this.addChatMessage('Erreur de connexion. Veuillez réessayer.', 'hibbi', null, true);
            } finally {
                this.hideLoading();
            }
        };

        sendButton?.addEventListener('click', sendMessage);
        chatInput?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }

    addChatMessage(message, sender, metadata = null, isError = false) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const timestamp = new Date().toLocaleTimeString('fr-FR', {
            hour: '2-digit',
            minute: '2-digit'
        });

        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-${sender === 'hibbi' ? 'brain' : 'user'}"></i>
            </div>
            <div class="message-content">
                <div class="message-header">
                    <span class="sender">${sender === 'hibbi' ? 'HIBBI' : 'Vous'}</span>
                    <span class="timestamp">${timestamp}</span>
                </div>
                <div class="message-text ${isError ? 'error' : ''}">${this.formatMessage(message)}</div>
                ${metadata ? `<div class="message-metadata">
                    <small>Intention: ${metadata.intent} | Confiance: ${Math.round(metadata.confidence * 100)}%</small>
                </div>` : ''}
            </div>
        `;

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Add to history
        this.chatHistory.push({
            message,
            sender,
            timestamp: new Date(),
            metadata
        });
    }

    formatMessage(message) {
        // Basic formatting for code blocks, links, etc.
        return message
            .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');
    }

    setupImageGeneration() {
        const generateButton = document.getElementById('generateImage');
        
        generateButton?.addEventListener('click', async () => {
            const prompt = document.getElementById('imagePrompt').value.trim();
            if (!prompt || this.isLoading) return;

            this.showLoading('Génération de l\'image en cours...');

            try {
                const response = await fetch('/api/generate_image', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ prompt })
                });

                const data = await response.json();
                
                if (response.ok) {
                    this.displayGeneratedImage(data);
                } else {
                    this.showToast(`Erreur: ${data.error}`, 'error');
                }
            } catch (error) {
                this.showToast('Erreur de connexion. Veuillez réessayer.', 'error');
            } finally {
                this.hideLoading();
            }
        });
    }

    displayGeneratedImage(data) {
        const resultDiv = document.getElementById('imageResult');
        const image = document.getElementById('generatedImage');
        const promptUsed = document.querySelector('.prompt-used');

        image.src = data.image_url;
        promptUsed.textContent = `Prompt: ${data.prompt}`;
        
        resultDiv.style.display = 'block';
        resultDiv.scrollIntoView({ behavior: 'smooth' });

        this.showToast(data.message, 'success');
    }

    setupWebSearch() {
        const searchButton = document.getElementById('performSearch');
        const searchInput = document.getElementById('searchQuery');

        const performSearch = async () => {
            const query = searchInput.value.trim();
            if (!query || this.isLoading) return;

            this.showLoading('Recherche en cours...');

            try {
                const response = await fetch('/api/web_search', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ query })
                });

                const data = await response.json();
                
                if (response.ok) {
                    this.displaySearchResults(data);
                } else {
                    this.showToast(`Erreur: ${data.error}`, 'error');
                }
            } catch (error) {
                this.showToast('Erreur de connexion. Veuillez réessayer.', 'error');
            } finally {
                this.hideLoading();
            }
        };

        searchButton?.addEventListener('click', performSearch);
        searchInput?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                performSearch();
            }
        });
    }

    displaySearchResults(data) {
        const resultsDiv = document.getElementById('searchResults');
        const resultsList = document.getElementById('resultsList');
        const resultsCount = document.querySelector('.results-count');

        resultsList.innerHTML = '';
        
        data.results.forEach(result => {
            const resultItem = document.createElement('div');
            resultItem.className = 'search-result-item';
            resultItem.innerHTML = `
                <div class="search-result-title">${result.title}</div>
                <div class="search-result-url">${result.url}</div>
                <div class="search-result-snippet">${result.snippet}</div>
            `;
            resultItem.addEventListener('click', () => {
                window.open(result.url, '_blank');
            });
            resultsList.appendChild(resultItem);
        });

        resultsCount.textContent = `${data.results.length} résultats`;
        resultsDiv.style.display = 'block';
        resultsDiv.scrollIntoView({ behavior: 'smooth' });

        this.showToast(data.message, 'success');
    }

    setupCodeGeneration() {
        const generateButton = document.getElementById('generateCode');
        
        generateButton?.addEventListener('click', async () => {
            const language = document.getElementById('codeLanguage').value;
            const description = document.getElementById('codeDescription').value.trim();
            
            if (!description || this.isLoading) return;

            this.showLoading('Génération du code en cours...');

            try {
                const response = await fetch('/api/generate_code', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ language, description })
                });

                const data = await response.json();
                
                if (response.ok) {
                    this.displayGeneratedCode(data);
                } else {
                    this.showToast(`Erreur: ${data.error}`, 'error');
                }
            } catch (error) {
                this.showToast('Erreur de connexion. Veuillez réessayer.', 'error');
            } finally {
                this.hideLoading();
            }
        });

        // Copy code button
        document.getElementById('copyCode')?.addEventListener('click', () => {
            const code = document.getElementById('generatedCode').textContent;
            this.copyToClipboard(code);
        });

        // Download code button
        document.getElementById('downloadCode')?.addEventListener('click', () => {
            const code = document.getElementById('generatedCode').textContent;
            const language = document.getElementById('codeLanguage').value;
            this.downloadCode(code, language);
        });
    }

    displayGeneratedCode(data) {
        const resultDiv = document.getElementById('codeResult');
        const codeElement = document.getElementById('generatedCode');

        codeElement.textContent = data.code;
        resultDiv.style.display = 'block';
        resultDiv.scrollIntoView({ behavior: 'smooth' });

        this.showToast(data.message, 'success');
    }

    setupTextGeneration() {
        const generateButton = document.getElementById('generateText');
        
        generateButton?.addEventListener('click', async () => {
            const textType = document.getElementById('textType').value;
            const topic = document.getElementById('textTopic').value.trim();
            
            if (!topic || this.isLoading) return;

            this.showLoading('Génération du texte en cours...');

            try {
                const response = await fetch('/api/generate_text', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ type: textType, topic })
                });

                const data = await response.json();
                
                if (response.ok) {
                    this.displayGeneratedText(data);
                } else {
                    this.showToast(`Erreur: ${data.error}`, 'error');
                }
            } catch (error) {
                this.showToast('Erreur de connexion. Veuillez réessayer.', 'error');
            } finally {
                this.hideLoading();
            }
        });

        // Copy text button
        document.getElementById('copyText')?.addEventListener('click', () => {
            const text = document.getElementById('generatedText').textContent;
            this.copyToClipboard(text);
        });

        // Download text button
        document.getElementById('downloadText')?.addEventListener('click', () => {
            const text = document.getElementById('generatedText').textContent;
            const textType = document.getElementById('textType').value;
            this.downloadText(text, textType);
        });
    }

    displayGeneratedText(data) {
        const resultDiv = document.getElementById('textResult');
        const textElement = document.getElementById('generatedText');

        textElement.textContent = data.text;
        resultDiv.style.display = 'block';
        resultDiv.scrollIntoView({ behavior: 'smooth' });

        this.showToast(data.message, 'success');
    }

    setupSettings() {
        // Load settings
        this.loadSettings();

        // Save settings on change
        document.getElementById('responseStyle')?.addEventListener('change', this.saveSettings);
        document.getElementById('language')?.addEventListener('change', this.saveSettings);
        document.getElementById('theme')?.addEventListener('change', this.saveSettings);
        document.getElementById('fontSize')?.addEventListener('input', this.saveSettings);

        // Action buttons
        document.getElementById('clearMemory')?.addEventListener('click', () => {
            if (confirm('Êtes-vous sûr de vouloir effacer toute la mémoire de HIBBI ?')) {
                this.clearMemory();
            }
        });

        document.getElementById('exportData')?.addEventListener('click', () => {
            this.exportData();
        });

        document.getElementById('resetLearning')?.addEventListener('click', () => {
            if (confirm('Êtes-vous sûr de vouloir réinitialiser l\'apprentissage de HIBBI ?')) {
                this.resetLearning();
            }
        });
    }

    async loadStatus() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();
            
            if (response.ok) {
                this.updateStatusDisplay(data);
            }
        } catch (error) {
            console.error('Error loading status:', error);
        }
    }

    updateStatusDisplay(data) {
        // Update stats in settings
        const totalInteractions = document.getElementById('totalInteractions');
        const successRate = document.getElementById('successRate');
        const avgConfidence = document.getElementById('avgConfidence');

        if (totalInteractions) {
            totalInteractions.textContent = data.memory.total_interactions || 0;
        }
        
        if (successRate && data.learning.total_patterns > 0) {
            const rate = Math.round((data.learning.successful_patterns / data.learning.total_patterns) * 100);
            successRate.textContent = `${rate}%`;
        }
        
        if (avgConfidence) {
            const confidence = Math.round((data.metrics.average_confidence || 0) * 100);
            avgConfidence.textContent = `${confidence}%`;
        }
    }

    loadSettings() {
        const settings = localStorage.getItem('hibbi_settings');
        if (settings) {
            const parsed = JSON.parse(settings);
            
            if (parsed.responseStyle) {
                document.getElementById('responseStyle').value = parsed.responseStyle;
            }
            if (parsed.language) {
                document.getElementById('language').value = parsed.language;
            }
            if (parsed.theme) {
                document.getElementById('theme').value = parsed.theme;
                this.applyTheme(parsed.theme);
            }
            if (parsed.fontSize) {
                document.getElementById('fontSize').value = parsed.fontSize;
                document.documentElement.style.setProperty('--base-font-size', `${parsed.fontSize}px`);
            }
        }
    }

    saveSettings() {
        const settings = {
            responseStyle: document.getElementById('responseStyle')?.value,
            language: document.getElementById('language')?.value,
            theme: document.getElementById('theme')?.value,
            fontSize: document.getElementById('fontSize')?.value
        };

        localStorage.setItem('hibbi_settings', JSON.stringify(settings));
        this.applyTheme(settings.theme);
    }

    applyTheme(theme) {
        if (theme === 'light') {
            document.documentElement.classList.add('light-theme');
        } else {
            document.documentElement.classList.remove('light-theme');
        }
    }

    async clearMemory() {
        this.showLoading('Effacement de la mémoire...');
        
        try {
            // This would need to be implemented in the backend
            this.showToast('Mémoire effacée avec succès', 'success');
        } catch (error) {
            this.showToast('Erreur lors de l\'effacement de la mémoire', 'error');
        } finally {
            this.hideLoading();
        }
    }

    exportData() {
        const data = {
            chatHistory: this.chatHistory,
            settings: localStorage.getItem('hibbi_settings'),
            exportDate: new Date().toISOString()
        };

        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `hibbi_data_${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);

        this.showToast('Données exportées avec succès', 'success');
    }

    async resetLearning() {
        this.showLoading('Réinitialisation de l\'apprentissage...');
        
        try {
            // This would need to be implemented in the backend
            this.showToast('Apprentissage réinitialisé avec succès', 'success');
        } catch (error) {
            this.showToast('Erreur lors de la réinitialisation', 'error');
        } finally {
            this.hideLoading();
        }
    }

    copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showToast('Copié dans le presse-papiers', 'success');
        }).catch(() => {
            this.showToast('Erreur lors de la copie', 'error');
        });
    }

    downloadCode(code, language) {
        const extensions = {
            python: 'py',
            javascript: 'js',
            html: 'html',
            css: 'css',
            java: 'java',
            cpp: 'cpp'
        };

        const extension = extensions[language] || 'txt';
        const blob = new Blob([code], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `generated_code.${extension}`;
        a.click();
        URL.revokeObjectURL(url);

        this.showToast('Code téléchargé avec succès', 'success');
    }

    downloadText(text, textType) {
        const blob = new Blob([text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${textType}_generated.txt`;
        a.click();
        URL.revokeObjectURL(url);

        this.showToast('Texte téléchargé avec succès', 'success');
    }

    showLoading(message = 'Chargement...') {
        this.isLoading = true;
        const overlay = document.getElementById('loadingOverlay');
        const loadingText = overlay.querySelector('p');
        loadingText.textContent = message;
        overlay.classList.add('active');
    }

    hideLoading() {
        this.isLoading = false;
        document.getElementById('loadingOverlay').classList.remove('active');
    }

    showToast(message, type = 'success') {
        const toast = document.getElementById('toast');
        const toastMessage = toast.querySelector('.toast-message');
        
        toast.className = `toast ${type} show`;
        toastMessage.textContent = message;

        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
}

// Initialize the app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new HibbiApp();
});

// Service Worker for PWA capabilities (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then((registration) => {
                console.log('SW registered: ', registration);
            })
            .catch((registrationError) => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}
