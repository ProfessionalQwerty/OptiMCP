"""CLI for the OptiMCP verification daemon and ruleset helpers."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional

from optimcp.daemon.auth import AuthError, is_loopback_host
from optimcp.monitor.models import RulesetRecord
from optimcp.monitor.service import MonitorService
from optimcp.monitor.store import MonitorStore, default_home


def _load_ruleset_file(path: Path) -> RulesetRecord:
    data = MonitorStore._parse_mapping(path.read_text(encoding="utf-8"))
    if not data:
        raise SystemExit(f"ruleset file must be a mapping: {path}")
    if "id" not in data:
        data["id"] = path.stem
    return RulesetRecord.model_validate(data)


def cmd_daemon(args: argparse.Namespace) -> None:
    store = MonitorStore(home=Path(args.home) if args.home else None)
    config = store.load_config()
    host = args.host or config.host
    port = args.port or config.port
    allow = (
        True
        if args.allow_unauthenticated_localhost
        else config.allow_unauthenticated_localhost
    )
    if args.token:
        os.environ["OPTIMCP_DAEMON_TOKEN"] = args.token
        config = config.model_copy(update={"daemon_token": args.token})
        store.save_config(config)

    try:
        from optimcp.daemon.app import create_app
    except ImportError as exc:
        raise SystemExit(
            "Daemon extras required. Install with: pip install 'optimcp[daemon]'"
        ) from exc

    try:
        app = create_app(
            service=MonitorService(store=store),
            config=config,
            host=host,
            allow_unauthenticated_localhost=allow,
        )
    except AuthError as exc:
        raise SystemExit(str(exc.message)) from exc

    if not is_loopback_host(host) and allow:
        print(
            "warning: --allow-unauthenticated-localhost is ignored for "
            f"non-loopback host {host!r}; token auth is required.",
            file=sys.stderr,
        )

    try:
        import uvicorn
    except ImportError as exc:
        raise SystemExit(
            "uvicorn is required. Install with: pip install 'optimcp[daemon]'"
        ) from exc

    print(f"OptiMCP daemon on http://{host}:{port}  (home={store.home})", flush=True)
    uvicorn.run(app, host=host, port=int(port), log_level="info")


def cmd_register(args: argparse.Namespace) -> None:
    store = MonitorStore(home=Path(args.home) if args.home else None)
    record = _load_ruleset_file(Path(args.file))
    if args.id:
        record = record.model_copy(update={"id": args.id})
    if args.policy:
        record = record.model_copy(update={"policy": args.policy})
    saved = MonitorService(store=store).register_ruleset(record)
    print(json.dumps(saved.model_dump(mode="json"), indent=2))


def cmd_list(args: argparse.Namespace) -> None:
    store = MonitorStore(home=Path(args.home) if args.home else None)
    rows = MonitorService(store=store).list_rulesets()
    print(json.dumps([r.model_dump(mode="json") for r in rows], indent=2))


def _add_serve_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--host", default=None)
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--token", default=None, help="Set OPTIMCP_DAEMON_TOKEN for this process")
    parser.add_argument(
        "--allow-unauthenticated-localhost",
        action="store_true",
        help="Allow unauthenticated /v1 when binding loopback AND no token is set",
    )
    parser.set_defaults(func=cmd_daemon)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="optimcp-daemon", description="OptiMCP verification daemon")
    p.add_argument(
        "--home",
        default=os.getenv("OPTIMCP_HOME"),
        help=f"Data directory (default: {default_home()})",
    )
    sub = p.add_subparsers(dest="command", required=True)

    _add_serve_args(sub.add_parser("serve", help="Run the HTTP daemon"))
    _add_serve_args(sub.add_parser("daemon", help="Alias for serve"))

    r = sub.add_parser("register", help="Register a ruleset from a YAML/JSON file")
    r.add_argument("file", help="Path to ruleset file")
    r.add_argument("--id", default=None)
    r.add_argument("--policy", choices=["observe", "refuse"], default=None)
    r.set_defaults(func=cmd_register)

    l = sub.add_parser("list", help="List registered rulesets")
    l.set_defaults(func=cmd_list)

    return p


def main(argv: Optional[list] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
