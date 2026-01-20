/**
 * Secure Node.js server demonstrating Docker best practices.
 *
 * Security features demonstrated:
 * - Graceful shutdown handling
 * - Proper signal handling (with dumb-init)
 * - Non-root user execution
 * - Environment-based configuration
 */

const http = require('http');
const os = require('os');

const PORT = process.env.PORT || 3000;
const VERSION = process.env.VERSION || '1.0.0';

/**
 * Request handler with routing.
 */
function requestHandler(req, res) {
    const url = new URL(req.url, `http://${req.headers.host}`);

    // Set JSON content type for all responses
    res.setHeader('Content-Type', 'application/json');

    switch (url.pathname) {
        case '/':
            handleRoot(req, res);
            break;
        case '/health':
            handleHealth(req, res);
            break;
        case '/info':
            handleInfo(req, res);
            break;
        default:
            handleNotFound(req, res);
    }
}

function handleRoot(req, res) {
    res.writeHead(200);
    res.end(JSON.stringify({
        message: 'Hello from secure Node.js in Docker!',
        hostname: os.hostname()
    }));
}

function handleHealth(req, res) {
    res.writeHead(200);
    res.end(JSON.stringify({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        version: VERSION
    }));
}

function handleInfo(req, res) {
    res.writeHead(200);
    res.end(JSON.stringify({
        nodeVersion: process.version,
        platform: process.platform,
        arch: process.arch,
        hostname: os.hostname(),
        uptime: process.uptime(),
        memoryUsage: process.memoryUsage(),
        user: os.userInfo().username
    }));
}

function handleNotFound(req, res) {
    res.writeHead(404);
    res.end(JSON.stringify({
        error: 'Not Found',
        path: req.url
    }));
}

// Create server
const server = http.createServer(requestHandler);

// Graceful shutdown handling
let isShuttingDown = false;

function gracefulShutdown(signal) {
    if (isShuttingDown) return;
    isShuttingDown = true;

    console.log(`\nReceived ${signal}. Starting graceful shutdown...`);

    server.close((err) => {
        if (err) {
            console.error('Error during shutdown:', err);
            process.exit(1);
        }
        console.log('Server closed. Exiting.');
        process.exit(0);
    });

    // Force exit after 10 seconds
    setTimeout(() => {
        console.error('Forced shutdown after timeout');
        process.exit(1);
    }, 10000);
}

// Handle termination signals
process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));

// Handle uncaught errors
process.on('uncaughtException', (err) => {
    console.error('Uncaught Exception:', err);
    gracefulShutdown('uncaughtException');
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});

// Start server
server.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running on port ${PORT}`);
    console.log(`Version: ${VERSION}`);
    console.log(`Node.js: ${process.version}`);
    console.log(`User: ${os.userInfo().username}`);
});
