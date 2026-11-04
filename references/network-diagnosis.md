# 固定網址部署受阻：調查結果及解決步驟

2026-11-04，香港時間。這份記錄區分已確認的原因與尚未能查到的遠端狀態。

## 已確認的原因

目前生效的雲端環境仍為 **spec revision 1**，網路政策為 `restricted / enforced`，沒有自訂允許網域。設定草稿已是 **revision 3**，四個必要網域已成功儲存，但草稿不是執行中的設定。草稿的 base version 亦與目前執行個體的來源版本相同。

實際對照測試（不帶 GitHub API 憑證的 HEAD 請求，保持代理及 TLS 驗證）：

| 目的 | 網域 | 代理 CONNECT | 遠端 HTTP | 判定 |
| --- | --- | --- | --- | --- |
| 允許的對照網站 | registry.npmjs.org | 200 | 200 | 代理連線及 TLS 正常 |
| Pages 管理 API | api.github.com | 403 | 尚未連到 | 雲端代理拒絕連線 |
| 正式網站檢查 | angusqaq.github.io | 403 | 尚未連到 | 雲端代理拒絕連線 |
| 粵拼字庫 | humanum.arts.cuhk.edu.hk | 403 | 尚未連到 | 雲端代理拒絕連線 |
| 香港粵語預錄 | speech.platform.bing.com | 403 | 尚未連到 | 雲端代理拒絕連線 |

因此，本輪收到的 403 發生在連到 GitHub／字庫／語音服務之前，不能當成 GitHub token 無效、GitHub Pages 自身拒絕存取或網站程式錯誤。TLS 尚未開始的目標不記為 TLS 驗證通過。機器可讀證據保留在 `evidence/network-diagnostics.json`。

`git ls-remote origin refs/heads/main` 成功，確認遊戲已在指定 GitHub 專案；這僅證明 Git 讀取路徑可用，不能推論 API 授權。已檢查憑證名稱／是否存在，沒有輸出憑證值，也沒有要求額外 token。

平台沒有保留本次可讀的網路診斷紀錄；這不表示網路正常。上述結論由目前狀態、草稿差異及實際連線結果共同支持。

## 另一項發布前置條件

重新執行 `npm run check:release`：九項核心測試全部通過，圖片及字型檢查通過；**78 段正式配音缺少、75 個字待字庫核查**，因此正式發布檢查結束碼為 1。

`.github/workflows/pages.yml` 要在這項檢查通過後才部署。不能用移除檢查或部署無配音版本來宣稱完成原先要求。GitHub Actions 的實際遠端執行結果、Pages 是否已啟用，仍因 API 連線被擋而未能查核。

## 已備妥的解決方案

四個必要網域與完整安裝／啟動說明均已成功存入環境設定草稿，無需再次新增相同設定。平台回覆 `status: saved` 及 `requires_publish: true`；該工具明確只儲存草稿，不套用、不重新啟動，也不發佈。

**需在雲端環境設定頁檢閱、儲存該草稿，再發佈環境。** 目前提供給代理的工具沒有「發佈環境」操作；聊天中的同意並不會自動把草稿套用到執行個體。無需在聊天提供密鑰。

套用後，由代理依下列順序繼續：

1. 重新讀取平台 `environment_status`，確認目前生效規則已包含這四個網域；不能僅憑舊的啟動快照判定。
2. 執行 `npm run check:network`。應能連到遠端服務；HTTP 401／403／404 若來自遠端，與目前的代理 CONNECT 403 是不同問題，須再依實際操作診斷。
3. 執行 `python3 scripts/verify_cuhk.py` 核查剩餘字音，執行 `.venv/bin/python scripts/prepare_audio.py` 製作新句子的預錄粵語，核對實際配音。
4. 執行 `npm run check:release`；通過後以正常提交保存素材，讓此專案 Pages 工作流程部署。
5. 確認 GitHub Actions 部署成功，再實際開啟正式網址、檢查圖片及音訊，才交付固定連結。

可重跑的診斷指令：

```sh
npm run check:network
# 如需保留新一輪的非秘密證據：
python3 scripts/check_network.py --probe --output evidence/network-diagnostics.json
```

它使用現有代理、保持 TLS 驗證、只發送唯讀 HEAD 請求，不修改網路政策。`--probe` 遇到代理拒絕、TLS 失敗或其他連線問題時返回結束碼 2，不偽裝成成功。遠端有回應只代表連線可達，不代表 API 權限或實際語音生成已通過。
