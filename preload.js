const { contextBridge, ipcRenderer } = require('electron');

// Exposer les API sécurisées au processus de rendu
contextBridge.exposeInMainWorld('electronAPI', {
    // Informations sur l'application
    getAppVersion: () => ipcRenderer.invoke('get-app-version'),
    
    // Opérations sur les fichiers
    saveFile: (data, filename) => ipcRenderer.invoke('save-file', data, filename),
    
    // Boîtes de dialogue
    showMessageBox: (options) => ipcRenderer.invoke('show-message-box', options),
    
    // Événements de l'application
    onNewConversation: (callback) => ipcRenderer.on('new-conversation', callback),
    onExportConversation: (callback) => ipcRenderer.on('export-conversation', callback),
    onShowWelcome: (callback) => ipcRenderer.on('show-welcome', callback),
    
    // Utilitaires
    platform: process.platform,
    versions: process.versions
});

// Fonctions utilitaires pour HIBBI
window.HIBBI = {
    // Sauvegarder la conversation
    saveConversation: async (conversation, filename = 'hibbi-conversation.txt') => {
        try {
            const result = await window.electronAPI.saveFile(conversation, filename);
            return result;
        } catch (error) {
            console.error('Erreur lors de la sauvegarde:', error);
            return { success: false, error: error.message };
        }
    },
    
    // Afficher une notification
    showNotification: (title, body) => {
        if (window.Notification && Notification.permission === 'granted') {
            new Notification(title, { body, icon: 'assets/hibbi.png' });
        }
    },
    
    // Demander la permission pour les notifications
    requestNotificationPermission: async () => {
        if (window.Notification) {
            const permission = await Notification.requestPermission();
            return permission;
        }
        return 'denied';
    },
    
    // Obtenir la version de l'application
    getVersion: async () => {
        try {
            return await window.electronAPI.getAppVersion();
        } catch (error) {
            console.error('Erreur lors de l\'obtention de la version:', error);
            return '1.0.0';
        }
    },
    
    // Ouvrir un lien externe
    openExternal: (url) => {
        window.open(url, '_blank');
    },
    
    // Formater la date
    formatDate: (date) => {
        return new Date(date).toLocaleString('fr-FR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
};

// Écouter les événements de l'application
window.addEventListener('DOMContentLoaded', async () => {
    // Demander la permission pour les notifications
    await window.HIBBI.requestNotificationPermission();
    
    // Écouter les événements
    window.electronAPI.onNewConversation(() => {
        if (window.hibbiApp && window.hibbiApp.clearConversation) {
            window.hibbiApp.clearConversation();
        }
    });
    
    window.electronAPI.onExportConversation((event, filePath) => {
        if (window.hibbiApp && window.hibbiApp.exportConversation) {
            window.hibbiApp.exportConversation(filePath);
        }
    });
    
    window.electronAPI.onShowWelcome(() => {
        if (window.hIBBI && window.hibbiApp && window.hibbiApp.showWelcome) {
            window.hibbiApp.showWelcome();
        }
    });
});
