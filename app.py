import streamlit as st
import pandas as pd
from simulation import simulate_months

st.set_page_config(page_title="부부 자산 시뮬레이션 대시보드", layout="wide")

st.title("👨‍👩‍👧 부부 자산 시뮬레이션 대시보드")
st.caption("민감 데이터는 깃에 올리지 말고 업로드하세요. (레포는 Public로 배포)")

with st.sidebar:
    st.header("⚙️ 기본 설정")
    income0 = st.number_input("초기 실질 월소득(만원)", 0.0, 5000.0, 1250.0, 10.0)
    income_g = st.number_input("연 소득 증가율(%)", 0.0, 20.0, 5.0, 0.1)
    expense0 = st.number_input("월 지출(저축 제외, 만원)", 0.0, 5000.0, 583.0, 1.0)
    expense_g = st.number_input("연 지출 증가율(%)", 0.0, 10.0, 2.0, 0.1)
    auto_save = st.number_input("자동저축(연금+청약, 만원)", 0.0, 1000.0, 85.0, 1.0)
    extra_inv = st.number_input("추가 월 투자금(만원)", 0.0, 1000.0, 50.0, 1.0)
    invest_r = st.number_input("투자 연수익률(%)", 0.0, 20.0, 5.0, 0.1)

    st.header("🏠 부동산 & 대출")
    re0 = st.number_input("부동산 가치(초기, 만원)", 0.0, 10000000.0, 119000.0, 100.0)
    re_g = st.number_input("부동산 연상승률(%)", 0.0, 10.0, 1.5, 0.1)

    m1_pv = st.number_input("모기지1 원금(만원)", 0.0, 1000000.0, 30000.0, 10.0)
    m1_rate = st.number_input("모기지1 연금리(%)", 0.0, 20.0, 2.6, 0.1)
    m1_n = st.number_input("모기지1 남은 기간(개월)", 1, 600, 360, 1)

    m3_pv = st.number_input("모기지3 원금(만원)", 0.0, 1000000.0, 40000.0, 10.0)
    m3_rate = st.number_input("모기지3 연금리(%)", 0.0, 20.0, 4.0, 0.1)
    m3_n = st.number_input("모기지3 남은 기간(개월)", 1, 600, 360, 1)

    cl_pv = st.number_input("신용대출 잔액(만원)", 0.0, 1000000.0, 4000.0, 10.0)
    cl_rate = st.number_input("신용대출 연금리(%)", 0.0, 20.0, 5.0, 0.1)
    cl_n = st.number_input("신용대출 상환개월", 1, 120, 24, 1)

    st.header("📅 시뮬레이션 기간")
    start_year = st.number_input("시작 연도", 2000, 2100, 2025, 1)
    start_month = st.number_input("시작 월", 1, 12, 11, 1)
    months = st.number_input("개월 수", 1, 360, 60, 1)

params = dict(
    income0=income0, income_growth=income_g,
    expense0=expense0, expense_growth=expense_g,
    auto_save=auto_save, extra_invest=extra_inv,
    invest_return=invest_r,
    realestate0=re0, realestate_growth=re_g,
    mort1_pv=m1_pv, mort1_rate=m1_rate, mort1_n=m1_n,
    mort3_pv=m3_pv, mort3_rate=m3_rate, mort3_n=m3_n,
    credit_pv=cl_pv, credit_rate=cl_rate, credit_months=cl_n,
    financial0=5202.0
)

st.subheader("📈 시뮬레이션 결과 (월별)")
df = simulate_months(params, months=int(months), start_year=int(start_year), start_month=int(start_month))
st.dataframe(df, use_container_width=True, height=360)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("마지막 달 순자산(억원)", f"{df['순자산'].iloc[-1]/10000:.2f}")
with col2:
    st.metric("마지막 달 금융자산(억원)", f"{df['금융자산'].iloc[-1]/10000:.2f}")
with col3:
    st.metric("평균 저축률(%)", f"{df['저축률(%)'].mean():.1f}%")

st.subheader("📊 간단 차트")
st.line_chart(df.set_index("연-월")[["순자산","금융자산","총부채"]])

st.markdown("---")
st.subheader("📥 실제 값 업로드 (선택)")
st.caption("CSV에 월별 '연-월, 실제 월소득, 실제 지출(저축제외), 실제 자동저축, 실제 대출상환합계, 실제 총저축액, 실제 총자산' 컬럼을 포함하면 갭 분석이 가능해요.")
template = "연-월,실제 월소득,실제 지출(저축제외),실제 자동저축,실제 대출상환합계,실제 총저축액,실제 총자산\n2025-11,1250,583,85,210,650,99000\n"
st.download_button("템플릿 CSV 다운로드", template, file_name="actuals_template.csv", mime="text/csv")
up = st.file_uploader("CSV 업로드", type=["csv"])
if up is not None:
    real = pd.read_csv(up)
    st.success(f"로드 완료! {len(real)}행")
    merged = df.merge(real, how="left", left_on="연-월", right_on=real.columns[0])
    merged["실제_순자산"] = merged.get("실제 총자산", float("nan")) - (merged["모기지1잔액"]+merged["모기지3잔액"]+merged["신용잔액"])
    merged["순자산_차이(만원)"] = merged["실제_순자산"] - merged["순자산"]
    merged["순자산_차이율(%)"] = merged["순자산_차이(만원)"] / merged["순자산"] * 100.0
    st.subheader("🔍 갭 분석")
    st.dataframe(merged[["연-월","순자산","실제_순자산","순자산_차이(만원)","순자산_차이율(%)"]].tail(12), use_container_width=True)
    st.line_chart(merged.set_index("연-월")[["순자산","실제_순자산"]])