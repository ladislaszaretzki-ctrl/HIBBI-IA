const { app, BrowserWindow, Menu, ipcMain, dialog, shell } = require('electron');
const path = require('path');
const fs = require('fs');

// Variables globales
let mainWindow;
let isDev = process.env.NODE_ENV === 'development';

// Créer la fenêtre principale
function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        minWidth: 800,
        minHeight: 600,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        },
        icon: path.join(__dirname, 'assets', 'hibbi.png'),
        show: false,
        titleBarStyle: 'hiddenInset'
    });

    // Charger l'application
    if (isDev) {
        mainWindow.loadURL('http://localhost:3000');
        mainWindow.webContents.openDevTools();
    } else {
        mainWindow.loadFile(path.join(__dirname, 'app', 'index.html'));
    }

    // Afficher la fenêtre quand prête
    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
        
        // Message de bienvenue
        if (!isDev) {
            setTimeout(() => {
                mainWindow.webContents.send('show-welcome');
            }, 1000);
        }
    });

    // Gérer la fermeture
    mainWindow.on('closed', () => {
        mainWindow = null;
    });

    // Ouvrir les liens externes dans le navigateur par défaut
    mainWindow.webContents.setWindowOpenHandler(({ url }) => {
        shell.openExternal(url);
        return { action: 'deny' };
    });
}

// Créer le menu
function createMenu() {
    const template = [
        {
            label: 'Fichier',
            submenu: [
                {
                    label: 'Nouvelle conversation',
                    accelerator: 'CmdOrCtrl+N',
                    click: () => {
                        mainWindow.webContents.send('new-conversation');
                    }
                },
                { type: 'separator' },
                {
                    label: 'Exporter la conversation',
                    accelerator: 'CmdOrCtrl+E',
                    click: async () => {
                        const result = await dialog.showSaveDialog(mainWindow, {
                            defaultPath: 'hibbi-conversation.txt',
                            filters: [
                                { name: 'Fichiers texte', extensions: ['txt'] },
                                { name: 'Tous les fichiers', extensions: ['*'] }
                            ]
                        });
                        
                        if (!result.canceled) {
                            mainWindow.webContents.send('export-conversation', result.filePath);
                        }
                    }
                },
                { type: 'separator' },
                {
                    label: 'Quitter',
                    accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
                    click: () => {
                        app.quit();
                    }
                }
            ]
        },
        {
            label: 'Edition',
            submenu: [
                { role: 'undo', label: 'Annuler' },
                { role: 'redo', label: 'Refaire' },
                { type: 'separator' },
                { role: 'cut', label: 'Couper' },
                { role: 'copy', label: 'Copier' },
                { role: 'paste', label: 'Coller' },
                { role: 'selectall', label: 'Tout sélectionner' }
            ]
        },
        {
            label: 'Affichage',
            submenu: [
                { role: 'reload', label: 'Actualiser' },
                { role: 'forceReload', label: 'Forcer l\'actualisation' },
                { role: 'toggleDevTools', label: 'Outils de développement' },
                { type: 'separator' },
                { role: 'resetZoom', label: 'Taille réelle' },
                { role: 'zoomIn', label: 'Zoom avant' },
                { role: 'zoomOut', label: 'Zoom arrière' },
                { type: 'separator' },
                { role: 'togglefullscreen', label: 'Plein écran' }
            ]
        },
        {
            label: 'HIBBI',
            submenu: [
                {
                    label: 'À propos de HIBBI',
                    click: () => {
                        dialog.showMessageBox(mainWindow, {
                            type: 'info',
                            title: 'À propos de HIBBI',
                            message: 'HIBBI v1.0.0',
                            detail: 'Intelligence Artificielle Complète\n\nHIBBI est votre IA personnelle capable de converser, générer des images, créer du code et bien plus encore !\n\nCréé avec ❤️ par l\'équipe HIBBI',
                            buttons: ['OK']
                        });
                    }
                },
                {
                    label: 'Documentation',
                    click: () => {
                        shell.openExternal('https://github.com/hibbi-ia/documentation');
                    }
                },
                {
                    label: 'Signaler un bug',
                    click: () => {
                        shell.openExternal('https://github.com/hibbi-ia/issues');
                    }
                }
            ]
        }
    ];

    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
}

// IPC Handlers
ipcMain.handle('get-app-version', () => {
    return app.getVersion();
});

ipcMain.handle('save-file', async (event, data, filename) => {
    try {
        const result = await dialog.showSaveDialog(mainWindow, {
            defaultPath: filename,
            filters: [
                { name: 'Fichiers texte', extensions: ['txt'] },
                { name: 'Tous les fichiers', extensions: ['*'] }
            ]
        });
        
        if (!result.canceled) {
            fs.writeFileSync(result.filePath, data, 'utf8');
            return { success: true };
        }
        return { success: false };
    } catch (error) {
        return { success: false, error: error.message };
    }
});

ipcMain.handle('show-message-box', async (event, options) => {
    const result = await dialog.showMessageBox(mainWindow, options);
    return result;
});

// Événements de l'application
app.whenReady().then(() => {
    createWindow();
    createMenu();
    
    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

// Sécurité : empêcher la navigation externe
app.on('web-contents-created', (event, contents) => {
    contents.on('will-navigate', (event, navigationUrl) => {
        const parsedUrl = new URL(navigationUrl);
        
        if (parsedUrl.origin !== 'file://' && !isDev) {
            event.preventDefault();
        }
    });
});

// Gestion des erreurs non capturées
process.on('uncaughtException', (error) => {
    console.error('Erreur non capturée:', error);
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('Rejet non géré à:', promise, 'raison:', reason);
});
