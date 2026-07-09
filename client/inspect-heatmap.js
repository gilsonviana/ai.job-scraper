const { chromium } = require('@playwright/test');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({
    viewport: { width: 1440, height: 900 }
  });
  
  const logs = [];
  const errors = [];
  
  page.on('console', msg => {
    logs.push(`[${msg.type()}] ${msg.text()}`);
  });
  
  page.on('pageerror', err => {
    errors.push(`Page Error: ${err.message}\n${err.stack}`);
  });
  
  try {
    console.log('Navigating to http://localhost:5174/skills-summary...');
    await page.goto('http://localhost:5174/skills-summary', { 
      waitUntil: 'networkidle',
      timeout: 30000
    });
    
    console.log('Page loaded, waiting for content to render...');
    await page.waitForTimeout(2000);
    
    // Take full page screenshot
    console.log('Taking full page screenshot...');
    await page.screenshot({ 
      path: '/private/tmp/claude-501/-Volumes-KINGSTON-Programming-portfolio-ai-job-scraper/706b7279-4cfb-460d-b527-79740cc483d8/scratchpad/heatmap-full.png',
      fullPage: true
    });
    
    // Get page title and URL
    console.log('Page title:', await page.title());
    console.log('Current URL:', page.url());
    
    // Look for the heatmap container
    const heatmapContainer = await page.$('.heatmap-container, [class*="eatmap"], [class*="Heatmap"]');
    if (heatmapContainer) {
      const bbox = await heatmapContainer.boundingBox();
      console.log('Heatmap container found at:', bbox);
      await heatmapContainer.screenshot({ 
        path: '/private/tmp/claude-501/-Volumes-KINGSTON-Programming-portfolio-ai-job-scraper/706b7279-4cfb-460d-b527-79740cc483d8/scratchpad/heatmap-component.png' 
      });
    } else {
      console.log('Heatmap container not found');
    }
    
    // Check for CSS issues - get computed styles of elements
    const elements = await page.$$('div, canvas, svg');
    console.log(`Found ${elements.length} elements on page`);
    
    // Look for any render errors
    const errorTexts = await page.locator('text=/error|Error|ERROR|warning|Warning|failed/i').count();
    console.log(`Found ${errorTexts} error/warning text elements`);
    
    // Get all console logs and errors
    console.log('\n=== Console Logs ===');
    logs.forEach(log => console.log(log));
    
    if (errors.length > 0) {
      console.log('\n=== Page Errors ===');
      errors.forEach(err => console.log(err));
    }
    
    // Check page for specific issues
    const hasNetworkErrors = logs.some(l => l.includes('Failed') || l.includes('error'));
    console.log('\nNetwork errors detected:', hasNetworkErrors);
    
    // Get HTML snippet to check structure
    const bodyHTML = await page.locator('body').innerHTML();
    fs.writeFileSync('/private/tmp/claude-501/-Volumes-KINGSTON-Programming-portfolio-ai-job-scraper/706b7279-4cfb-460d-b527-79740cc483d8/scratchpad/page-html.txt', bodyHTML.substring(0, 5000));
    
  } catch (error) {
    console.error('Error during inspection:', error.message);
    errors.push(error.toString());
  } finally {
    await browser.close();
    console.log('\nBrowser closed');
  }
})();
