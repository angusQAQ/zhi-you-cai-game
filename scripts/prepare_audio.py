"""Generate prerecorded HK Cantonese in authorized cloud/CI, never in the game."""
import asyncio
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import truststore

# Application-level integration recommended by https://truststore.readthedocs.io/.
# Includes managed OS CA trust while preserving certificate/hostname verification.
truststore.inject_into_ssl()
import edge_tts

ROOT = pathlib.Path(__file__).resolve().parents[1]


def duration(path):
    return float(subprocess.check_output(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'csv=p=0', str(path)], text=True).strip())


async def main():
    data = json.loads((ROOT / 'dist/content.json').read_text())
    files, audit = [], {}
    proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
    for id, clip in data['audio'].items():
        target = ROOT / 'dist' / clip['file']
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            temporary = target.with_suffix('.partial.mp3')
            try:
                # Let each Communicate own its connector. Sharing an aiohttp
                # connector across sessions breaks retries when one closes it.
                await edge_tts.Communicate(
                    clip['text'], clip['voice'], rate='-8%', proxy=proxy,
                ).save(str(temporary))
                if duration(temporary) <= 0:
                    raise ValueError('Empty narration: ' + id)
                temporary.replace(target)
            finally:
                temporary.unlink(missing_ok=True)
        seconds = duration(target)
        if seconds <= 0 or target.stat().st_size < 1000:
            raise ValueError('Invalid narration: ' + id)
        audit[id] = {
            **clip, 'duration': seconds,
            'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
            'provider': 'Microsoft Edge Read Aloud; not CUHK recordings',
        }
        files.append(clip['file'])
        print('Verified', id, flush=True)
    (ROOT / 'dist/audio-ready.json').write_text(
        json.dumps({'files': files}, ensure_ascii=False, indent=2) + '\n')
    (ROOT / 'references/audio-manifest.json').write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as exc:
        # Client error URLs can include authentication parameters: do not dump them.
        print('Narration preparation failed:', type(exc).__name__,
              'HTTP status:', getattr(exc, 'status', 'n/a'), file=sys.stderr)
        raise SystemExit(1)
