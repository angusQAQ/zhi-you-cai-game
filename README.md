# 「……只有……，才……。」小島中文遊戲

香港小學二年級、語文能力較弱及非華語學生的雙人電子白板教材。專案：<https://github.com/angusQAQ/zhi-you-cai-game>。

**目前為製作版本，尚未交付正式網址。** 程式及彩繪圖已完成本機雲端驗證；78 段香港粵語預錄音尚未生成，另有 75 個字待中大字庫核查。雲端網路政策目前拒絕相關服務與 GitHub API。發布檢查會阻止缺少配音／核查資料的版本部署。`https://angusqaq.github.io/zhi-you-cai-game/` 只是預期路徑，未經實際部署及開啟確認，不能視為交付連結。

## 內容

- **小島生活任務**：10 題。前五題補左邊，後五題補右邊，以虛線空框、問號及可重播小手動畫提示。一人選卡，另一人按固定動作按鈕；逐題交換角色。答對不會略過第二位同學。
- **小島句子列車**：5 題，前 3 題「★ 初階」提供空格長度，後 2 題「★★ 高階」等長空格。每題依指定詞組產生 7 或 8 節車廂，逗號與句號獨立。支援雙觸控、交換、放回詞庫、取消拖動、點卡後點車廂，以及鍵盤 Enter／空白鍵選放、Delete／Backspace 移回。
- 沒有倒數或分數競賽。教師可隨時暫停、繼續、重開、跳題、回主頁、開關聲音及進入全題圖文重溫。暫停凍結教材，不加遮罩。
- 生活任務有 10 組各 16 幀新彩繪動畫；列車沿用參考專案的 16 幀車輪及蒸氣素材。新情境、詞義圖與字型隨網站載入，遊玩時不呼叫 AI／配音服務。

最新已採用的題庫更正：第 1 題為「小明只有打開水樽蓋，才可以喝水。」；第 4 題為「我們只有拿出車票，才可以坐火車。」沒有鑰匙開門題。

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

先在環境設定套用已儲存的四個必要網域：`humanum.arts.cuhk.edu.hk`、`speech.platform.bing.com`、`api.github.com`、`angusqaq.github.io`。這是網路需求，不需在聊天中提供密鑰。

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
