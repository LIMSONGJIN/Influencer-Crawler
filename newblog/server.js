/**
 * BlogCraft Pro Local Server (Node.js 버전)
 * Node.js가 설치된 경우 사용
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

const PORT = 8000;
const HOST = 'localhost';

// MIME 타입 설정
const mimeTypes = {
    '.html': 'text/html',
    '.js': 'text/javascript',
    '.css': 'text/css',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpg',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.ico': 'image/x-icon'
};

const server = http.createServer((req, res) => {
    console.log(`[${new Date().toLocaleString('ko-KR')}] ${req.method} ${req.url}`);
    
    // 기본 경로 처리
    let filePath = '.' + req.url;
    if (filePath === './') {
        filePath = './index-saas.html';
    }
    
    const extname = String(path.extname(filePath)).toLowerCase();
    const contentType = mimeTypes[extname] || 'application/octet-stream';
    
    fs.readFile(filePath, (error, content) => {
        if (error) {
            if (error.code === 'ENOENT') {
                res.writeHead(404, { 'Content-Type': 'text/html' });
                res.end('<h1>404 - File Not Found</h1>', 'utf-8');
            } else {
                res.writeHead(500);
                res.end(`Server Error: ${error.code}`, 'utf-8');
            }
        } else {
            // CORS 헤더 추가
            res.writeHead(200, {
                'Content-Type': contentType,
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Cache-Control': 'no-cache'
            });
            res.end(content, 'utf-8');
        }
    });
});

server.listen(PORT, HOST, () => {
    const url = `http://${HOST}:${PORT}`;
    console.log(`
    ╔════════════════════════════════════════════════╗
    ║         BlogCraft Pro - Local Server           ║
    ╠════════════════════════════════════════════════╣
    ║  서버 시작됨: ${url}             ║
    ║  종료하려면: Ctrl+C를 누르세요                 ║
    ╚════════════════════════════════════════════════╝
    
    📁 서빙 디렉토리: ${__dirname}
    
    🔗 주요 페이지:
    ├── ${url}/index-saas.html     (메인 홈)
    ├── ${url}/saas-login.html     (로그인)
    ├── ${url}/index.html          (블로그 작성)
    ├── ${url}/saas-dashboard.html (대시보드)
    └── ${url}/saas-pricing.html   (요금제)
    
    🌟 브라우저를 여는 중...
    `);
    
    // 브라우저 자동 열기
    const start = process.platform === 'darwin' ? 'open' : 
                  process.platform === 'win32' ? 'start' : 'xdg-open';
    exec(`${start} ${url}/index-saas.html`);
});

// 종료 처리
process.on('SIGINT', () => {
    console.log('\n\n🛑 서버를 종료합니다...');
    console.log('👋 안녕히 가세요!');
    process.exit();
});