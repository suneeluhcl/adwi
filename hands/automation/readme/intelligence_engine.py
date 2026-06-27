#!/usr/bin/env python3
"""
README Intelligence Engine — analyzes every workspace folder and produces
structured JSON describing purpose, contents, dependencies, and gaps.
"""
import ast
import json
import os
import subprocess
from pathlib import Path
from typing import Optional

WORKSPACE = Path(subprocess.check_output(
    ["git", "rev-parse", "--show-toplevel"], text=True,
    cwd=os.path.dirname(os.path.abspath(__file__))
).strip())

IGNORED_DIRS = {".git", "node_modules", ".venv", "__pycache__", "logs", ".DS_Store", "nerve_inbox"}
IGNORED_EXTS = {".log", ".pyc", ".pyo", ".DS_Store"}

ORGANS = {
    "brain", "heart", "eyes", "ears", "nervous", "skeleton",
    "blood", "hands", "mouth", "dna", "lab", "spine"
}

ORGAN_PURPOSE = {
    "brain": "Vector memory search, context anticipation, and research aggregation",
    "heart": "Goal scheduling, task queue management, and model fallback routing",
    "eyes": "Web dashboard serving, visual monitoring, and screenshot healing",
    "ears": "External RSS monitoring, GitHub event watching, and morning briefing build",
    "nervous": "Event propagation, MCP server connections, and nerve routing",
    "skeleton": "Agent rules enforcement, safety gate checks, and shared instructions",
    "blood": "Telemetry logging, SQLite database management, and anomaly detection",
    "hands": "Script execution, LaunchD automation, and CI runner",
    "mouth": "Communication dispatch, Mail and iMessage delivery",
    "dna": "Identity prompt management and adapt loop scoring",
    "lab": "Autolab experiment execution and self-evolution cycles",
    "spine": "Health state tracking and workspace index management",
}

ORGAN_RESPONSIBILITIES = {
    "brain": ["Vector memory search", "Context anticipation", "Research aggregation"],
    "heart": ["Goal scheduling", "Task queue management", "Model fallback routing"],
    "eyes": ["Web dashboard serving", "Visual monitoring", "Screenshot healing"],
    "ears": ["External RSS monitoring", "GitHub event watching", "Morning briefing build"],
    "nervous": ["Event propagation", "MCP server connections", "Nerve routing"],
    "skeleton": ["Agent rules enforcement", "Safety gate checks", "Shared instructions"],
    "blood": ["Telemetry logging", "SQLite database management", "Anomaly detection"],
    "hands": ["Script execution", "LaunchD automation", "CI runner"],
    "mouth": ["Communication dispatch", "Mail delivery", "iMessage delivery"],
    "dna": ["Identity prompt management", "Adapt loop scoring"],
    "lab": ["Autolab experiment execution", "Self-evolution cycles"],
    "spine": ["Health state tracking", "Workspace index management"],
}


def _classify_organ(folder_path: Path) -> Optional[str]:
    try:
        rel = folder_path.relative_to(WORKSPACE)
        parts = rel.parts
        if parts and parts[0] in ORGANS:
            return parts[0]
    except ValueError:
        pass
    return None


def _scan_python_imports(py_file: Path) -> list:
    try:
        tree = ast.parse(py_file.read_text(errors="ignore"))
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(n.name for n in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.append(node.module)
        return imports
    except Exception:
        return []


def _scan_json_keys(json_file: Path) -> list:
    try:
        data = json.loads(json_file.read_text(errors="ignore"))
        if isinstance(data, dict):
            return list(data.keys())[:20]
    except Exception:
        pass
    return []


def _infer_purpose(folder_path: Path, organ: Optional[str]) -> str:
    if organ and organ in ORGAN_PURPOSE:
        return ORGAN_PURPOSE[organ]
    name = folder_path.name.lower()
    if "test" in name:
        return "Test suite"
    if "server" in name or "api" in name:
        return "API/server component"
    if "router" in name or "dispatch" in name:
        return "Routing and dispatch layer"
    if "hook" in name:
        return "Automation hooks"
    if "config" in name or "settings" in name:
        return "Configuration management"
    if "script" in name or "bin" in name:
        return "Executable scripts and CLI tools"
    return "Workspace component"


def _detect_gaps(files: list, subdirs: list) -> list:
    gaps = []
    all_names = [f.lower() for f in files + subdirs]
    if not any("test" in n for n in all_names):
        gaps.append("No test coverage detected")
    if not any(n == "readme.md" for n in all_names):
        gaps.append("Missing README.md")
    if not any(n.endswith(".py") or n.endswith(".sh") for n in files):
        gaps.append("No executable code found")
    return gaps


def _detect_capabilities(files: list, subdirs: list, imports: list) -> list:
    caps = []
    all_names = [f.lower() for f in files + subdirs]
    if any("api" in n or "server" in n for n in all_names):
        caps.append("HTTP API")
    if any("db" in n or "sqlite" in n for n in all_names + imports):
        caps.append("Database storage")
    if any("schedule" in n or "cron" in n or "plist" in n for n in all_names):
        caps.append("Scheduled automation")
    if any("claude" in i or "anthropic" in i for i in imports):
        caps.append("Claude AI integration")
    if any("webhook" in n or "dispatch" in n for n in all_names):
        caps.append("Event dispatch")
    if any("test" in n for n in all_names):
        caps.append("Test suite")
    return caps


def analyze_folder(folder_path: str) -> dict:
    path = Path(folder_path).resolve()
    if not path.is_dir():
        return {}

    files = []
    subdirs = []
    all_imports = []
    json_structures = []
    script_names = []
    config_files = []

    try:
        for item in sorted(path.iterdir()):
            if item.name in IGNORED_DIRS or item.suffix in IGNORED_EXTS:
                continue
            if item.is_dir():
                subdirs.append(item.name)
            else:
                files.append(item.name)
                if item.suffix == ".py":
                    imports = _scan_python_imports(item)
                    all_imports.extend(imports)
                    try:
                        if "__main__" in item.read_text(errors="ignore"):
                            script_names.append(item.name)
                    except Exception:
                        pass
                elif item.suffix == ".json":
                    json_structures.append({item.name: _scan_json_keys(item)})
                    config_files.append(item.name)
                elif item.suffix in (".yaml", ".yml", ".toml", ".sh", ".plist"):
                    config_files.append(item.name)
    except PermissionError:
        pass

    workspace_refs = sorted({
        imp.split(".")[0] for imp in all_imports
        if imp.split(".")[0] in ORGANS
    })

    organ = _classify_organ(path)
    purpose = _infer_purpose(path, organ)

    try:
        rel_path = str(path.relative_to(WORKSPACE))
    except ValueError:
        rel_path = str(path)

    readme_path = path / "README.md"
    if readme_path.exists():
        try:
            content = readme_path.read_text(errors="ignore")
            existing_readme = {
                "exists": True,
                "lines": len(content.splitlines()),
                "has_manual_sections": "<!-- MANUAL SECTION START -->" in content,
            }
        except Exception:
            existing_readme = {"exists": True, "lines": 0, "has_manual_sections": False}
    else:
        existing_readme = {"exists": False}

    return {
        "path": rel_path,
        "name": path.name,
        "organ": organ,
        "purpose": purpose,
        "files": files,
        "subdirectories": subdirs,
        "python_imports": sorted(set(all_imports))[:30],
        "workspace_references": workspace_refs,
        "config_files": config_files,
        "json_structures": json_structures[:5],
        "script_names": script_names,
        "file_count": len(files),
        "subdir_count": len(subdirs),
        "existing_readme": existing_readme,
        "gaps": _detect_gaps(files, subdirs),
        "capabilities": _detect_capabilities(files, subdirs, all_imports),
    }


def analyze_workspace(workspace_root: Optional[str] = None) -> list:
    root = Path(workspace_root) if workspace_root else WORKSPACE
    analyses = []

    for dirpath, dirnames, _ in os.walk(root):
        dirnames[:] = [d for d in sorted(dirnames) if d not in IGNORED_DIRS]
        path = Path(dirpath)
        try:
            rel = path.relative_to(root)
        except ValueError:
            continue
        if rel == Path(".") or len(rel.parts) > 3:
            continue
        result = analyze_folder(str(path))
        if result:
            analyses.append(result)

    return sorted(analyses, key=lambda x: x["path"])


def build_dependency_map(analyses: list) -> dict:
    dep_map = {}

    for analysis in analyses:
        path = analysis["path"]
        deps = []
        for ref in analysis.get("workspace_references", []):
            if ref in ORGANS and not path.startswith(ref + "/") and ref != path:
                deps.append(ref)
        dep_map[path] = {
            "dependencies": sorted(set(deps)),
            "reverse_dependencies": [],
            "organ": analysis.get("organ"),
        }

    # build reverse deps
    for path, data in dep_map.items():
        for dep in data["dependencies"]:
            for other_path in dep_map:
                if other_path.startswith(dep + "/") or other_path == dep:
                    if path not in dep_map[other_path]["reverse_dependencies"]:
                        dep_map[other_path]["reverse_dependencies"].append(path)

    return dep_map


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Analyze workspace folders")
    parser.add_argument("folder", nargs="?", help="Single folder to analyze (default: all)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    if args.folder:
        result = analyze_folder(args.folder)
        print(json.dumps(result, indent=2))
    else:
        results = analyze_workspace()
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(f"Analyzed {len(results)} folders")
            for r in results:
                print(f"  {r['path']} ({r['file_count']} files, organ={r['organ']})")
