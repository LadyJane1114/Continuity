import { contextBridge, ipcRenderer } from 'electron';

//API STUFF


//exit app
contextBridge.exposeInMainWorld('api', {
    quitApp: () => ipcRenderer.send('app:quit')
});
