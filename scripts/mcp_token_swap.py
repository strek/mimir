"""
MCP Token Swap — writes ~/.cursor/mcp.json to point at the Mimir MCP server.

Three modes:

  --token <TOKEN> [--docker]        UAT / production path.
      Default (no --docker): local facade (.venv/bin/python -m mcp_integration.facade.server)
      With --docker:          Docker container (public Docker Hub image) — use this for UAT.

  --user <USERNAME>                 Dev / admin path.
      Local subprocess (manage.py mcp_server --user=<USERNAME>), bypasses HTTP auth.

After running, toggle the 'mimir' MCP server OFF → ON in Cursor Settings → MCP Servers
to reload Cursor with the updated config.

Usage:
    # UAT — Docker container with user token (production-identical code path):
    python scripts/mcp_token_swap.py --token <DRF_TOKEN> --docker

    # Dev — local facade (no Docker required):
    python scripts/mcp_token_swap.py --token <DRF_TOKEN> --server http://localhost:8000

    # Dev/admin — local subprocess (no token):
    python scripts/mcp_token_swap.py --user admin
"""
import argparse
import json
import logging
import pathlib

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
MCP_JSON_PATH = pathlib.Path.home() / ".cursor" / "mcp.json"
# Canonical public image (CI publishes to Docker Hub: featurefactory/mimir-mcp)
MCP_DOCKER_IMAGE = "featurefactory/mimir-mcp:latest"
DOCKER_IMAGE = MCP_DOCKER_IMAGE


def _docker_entry(token: str, server_url: str) -> dict:
    return {
        "command": "docker",
        "args": [
            "run", "--rm", "-i",
            "-e", f"BASE_URL={server_url}",
            "-e", f"TOKEN={token}",
            "-e", "MCP_TRANSPORT=stdio",
            DOCKER_IMAGE,
        ],
    }


def _facade_entry(token: str, server_url: str) -> dict:
    return {
        "command": str(REPO_ROOT / ".venv" / "bin" / "python"),
        "args": [
            "-m", "mcp_integration.facade.server",
            f"--token={token}",
            f"--server={server_url}",
        ],
    }


def _subprocess_entry(username: str) -> dict:
    return {
        "command": str(REPO_ROOT / ".venv" / "bin" / "python"),
        "args": [
            str(REPO_ROOT / "manage.py"),
            "mcp_server",
            f"--user={username}",
        ],
        "env": {
            "DJANGO_SETTINGS_MODULE": "mimir.settings",
            "PYTHONPATH": str(REPO_ROOT),
        },
    }


def _read_mcp_json() -> dict:
    if MCP_JSON_PATH.exists():
        return json.loads(MCP_JSON_PATH.read_text())
    return {"mcpServers": {}}


def _write_mcp_json(cfg: dict) -> None:
    MCP_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    MCP_JSON_PATH.write_text(json.dumps(cfg, indent=2) + "\n")
    logger.info(f"Wrote {MCP_JSON_PATH}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--token", help="DRF auth token")
    group.add_argument("--user", help="Django username (local subprocess, bypasses token auth)")
    p.add_argument("--docker", action="store_true",
                   help=f"Use Docker container ({DOCKER_IMAGE}). Requires --token. Use for UAT.")
    p.add_argument("--server", default="http://localhost:8000", help="Mimir base URL")
    args = p.parse_args()

    if args.docker and not args.token:
        p.error("--docker requires --token")

    cfg = _read_mcp_json()
    cfg.setdefault("mcpServers", {})

    if args.token and args.docker:
        entry = _docker_entry(args.token, args.server)
        mode = f"docker image={DOCKER_IMAGE} token=****{args.token[-6:]}"
    elif args.token:
        entry = _facade_entry(args.token, args.server)
        mode = f"facade token=****{args.token[-6:]}"
    else:
        entry = _subprocess_entry(args.user)
        mode = f"subprocess user={args.user}"

    cfg["mcpServers"]["mimir"] = entry
    _write_mcp_json(cfg)

    logger.info(f"mimir MCP server → {mode}")
    logger.info("")
    logger.info("ACTION REQUIRED: Toggle 'mimir' MCP server OFF → ON in Cursor Settings → MCP Servers")
    logger.info("Then smoke-check: CallMcpTool server='user-mimir' toolName='list_playbooks' arguments={}")


if __name__ == "__main__":
    main()
