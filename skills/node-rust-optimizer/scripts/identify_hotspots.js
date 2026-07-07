#!/usr/bin/env node

/**
 * Node.js 效能熱點識別工具
 * 掃描程式碼找出適合 Rust 優化的候選項
 */

const fs = require('fs');
const path = require('path');

const PATTERNS = {
  largeJson: /JSON\.(parse|stringify)\([^)]{50,}\)/g,
  complexRegex: /new RegExp\(['"`](.{50,})['"`]\)|\/(.{50,})\//g,
  crypto: /(encrypt|decrypt|hash|cipher|createCipher)/gi,
  heavyLoop: /for\s*\([^)]+\)\s*\{[\s\S]{200,}?\}/g,
};

function analyzeFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const results = [];

  // 檢查大型 JSON 操作
  const jsonMatches = content.match(PATTERNS.largeJson);
  if (jsonMatches) {
    results.push({
      type: 'JSON',
      count: jsonMatches.length,
      suggestion: '考慮使用 Rust + simd-json 優化',
      priority: 'HIGH'
    });
  }

  // 檢查複雜正規表示式
  const regexMatches = content.match(PATTERNS.complexRegex);
  if (regexMatches) {
    results.push({
      type: 'Regex',
      count: regexMatches.length,
      suggestion: '考慮使用 Rust regex crate 優化',
      priority: 'MEDIUM'
    });
  }

  // 檢查加密操作
  const cryptoMatches = content.match(PATTERNS.crypto);
  if (cryptoMatches) {
    results.push({
      type: 'Crypto',
      count: cryptoMatches.length,
      suggestion: '考慮使用 Rust ring/aes-gcm 優化',
      priority: 'MEDIUM'
    });
  }

  // 檢查重型迴圈
  const loopMatches = content.match(PATTERNS.heavyLoop);
  if (loopMatches) {
    results.push({
      type: 'Heavy Loop',
      count: loopMatches.length,
      suggestion: '考慮將迴圈邏輯移至 Rust',
      priority: 'HIGH'
    });
  }

  return results;
}

function scanDirectory(dir) {
  const files = fs.readdirSync(dir, { withFileTypes: true });
  const report = {};

  for (const file of files) {
    const fullPath = path.join(dir, file.name);
    
    if (file.isDirectory() && !file.name.startsWith('.') && file.name !== 'node_modules') {
      Object.assign(report, scanDirectory(fullPath));
    } else if (file.isFile() && /\.(js|ts)$/.test(file.name)) {
      const results = analyzeFile(fullPath);
      if (results.length > 0) {
        report[fullPath] = results;
      }
    }
  }

  return report;
}

function printReport(report) {
  console.log('\n🔍 Node.js 效能熱點分析報告\n');
  console.log('=' .repeat(60));

  let totalIssues = 0;
  const summary = { HIGH: 0, MEDIUM: 0, LOW: 0 };

  for (const [file, issues] of Object.entries(report)) {
    console.log(`\n📄 ${file}`);
    for (const issue of issues) {
      console.log(`  ⚠️  ${issue.type} (${issue.count} 次) - ${issue.priority}`);
      console.log(`      💡 ${issue.suggestion}`);
      totalIssues++;
      summary[issue.priority]++;
    }
  }

  console.log('\n' + '='.repeat(60));
  console.log(`\n📊 總結:`);
  console.log(`  - 總問題數: ${totalIssues}`);
  console.log(`  - 高優先級: ${summary.HIGH}`);
  console.log(`  - 中優先級: ${summary.MEDIUM}`);
  console.log(`  - 低優先級: ${summary.LOW}`);
  
  if (totalIssues > 0) {
    console.log(`\n✅ 建議: 優先處理高優先級項目，預期可獲得 2-5x 效能提升\n`);
  } else {
    console.log(`\n✅ 未發現明顯效能瓶頸\n`);
  }
}

// 主程式
const targetDir = process.argv[2] || './src';

if (!fs.existsSync(targetDir)) {
  console.error(`❌ 目錄不存在: ${targetDir}`);
  process.exit(1);
}

const report = scanDirectory(targetDir);
printReport(report);
