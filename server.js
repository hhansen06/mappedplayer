const http = require('http');
const WebSocket = require('ws');
const fs = require('fs');

// Framebuffer setup
const fbPath = '/dev/fb0';
const fbWidth = 1920; // Adjust to your screen width
const fbHeight = 1080; // Adjust to your screen height
const bytesPerPixel = 4; // Assuming 32-bit color
const framebuffer = fs.openSync(fbPath, 'r+');

// Clear the framebuffer
function clearFramebuffer() {
    const black = Buffer.alloc(fbWidth * fbHeight * bytesPerPixel, 0x00);
    fs.writeSync(framebuffer, black, 0, black.length, 0);
}

// Draw a pixel on the framebuffer
function drawPixel(x, y, color) {
    if (x < 0 || y < 0 || x >= fbWidth || y >= fbHeight) return; // Bounds check
    const buffer = Buffer.alloc(bytesPerPixel);
    buffer.writeUInt32LE(color, 0); // Color in ARGB format
    const offset = (x + y * fbWidth) * bytesPerPixel;
    fs.writeSync(framebuffer, buffer, 0, buffer.length, offset);
}

// Draw a line using Bresenham's algorithm
function drawLine(x0, y0, x1, y1, color) {
    let dx = Math.abs(x1 - x0);
    let dy = Math.abs(y1 - y0);
    let sx = x0 < x1 ? 1 : -1;
    let sy = y0 < y1 ? 1 : -1;
    let err = dx - dy;

    while (true) {
        drawPixel(x0, y0, color);

        if (x0 === x1 && y0 === y1) break;
        let e2 = 2 * err;
        if (e2 > -dy) {
            err -= dy;
            x0 += sx;
        }
        if (e2 < dx) {
            err += dx;
            y0 += sy;
        }
    }
}

// Read HTML Content from external file
const htmlFilePath = './index.html';

// Create an HTTP server
const server = http.createServer((req, res) => {
    if (req.method === 'GET' && req.url === '/') {
        // Serve the HTML content
        fs.readFile(htmlFilePath, 'utf-8', (err, data) => {
            if (err) {
                res.writeHead(500, { 'Content-Type': 'text/plain' });
                res.end('Internal Server Error');
                return;
            }
            res.writeHead(200, { 'Content-Type': 'text/html' });
            res.end(data);
        });
    } else {
        // Handle 404 - Not Found
        res.writeHead(404, { 'Content-Type': 'text/plain' });
        res.end('404 Not Found');
    }
});

// Start the HTTP server on port 3000
const PORT = 3000;
server.listen(PORT, () => {
    console.log(`HTTP server is running on http://localhost:${PORT}`);
});

// Create a WebSocket server
const wss = new WebSocket.Server({ port: 3001 });

wss.on('connection', (ws) => {
    console.log('WebSocket connection established.');

    ws.on('message', (message) => {
        const data = JSON.parse(message);
        if (data.type === 'polygon') {
            console.log(`Polygon points: ${JSON.stringify(data.points)}`);

            // Draw the polygon in the framebuffer
            const color = 0xFFFF0000; // Red color in ARGB format
            const points = data.points;
            for (let i = 0; i < points.length; i++) {
                const start = points[i];
                const end = points[(i + 1) % points.length]; // Connect to the next point, looping to the first
                drawLine(start.x, start.y, end.x, end.y, color);
            }
        }
    });

    ws.on('close', () => {
        console.log('WebSocket connection closed.');
    });
});