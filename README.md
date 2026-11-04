# 「……只有……，才……。」中文句式遊戲

香港小學二年級、語文能力較弱及非華語學生的雙人電子白板教材。專案：<https://github.com/angusQAQ/zhi-you-cai-game>。

**固定遊戲網址：[https://angusqaq.github.io/zhi-you-cai-game/](https://angusqaq.github.io/zhi-you-cai-game/)**

GitHub Pages 已成功部署，正式網址已確認回傳 HTTP 200。79 段香港粵語預錄音及 111 個字的粵拼核查齊備，正式發布檢查與 GitHub Actions 全部通過。遊玩時不需登入、不需安裝或啟動伺服器。後續在同一專案正常提交，會自動更新同一網址。

## 內容

- **小島生活任務**：10 題。前五題補左邊，後五題補右邊，以虛線空框、問號及可重播小手動畫提示。一人選卡，另一人按固定動作按鈕；逐題交換角色。答對不會略過第二位同學。
- **小島句子列車**：5 題，前 3 題「★ 初階」提供空格長度，後 2 題「★★ 高階」等長空格。每題依指定詞組產生 7 或 8 節車廂，逗號與句號獨立。支援雙觸控、交換、放回詞庫、取消拖動、點卡後點車廂，以及鍵盤 Enter／空白鍵選放、Delete／Backspace 移回。
- 沒有倒數或分數競賽。教師可隨時暫停、繼續、重開、跳題、回主頁、開關聲音及進入全題圖文重溫。暫停凍結教材，不加遮罩。
- 生活任務有 10 組各 16 幀新彩繪動畫；列車沿用參考專案的 16 幀車輪及蒸氣素材。新情境、詞義圖與字型隨網站載入，遊玩時不呼叫 AI／配音服務。

最新已採用的題庫更正：第 1 題為「小明只有打開水樽蓋，才可以喝水。」；第 4 題為「我們只有拿出車票，才可以坐火車。」列車雨傘題為「只有雨傘打開，才可以擋雨。」沒有鑰匙開門題。

## 開發與雲端驗證

純 HTML、CSS、JavaScript，沒有應用程式套件依賴或建置步驟。Node 24、Python 3.12；瀏覽器測試使用 Playwright 1.62.0、Chromium 與 ffmpeg。

```sh
npm run check
python3 scripts/check_assets.py
npm run serve
# 在另一個雲端終端執行；伺服器必須已就緒
python3 tests/browser.py
python3 tests/audio_browser.py
```

不要在教師電腦建立副本或啟動伺服器。每個雲端工作已有獨立 checkout，直接使用現有專案，不建立額外 worktree。測試伺服器僅綁定雲端 loopback，並非正式網址。

實際證據見 [references/validation.md](references/validation.md)。`tests/audio_browser.py` 在瀏覽器路由中隔離使用測試聲音，只驗證原生音訊生命週期；不代表正式粵語配音已完成，也不把測試聲音放入網站。

## 完成配音、核查與部署

診斷證據與具體解決步驟見 [references/network-diagnosis.md](references/network-diagnosis.md)。可執行 `npm run check:network` 區分代理阻擋、TLS 問題與已連到遠端但尚未驗證授權；此指令不修改網路規則。

製作音檔或重新核查字音時，環境需能存取以下四個網域：`humanum.arts.cuhk.edu.hk`、`speech.platform.bing.com`、`api.github.com`、`angusqaq.github.io`。遊玩時只讀取網站已部署的靜態素材，不會即時呼叫配音或字庫服務。

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r scripts/audio-requirements.txt
python3 scripts/verify_cuhk.py
.venv/bin/python scripts/prepare_audio.py
npm run check:release
```

配音固定使用 `zh-HK-HiuMaanNeural` 香港粵語，朗讀 `dist/content.json` 中的書面文字。所有音檔 ID 含新文字的 SHA-256 前綴，與舊專案句子音檔不同。腳本遵循環境 HTTPS 代理和系統 TLS 信任，不停用驗證。生成完畢後需實際聆聽核對讀音，再提交音檔、`audio-ready.json` 與來源記錄。

字庫核查若提供其他讀音，先按本句字義檢查，再更新 `scripts/build_content.py` 的讀音並重新產生資料；不能修改預期讀音來掩蓋未查核項目。網站只顯示無聲調粵拼，中大字庫不是配音來源。

`.github/workflows/pages.yml` 會先執行九項核心測試、素材檢查及瀏覽器測試；`release-readiness` 要求全數真實配音與粵拼核查通過，之後才部署此專案的 `dist/` 至 GitHub Pages。使用正常 fast-forward 提交，不 force-push；不修改參考專案，也不建立替代儲存庫。部署後還必須檢查 Actions 結果及正式網站所有資源。

## 資料與來源

- `dist/content.json`：兩款遊戲、答案、詞卡、粵拼、配音文字與重溫共用唯一資料；修改來源為 `scripts/build_content.py`。
- `references/art-manifest.json`：新彩繪素材來源、構圖說明、尺寸、逐幀雜湊及目視檢查記錄。
- `references/cuhk-audit.json`、`references/cuhk-retained/`：字庫選音狀態與參考專案保留的查核證據；未核查項目明示 pending。
- `dist/assets/font-source.txt`、`kai-variant-license.txt`：原樣教育部標準楷書及「牀」單字補字來源與授權。
- [references/sources.md](references/sources.md)：程式與共用素材來源。

本輪只製作網頁版，沒有離線 HTML 匯出、下載發佈、登入、資料庫或排行榜。

## 本輪介面更新

兩款遊戲的版面直接沿用「一……就……」對應的小島遊戲：原始樣式完整保存在 `dist/reference-ui.css`，新句式需要的左右關係空框、只有／才詞卡及雙人流程由 `dist/style.css` 配合。保留 10+5 題及雙人操作流程。

首頁改為水彩海島背景、兩個圖像入口及開始按鈕，不再顯示「小島中文」「小島生活任務」「小島句子列車」三段名稱；介紹及遊玩畫面保留對應遊戲標題。漢字採原版粗體標楷體設定，字型檔不改動，詞卡粵拼維持 Times New Roman。

參考版本、樣式雜湊與適配範圍見 `references/ui-reference-manifest.json`；10 項主要版面幾何對照及新畫面證據見 `evidence/ui-reference-layout-comparison.json`、`evidence/ui-*.png`。

生活任務在動作開始前可反覆點選任何選項；每次點選都在空格顯示所選圖片、填入所選詞語並播放該選項的香港粵語預錄音，重複點同一選項也會重播。任何選項均可按「提交」，提交時才判斷答案；答錯保留圖片，顯示紅框、大叉號和「請試一試！」，同時播放提示音，可立即重新選圖或再次提交，答對才播放動作及完整句子。原先刪除的成功／玩家角色圖標維持隱藏。雨傘題的詞卡順序、完整句、配音及重溫維持最新修訂。
