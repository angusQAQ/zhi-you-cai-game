# Project workflow

Use the existing checkout in this authorized cloud environment. Do not create a worktree or a copy on the teacher's computer. The reference repository `angusQAQ/yi-jiu-games` is read-only. This repository is the only destination for new code and assets.

Static site: `dist/`. Source of curriculum: `scripts/build_content.py` → `dist/content.json`. Preserve the teacher's latest two corrections: bottle-cap/drinking replaces the key/door question; ticket sentence ends「坐火車」.

Run `npm run check`, `python3 scripts/check_assets.py`, and relevant real-browser checks. Run `npm run check:release` before any production deployment. Do not bypass missing narration, CUHK checks, image logic checks, or a failing release gate. See `references/validation.md` for current evidence and blockers. Tests must actually execute, not merely report a file-level pass.

For text changes update pictures, Jyutping, audio text/hash IDs and review data together. Complete sentences use「主語＋只有＋條件，＋才＋結果。」except the teacher's latest umbrella correction「只有雨傘打開，才可以擋雨。」. Life choices remain repeatable and always preview the selected image in the missing side. Any selection enables submission; only submission grades it. Incorrect submissions retain the image with a clear red border/cross and「請試一試！」plus the prerecorded prompt, allow retries, and never start the success animation or advance. Do not display the life success/role icon rows. Keep large bold Kai Chinese, Times New Roman toneless Jyutping, full-width punctuation, no countdown, two-person cooperation, teacher navigation, direct freeze on pause, and full reviews.

Visually inspect every new image for physical logic and character duplication. Distinct frame hashes alone do not establish a correct 16-frame animation. Never substitute a mismatched old recording, a missing image, or a static frame for an unfinished asset. Keep source notices, original fonts, and image proportions.

Use normal commits and fast-forward pushes; preserve concurrent changes, no force push. Deploy only this project's Pages after readiness passes, then check the live URL. No offline exports or releases in this task.
