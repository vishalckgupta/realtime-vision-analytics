// ui/web/backend/stream_router.js

const net = require('net');
const WebSocket = require('ws');

const WS_PORT = 8082;

const STREAMS = [
    {
        name: 'RAW',
        tcpPort: 9001,
        wsPath: '/raw',
        clients: new Set()
    },
    {
        name: 'AI',
        tcpPort: 9002,
        wsPath: '/ai',
        clients: new Set()
    }
];


// =====================================================
// WebSocket Server
// =====================================================

const wss = new WebSocket.Server({ port: WS_PORT });

console.log(`WebSocket server listening on ws://0.0.0.0:${WS_PORT}`);


wss.on('connection', (ws, req) => {

    const path = req.url;

    const stream = STREAMS.find(s => s.wsPath === path);

    if (!stream) {
        console.log(`Unknown WS path: ${path}`);
        ws.close();
        return;
    }

    stream.clients.add(ws);

    console.log(`[${stream.name}] WS client connected`);

    ws.on('close', () => {
        stream.clients.delete(ws);
        console.log(`[${stream.name}] WS client disconnected`);
    });
});


// =====================================================
// TCP -> WebSocket Bridge
// =====================================================

function connectStream(stream) {

    console.log(`[${stream.name}] Connecting to TCP source on port ${stream.tcpPort}...`);

    const socket = net.connect(stream.tcpPort, '127.0.0.1');

    socket.on('connect', () => {
        console.log(`[${stream.name}] Connected to TCP stream`);
    });

    socket.on('data', (chunk) => {

        // Debug
        //console.log(`[${stream.name}] Incoming data: ${chunk.length} bytes`);

        for (const ws of stream.clients) {

            if (ws.readyState === WebSocket.OPEN) {
                ws.send(chunk);
            }
        }
    });

    socket.on('close', () => {
        console.log(`[${stream.name}] TCP connection closed. Reconnecting in 2 sec...`);

        setTimeout(() => {
            connectStream(stream);
        }, 2000);
    });

    socket.on('error', (err) => {
        console.log(`[${stream.name}] TCP error: ${err.message}`);

        socket.destroy();

        setTimeout(() => {
            connectStream(stream);
        }, 2000);
    });
}


// =====================================================
// Start all stream bridges
// =====================================================

for (const stream of STREAMS) {
    connectStream(stream);
}

