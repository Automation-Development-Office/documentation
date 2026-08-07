#!/usr/bin/env python3
"""Generate release-status.md, versions.json, and auto-fill deployments.yml."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    print("PyYAML is required: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]
STATUS_DIR = ROOT / "release-status"
PRODUCTS_PATH = STATUS_DIR / "products.yml"
DEPLOYMENTS_PATH = STATUS_DIR / "deployments.yml"
OUT_MD = STATUS_DIR / "release-status.md"
OUT_JSON = STATUS_DIR / "versions.json"

API = "https://api.github.com"
GHCR = "https://ghcr.io"
USER_AGENT = "ado-release-status/1.0"
SEMVER_TAG_RE = re.compile(
    r"^v?(?P<version>\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?)$"
)
NON_VERSION_TAGS = frozenset({"latest", "stable", "prod", "stage", "dev", "v1"})


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_yaml(path: Path) -> Any:
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def dump_deployments(path: Path, data: dict[str, Any], generated_at: str) -> None:
    header = (
        "# Deployed version pins — mostly auto-populated by the nightly release-status job.\n"
        "#\n"
        f"# Last discovery: {generated_at}\n"
        "# Sources are defined under deploy_channels in products.yml (GHCR :latest,\n"
        "# GitHub Releases, Galaxy, etc.).\n"
        "#\n"
        "# To pin an environment by hand and stop overwrites, set manual: true:\n"
        "#\n"
        "#   ado-ee:\n"
        "#     prod:\n"
        "#       manual: true\n"
        "#       version: \"1.0.1\"\n"
        "#       updated_at: \"2026-08-01T12:00:00Z\"\n"
        "#       notes: Held back for soak testing\n"
        "#\n"
    )
    body = yaml.safe_dump(data, default_flow_style=False, sort_keys=False)
    path.write_text(header + body, encoding="utf-8")


def http_json(url: str, headers: dict[str, str], method: str = "GET") -> tuple[Any, dict[str, str]]:
    req = urllib.request.Request(url, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read()
            payload = json.loads(raw.decode("utf-8")) if raw else None
            return payload, {k.lower(): v for k, v in resp.headers.items()}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} for {url}: {body[:500]}") from exc


def gh_request(url: str, token: str | None) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": USER_AGENT,
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data, _ = http_json(url, headers)
    return data


def fetch_releases(org: str, repo: str, token: str | None, per_page: int = 30) -> list[dict]:
    url = f"{API}/repos/{org}/{repo}/releases?per_page={per_page}"
    data = gh_request(url, token)
    if not isinstance(data, list):
        return []
    return [r for r in data if not r.get("draft")]


def pick_latest(releases: list[dict], *, prerelease: bool | None) -> dict | None:
    for rel in releases:
        is_pre = bool(rel.get("prerelease"))
        if prerelease is None or is_pre is prerelease:
            return rel
    return None


def release_url(org: str, repo: str, tag: str) -> str:
    return f"https://github.com/{org}/{repo}/releases/tag/{tag}"


def artifact_for(product: dict, tag: str | None) -> str | None:
    if not tag:
        return None
    kind = product.get("kind")
    if kind == "ansible_collection" and product.get("galaxy"):
        return f"{product['galaxy']}:{tag}"
    if kind == "container" and product.get("image"):
        return f"{product['image']}:{tag}"
    return tag


def parse_ghcr_image(image: str) -> tuple[str, str]:
    """Return (registry_host, repository_path) for a ghcr.io image ref without tag."""
    image = image.removeprefix("https://").removeprefix("http://")
    if image.startswith("ghcr.io/"):
        return "ghcr.io", image[len("ghcr.io/") :]
    raise ValueError(f"Only ghcr.io images are supported for auto-discovery, got: {image}")


def ghcr_registry_token(gh_token: str | None, repository: str) -> str:
    headers = {"User-Agent": USER_AGENT}
    if gh_token:
        headers["Authorization"] = f"Bearer {gh_token}"
    url = f"{GHCR}/token?service=ghcr.io&scope=repository:{repository}:pull"
    data, _ = http_json(url, headers)
    token = data.get("token") if isinstance(data, dict) else None
    if not token:
        raise RuntimeError(f"Could not obtain GHCR pull token for {repository}")
    return token


def ghcr_list_tags(repository: str, registry_token: str) -> list[str]:
    headers = {
        "Authorization": f"Bearer {registry_token}",
        "User-Agent": USER_AGENT,
    }
    data, _ = http_json(f"{GHCR}/v2/{repository}/tags/list", headers)
    return list(data.get("tags") or []) if isinstance(data, dict) else []


def ghcr_manifest_digest(repository: str, tag: str, registry_token: str) -> str:
    headers = {
        "Authorization": f"Bearer {registry_token}",
        "User-Agent": USER_AGENT,
        "Accept": ",".join(
            [
                "application/vnd.oci.image.index.v1+json",
                "application/vnd.docker.distribution.manifest.list.v2+json",
                "application/vnd.oci.image.manifest.v1+json",
                "application/vnd.docker.distribution.manifest.v2+json",
            ]
        ),
    }
    _, response_headers = http_json(
        f"{GHCR}/v2/{repository}/manifests/{tag}", headers
    )
    digest = response_headers.get("docker-content-digest")
    if not digest:
        raise RuntimeError(f"No digest returned for {repository}:{tag}")
    return digest


def is_version_tag(tag: str) -> bool:
    if tag in NON_VERSION_TAGS or tag.startswith("dev-"):
        return False
    return bool(SEMVER_TAG_RE.match(tag))


def is_stable_version_tag(tag: str) -> bool:
    match = SEMVER_TAG_RE.match(tag)
    if not match:
        return False
    version = match.group("version")
    return "-" not in version.split("+", 1)[0]


def resolve_version_for_digest(
    repository: str,
    target_digest: str,
    tags: list[str],
    registry_token: str,
    *,
    prefer_stable: bool,
) -> str | None:
    candidates = [t for t in tags if is_version_tag(t)]
    if prefer_stable:
        ordered = [t for t in candidates if is_stable_version_tag(t)] + [
            t for t in candidates if not is_stable_version_tag(t)
        ]
    else:
        ordered = [t for t in candidates if not is_stable_version_tag(t)] + [
            t for t in candidates if is_stable_version_tag(t)
        ]

    matches: list[str] = []
    for tag in ordered:
        try:
            digest = ghcr_manifest_digest(repository, tag, registry_token)
        except RuntimeError:
            continue
        if digest == target_digest:
            matches.append(tag)
    if not matches:
        return None
    # Prefer the first match in preference order.
    return matches[0]


def discover_ghcr(product: dict, channel: dict, token: str | None) -> dict[str, Any]:
    image = product.get("image")
    if not image:
        raise RuntimeError(f"{product['id']}: ghcr channel requires product.image")
    _, repository = parse_ghcr_image(image)
    tag = channel.get("tag") or "latest"
    registry_token = ghcr_registry_token(token, repository)
    tags = ghcr_list_tags(repository, registry_token)
    if tag not in tags:
        return {
            "version": None,
            "updated_at": None,
            "source": f"ghcr:{tag}",
            "notes": f"Image tag `{tag}` not present in GHCR.",
        }
    digest = ghcr_manifest_digest(repository, tag, registry_token)
    version = resolve_version_for_digest(
        repository,
        digest,
        tags,
        registry_token,
        prefer_stable=True,
    )
    return {
        "version": version,
        "updated_at": utc_now() if version else None,
        "source": f"ghcr:{tag}",
        "digest": digest,
        "notes": (
            f"Resolved `{image}:{tag}` to `{version}` by digest."
            if version
            else f"Found `{image}:{tag}` but no matching version tag for digest."
        ),
    }


def discover_ghcr_prerelease(
    product: dict,
    releases: list[dict],
    token: str | None,
) -> dict[str, Any]:
    image = product.get("image")
    if not image:
        raise RuntimeError(f"{product['id']}: ghcr_prerelease requires product.image")
    _, repository = parse_ghcr_image(image)
    registry_token = ghcr_registry_token(token, repository)
    tags = set(ghcr_list_tags(repository, registry_token))
    for rel in releases:
        if not rel.get("prerelease"):
            continue
        tag = rel.get("tag_name")
        if not tag or tag not in tags:
            continue
        digest = ghcr_manifest_digest(repository, tag, registry_token)
        return {
            "version": tag,
            "updated_at": rel.get("published_at") or utc_now(),
            "source": "ghcr_prerelease",
            "digest": digest,
            "notes": f"Newest GitHub prerelease present in GHCR (`{image}:{tag}`).",
        }
    return {
        "version": None,
        "updated_at": None,
        "source": "ghcr_prerelease",
        "notes": "No GitHub prerelease tag found in GHCR.",
    }


def discover_github_release(releases: list[dict], *, prerelease: bool) -> dict[str, Any]:
    rel = pick_latest(releases, prerelease=prerelease)
    if not rel:
        return {
            "version": None,
            "updated_at": None,
            "source": "github_release",
            "notes": (
                "No prerelease GitHub Release found."
                if prerelease
                else "No stable GitHub Release found."
            ),
        }
    kind = "prerelease" if prerelease else "stable"
    return {
        "version": rel.get("tag_name"),
        "updated_at": rel.get("published_at") or utc_now(),
        "source": f"github_release:{kind}",
        "notes": (
            f"From GitHub Releases ({kind}). Not a runtime cluster pin; "
            "replace with Galaxy/Hub or cluster discovery when available."
        ),
    }


def discover_galaxy(product: dict) -> dict[str, Any]:
    galaxy = product.get("galaxy")
    if not galaxy or "." not in galaxy:
        raise RuntimeError(f"{product['id']}: galaxy channel requires product.galaxy like infra.ado")
    namespace, name = galaxy.split(".", 1)
    url = (
        "https://galaxy.ansible.com/api/v3/plugin/ansible/content/published/"
        f"collections/index/{namespace}/{name}/versions/?limit=1"
    )
    try:
        data, _ = http_json(url, {"User-Agent": USER_AGENT, "Accept": "application/json"})
    except RuntimeError as exc:
        return {
            "version": None,
            "updated_at": None,
            "source": "galaxy",
            "notes": f"Galaxy lookup failed: {exc}",
        }
    items = (data or {}).get("data") or []
    if not items:
        return {
            "version": None,
            "updated_at": None,
            "source": "galaxy",
            "notes": f"No published versions for {galaxy} on Ansible Galaxy.",
        }
    item = items[0]
    return {
        "version": item.get("version"),
        "updated_at": item.get("created_at") or utc_now(),
        "source": "galaxy",
        "notes": f"Newest version on Ansible Galaxy for {galaxy}.",
    }


def discover_channel(
    product: dict,
    env_name: str,
    channel: dict,
    releases: list[dict],
    token: str | None,
) -> dict[str, Any]:
    channel_type = channel.get("type")
    if channel_type == "ghcr":
        return discover_ghcr(product, channel, token)
    if channel_type == "ghcr_prerelease":
        return discover_ghcr_prerelease(product, releases, token)
    if channel_type == "github_release":
        return discover_github_release(
            releases, prerelease=bool(channel.get("prerelease", False))
        )
    if channel_type == "galaxy":
        return discover_galaxy(product)
    if channel_type == "manual":
        return {
            "version": None,
            "updated_at": None,
            "source": "manual",
            "manual": True,
            "notes": f"{env_name}: manual-only channel; set version in deployments.yml.",
        }
    raise RuntimeError(
        f"{product['id']}.{env_name}: unsupported deploy channel type '{channel_type}'"
    )


def merge_discovered(
    existing: dict[str, Any] | None,
    discovered: dict[str, Any],
) -> dict[str, Any]:
    existing = existing if isinstance(existing, dict) else {}
    if existing.get("manual") is True:
        # Keep human pins; still record that discovery was skipped.
        pin = dict(existing)
        pin.setdefault("source", "manual")
        pin["notes"] = existing.get("notes") or "manual: true — nightly discovery skipped."
        return pin

    pin = {
        "version": discovered.get("version"),
        "updated_at": discovered.get("updated_at"),
        "source": discovered.get("source"),
    }
    if discovered.get("digest"):
        pin["digest"] = discovered["digest"]
    if discovered.get("notes"):
        pin["notes"] = discovered["notes"]
    if discovered.get("manual") is True:
        pin["manual"] = True
    return pin


def discover_deployments(
    products_cfg: list[dict],
    existing: dict[str, Any],
    release_cache: dict[str, list[dict]],
    token: str | None,
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for product in products_cfg:
        pid = product["id"]
        channels = product.get("deploy_channels") or {}
        if not channels:
            # Preserve any existing pins when no channels are configured.
            if pid in existing:
                result[pid] = existing[pid]
            continue
        product_pins: dict[str, Any] = {}
        releases = release_cache[pid]
        for env_name, channel in channels.items():
            try:
                discovered = discover_channel(
                    product, env_name, channel, releases, token
                )
            except Exception as exc:  # noqa: BLE001 - keep board generation alive
                discovered = {
                    "version": None,
                    "updated_at": None,
                    "source": channel.get("type"),
                    "notes": f"Discovery error: {exc}",
                }
                print(f"WARN {pid}.{env_name}: {exc}", file=sys.stderr)
            previous = (existing.get(pid) or {}).get(env_name)
            product_pins[env_name] = merge_discovered(previous, discovered)
            version = product_pins[env_name].get("version") or "(none)"
            print(f"  deploy {pid}.{env_name}: {version} [{product_pins[env_name].get('source')}]")
        result[pid] = product_pins
    return result


def fmt_dt(value: str | None) -> str:
    if not value:
        return "—"
    return value[:10]


def cell(value: str | None) -> str:
    return value if value else "—"


def md_link(label: str, url: str | None) -> str:
    if not url:
        return cell(label)
    return f"[{label}]({url})"


def build_product_row(
    org: str,
    product: dict,
    releases: list[dict],
    deployments: dict,
) -> dict:
    stable = pick_latest(releases, prerelease=False)
    prerelease = pick_latest(releases, prerelease=True)

    stable_tag = stable.get("tag_name") if stable else None
    pre_tag = prerelease.get("tag_name") if prerelease else None

    env_pins = deployments.get(product["id"]) or {}
    deployed: dict[str, Any] = {}
    for env_name, pin in env_pins.items():
        if not isinstance(pin, dict):
            continue
        deployed[env_name] = {
            "version": pin.get("version"),
            "updated_at": pin.get("updated_at"),
            "notes": pin.get("notes"),
            "source": pin.get("source"),
            "digest": pin.get("digest"),
            "manual": pin.get("manual"),
        }

    return {
        "id": product["id"],
        "name": product["name"],
        "repo": product["repo"],
        "kind": product.get("kind"),
        "repo_url": f"https://github.com/{org}/{product['repo']}",
        "latest_stable": {
            "tag": stable_tag,
            "published_at": stable.get("published_at") if stable else None,
            "url": release_url(org, product["repo"], stable_tag) if stable_tag else None,
            "name": stable.get("name") if stable else None,
            "artifact": artifact_for(product, stable_tag),
        },
        "latest_prerelease": {
            "tag": pre_tag,
            "published_at": prerelease.get("published_at") if prerelease else None,
            "url": release_url(org, product["repo"], pre_tag) if pre_tag else None,
            "name": prerelease.get("name") if prerelease else None,
            "artifact": artifact_for(product, pre_tag),
        },
        "deployed": deployed,
        "notes": product.get("notes") or "",
    }


def render_markdown(org: str, generated_at: str, products: list[dict], env_names: list[str]) -> str:
    lines: list[str] = [
        "# ADO release and deployment status",
        "",
        f"_Generated automatically for [`{org}`](https://github.com/{org}). "
        f"Last refresh: `{generated_at}`._",
        "",
        "This page tracks **released** versions (GitHub Releases) and **deployed / "
        "published channel** versions from [`deployments.yml`](deployments.yml), which "
        "the nightly workflow auto-fills from GHCR and configured sources.",
        "",
        "## Product board",
        "",
    ]

    headers = [
        "Product",
        "Latest stable",
        "Published",
        "Artifact",
        "Latest prerelease",
    ]
    headers.extend(f"Deployed ({env})" for env in env_names)
    headers.append("Notes")

    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join("---" for _ in headers) + " |")

    for row in products:
        stable = row["latest_stable"]
        pre = row["latest_prerelease"]
        product_cell = md_link(row["name"], row["repo_url"])
        stable_cell = md_link(stable["tag"], stable["url"]) if stable["tag"] else "—"
        pre_cell = md_link(pre["tag"], pre["url"]) if pre["tag"] else "—"
        cells = [
            product_cell,
            stable_cell,
            fmt_dt(stable.get("published_at")),
            cell(stable.get("artifact")),
            pre_cell,
        ]
        for env in env_names:
            pin = (row.get("deployed") or {}).get(env) or {}
            ver = pin.get("version")
            if ver:
                updated = fmt_dt(pin.get("updated_at"))
                source = pin.get("source")
                label = f"`{ver}`"
                if updated != "—":
                    label += f" ({updated})"
                if source:
                    label += f" · _{source}_"
                cells.append(label)
            else:
                cells.append("—")
        notes = row.get("notes") or ""
        cells.append(notes.replace("|", "\\|"))
        lines.append("| " + " | ".join(cells) + " |")

    lines.extend(
        [
            "",
            "## How this is maintained",
            "",
            "| Piece | Role |",
            "| --- | --- |",
            "| [`products.yml`](products.yml) | Repos on the board + `deploy_channels` discovery rules |",
            "| [`deployments.yml`](deployments.yml) | Auto-filled channel pins (override with `manual: true`) |",
            "| [`versions.json`](versions.json) | Machine-readable snapshot |",
            "| [`../scripts/generate_release_status.py`](../scripts/generate_release_status.py) | Discovers pins and regenerates this page |",
            "| `.github/workflows/update-release-status.yml` | Nightly + on-demand refresh |",
            "",
            "### What “deployed” means today",
            "",
            "| Product | `prod` source | `stage` source |",
            "| --- | --- | --- |",
            "| infra.ado | Newest stable GitHub Release (Galaxy not publicly queryable yet) | Newest GitHub prerelease |",
            "| ado-ee | GHCR `:latest` resolved to a version tag by digest | Newest prerelease tag present in GHCR |",
            "| ado-preflight-ui | GHCR `:latest` resolved to a version tag by digest | Newest prerelease tag present in GHCR |",
            "",
            "This is a **published artifact channel**, not a live OpenShift/AAP inventory. "
            "When cluster or Automation Hub APIs are available, add a channel type and "
            "point `deploy_channels` at them.",
            "",
            "### Refresh locally",
            "",
            "```bash",
            "pip install pyyaml",
            "export GITHUB_TOKEN=$(gh auth token)  # needed for GHCR pull on private packages",
            "python3 scripts/generate_release_status.py",
            "```",
            "",
            "### Hold a pin manually",
            "",
            "```yaml",
            "ado-ee:",
            "  prod:",
            "    manual: true",
            "    version: \"1.0.1\"",
            "    updated_at: \"2026-08-01T12:00:00Z\"",
            "    notes: Held back for soak testing",
            "```",
            "",
            "## Source repositories",
            "",
        ]
    )

    for row in products:
        lines.append(
            f"- [{row['name']}]({row['repo_url']}) — "
            f"[releases]({row['repo_url']}/releases)"
        )

    lines.append("")
    return "\n".join(lines)


def collect_env_names(deployments: dict, product_ids: list[str]) -> list[str]:
    order = ["prod", "stage", "dev"]
    seen: list[str] = []
    for env in order:
        for pid in product_ids:
            pins = deployments.get(pid) or {}
            if env in pins and env not in seen:
                seen.append(env)
    for pid in product_ids:
        for env in deployments.get(pid) or {}:
            if env not in seen:
                seen.append(env)
    return seen or ["prod"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--no-discover",
        action="store_true",
        help="Do not refresh deployments.yml from deploy_channels; use the file as-is.",
    )
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    products_doc = load_yaml(PRODUCTS_PATH)
    existing_deployments = load_yaml(DEPLOYMENTS_PATH) or {}

    org = products_doc["organization"]
    products_cfg = products_doc["products"]
    generated_at = utc_now()

    release_cache: dict[str, list[dict]] = {}
    for product in products_cfg:
        release_cache[product["id"]] = fetch_releases(org, product["repo"], token)

    if args.no_discover:
        deployments = existing_deployments
        print("Skipping deploy-channel discovery (--no-discover).")
    else:
        print("Discovering deployment channels...")
        deployments = discover_deployments(
            products_cfg, existing_deployments, release_cache, token
        )
        dump_deployments(DEPLOYMENTS_PATH, deployments, generated_at)
        print(f"Wrote {DEPLOYMENTS_PATH.relative_to(ROOT)}")

    rows: list[dict] = []
    for product in products_cfg:
        rows.append(
            build_product_row(org, product, release_cache[product["id"]], deployments)
        )

    env_names = collect_env_names(deployments, [p["id"] for p in products_cfg])
    payload = {
        "organization": org,
        "generated_at": generated_at,
        "products": rows,
        "environments": env_names,
    }

    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(org, generated_at, rows, env_names), encoding="utf-8")

    print(f"Wrote {OUT_MD.relative_to(ROOT)}")
    print(f"Wrote {OUT_JSON.relative_to(ROOT)}")
    for row in rows:
        tag = row["latest_stable"]["tag"] or "(none)"
        print(f"  {row['id']}: stable={tag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
