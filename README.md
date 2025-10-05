# Family Finance Dashboard (Streamlit)

> 공개 레포 + 민감 데이터 업로드 방식. 코드만 공개하고, 자산 CSV/엑셀은 깃에 올리지 않습니다.

## Quick Start (Local)
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy (Streamlit Community Cloud)
1. 이 폴더를 **Public** GitHub repo로 업로드
2. Streamlit Cloud에서 `app.py` 지정 → Deploy
3. 실제 데이터는 **CSV 업로드**로 주입 (레포에는 올리지 않음)

## Data Privacy
- `.gitignore`로 `data/`, `*.csv`, `.streamlit/secrets.toml` 등 **민감 파일 전체 제외**
- 운영 중에는 좌측 사이드바에서 파라미터 조정, 실제 값은 **CSV 업로드**로 비교

## Folder
```
.
├─ app.py
├─ simulation.py
├─ requirements.txt
├─ .gitignore
└─ data/
   └─ README.md   # 실제 CSV/엑셀은 여기에 (깃 무시됨)
```