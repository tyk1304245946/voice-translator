import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
    plugins: [react()],
    server: {
        port: 3000,
        proxy: {
            // 开发时代理到后端，生产由 nginx 处理
            '/api': 'http://localhost:8000',
            '/audio': 'http://localhost:8000',
        },
    },
})
