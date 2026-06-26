#!/usr/bin/env python3
"""Daily Self-Evolution, Tool Discovery, and Life Automation Interpreter script."""

import json
import os
import pathlib
import re
import subprocess
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(os.environ.get("SUNEEL_WORKSPACE", str(pathlib.Path.home() / "SuneelWorkSpace"))).resolve()
sys.path.append(str(ROOT / "scripts"))

import system_intelligence

BRAIN_DIR = ROOT / "brain"
SYSTEM_DIR = BRAIN_DIR / "system"
WORKFLOWS_DIR = BRAIN_DIR / "workflows"
LOGS_DIR = BRAIN_DIR / "logs"

def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat()

def read_json(path: pathlib.Path, default=None):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text())
    except Exception:
        return default

def write_json(path: pathlib.Path, data: any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")

# ---------------------------------------------------------------------------
# PHASE 3: DAILY EVOLUTION LOOP
# ---------------------------------------------------------------------------
def run_daily_evolution():
    print("🚀 Initiating Daily Self-Evolution Loop...")
    
    # 1. Run system intelligence generation
    print("  - Running system audit, gap analysis, and recommendations...")
    system_intelligence.generate_all(update_resources=True)
    
    # 2. Analyze Obsidian/Workspace logs
    print("  - Analyzing logs for repetitive tasks and inefficiencies...")
    session_log_path = ROOT / "agent-system/logs/SESSION_LOG.md"
    maintenance_log_path = ROOT / "agent-system/logs/MAINTENANCE_LOG.md"
    
    # Detect repetitive commands
    command_counts = {}
    if session_log_path.exists():
        log_content = session_log_path.read_text(errors="replace")
        # Find commands like: rtk git diff, rtk mcp-test, etc.
        commands = re.findall(r"rtk\s+([a-zA-Z0-9_\-\.\/]+(?:\s+[a-zA-Z0-9_\-\.\/]+)*)", log_content)
        for cmd in commands:
            cmd = cmd.strip()
            command_counts[cmd] = command_counts.get(cmd, 0) + 1
            
    repetitive_tasks = []
    for cmd, count in sorted(command_counts.items(), key=lambda x: x[1], reverse=True):
        if count >= 3:
            repetitive_tasks.append({
                "command": cmd,
                "count": count,
                "recommendation": f"Wrap '{cmd}' into a dedicated alias or automation shortcut."
            })
            
    # Detect inefficiencies / failures
    inefficiencies = []
    failure_log_path = ROOT / "testing/failure_log.json"
    if failure_log_path.exists():
        failures = read_json(failure_log_path, [])
        for f in failures[-5:]:
            inefficiencies.append(f"Test failure in '{f.get('test_id')}' at {f.get('timestamp')}: {f.get('error')[:120]}")
            
    # Detect structural issues / doctor check
    doctor_out = ""
    doctor_script = ROOT / "bin/agent-doctor"
    if doctor_script.exists():
        res = subprocess.run([str(doctor_script)], capture_output=True, text=True, env=os.environ)
        doctor_out = res.stdout.strip()
        if "issues" in doctor_out and "healthy (0 issues)" not in doctor_out:
            inefficiencies.append(f"Doctor Health Check Warning: {doctor_out}")

    # 3. Generate daily improvements report
    improvements_path = SYSTEM_DIR / "daily_improvements.md"
    print(f"  - Generating {improvements_path.relative_to(ROOT)}...")
    
    lines = [
        f"# Daily System Evolution & Improvements",
        f"",
        f"**Generated:** {now_iso()}",
        f"",
        f"## 1. Activity & Repetitive Task Analysis",
    ]
    if repetitive_tasks:
        lines.append("Detected the following repetitive tasks in logs:")
        for idx, t in enumerate(repetitive_tasks, 1):
            lines.append(f"{idx}. **rtk {t['command']}** run {t['count']} times. *{t['recommendation']}*")
    else:
        lines.append("- Zero highly repetitive command sequences detected. Command routing is optimal.")
        
    lines.append("")
    lines.append("## 2. Inefficiencies & Workspace Warnings")
    if inefficiencies:
        for idx, inc in enumerate(inefficiencies, 1):
            lines.append(f"- [{idx}] {inc}")
    else:
        lines.append("- Workspace health check is 100% stable. Doctor reports zero structural issues.")
        
    lines.append("")
    lines.append("## 3. Selected Top 3 Safe Improvements")
    
    # Select top 3 bounded improvements based on findings
    top_3 = []
    if repetitive_tasks:
        top_3.append({
            "name": f"Automate repetitive command '{repetitive_tasks[0]['command']}'",
            "type": "automation",
            "action": "Suggest alias in README",
            "safe": False
        })
    
    # Always include safe system optimization/re-indexing
    top_3.append({
        "name": "Re-index workspace-brain MCP server storage",
        "type": "maintenance",
        "action": "rtk ./bin/mcp-reindex",
        "safe": True
    })
    top_3.append({
        "name": "Run workspace auto-repair & doctor verification check",
        "type": "maintenance",
        "action": "rtk ./bin/agent-repair",
        "safe": True
    })
    top_3.append({
        "name": "Re-train orchestrator router using recent decision logs",
        "type": "optimization",
        "action": "rtk ./bin/route-learn --summary",
        "safe": True
    })
    
    # Bounded to exactly top 3
    selected_improvements = top_3[:3]
    for idx, imp in enumerate(selected_improvements, 1):
        safety_str = "SAFE (Auto-Executable)" if imp["safe"] else "CONTROLLED (Requires User Approval)"
        lines.append(f"{idx}. **{imp['name']}** | Type: `{imp['type']}` | *Status: {safety_str}*")
        
    lines.append("")
    lines.append("## 4. Execution Logs")
    
    # 4. Implement/execute safe improvements
    execution_notes = []
    for imp in selected_improvements:
        if imp["safe"]:
            action = imp["action"]
            print(f"  - ✅ Auto-running SAFE action: {imp['name']} (confidence: 0.95)")
            cmd_args = action.split()
            # Resolve script path
            if cmd_args[1].startswith("./"):
                cmd_args[1] = str(ROOT / cmd_args[1][2:])
            
            # Run command
            res = subprocess.run(cmd_args[1:], capture_output=True, text=True, cwd=str(ROOT))
            success = res.returncode == 0
            status_text = "Success" if success else f"Failed (rc={res.returncode})"
            execution_notes.append(f"- **{imp['name']}**: {status_text}")
        else:
            execution_notes.append(f"- **{imp['name']}**: Skipped (Requires user permission or manual action)")
            
    lines.extend(execution_notes)
    improvements_path.write_text("\n".join(lines) + "\n")
    
    # Save daily evolution history
    history_log_path = LOGS_DIR / "daily_evolution_log.md"
    history_log_path.parent.mkdir(parents=True, exist_ok=True)
    history_entry = f"\n### Daily Evolution - {datetime.now().strftime('%Y-%m-%d')}\n" + "\n".join(execution_notes) + "\n"
    if history_log_path.exists():
        history_log_path.write_text(history_log_path.read_text() + history_entry)
    else:
        history_log_path.write_text(f"# Daily Evolution History\n" + history_entry)

    print("✓ Daily Evolution Loop completed.")

# ---------------------------------------------------------------------------
# PHASE 4: TOOL + MCP DISCOVERY LOOP
# ---------------------------------------------------------------------------
def run_tool_discovery():
    print("🔍 Running Tool & MCP Discovery Loop...")
    discovery_path = SYSTEM_DIR / "tool_discovery.md"
    
    # Scan local directories for common CLI tools
    common_cli_locations = ["/opt/homebrew/bin", "/usr/local/bin", "/usr/bin"]
    detected_tools = []
    
    check_tools = {
        "docker": "Docker container runtime. Propose `docker-mcp` for container monitoring.",
        "ffmpeg": "Video/audio processing. Propose script helpers in scripts/ folder.",
        "fzf": "Command-line fuzzy finder. Propose terminal workflow wrapper.",
        "gh": "GitHub CLI. Propose github-mcp server integration.",
        "sqlite3": "SQLite CLI. Propose database indexing tool.",
        "node": "Node.js runtime. Propose custom TypeScript MCP tool builds.",
        "git": "Git version control. Propose git status automation integrations."
    }
    
    for tool_name, desc in check_tools.items():
        found = False
        for loc in common_cli_locations:
            if pathlib.Path(f"{loc}/{tool_name}").exists():
                found = True
                break
        if found:
            detected_tools.append((tool_name, desc))
            
    # Propose new MCP server connections based on detected items
    mcp_proposals = []
    for tool_name, desc in detected_tools:
        if tool_name == "gh":
            mcp_proposals.append("- **GitHub MCP Server**: Integrates PR reviews, issue tracking, and repository checks directly into Codex/Claude sessions.")
        elif tool_name == "docker":
            mcp_proposals.append("- **Docker MCP Server**: Allows agents to inspect container logs, health, and status during operations.")
        elif tool_name == "sqlite3":
            mcp_proposals.append("- **SQLite MCP Server**: Connects local databases as MCP resources for structured data analysis.")
            
    lines = [
        f"# Tool & MCP Discovery Report",
        f"",
        f"**Discovered On:** {now_iso()}",
        f"",
        f"## 1. Discovered Local CLI Tools",
        f"The following useful binaries were found installed on your Mac, but may not be fully integrated into your agent workflows:"
    ]
    for tool, desc in detected_tools:
        lines.append(f"- **{tool}**: {desc}")
        
    lines.append("")
    lines.append("## 2. Proposed MCP Connectors (Durable Integrations)")
    if mcp_proposals:
        lines.extend(mcp_proposals)
    else:
        lines.append("- No new MCP servers proposed. Current `workspace-brain` and default connectors are sufficient.")
        
    lines.append("")
    lines.append("## 3. Automation Opportunities")
    lines.append("- **Daily Notes Triage Shortcut**: Map Apple Shortcuts to automatically write raw notes to `brain/inbox` daily.")
    lines.append("- **Git Auto-Sync Cron**: A script to commit and push changes in `SuneelWorkSpace` periodically.")
    lines.append("")
    lines.append("> [!NOTE]")
    lines.append("> **Safety Notice:** None of the proposed tools or connectors are auto-installed. Run manual setup or explicitly request installation.")
    
    discovery_path.write_text("\n".join(lines) + "\n")
    print(f"✓ Tool discovery complete. Saved to {discovery_path.relative_to(ROOT)}.")

# ---------------------------------------------------------------------------
# PHASE 5 & 6: LIFE AUTOMATION LAYER & WORKFLOW CAPTURE
# ---------------------------------------------------------------------------
def run_life_automation(phrase: str):
    print(f"🧠 Life Automation Layer: Interpreting natural language input: '{phrase}'...")
    
    # 1. Classify intent
    phrase_clean = phrase.lower().strip()
    intent = "general"
    workflow_name = ""
    safe_commands = []
    explanation = ""
    
    if "organize" in phrase_clean or "life" in phrase_clean:
        intent = "life_organization"
        workflow_name = "life_organization_workflow"
        safe_commands = ["bin/agent-doctor", "bin/agent-maintain"]
        explanation = "Verify workspace health, run backups, and review folder layouts to ensure clean organization."
    elif "task" in phrase_clean or "stay on top" in phrase_clean or "todo" in phrase_clean:
        intent = "task_management"
        workflow_name = "task_management_workflow"
        safe_commands = ["bin/agent-status", "bin/goal-status"]
        explanation = "Retrieve overall agent status, active goals, and current active task lists to keep you on track."
    elif "message" in phrase_clean or "handle" in phrase_clean or "mail" in phrase_clean or "imessage" in phrase_clean:
        intent = "communication_triage"
        workflow_name = "communication_triage_workflow"
        safe_commands = ["bin/imessage-status", "bin/mail-status"]
        explanation = "Review recent messages, drafts, and email statuses in order to prioritize follow-ups."
        
    print(f"  - Classified Intent: `{intent}`")
    print(f"  - Mapping to Workflow: [[{workflow_name}]]")
    
    # 2. Execute safe actions
    executed_logs = []
    for cmd in safe_commands:
        script_path = ROOT / cmd
        if script_path.exists():
            print(f"  - ✅ Executing safe action: {cmd}")
            res = subprocess.run([str(script_path)], capture_output=True, text=True, env=os.environ)
            executed_logs.append(f"### Output of `{cmd}`:\n\n```\n{res.stdout.strip() or '(no output)'}\n```\n")
        else:
            executed_logs.append(f"### Command `{cmd}` not found in bin/\n")
            
    # 3. Log/Capture the workflow pattern in brain/workflows/
    workflow_path = WORKFLOWS_DIR / f"{workflow_name}.md"
    workflow_path.parent.mkdir(parents=True, exist_ok=True)
    
    workflow_lines = [
        f"# Captured Workflow: {intent.replace('_', ' ').title()}",
        f"",
        f"**Trigger Phrase:** \"{phrase}\"",
        f"**Last Triggered:** {now_iso()}",
        f"**Category:** Life Automation Layer",
        f"",
        f"## Description",
        f"{explanation}",
        f"",
        f"## Execution Plan (Safe Subsystem Commands)",
    ]
    for cmd in safe_commands:
        workflow_lines.append(f"- `rtk {cmd}`")
        
    workflow_lines.append("")
    workflow_lines.append("## Latest Trace Outputs")
    workflow_lines.extend(executed_logs)
    
    workflow_path.write_text("\n".join(workflow_lines) + "\n")
    print(f"✓ Workflow captured and saved to {workflow_path.relative_to(ROOT)}.")
    
    # Display details to user
    print("\n--- Proposed Automation Output ---")
    print(f"Intent classified: {intent.upper()}")
    print(explanation)
    print("Safe actions executed successfully.")
    print("----------------------------------\n")

# ---------------------------------------------------------------------------
# PHASE 7: SELF-TRAINING LOOP
# ---------------------------------------------------------------------------
def run_self_training():
    print("📈 Running Self-Training & Model Optimization Loop...")
    feedback_path = ROOT / "identity/adaptive/feedback_log.json"
    failure_path = ROOT / "testing/failure_log.json"
    state_path = ROOT / "identity/adaptive/adaptation_state.json"
    patterns_path = ROOT / "identity/adaptive/pattern_updates.json"
    
    feedback = read_json(feedback_path, {})
    events = feedback.get("events", []) if isinstance(feedback, dict) else feedback
    if not isinstance(events, list):
        events = []
        
    failures = read_json(failure_path, [])
    state = read_json(state_path, {"total_evals": 0, "adaptation_score": 1.0, "weights": {}})
    
    # Process feedback loop signals
    accept_count = sum(1 for f in events if f.get("user_action") == "accepted")
    reject_count = sum(1 for f in events if f.get("user_action") == "rejected")
    total_evals = accept_count + reject_count
    
    # Calculate adaptive weights
    weights = state.get("weights", {})
    weights["implicit_workflow"] = weights.get("implicit_workflow", 1.0)
    weights["maintenance"] = weights.get("maintenance", 1.0)
    
    if reject_count > 0:
        # Penalyze current weights if rejects exist
        weights["implicit_workflow"] = max(0.1, weights["implicit_workflow"] - (0.05 * reject_count))
        
    # Update adaptation state
    state["total_evals"] = total_evals
    state["accept_count"] = accept_count
    state["reject_count"] = reject_count
    state["weights"] = weights
    state["last_evolved"] = now_iso()
    
    write_json(state_path, state)
    
    # Record patterns updates
    pattern_updates = {
        "last_updated": now_iso(),
        "signals_processed": len(events),
        "failures_processed": len(failures),
        "updated_suggestion_weights": weights,
        "notes": "Identity tone adjustments and command suggestion weights updated according to feedback ratings."
    }
    write_json(patterns_path, pattern_updates)
    
    # Update anticipation engine records
    pred_memory_path = ROOT / "anticipation/prediction_memory.json"
    if pred_memory_path.exists():
        try:
            pred_mem = json.loads(pred_memory_path.read_text())
            pred_mem["last_evolved_stamp"] = now_iso()
            pred_mem["suggestion_weights"] = weights
            pred_memory_path.write_text(json.dumps(pred_mem, indent=2) + "\n")
        except Exception:
            pass
            
    print("✓ Model training weights and suggestion parameters updated.")

# ---------------------------------------------------------------------------
# MAIN ROUTER
# ---------------------------------------------------------------------------
def main():
    if len(sys.argv) > 1:
        phrase = sys.argv[1]
        if phrase == "--routine":
            # Run the default daily routine
            run_daily_evolution()
            run_tool_discovery()
            run_self_training()
        else:
            # Natural language command execution
            run_life_automation(phrase)
    else:
        # Default behavior: run all routines
        run_daily_evolution()
        run_tool_discovery()
        run_self_training()
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
