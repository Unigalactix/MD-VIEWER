const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3001;

app.use(cors());
app.use(express.json());

// Helper to get safe path
const getSafePath = (reqPath) => {
    // Default to current working directory (project root) or a specific directory
    // For this app, let's allow browsing from the location where the server is started up or User home
    // Since this is a local tool, we want to access local files.
    // We'll use the 'root' query param or default to CWD's parent (assuming server is in project/server)
    
    // Simplification: We'll serve from the user's requested path, defaulting to C:/Users/RajeshKodaganti(Quad/Downloads
    // But for safety let's just use the query param 'path' directly but ensure it exists.
    
    let targetPath = reqPath || path.resolve(__dirname, '..', '..'); // Default to Downloads/GITHUB/MD VIEWER's parent?
                                                                      // Better: Default to user home or just root.
                                                                      // Let's default to C:/
    
    if (!targetPath) targetPath = 'C:/';
    
    return targetPath;
};

// API: List files
app.get('/api/files', (req, res) => {
    const dirPath = req.query.path || 'C:/';
    
    try {
        if (!fs.existsSync(dirPath)) {
            return res.status(404).json({ error: 'Directory not found' });
        }
        
        const items = fs.readdirSync(dirPath, { withFileTypes: true });
        
        const responseItems = items.map(item => ({
            name: item.name,
            isDirectory: item.isDirectory(),
            path: path.join(dirPath, item.name),
            size: item.isDirectory() ? 0 : (fs.statSync(path.join(dirPath, item.name)).size) 
        })).sort((a, b) => { // Sort directories first
            if (a.isDirectory === b.isDirectory) {
                return a.name.localeCompare(b.name);
            }
            return a.isDirectory ? -1 : 1;
        });
        
        res.json({ currentPath: dirPath, items: responseItems });
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: err.message });
    }
});

// API: Read file content
app.get('/api/content', (req, res) => {
    const filePath = req.query.path;
    
    if (!filePath) {
        return res.status(400).json({ error: 'Path is required' });
    }
    
    try {
        if (!fs.existsSync(filePath)) {
            return res.status(404).json({ error: 'File not found' });
        }
        
        // Check if it's text/markdown
        // For now just read as utf-8
        const content = fs.readFileSync(filePath, 'utf-8');
        res.json({ content });
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: err.message });
    }
});

app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
