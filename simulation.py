import math
import pandas as pd

def pmt(rate, nper, pv):
    """Monthly payment for an annuity (loan). rate is monthly (e.g., 0.04/12)."""
    if rate == 0:
        return -(pv / nper)
    return -(rate * pv) / (1 - (1 + rate) ** (-nper))

def simulate_months(params, months=60, start_year=2025, start_month=11):
    """
    params dict expects:
      income0, income_growth, expense0, expense_growth, auto_save, extra_invest,
      invest_return, realestate0, realestate_growth,
      mort1_pv, mort1_rate, mort1_n,
      mort3_pv, mort3_rate, mort3_n,
      credit_pv, credit_rate, credit_months,
      financial0
    All rates are annual (%) except *_pv are in 10,000 KRW (만원).
    """
    p = dict(params)
    r_inv_m = p["invest_return"] / 100.0 / 12.0
    r_re_m  = p["realestate_growth"] / 100.0 / 12.0
    r_m1_m  = p["mort1_rate"] / 100.0 / 12.0
    r_m3_m  = p["mort3_rate"] / 100.0 / 12.0
    r_cl_m  = p["credit_rate"] / 100.0 / 12.0

    def _pmt(rate, nper, pv):
        return pmt(rate, nper, pv)

    pmt_m1 = _pmt(r_m1_m, p["mort1_n"], p["mort1_pv"])
    pmt_m3 = _pmt(r_m3_m, p["mort3_n"], p["mort3_pv"])

    credit_left = p["credit_pv"]
    credit_n    = max(1, p["credit_months"])

    rows = []
    fin_prev = p["financial0"]
    re_prev  = p["realestate0"]
    m1_prev  = p["mort1_pv"]
    m3_prev  = p["mort3_pv"]
    cl_prev  = credit_left

    for i in range(months):
        year = start_year + (start_month - 1 + i) // 12
        month = (start_month - 1 + i) % 12 + 1

        year_offset = i // 12
        income = p["income0"] * ((1 + p["income_growth"]/100.0) ** year_offset)
        expense = p["expense0"] * ((1 + p["expense_growth"]/100.0) ** year_offset)
        auto_save = p["auto_save"]
        extra_invest = p["extra_invest"]

        pay_m1 = -pmt_m1
        pay_m3 = -pmt_m3
        pay_cl = 0.0
        if cl_prev > 0.0:
            remain = max(1, credit_n - i)
            pay_cl = -_pmt(r_cl_m, remain, cl_prev)

        loan_out = pay_m1 + pay_m3 + pay_cl

        net_save = income - expense - auto_save - loan_out
        invest_in = auto_save + max(net_save, 0) + extra_invest

        fin_now = fin_prev * (1 + r_inv_m) + invest_in
        re_now = re_prev * (1 + r_re_m)

        m1_now = max(m1_prev * (1 + r_m1_m) - pay_m1, 0)
        m3_now = max(m3_prev * (1 + r_m3_m) - pay_m3, 0)
        cl_now = max(cl_prev * (1 + r_cl_m) - pay_cl, 0)

        total_assets = fin_now + re_now
        total_debt   = m1_now + m3_now + cl_now
        net_worth    = total_assets - total_debt
        save_rate    = (invest_in / income) if income > 0 else 0.0

        rows.append({
            "연-월": f"{year}-{month:02d}",
            "월소득(시뮬)": round(income,1),
            "월지출(저축제외)": round(expense,1),
            "자동저축": round(auto_save,1),
            "대출상환합계": round(loan_out,1),
            "월_투자반영액": round(invest_in,1),
            "금융자산": round(fin_now,1),
            "부동산가치": round(re_now,1),
            "모기지1잔액": round(m1_now,1),
            "모기지3잔액": round(m3_now,1),
            "신용잔액": round(cl_now,1),
            "총자산": round(total_assets,1),
            "총부채": round(total_debt,1),
            "순자산": round(net_worth,1),
            "저축률(%)": round(save_rate*100,1),
        })

        fin_prev, re_prev = fin_now, re_now
        m1_prev, m3_prev, cl_prev = m1_now, m3_now, cl_now

    return pd.DataFrame(rows)