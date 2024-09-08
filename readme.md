## 如何執行

1. 確保已經安裝 poetry 套件管理工具，在此資料夾下執行以下指令來建立虛擬環境和自動安裝套件

```shell
poetry install
```

2. 使用以下指令，透過虛擬環境中的 python 來執行腳本

```shell
poetry run python ${crawler_script.py}
```

3. 輸出結果會在當前的資料夾或是子資料夾中以 json 形式儲存
