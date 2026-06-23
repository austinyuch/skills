#!/usr/bin/env node

/**
 * 靜態程式碼分析工具
 * 深度分析程式碼複雜度和效能特徵
 */

const fs = require('fs');
const path = require('path');

class CodeAnalyzer {
  constructor() {
    this.metrics = {
      jsonOps: [],
      regexOps: [],
      cryptoOps: [],
      loops: [],
      complexity: 0
    };
  }

  analyzeComplexity(code) {
    // 計算循環複雜度
    const branches = (code.match(/if|else|for|while|switch|case|\?/g) || []).length;
    return branches + 1;
  }

  analyzeJsonOperations(code, filePath) {
    const patterns = [
      { regex: /JSON\.parse\(([^)]+)\)/g, type: 'parse' },
      { regex: /JSON\.stringify\(([^)]+)\)/g, type: 'stringify' }
    ];

    patterns.forEach(({ regex, type }) => {
      let match;
      while ((match = regex.exec(code)) !== null) {
        const arg = match[1];
        const size = this.estimateSize(arg);
        
        this.metrics.jsonOps.push({
          file: filePath,
          type,
          line: this.getLineNumber(code, match.index),
          estimatedSize: size,
          recommendation: size > 10000 ? 'HIGH' : size > 1000 ? 'MEDIUM' : 'LOW'
        });
      }
    });
  }

  analyzeRegexOperations(code, filePath) {
    const patterns = [
      /new RegExp\(['"`]([^'"`]+)['"`][^)]*\)/g,
      /\/([^\/]+)\/[gimuy]*/g
    ];

    patterns.forEach(regex => {
      let match;
      while ((match = regex.exec(code)) !== null) {
        const pattern = match[1];
        const complexity = this.calculateRegexComplexity(pattern);
        
        if (complexity > 10) {
          this.metrics.regexOps.push({
            file: filePath,
            pattern: pattern.substring(0, 50),
            line: this.getLineNumber(code, match.index),
            complexity,
            recommendation: complexity > 50 ? 'HIGH' : 'MEDIUM'
          });
        }
      }
    });
  }

  analyzeCryptoOperations(code, filePath) {
    const cryptoPattern = /(encrypt|decrypt|hash|cipher|createCipher|createDecipher|pbkdf2|scrypt)/gi;
    let match;
    
    while ((match = cryptoPattern.exec(code)) !== null) {
      this.metrics.cryptoOps.push({
        file: filePath,
        operation: match[1],
        line: this.getLineNumber(code, match.index),
        recommendation: 'MEDIUM'
      });
    }
  }

  analyzeLoops(code, filePath) {
    const loopPattern = /for\s*\([^)]+\)\s*\{([\s\S]*?)\}/g;
    let match;
    
    while ((match = loopPattern.exec(code)) !== null) {
      const body = match[1];
      const bodySize = body.length;
      const nestedLoops = (body.match(/for\s*\(/g) || []).length;
      
      if (bodySize > 200 || nestedLoops > 0) {
        this.metrics.loops.push({
          file: filePath,
          line: this.getLineNumber(code, match.index),
          bodySize,
          nestedLoops,
          recommendation: nestedLoops > 1 ? 'HIGH' : bodySize > 500 ? 'MEDIUM' : 'LOW'
        });
      }
    }
  }

  estimateSize(arg) {
    // 簡單估算：檢查是否讀取檔案或大型變數
    if (/readFileSync|readFile/.test(arg)) return 100000;
    if (/\.length\s*>\s*(\d+)/.test(arg)) {
      const match = arg.match(/\.length\s*>\s*(\d+)/);
      return parseInt(match[1]);
    }
    return 100; // 預設小型
  }

  calculateRegexComplexity(pattern) {
    let complexity = pattern.length;
    complexity += (pattern.match(/[*+?{]/g) || []).length * 5;
    complexity += (pattern.match(/\((?!\?:)/g) || []).length * 3;
    complexity += (pattern.match(/\|/g) || []).length * 2;
    return complexity;
  }

  getLineNumber(code, index) {
    return code.substring(0, index).split('\n').length;
  }

  analyze(filePath) {
    const code = fs.readFileSync(filePath, 'utf8');
    
    this.analyzeJsonOperations(code, filePath);
    this.analyzeRegexOperations(code, filePath);
    this.analyzeCryptoOperations(code, filePath);
    this.analyzeLoops(code, filePath);
    this.metrics.complexity = this.analyzeComplexity(code);
  }

  generateReport() {
    console.log('\n📊 靜態程式碼分析報告\n');
    console.log('='.repeat(70));

    // JSON 操作
    if (this.metrics.jsonOps.length > 0) {
      console.log('\n📄 JSON 操作:');
      this.metrics.jsonOps.forEach(op => {
        console.log(`  ${op.file}:${op.line}`);
        console.log(`    類型: ${op.type}, 估計大小: ${op.estimatedSize} bytes`);
        console.log(`    建議: ${op.recommendation} - ${this.getRecommendation('json', op.recommendation)}`);
      });
    }

    // Regex 操作
    if (this.metrics.regexOps.length > 0) {
      console.log('\n🔍 複雜正規表示式:');
      this.metrics.regexOps.forEach(op => {
        console.log(`  ${op.file}:${op.line}`);
        console.log(`    模式: ${op.pattern}...`);
        console.log(`    複雜度: ${op.complexity}`);
        console.log(`    建議: ${op.recommendation} - ${this.getRecommendation('regex', op.recommendation)}`);
      });
    }

    // 加密操作
    if (this.metrics.cryptoOps.length > 0) {
      console.log('\n🔐 加密操作:');
      this.metrics.cryptoOps.forEach(op => {
        console.log(`  ${op.file}:${op.line}`);
        console.log(`    操作: ${op.operation}`);
        console.log(`    建議: ${this.getRecommendation('crypto', op.recommendation)}`);
      });
    }

    // 重型迴圈
    if (this.metrics.loops.length > 0) {
      console.log('\n🔄 重型迴圈:');
      this.metrics.loops.forEach(loop => {
        console.log(`  ${loop.file}:${loop.line}`);
        console.log(`    主體大小: ${loop.bodySize} 字元, 巢狀層數: ${loop.nestedLoops}`);
        console.log(`    建議: ${loop.recommendation} - ${this.getRecommendation('loop', loop.recommendation)}`);
      });
    }

    console.log('\n' + '='.repeat(70));
    console.log(`\n總循環複雜度: ${this.metrics.complexity}`);
    
    const total = this.metrics.jsonOps.length + this.metrics.regexOps.length + 
                  this.metrics.cryptoOps.length + this.metrics.loops.length;
    
    if (total > 0) {
      console.log(`\n✅ 發現 ${total} 個潛在優化點`);
      console.log(`💡 建議使用 NAPI-RS 優化高優先級項目\n`);
    } else {
      console.log(`\n✅ 未發現明顯優化機會\n`);
    }
  }

  getRecommendation(type, priority) {
    const recommendations = {
      json: {
        HIGH: '強烈建議使用 simd-json',
        MEDIUM: '可考慮使用 Rust 優化',
        LOW: '保持 JavaScript 實作'
      },
      regex: {
        HIGH: '使用 Rust regex crate',
        MEDIUM: '考慮預編譯或快取'
      },
      crypto: {
        MEDIUM: '考慮使用 ring 或 aes-gcm'
      },
      loop: {
        HIGH: '將迴圈邏輯移至 Rust',
        MEDIUM: '考慮批次處理優化',
        LOW: '保持 JavaScript 實作'
      }
    };
    
    return recommendations[type]?.[priority] || '評估效能影響';
  }
}

// 主程式
function scanDirectory(dir, analyzer) {
  const files = fs.readdirSync(dir, { withFileTypes: true });

  for (const file of files) {
    const fullPath = path.join(dir, file.name);
    
    if (file.isDirectory() && !file.name.startsWith('.') && file.name !== 'node_modules') {
      scanDirectory(fullPath, analyzer);
    } else if (file.isFile() && /\.(js|ts)$/.test(file.name)) {
      analyzer.analyze(fullPath);
    }
  }
}

const targetDir = process.argv[2] || './src';

if (!fs.existsSync(targetDir)) {
  console.error(`❌ 目錄不存在: ${targetDir}`);
  process.exit(1);
}

const analyzer = new CodeAnalyzer();
scanDirectory(targetDir, analyzer);
analyzer.generateReport();
