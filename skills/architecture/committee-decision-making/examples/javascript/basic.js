#!/usr/bin/env node

/**
 * Basic Example: Committee Decision Making
 * 
 * This example shows the simplest way to use the committee decision-making skill.
 */

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { SSEClientTransport } from "@modelcontextprotocol/sdk/client/sse.js";

const SERVER_URL = process.env.MCP_SERVER_URL || "http://localhost:8000/mcp";

async function main() {
  console.log("🚀 Starting basic committee discussion...\n");

  // 1. Connect to MCP server
  const client = new Client(
    { name: "basic-example", version: "1.0.0" },
    { capabilities: {} }
  );

  await client.connect(new SSEClientTransport(new URL(SERVER_URL)));
  console.log("✅ Connected to MCP server\n");

  // 2. Start committee session
  const result = await client.callTool({
    name: "start_committee_session",
    arguments: {
      topic: "Should we adopt microservices architecture?",
      participants: [
        { role: "architect", provider: "openai", model: "gpt-4" },
        { role: "devops", provider: "anthropic", model: "claude-3-sonnet" }
      ],
      debate_rounds: 1
    }
  });

  const sessionId = result.session_id;
  console.log(`📋 Session started: ${sessionId}\n`);

  // 3. Poll for completion
  console.log("⏳ Waiting for discussion to complete...\n");
  
  let status;
  do {
    await sleep(5000);
    status = await client.callTool({
      name: "get_session_status",
      arguments: { session_id: sessionId }
    });
    console.log(`   Status: ${status.status}, Phase: ${status.current_phase}`);
  } while (status.status !== "completed" && status.status !== "error");

  if (status.status === "error") {
    console.error("\n❌ Session failed");
    process.exit(1);
  }

  // 4. Get synthesis
  console.log("\n📊 Getting synthesis...\n");
  
  const synthesis = await client.callTool({
    name: "synthesize_discussion",
    arguments: { session_id: sessionId }
  });

  // 5. Display results
  console.log("=== Committee Decision ===\n");
  console.log("Summary:");
  console.log(synthesis.synthesis.summary);
  console.log("\nRecommendations:");
  synthesis.synthesis.recommendations.forEach((rec, i) => {
    console.log(`${i + 1}. ${rec}`);
  });

  console.log("\n✅ Done!");
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

main().catch(error => {
  console.error("❌ Error:", error.message);
  process.exit(1);
});
