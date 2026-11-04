"""Cloud-only transport preflight. Keep proxy/TLS verification; never print secrets.

The policy file is a startup snapshot. Use the platform environment_status tool
for current configuration and --probe to establish the actual transport result.
An HTTP response from the origin does not certify API authorization or TTS.
"""
import argparse
import concurrent.futures
import datetime
import json
import pathlib
import subprocess
import sys
from urllib.parse import urlsplit

TARGETS = {
    'package_registry_control': 'https://registry.npmjs.org/',
    'github_pages_api': 'https://api.github.com/repos/angusQAQ/zhi-you-cai-game/pages',
    'published_site': 'https://angusqaq.github.io/zhi-you-cai-game/',
    'cuhk_dictionary': 'https://humanum.arts.cuhk.edu.hk/Lexis/lexi-can/',
    'cantonese_voice': 'https://speech.platform.bing.com/consumer/speech/synthesize/readaloud/edge/v1',
}


def probe(item):
    name, url = item
    result = subprocess.run(
        ['curl', '--silent', '--show-error', '--head', '--max-time', '15',
         '--output', '/dev/null', '--write-out',
         '%{http_connect} %{http_code} %{ssl_verify_result}', url],
        text=True, capture_output=True,
    )
    fields = result.stdout.strip().split()
    connect, origin, tls = (fields + ['unknown'] * 3)[:3]
    if connect == '403' and origin == '000':
        state = 'proxy_denied_before_origin'
    elif origin != '000' and tls == '0':
        state = 'origin_reached_authorization_not_checked'
    elif result.returncode == 60:
        state = 'tls_verification_failed'
    else:
        state = 'transport_failed'
    return {
        'check': name,
        'host': urlsplit(url).hostname,
        'state': state,
        'exit_code': result.returncode,
        'proxy_connect_status': connect,
        'origin_status': origin,
        'tls_verify': tls if origin != '000' else 'not_reached',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--probe', action='store_true', help='Make read-only HEAD requests through inherited proxy settings')
    parser.add_argument('--output', type=pathlib.Path, help='Save only non-secret diagnostic evidence as JSON')
    args = parser.parse_args()
    snapshot = pathlib.Path('/etc/codex/network-policy.json')
    policy = json.loads(snapshot.read_text()) if snapshot.is_file() else {}
    allowed = {entry['host'] for entry in policy.get('http_network_policy', {}).get('egress_rules', [])}
    report = {
        'observed_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'policy_source': 'startup snapshot; platform environment_status is authoritative for current policy',
        'snapshot_version': policy.get('version'),
        'targets': {name: {'host': urlsplit(url).hostname,
                           'present_in_snapshot': urlsplit(url).hostname in allowed}
                    for name, url in TARGETS.items()},
        'probes': [],
    }
    if args.probe:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            report['probes'] = list(executor.map(probe, TARGETS.items()))
    output = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output)
    sys.stdout.write(output)
    if any(not p['state'].startswith('origin_reached') for p in report['probes']):
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
