# ======================= FinancialDataCollection (Enhanced with Institutional & Insider Activity + S&P 500) =======================
import os
import re
from pathlib import Path
import glob
import time
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import requests
from .fred_collector import FREDCollector

def _ensure_dir(p: str) -> None:
    os.makedirs(p, exist_ok=True)


def _safe_float(x, default=np.nan):
    try:
        if x is None:
            return default
        if isinstance(x, str):
            s = x.replace(",", "").strip()
            if s == "" or s.lower() in ("nan", "null", "none"):
                return default
            return float(s)
        return float(x)
    except Exception:
        return default


class FinancialDataCollection:
    """
    V3 (Enhanced):
      - Collects profiles, IS/BS/CF (annual), ratios (annual), key metrics (annual)
      - EV history (annual): marketCapitalization, enterpriseValue, addTotalDebt, minusCashAndCashEquivalents
      - Employee history (annual by periodOfReport)
      - Prices (EOD full) with explicit ?from=YYYY-MM-DD covering (years+1) back; preserves API columns exactly.
        -> Monthly resample (export-only) uses "last" per month for *all* columns when possible (no column guessing).
      - S&P 500 index prices (^GSPC) collected for the same time period
      - Analyst: analyst-estimates (annual), price-target-consensus (export-only)
      - NEW: Institutional & Insider Activity:
        * Latest insider trading activity
        * Institutional ownership summaries
        * Insider trading statistics
        * 13F extract capability (separate method)
      - All_Financial_Data keeps ALL original fields from the five accounting/metric blocks;
        collisions resolved by precedence (later overwrites earlier).
      - Adds absolute YoY deltas for a set of key numeric indicators as <col>_YoY (no %).
      - Economic indicators: load latest economics/fred_full_history_YYYYMMDD_HHMM.xlsx;
        if missing/stale, calls FREDCollector to build a new workbook. Exports Economic_Annual sheet.
    """

    ENDPOINTS = {
        "profile": "https://financialmodelingprep.com/stable/profile",
        "income_statement": "https://financialmodelingprep.com/stable/income-statement",
        "balance_sheet": "https://financialmodelingprep.com/stable/balance-sheet-statement",
        "cash_flow": "https://financialmodelingprep.com/stable/cash-flow-statement",
        "ratios": "https://financialmodelingprep.com/stable/ratios",
        "key_metrics": "https://financialmodelingprep.com/stable/key-metrics",
        "enterprise_values": "https://financialmodelingprep.com/stable/enterprise-values",
        "employee_history": "https://financialmodelingprep.com/stable/historical-employee-count",
        "prices_full": "https://financialmodelingprep.com/stable/historical-price-eod/full",
        "analyst_estimates": "https://financialmodelingprep.com/stable/analyst-estimates",
        "price_target_consensus": "https://financialmodelingprep.com/stable/price-target-consensus",
        "insider_trading_search": "https://financialmodelingprep.com/stable/insider-trading/search",
        "institutional_ownership_summary": "https://financialmodelingprep.com/stable/institutional-ownership/symbol-positions-summary",
        "institutional_13f_extract": "https://financialmodelingprep.com/stable/institutional-ownership/extract",
        "insider_trading_statistics": "https://financialmodelingprep.com/stable/insider-trading/statistics",
    }

    PRECEDENCE = ("ratios", "key_metrics", "balance_sheet", "cash_flow", "income_statement")

    def __init__(
        self,
        api_key: str,
        companies: Dict[str, str],
        years: int = 10,
        include_analyst: bool = True,
        include_institutional: bool = True,
        include_sp500: bool = True,
        sleep_sec: float = 0.0,
        timeout: int = 30,
        retries: int = 3,
        backoff: float = 0.7,
        export_dir: Path = Path("export"),
        econ_dir: Path =Path("export")
    ):
        self.api_key = api_key
        self.companies = {k: (v or "").upper().strip() for k, v in companies.items()}
        self.years = int(years)
        self.include_analyst = include_analyst
        self.include_institutional = include_institutional
        self.include_sp500 = include_sp500

        self.sleep_sec = float(sleep_sec)
        self.timeout = int(timeout)
        self.retries = int(retries)
        self.backoff = float(backoff)

        self.export_dir = Path(export_dir)
        _ensure_dir(self.export_dir)
        self.econ_dir = econ_dir

        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "CollectorV3/1.3"})

        # Raw per-company stores
        self.profiles: Dict[str, dict] = {}
        self.is_hist: Dict[str, list] = {}
        self.bs_hist: Dict[str, list] = {}
        self.cf_hist: Dict[str, list] = {}
        self.ratios_hist: Dict[str, list] = {}
        self.km_hist: Dict[str, list] = {}
        self.ev_hist: Dict[str, pd.DataFrame] = {}
        self.emp_hist: Dict[str, pd.DataFrame] = {}
        self.prices_daily: Dict[str, pd.DataFrame] = {}
        self.prices_monthly: Dict[str, pd.DataFrame] = {}
        self.analyst_estimates: Dict[str, pd.DataFrame] = {}
        self.price_targets: Dict[str, pd.DataFrame] = {}

        # S&P 500 storage
        self.sp500_daily: pd.DataFrame = pd.DataFrame()
        self.sp500_monthly: pd.DataFrame = pd.DataFrame()

        # Institutional & Insider data stores
        self.insider_trading_latest: Dict[str, pd.DataFrame] = {}
        self.institutional_ownership: Dict[str, pd.DataFrame] = {}
        self.insider_statistics: Dict[str, pd.DataFrame] = {}

        # Consolidated tables
        self.raw_tables: Dict[str, pd.DataFrame] = {}
        self.all_fin_df: pd.DataFrame = pd.DataFrame()
        self.metrics_df: pd.DataFrame = pd.DataFrame()

        self._collected = False
        self.availability = True

    # ---------------------------- HTTP helper ----------------------------
    def _get(self, url: str, params: dict) -> Optional[requests.Response]:
        params = dict(params or {})
        params["apikey"] = self.api_key
        for i in range(self.retries):
            try:
                r = self.session.get(url, params=params, timeout=self.timeout)
                if r.status_code == 200:
                    return r
                if r.status_code in (429, 500, 502, 503, 504):
                    time.sleep(self.backoff * (2 ** i))
                    continue
                break
            except Exception:
                time.sleep(self.backoff * (2 ** i))
        return None

    @staticmethod
    def _to_df(obj) -> pd.DataFrame:
        if obj is None:
            return pd.DataFrame()
        if isinstance(obj, list):
            return pd.DataFrame(obj)
        if isinstance(obj, dict):
            return pd.DataFrame([obj])
        return pd.DataFrame()

    @staticmethod
    def _json_safe(resp: Optional[requests.Response]):
        if resp is None:
            return None
        try:
            return resp.json()
        except Exception:
            return None

    def _firstword_key(self, name: str, ticker: str) -> str:
        m = re.search(r"[A-Za-z0-9]+", name or "")
        head = m.group(0) if m else ""
        if not head:
            head = ticker or "CO"
        return f"{head}_{(ticker or '').upper()}"

    # ------------------------ Collection ------------------------
    def _collect_profiles(self):
        new_profiles  = {}
        new_companies = {}
        for name, sym in self.companies.items():
            r  = self._get(self.ENDPOINTS["profile"], {"symbol": sym})
            js = self._json_safe(r)
            rec = js[0] if isinstance(js, list) and js else (js if isinstance(js, dict) else {})
            if not rec or not isinstance(rec, dict) or not rec.get("symbol"):
                print(
                    f"Hint: ticker '{sym}' (input name '{name}') is unavailable or returned no profile data. "
                    f"Please verify the symbol or your API access. Exiting _collect_profiles with no changes."
                )
                self.availability = False
                return  
            real_name = (rec.get("companyName") or name or sym).strip()
            real_sym  = (rec.get("symbol") or sym).strip().upper()
    
            rec["Company"] = real_name
            rec["Symbol"] = real_sym
    
            key = self._firstword_key(real_name, real_sym)
    
            new_profiles[key]  = rec
            new_companies[key] = real_sym
    
            if self.sleep_sec:
                time.sleep(self.sleep_sec)

        self.profiles  = new_profiles
        self.companies = new_companies

    def _collect_statements(self):
        lim = self.years + 1
        stores = [
            ("income_statement", self.is_hist),
            ("balance_sheet", self.bs_hist),
            ("cash_flow", self.cf_hist),
            ("ratios", self.ratios_hist),
            ("key_metrics", self.km_hist),
        ]
        for name, sym in self.companies.items():
            for key, store in stores:
                r = self._get(self.ENDPOINTS[key], {"symbol": sym, "period": "annual", "limit": lim})
                js = self._json_safe(r)
                if isinstance(js, dict):
                    js = [js]
                store[name] = js or []
                if self.sleep_sec:
                    time.sleep(self.sleep_sec)

    def _collect_ev(self):
        lim = self.years + 1
        for name, sym in self.companies.items():
            r = self._get(self.ENDPOINTS["enterprise_values"],
                          {"symbol": sym, "period": "annual", "limit": lim})
            js = self._json_safe(r)
            df = self._to_df(js)

            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"], errors="coerce")

            df["Company"] = name
            df["Symbol"] = sym

            if "date" in df.columns:
                df = df.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)
            else:
                df = df.reset_index(drop=True)

            self.ev_hist[name] = df
            if self.sleep_sec:
                time.sleep(self.sleep_sec)

    def _collect_employees(self):
        lim = self.years + 1
        for name, sym in self.companies.items():
            r = self._get(self.ENDPOINTS["employee_history"], {"symbol": sym, "limit": lim})
            js = self._json_safe(r)
            df = self._to_df(js)
            if "periodOfReport" in df.columns:
                df["periodOfReport"] = pd.to_datetime(df["periodOfReport"], errors="coerce")
            if "filingDate" in df.columns:
                df["filingDate"] = pd.to_datetime(df["filingDate"], errors="coerce")
            self.emp_hist[name] = df.sort_values("periodOfReport" if "periodOfReport" in df.columns else df.columns[0]).reset_index(drop=True)
            if self.sleep_sec:
                time.sleep(self.sleep_sec)

    def _collect_prices(self):
        """
        FIX 1: Use ?from=YYYY-MM-DD to cover (years+1) years back from 'today'.
        FIX 2: Preserve response columns exactly; do not guess or rename. Add Company/Symbol for ID only.
        Also provide a monthly resample (export-only) that uses 'last' per month across all columns when possible.
        NEW: Also collect S&P 500 (^GSPC) prices if include_sp500=True.
        """
        start_date = (pd.Timestamp.today().normalize() - pd.DateOffset(years=self.years + 1)).strftime("%Y-%m-%d")

        for name, sym in self.companies.items():
            r = self._get(self.ENDPOINTS["prices_full"], {"symbol": sym, "from": start_date})
            js = self._json_safe(r)

            if isinstance(js, list):
                arr = js
            elif isinstance(js, dict) and "historical" in js:
                arr = js.get("historical") or []
            else:
                arr = []

            df = self._to_df(arr)

            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"], errors="coerce")

            dfd = df.copy()
            dfd["Company"] = name
            dfd["Symbol"] = sym

            if "date" in dfd.columns:
                dfd = dfd.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)
            else:
                dfd = dfd.reset_index(drop=True)

            self.prices_daily[name] = dfd

            if "date" in dfd.columns and not dfd.empty:
                tmp = dfd.set_index("date").sort_index()
                try:
                    pm = tmp.resample("ME").last().reset_index()
                except Exception:
                    pm = pd.DataFrame(columns=["date"])
                if not pm.empty:
                    pm["Company"] = name
                    pm["Symbol"] = sym
                self.prices_monthly[name] = pm
            else:
                self.prices_monthly[name] = pd.DataFrame()

            if self.sleep_sec:
                time.sleep(self.sleep_sec)

        # NEW: Collect S&P 500 index prices
        if self.include_sp500:
            r = self._get(self.ENDPOINTS["prices_full"], {"symbol": "^GSPC", "from": start_date})
            js = self._json_safe(r)

            if isinstance(js, list):
                arr = js
            elif isinstance(js, dict) and "historical" in js:
                arr = js.get("historical") or []
            else:
                arr = []

            df = self._to_df(arr)

            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"], errors="coerce")

            sp_daily = df.copy()
            sp_daily["Index"] = "S&P500"
            sp_daily["Symbol"] = "^GSPC"

            if "date" in sp_daily.columns:
                sp_daily = sp_daily.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)
            else:
                sp_daily = sp_daily.reset_index(drop=True)

            self.sp500_daily = sp_daily

            # Monthly resample for S&P 500
            if "date" in sp_daily.columns and not sp_daily.empty:
                tmp = sp_daily.set_index("date").sort_index()
                try:
                    sp_monthly = tmp.resample("ME").last().reset_index()
                except Exception:
                    sp_monthly = pd.DataFrame(columns=["date"])
                if not sp_monthly.empty:
                    sp_monthly["Index"] = "S&P500"
                    sp_monthly["Symbol"] = "^GSPC"
                self.sp500_monthly = sp_monthly
            else:
                self.sp500_monthly = pd.DataFrame()

            if self.sleep_sec:
                time.sleep(self.sleep_sec)

    def _collect_analyst(self):
        if not self.include_analyst:
            return
        lim = self.years + 1
        for name, sym in self.companies.items():
            r1 = self._get(self.ENDPOINTS["analyst_estimates"], {"symbol": sym, "period": "annual", "limit": lim})
            df1 = self._to_df(self._json_safe(r1))
            if "date" in df1.columns:
                df1["date"] = pd.to_datetime(df1["date"], errors="coerce")
            self.analyst_estimates[name] = df1.sort_values("date" if "date" in df1.columns else df1.columns[0]).reset_index(drop=True)

            r2 = self._get(self.ENDPOINTS["price_target_consensus"], {"symbol": sym})
            df2 = self._to_df(self._json_safe(r2))
            if "publishedDate" in df2.columns:
                df2["publishedDate"] = pd.to_datetime(df2["publishedDate"], errors="coerce")
            self.price_targets[name] = df2

            if self.sleep_sec:
                time.sleep(self.sleep_sec)

    # ------------------------ Institutional & Insider Collection ------------------------
    def _collect_insider_trading_latest(self):
        """
        Collect insider trading activity for each company using the search endpoint.
        Uses page=1 and limit=1000 for optimal data retrieval.
        """
        if not self.include_institutional:
            return
            
        for name, sym in self.companies.items():
            r = self._get(self.ENDPOINTS["insider_trading_search"], 
                          {"symbol": sym, "page": 1, "limit": 1000})
            js = self._json_safe(r)
            df = self._to_df(js)
            
            date_cols = ["filingDate", "transactionDate"]
            for col in date_cols:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors="coerce")
            
            df["Company"] = name
            df["Symbol"] = sym
            
            if "transactionDate" in df.columns:
                df = df.sort_values("transactionDate", ascending=False)
            
            self.insider_trading_latest[name] = df.reset_index(drop=True)
            
            if self.sleep_sec:
                time.sleep(self.sleep_sec)

    def _collect_institutional_ownership(self):
        if not self.include_institutional:
            return
            
        current_year = datetime.now().year
        quarters = [1, 2, 3, 4]
        
        for name, sym in self.companies.items():
            all_quarters = []
            
            for year_offset in [0, 1]:
                year = current_year - year_offset
                for quarter in quarters:
                    r = self._get(self.ENDPOINTS["institutional_ownership_summary"], 
                                  {"symbol": sym, "year": year, "quarter": quarter})
                    js = self._json_safe(r)
                    df = self._to_df(js)
                    
                    if not df.empty:
                        if "date" in df.columns:
                            df["date"] = pd.to_datetime(df["date"], errors="coerce")
                        
                        df["Company"] = name
                        df["Symbol"] = sym
                        df["CollectedYear"] = year
                        df["CollectedQuarter"] = quarter
                        
                        all_quarters.append(df)
                        
                    if self.sleep_sec:
                        time.sleep(self.sleep_sec)
            
            if all_quarters:
                combined = pd.concat(all_quarters, ignore_index=True)
                if "date" in combined.columns:
                    combined = combined.sort_values("date", ascending=False)
                else:
                    combined = combined.sort_values(["CollectedYear", "CollectedQuarter"], ascending=False)
                
                self.institutional_ownership[name] = combined.head(4).reset_index(drop=True)
            else:
                self.institutional_ownership[name] = pd.DataFrame()
                
            if self.sleep_sec:
                time.sleep(self.sleep_sec)

    def _collect_insider_statistics(self):
        if not self.include_institutional:
            return
            
        for name, sym in self.companies.items():
            r = self._get(self.ENDPOINTS["insider_trading_statistics"], 
                          {"symbol": sym})
            js = self._json_safe(r)
            df = self._to_df(js)
            
            df["Company"] = name
            df["Symbol"] = sym
            
            self.insider_statistics[name] = df.reset_index(drop=True)
                
            if self.sleep_sec:
                time.sleep(self.sleep_sec)

    def collect_13f_data(self, cik: str, year: int, quarter: int) -> pd.DataFrame:
        """
        Separate method for 13F data since it requires specific CIK parameter.
        
        Args:
            cik: Central Index Key of institution (e.g., "0001067983" for Berkshire Hathaway)
            year: Year (e.g., 2023)
            quarter: Quarter (1, 2, 3, 4)
        
        Returns:
            DataFrame with 13F holdings data
        """
        r = self._get(self.ENDPOINTS["institutional_13f_extract"], 
                      {"cik": cik, "year": year, "quarter": quarter})
        js = self._json_safe(r)
        df = self._to_df(js)
        
        date_cols = ["date", "acceptedDate"]
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")
        
        df["institutionCik"] = cik
        df["year"] = year
        df["quarter"] = quarter
        
        return df.sort_values("date" if "date" in df.columns else df.columns[0]).reset_index(drop=True)

    # ------------------------ Consolidation ------------------------
    def _series_to_annual_df(self, series: List[dict], company_name: str, symbol: str) -> pd.DataFrame:
        dfa = self._to_df(series)
        if dfa.empty:
            return pd.DataFrame(columns=["Company", "Symbol", "Year", "date"])
        if "fiscalYear" in dfa.columns:
            dfa["Year"] = pd.to_numeric(dfa["fiscalYear"], errors="coerce")
        elif "calendarYear" in dfa.columns:
            dfa["Year"] = pd.to_numeric(dfa["calendarYear"], errors="coerce")
        elif "date" in dfa.columns:
            dfa["Year"] = pd.to_datetime(dfa["date"], errors="coerce").dt.year
        else:
            dfa["Year"] = pd.NA
        if "date" in dfa.columns:
            dfa["date"] = pd.to_datetime(dfa["date"], errors="coerce")
        dfa["Company"] = company_name
        dfa["Symbol"] = symbol
        cols = ["Company", "Symbol", "Year"] + [c for c in dfa.columns if c not in ("Company", "Symbol", "Year")]
        return dfa[cols].dropna(subset=["Year"])

    def _consolidate_raw_tables(self) -> None:
        def stack_hist(store: Dict[str, list], label: str):
            frames = []
            for name, sym in self.companies.items():
                series = store.get(name)
                if series is None:
                    continue
                df = self._series_to_annual_df(series, name, sym)
                if not df.empty:
                    frames.append(df)
            self.raw_tables[label] = (
                pd.concat(frames, ignore_index=True)
                  .sort_values(["Company", "Year", "date"])
                  .reset_index(drop=True)
                if frames else pd.DataFrame()
            )

        stack_hist(self.is_hist, "Income_Statements")
        stack_hist(self.bs_hist, "Balance_Sheets")
        stack_hist(self.cf_hist, "Cash_Flows")
        stack_hist(self.ratios_hist, "Ratios")
        stack_hist(self.km_hist, "Key_Metrics")

        # EV
        ev_frames = []
        for name, sym in self.companies.items():
            df = self.ev_hist.get(name)
            if isinstance(df, pd.DataFrame) and not df.empty:
                d = df.copy()
                d["Company"] = name
                d["Symbol"] = sym
                ev_frames.append(d)
        self.raw_tables["Enterprise_Values"] = pd.concat(ev_frames, ignore_index=True) if ev_frames else pd.DataFrame()

        # Employees
        emp_frames = []
        for name, sym in self.companies.items():
            df = self.emp_hist.get(name)
            if isinstance(df, pd.DataFrame) and not df.empty:
                d = df.copy()
                d["Company"] = name
                d["Symbol"] = sym
                emp_frames.append(d)
        self.raw_tables["Employee_History"] = pd.concat(emp_frames, ignore_index=True) if emp_frames else pd.DataFrame()

        # Prices (daily)
        pd_frames = []
        for name, sym in self.companies.items():
            df = self.prices_daily.get(name)
            if isinstance(df, pd.DataFrame) and not df.empty:
                pd_frames.append(df.copy())
        self.raw_tables["Prices_Daily"] = pd.concat(pd_frames, ignore_index=True) if pd_frames else pd.DataFrame()

        # Prices (monthly)
        pm_frames = []
        for name, sym in self.companies.items():
            df = self.prices_monthly.get(name)
            if isinstance(df, pd.DataFrame) and not df.empty:
                pm_frames.append(df.copy())
        self.raw_tables["Prices_Monthly"] = pd.concat(pm_frames, ignore_index=True) if pm_frames else pd.DataFrame()

        # S&P 500 Prices
        if self.include_sp500:
            if isinstance(self.sp500_daily, pd.DataFrame) and not self.sp500_daily.empty:
                self.raw_tables["SP500_Daily"] = self.sp500_daily.copy()
            if isinstance(self.sp500_monthly, pd.DataFrame) and not self.sp500_monthly.empty:
                self.raw_tables["SP500_Monthly"] = self.sp500_monthly.copy()

        # Profiles
        pr_frames = []
        for name, sym in self.companies.items():
            prof = self.profiles.get(name)
            if isinstance(prof, dict) and prof:
                d = pd.DataFrame([prof])
                d["Company"] = name
                d["Symbol"] = sym
                pr_frames.append(d)
        self.raw_tables["Profiles"] = pd.concat(pr_frames, ignore_index=True) if pr_frames else pd.DataFrame()

        # Analyst
        if self.include_analyst:
            ae_frames, pt_frames = [], []
            for name, sym in self.companies.items():
                d1 = self.analyst_estimates.get(name)
                if isinstance(d1, pd.DataFrame) and not d1.empty:
                    t = d1.copy(); t["Company"] = name; t["Symbol"] = sym
                    ae_frames.append(t)
                d2 = self.price_targets.get(name)
                if isinstance(d2, pd.DataFrame) and not d2.empty:
                    t = d2.copy(); t["Company"] = name; t["Symbol"] = sym
                    pt_frames.append(t)
            self.raw_tables["Analyst_Estimates"] = pd.concat(ae_frames, ignore_index=True) if ae_frames else pd.DataFrame()
            self.raw_tables["Analyst_Targets"]  = pd.concat(pt_frames, ignore_index=True) if pt_frames else pd.DataFrame()

        # Institutional & Insider data
        if self.include_institutional:
            it_frames = []
            for name, sym in self.companies.items():
                df = self.insider_trading_latest.get(name)
                if isinstance(df, pd.DataFrame) and not df.empty:
                    it_frames.append(df.copy())
            self.raw_tables["Insider_Trading_Latest"] = pd.concat(it_frames, ignore_index=True) if it_frames else pd.DataFrame()
            
            io_frames = []
            for name, sym in self.companies.items():
                df = self.institutional_ownership.get(name)
                if isinstance(df, pd.DataFrame) and not df.empty:
                    io_frames.append(df.copy())
            self.raw_tables["Institutional_Ownership"] = pd.concat(io_frames, ignore_index=True) if io_frames else pd.DataFrame()
            
            is_frames = []
            for name, sym in self.companies.items():
                df = self.insider_statistics.get(name)
                if isinstance(df, pd.DataFrame) and not df.empty:
                    is_frames.append(df.copy())
            self.raw_tables["Insider_Statistics"] = pd.concat(is_frames, ignore_index=True) if is_frames else pd.DataFrame()

    # ------------------------ Build unified annual panel ------------------------
    def _build_all_financial_data(self) -> None:
        if not self.availability:
            return
        self._consolidate_raw_tables()

        is_all = self.raw_tables.get("Income_Statements", pd.DataFrame())
        bs_all = self.raw_tables.get("Balance_Sheets", pd.DataFrame())
        cf_all = self.raw_tables.get("Cash_Flows", pd.DataFrame())
        rt_all = self.raw_tables.get("Ratios", pd.DataFrame())
        km_all = self.raw_tables.get("Key_Metrics", pd.DataFrame())

        def latest_by_year(df: pd.DataFrame) -> dict:
            if df is None or df.empty:
                return {}
            d = df.copy()
            if "date" in d.columns:
                d = d.sort_values(["Company", "Year", "date"]).groupby(["Company", "Year"], as_index=False).tail(1)
            else:
                d = d.sort_values(["Company", "Year"]).groupby(["Company", "Year"], as_index=False).tail(1)
            d["Company"] = d["Company"].astype(str)
            d["Year"] = pd.to_numeric(d["Year"], errors="coerce")
            d = d.dropna(subset=["Company", "Year"])
            out = {}
            for _, r in d.iterrows():
                out[(r["Company"], int(r["Year"]))] = r.to_dict()
            return out

        look = {
            "income_statement": latest_by_year(is_all),
            "balance_sheet": latest_by_year(bs_all),
            "cash_flow": latest_by_year(cf_all),
            "ratios": latest_by_year(rt_all),
            "key_metrics": latest_by_year(km_all),
        }

        # Employees by year
        emp_by_year = {}
        for name, _ in self.companies.items():
            df = self.emp_hist.get(name)
            m = {}
            if isinstance(df, pd.DataFrame) and not df.empty and "periodOfReport" in df.columns:
                d = df.copy()
                d["Year"] = pd.to_datetime(d["periodOfReport"], errors="coerce").dt.year
                d = d.dropna(subset=["Year"])
                idx = d.groupby("Year")["periodOfReport"].idxmax()
                dd = d.loc[idx]
                for _, row in dd.iterrows():
                    m[int(row["Year"])] = row.to_dict()
            emp_by_year[name] = m

        # Universe of (Company, Year)
        keys = set()
        for df in (is_all, bs_all, cf_all, rt_all, km_all):
            if df is not None and not df.empty:
                for _, r in df[["Company", "Year"]].dropna().iterrows():
                    keys.add((str(r["Company"]), int(r["Year"])))

        rows = []
        for (company, year) in sorted(keys, key=lambda t: (t[0], t[1])):
            sym = self.companies.get(company, "")
            row = {"Company": company, "Symbol": sym, "Year": int(year)}

            for src in self.PRECEDENCE:
                blk = look.get(src, {}).get((company, year))
                if blk:
                    for k, v in blk.items():
                        if k in ("Company", "Symbol", "Year"):
                            continue
                        row[k] = v

            emp_blk = emp_by_year.get(company, {}).get(int(year))
            if emp_blk and "employeeCount" in emp_blk:
                row["employeeCount"] = emp_blk["employeeCount"]

            rows.append(row)

        out = pd.DataFrame(rows).sort_values(["Company", "Year"]).reset_index(drop=True)

        if "Year" in out.columns:
            out["Year"] = pd.to_numeric(out["Year"], errors="coerce").astype("Int64")

        # Gentle numeric casting
        id_cols = {"Company", "Symbol", "Year"}
        for c in out.columns:
            if c in id_cols or out[c].dtype != "O":
                continue
            converted = pd.to_numeric(out[c], errors="coerce")
            mask = converted.notna()
            if mask.any():
                out.loc[mask, c] = converted[mask]

        # YoY deltas
        key_for_yoy = [
            "revenue","netIncome","grossProfit","operatingIncome","ebitda","ebit",
            "totalAssets","totalLiabilities","totalStockholdersEquity","cashAndCashEquivalents",
            "operatingCashFlow","freeCashFlow","capitalExpenditure",
            "currentRatio","quickRatio","returnOnAssets","returnOnEquity",
        ]
        present = [c for c in key_for_yoy if c in out.columns]
        if present:
            out = out.sort_values(["Company", "Year"])
            for c in present:
                out[f"{c}_YoY"] = out.groupby("Company")[c].diff()

        self.all_fin_df = out
        numeric_cols = out.select_dtypes(include=[np.number]).columns.tolist()
        self.metrics_df = out[["Company", "Year"] + [c for c in numeric_cols if c != "Year"]].copy()

    # ------------------------ Economics integration ------------------------
    def _parse_econ_ts_from_name(self, path: str) -> Optional[pd.Timestamp]:
        try:
            base = os.path.basename(path)
            stem, _ = os.path.splitext(base)
            parts = stem.split("_")
            dt_token = parts[-2] + parts[-1]
            return pd.to_datetime(dt_token, format="%Y%m%d%H%M", errors="coerce")
        except Exception:
            return None

    def _find_latest_econ_file(self, econ_dir: str = "economics") -> Optional[str]:
        pattern = os.path.join(econ_dir, "fred_full_history_*.xlsx")
        files = glob.glob(pattern)
        if not files:
            return None
        def sort_key(p):
            ts = self._parse_econ_ts_from_name(p)
            return (ts is not None, ts or pd.Timestamp(os.path.getmtime(p), unit="s"))
        files.sort(key=sort_key, reverse=True)
        return files[0]

    def _load_econ_from_workbook(self, path: str) -> Dict[str, pd.DataFrame]:
        out = {}
        try:
            xl = pd.ExcelFile(path)
            for sheet in ("Raw_Long", "Monthly_Panel", "Quarterly_Panel", "Meta"):
                if sheet in xl.sheet_names:
                    out[sheet] = xl.parse(sheet)
        except Exception:
            out = {}
        return out

    def _build_econ_annual_from_book(self, book: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        if "Monthly_Panel" in book and not book["Monthly_Panel"].empty:
            mp = book["Monthly_Panel"].copy()
            if "Date" not in mp.columns:
                return pd.DataFrame()
            mp["Date"] = pd.to_datetime(mp["Date"], errors="coerce")
            mp = mp.dropna(subset=["Date"]).sort_values("Date").set_index("Date")
            ann = mp.resample("YE-DEC").last().reset_index()
            ann["Year"] = ann["Date"].dt.year.astype("Int64")
            cols = ["Year"] + [c for c in ann.columns if c not in ("Year")]
            return ann[cols]
        if "Raw_Long" in book and not book["Raw_Long"].empty:
            rl = book["Raw_Long"].copy()
            if not set(["Date", "Series", "Value"]).issubset(rl.columns):
                return pd.DataFrame()
            rl["Date"] = pd.to_datetime(rl["Date"], errors="coerce")
            rl = rl.dropna(subset=["Date"])
            wide = rl.pivot_table(index="Date", columns="Series", values="Value", aggfunc="last")
            ann = wide.resample("YE-DEC").last().reset_index()
            ann["Year"] = ann["Date"].dt.year.astype("Int64")
            cols = ["Year"] + [c for c in ann.columns if c not in ("Year")]
            return ann[cols]
        return pd.DataFrame()

    def get_economic(self, force_refresh: bool = False, econ_dir: str = "economics",
                     stale_days: int = 45) -> pd.DataFrame:
        existing = self.raw_tables.get("Economic_Annual")
        if isinstance(existing, pd.DataFrame) and not existing.empty and not force_refresh:
            return existing

        econ_path = None
        latest = self._find_latest_econ_file(econ_dir)
        use_fallback = False

        if latest is None:
            use_fallback = True
        else:
            ts = self._parse_econ_ts_from_name(latest)
            if ts is None:
                ts = pd.to_datetime(os.path.getmtime(latest), unit="s", errors="coerce")
            if pd.isna(ts) or (pd.Timestamp.now() - ts).days > int(stale_days):
                use_fallback = True

        if use_fallback:
            print("ℹ️ No recent macro workbook found - running FREDCollector to build one...")
            fc = FREDCollector(fmp_api_key=self.api_key, export_dir = str(self.econ_dir))
            econ_path = fc.run_export_single()
        else:
            econ_path = latest
            print(f"ℹ️ Using existing macro workbook: {econ_path}")

        book = self._load_econ_from_workbook(econ_path)
        econ_annual = self._build_econ_annual_from_book(book)

        self.raw_tables["Economic_Annual"] = econ_annual
        return econ_annual

    # ------------------------ Orchestration ------------------------
    def collect(self, force: bool = False):
        if self._collected and not force:
            return
        print("Collecting profiles ..."); self._collect_profiles()
        if not self.availability:
            return
        print("Collecting statements/ratios/key-metrics (annual) ..."); self._collect_statements()
        print("Collecting enterprise values (annual history) ..."); self._collect_ev()
        print("Collecting employee history ..."); self._collect_employees()
        print("Collecting prices (EOD full -> monthly) ..."); self._collect_prices()
        
        if self.include_institutional:
            print("Collecting latest insider trading ..."); self._collect_insider_trading_latest()
            print("Collecting institutional ownership summaries ..."); self._collect_institutional_ownership()
            print("Collecting insider trading statistics ..."); self._collect_insider_statistics()
        
        if self.include_analyst:
            print("Collecting analyst estimates & price target consensus ..."); self._collect_analyst()
        self._collected = True
        print("✅ Raw collection complete.")

    def get_all_financial_data(self, force_collect: bool = False) -> pd.DataFrame:
        self.collect(force=force_collect)
        if self.all_fin_df.empty:
            self._build_all_financial_data()
        return self.all_fin_df

    # ------------------------ Export ------------------------
    def export_excel(self, filename_base: Optional[str] = None) -> str:
        if not self.availability:
            return
        if self.all_fin_df is None or self.all_fin_df.empty:
            raise ValueError("No data to export. Call get_all_financial_data() first.")

        cohort = "_".join(self.companies.keys())
        ts = datetime.now().strftime("%Y%m%d_%H%M")
        base = filename_base or f"All_Financial_Data_{cohort}"
        path = self.export_dir / "raw_data.xlsx"   # ← Path join
        _ensure_dir(self.export_dir)                   # ← Path ok

        try:
            econ_ann = self.get_economic(force_refresh=False, econ_dir = str(self.econ_dir),)
        except Exception:
            econ_ann = pd.DataFrame()

        with pd.ExcelWriter(str(path), engine="openpyxl") as writer:  # ← cast to str for writer
            if isinstance(econ_ann, pd.DataFrame) and not econ_ann.empty:
                econ_ann.to_excel(writer, sheet_name="Economic_Annual", index=False)

            self.all_fin_df.to_excel(writer, sheet_name="All_Financial_Data", index=False)
            self.metrics_df.to_excel(writer, sheet_name="Metrics", index=False)

            for tab in [
                "Income_Statements","Balance_Sheets","Cash_Flows","Ratios","Key_Metrics",
                "Enterprise_Values","Employee_History","Profiles","Prices_Daily","Prices_Monthly",
                "SP500_Daily","SP500_Monthly"
            ]:
                df = self.raw_tables.get(tab, pd.DataFrame())
                df.to_excel(writer, sheet_name=tab[:31], index=False)

            if self.include_analyst:
                self.raw_tables.get("Analyst_Estimates", pd.DataFrame()).to_excel(writer, sheet_name="Analyst_Estimates", index=False)
                self.raw_tables.get("Analyst_Targets",  pd.DataFrame()).to_excel(writer, sheet_name="Analyst_Targets",  index=False)

            if self.include_institutional:
                for tab in ["Insider_Trading_Latest", "Institutional_Ownership", "Insider_Statistics"]:
                    df = self.raw_tables.get(tab, pd.DataFrame())
                    df.to_excel(writer, sheet_name=tab[:31], index=False)

        print(f"✅ Excel written: {path}")
        return str(path)  # ← keep return type as str

    # ------------------------ Convenience getters ------------------------
    def get_profiles(self) -> pd.DataFrame:
        rows = []
        for name, sym in self.companies.items():
            d = self.profiles.get(name) or {}
            if d:
                r = dict(d)
                r["Company"] = name
                r["Symbol"] = sym
                rows.append(r)
        return pd.DataFrame(rows)

    def get_enterprise_values(self) -> pd.DataFrame:
        frames = []
        for name, sym in self.companies.items():
            df = self.ev_hist.get(name)
            if isinstance(df, pd.DataFrame) and not df.empty:
                frames.append(df.copy())
        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

    def get_prices_daily(self, include_sp500: bool = True) -> pd.DataFrame:
        frames = []
        for name, sym in self.companies.items():
            df = self.prices_daily.get(name)
            if isinstance(df, pd.DataFrame) and not df.empty:
                frames.append(df.copy())
        
        if include_sp500 and isinstance(self.sp500_daily, pd.DataFrame) and not self.sp500_daily.empty:
            frames.append(self.sp500_daily.copy())
        
        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

    def get_prices_monthly(self, include_sp500: bool = True) -> pd.DataFrame:
        frames = []
        for name, sym in self.companies.items():
            df = self.prices_monthly.get(name)
            if isinstance(df, pd.DataFrame) and not df.empty:
                frames.append(df.copy())
        
        if include_sp500 and isinstance(self.sp500_monthly, pd.DataFrame) and not self.sp500_monthly.empty:
            frames.append(self.sp500_monthly.copy())
        
        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

    def get_analyst_estimates(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        est_frames, tgt_frames = [], []
        if self.include_analyst:
            for name, sym in self.companies.items():
                df1 = self.analyst_estimates.get(name)
                if isinstance(df1, pd.DataFrame) and not df1.empty:
                    t = df1.copy(); t["Company"] = name; t["Symbol"] = sym
                    est_frames.append(t)
                df2 = self.price_targets.get(name)
                if isinstance(df2, pd.DataFrame) and not df2.empty:
                    t = df2.copy(); t["Company"] = name; t["Symbol"] = sym
                    tgt_frames.append(t)
        return (
            pd.concat(est_frames, ignore_index=True) if est_frames else pd.DataFrame(),
            pd.concat(tgt_frames, ignore_index=True) if tgt_frames else pd.DataFrame(),
        )

    def get_insider_trading_latest(self) -> pd.DataFrame:
        return self.raw_tables.get("Insider_Trading_Latest", pd.DataFrame())

    def get_institutional_ownership(self) -> pd.DataFrame:
        return self.raw_tables.get("Institutional_Ownership", pd.DataFrame())

    def get_insider_statistics(self) -> pd.DataFrame:
        return self.raw_tables.get("Insider_Statistics", pd.DataFrame())