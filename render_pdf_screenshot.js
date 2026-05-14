const { chromium } = require("playwright");

async function main() {
  const pdfPath = process.argv[2];
  const outPath = process.argv[3];
  if (!pdfPath || !outPath) {
    console.error("Usage: node render_pdf_screenshot.js <input.pdf> <output.png>");
    process.exit(1);
  }

  const candidates = [
    "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
  ];

  let browser;
  let lastError;
  for (const executablePath of candidates) {
    try {
      browser = await chromium.launch({ headless: true, executablePath });
      break;
    } catch (error) {
      lastError = error;
    }
  }
  if (!browser) {
    throw lastError;
  }

  const page = await browser.newPage({
    viewport: { width: 1600, height: 2100 },
    deviceScaleFactor: 1
  });
  await page.goto(`file:///${pdfPath.replace(/\\/g, "/")}`, { waitUntil: "networkidle" });
  await page.waitForTimeout(1500);
  await page.screenshot({ path: outPath, fullPage: true });
  await browser.close();
  console.log(outPath);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
