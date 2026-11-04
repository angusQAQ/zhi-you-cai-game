# 實際驗證記錄

日期：2026-11-04（香港時間）。所有製作及測試在授權雲端完成，沒有在教師電腦建立遊戲或伺服器。

## 本輪正式發布前已通過

- `npm run check`：**9 項測試，9 通過、0 失敗、0 跳過**。題數、句式、唯一答案、兩次題庫更正、固定語意切分、標點、角色交替、動作閘門、暫停排程、交換、雙指擁有權及錯誤保留。
- `python3 tests/browser.py`：**16 項瀏覽器情境通過**。Chromium 實際測試全部 15 題在 1280×720、1920×1080 的版面，以及答錯重試、雙人角色／動作、完整列車答案、同時雙觸控、同卡防重複、交換／移回／取消、鍵盤、動畫逐格、暫停續播、跳題清理、重開及全題重溫。沒有瀏覽器例外或素材 HTTP 失敗。
- `python3 tests/audio_browser.py`：**4 項音訊生命週期情境通過**。隔離的六秒測試聲音驗證凍結及續播、音訊／動畫雙完成閘門、靜音中止、跳題及首頁清理、重溫朗讀暫停。測試音不隨網站發布。
- `python3 tests/production_audio.py`：**5 項正式音檔瀏覽器情境通過**。78 段真實香港粵語檔全部載入及解碼，15 句重溫逐一播放匹配音檔、暫停續播與回首頁清理，兩款遊戲各完成一題真實配音並在聲音及動畫結束後只推進一次。沒有替換測試音、放寬 autoplay 或瀏覽器／HTTP 錯誤。
- `npm run check:release`：**正式發布檢查通過**。78/78 音檔存在、可解碼、文字與雜湊對應；111/111 所需字的中大核查證據齊備；10 組各 16 幀新情境圖、5 組列車雙圖、詞義圖與原樣字型均通過檢查。

## 修正的部署前置問題

- 新環境已解除舊的代理網路阻擋，GitHub 管理 API 權限確認為 admin。
- `edge-tts` 升至 7.3.1，配合 `truststore` 0.10.5 使用環境的系統 CA，保持憑證及主機名稱驗證；取消會被關閉的共享 connector。未停用 TLS 驗證。
- 中大「袋」本字讀音核實為 doi6，證據保留；畫面無聲調粵拼不變。
- 實際讀取 GitHub Actions 失敗紀錄，確認 runner 缺少 ffmpeg。流程已明確安裝，正式素材檢查與瀏覽器測試共用同一 job，全部通過才部署。

## 證據與範圍

`evidence/` 保存兩個指定尺寸的關鍵畫面、`browser-results.json`、`audio-browser-results.json`、`production-audio-results.json`。新配音來源與時長為 `references/audio-manifest.json`；粵拼為 `cuhk-audit.json`、`cuhk-pages/` 與 `cuhk-retained/`；圖片為 `art-manifest.json`。

原生語音測試證明音檔可播放、對應文字且流程正確，未把自動測試宣稱為人工逐句聽審。尚未在實體電子白板測試硬體；雙觸控是透過 Chromium CDP 的兩個真實同時接點驗證。

已實際嘗試 Pages 建站 API：GitHub 回覆 **403 Resource not accessible by integration**，屬目前 GitHub App 的權限限制，不是舊的雲端代理 CONNECT 403。官方 configure-pages action 說明首次 enablement 要有 administration:write 及 pages:write 的其他 token，不能使用 GITHUB_TOKEN；流程已移除不適用的自動 enablement 選項。專案管理者已完成 Pages 設定，API 已確認 build_type=workflow，網址為 https://angusqaq.github.io/zhi-you-cai-game/ 。

GitHub runner 的原生音訊測試另發現固定 sleep 對較慢環境不足；保留「不能提早換題」斷言，將完成檢查改為等待實際題號／音訊狀態。再次在雲端重跑後，接續執行 Actions。

**GitHub Pages 已成功部署。** 首次成功執行：[Actions 41760276258](https://github.com/angusQAQ/zhi-you-cai-game/actions/runs/41760276258)，部署提交 `d1f1310b750a083796272bb25ffe51c71d390437`。正式網址 https://angusqaq.github.io/zhi-you-cai-game/ 已實際請求並確認 HTTP 200。

正式網址的瀏覽器、真實音訊與截圖複查交由 `.github/workflows/verify-live.yml` 執行，使用 GitHub runner 的既有公開網站憑證信任，不修改雲端瀏覽器的共用信任設定。結果及關鍵畫面保存在該 Actions 執行的 `live-website-evidence` artifact。

## 正式網址驗證已通過

[Verify live game website 41760814861](https://github.com/angusQAQ/zhi-you-cai-game/actions/runs/41760814861) 已成功完成。GitHub runner 在正式 HTTPS 網址實際載入及解碼全部 78 段配音，逐句播放 15 句重溫，操作兩款遊戲各一題並確認完整配音與動畫結束後只推進一次；無 JavaScript 或素材 HTTP 錯誤。共 5 項正式站情境全部通過。

另有 105 項正式站資源 HTTP 200 檢查通過；78 段音檔及程式／資料檔的 SHA-256 與提交內容相符。原始結果為 `evidence/live-http-assets.json`、`evidence/live-production-audio-results.json`。正式頁面截圖為 `evidence/live-home-1280.png`、`live-home-1920.png`、`live-life-1920.png`、`live-train-1920.png`，亦已目視檢查。

## UI 對照更新驗證

首頁已刪除指定品牌與兩款遊戲名稱，保留兩個可操作的圖像入口，並加入新的海島背景。兩個指定解像度皆無需捲動首頁；漢字計算樣式為 900 粗體標楷體，與參考版本同樣的描邊設定，粵拼維持 Times New Roman。

對照同一版本的「一……就……」實際頁面，分別量測生活任務的上方場景／句子面板及下方操作區，以及列車的情境面板、軌道、詞庫。在 1280×720、1920×1080 共 **10 項位置及尺寸對照全部一致**，最大差異 0 像素；原始數據及畫面存於 `evidence/ui-reference-layout-comparison.json` 與 `evidence/ui-*.png`。新句式必需的左右空框、第二人觸發、8／7 節車廂按新題庫保留。

本輪 16 項瀏覽器流程通過，包含所有 15 題、左右空格提示、角色交替、雙觸控拖動、交換／放回、暫停、跳題與重溫；4 項音訊生命週期、5 項正式音檔流程及 9 項核心檢查通過。字型、題庫、配音內容沒有更換。重溫重新遊玩改用原版標頭的「重新開始」按鈕，測試按實際按鈕操作。
