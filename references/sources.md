# 來源與素材處理

參考專案為使用者指定的 `https://github.com/angusQAQ/yi-jiu-games`。只讀取其「小島生活任務」「小島句子列車」的程式、畫風、資料、來源及教師控制設計；原專案未作修改。參考時的完整提交為 `74253623bed8183fcd3ba28e446bb4bcdb78af8b`。

`dist/engine.js` 的 logical AnimationQueue、列車放置／交換模型，及 `dist/app.js` 的題號導覽、音訊取消、Pointer Events 多拖動模式，依參考專案重新調整至本題庫。未引入原專案其餘兩款遊戲、離線下載工具及不相符的舊配音。

以下檔案原樣沿用：

- `dist/assets/education-kai.ttf`、`font-source.txt`：教育部標準楷書 Version 5.1，原字型未修改；授權見附帶來源文字。
- `dist/assets/kai-variant-7240.woff2`、`kai-variant-license.txt`：全字庫正楷體「牀」單字補字及政府資料開放授權說明。
- `dist/assets/train-engine-16-v1.png`、`train-carriages-16-v3.png`、`dist/train-art.js`：原彩繪逐幀車頭與車廂，以及每幀取景邊界。原始生成記錄保留於相鄰的 train manifest 檔。
- `references/cuhk-retained/`：逐字 CUHK 查核來源及讀音資料，僅當本題所選讀音確實存在於已保留證據內時才標記 verified-retained。

新圖使用實際 `image_gen` 工具在獲授權雲端生成。10 組生活動畫均為 4×4 逐格彩繪圖集，五張列車情境圖為左右兩張方圖，詞義圖為 4×4 方圖。網站以 SVG 視窗按原比例取景，不改繪原圖、不拉伸。圖像目視檢查和雜湊檢查分開記錄；雜湊不同不代表動作邏輯自動正確。

水樽圖曾重製以移除生成器加入的數字、回復正確圖集比例；書包圖移除桌上另一課本；校巴圖移除重複的已上車人物；果汁圖修正硬幣與投幣口的接觸方向。鑰匙題依使用者要求完全移除，未隨網站發布。

粵語音檔規劃採 Microsoft Edge Read Aloud 的 `zh-HK-HiuMaanNeural`，並非香港中文大學錄音。本次 78 段配音均已生成，音檔文字、識別名稱、時長及 SHA-256 保存在 `references/audio-manifest.json`。

本輪部署核查補記：「袋」的中大本字讀音列為 `doi6`，詞例包括布袋、手袋，並列出「筆」為配搭點；原暫訂 `doi2` 已改按本字讀音記錄。學生畫面仍顯示無聲調 `doi`。證據見 `references/cuhk-pages/888b.html`。
