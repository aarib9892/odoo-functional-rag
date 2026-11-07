import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  use: { baseURL: 'http://localhost:8017', headless: true },
  webServer: {
    command: '../backend/.venv/bin/python -m uvicorn tests.pilot_browser_server:app --app-dir ../backend --host 127.0.0.1 --port 8017',
    url: 'http://localhost:8017/health', reuseExistingServer: false, timeout: 15000,
  },
});
