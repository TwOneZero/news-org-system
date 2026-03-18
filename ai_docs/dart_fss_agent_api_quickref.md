# DART-FSS Open DART API Quick Reference for AI Agents

Source doc: Open DART API — dart-fss documentation v0.4.3. This reference compresses the API surface into the minimum an agent needs to call the right functions and normalize inputs. citeturn129663view0

## Scope
Use this when the agent needs to:
- resolve a Korean listed company to `corp_code`
- search recent filings
- fetch filing originals
- pull structured report info
- pull financial statement values
- pull major shareholder / ownership disclosures

## Required setup
- Set `DART_API_KEY` in environment. Many `info.*` APIs allow `api_key=None` when `DART_API_KEY` is configured. citeturn129663view0
- Normalize company identity to DART `corp_code` first. Most APIs require the 8-digit `corp_code`. citeturn129663view0

---

## 1) Company resolution

### `dart_fss.api.filings.get_corp_code() -> OrderedDict`
Download the master list of DART companies including corporate code, company name, CEO name, stock code, and recent change date. Cache this locally and refresh periodically. citeturn129663view0

**Agent use**
- Build `corp_name -> corp_code` map
- Build `stock_code -> corp_code` map
- Fuzzy-match user company names before any downstream call

### `dart_fss.api.filings.get_corp_info(corp_code: str) -> dict`
Fetch company profile / overview for a given 8-digit `corp_code`. citeturn129663view0

**Agent use**
- enrich answer context
- verify the resolved entity before searching filings

---

## 2) Filing search

### `dart_fss.api.filings.search_filings(...) -> dict`
Search filings.

**Key parameters** citeturn129663view0
- `corp_code: str | None`
  - target company corporate code
  - if omitted, search period is limited to 3 months
- `bgn_de: str | None`
  - start date `YYYYMMDD`
- `end_de: str | None`
  - end date `YYYYMMDD`, default is today if omitted
- `last_reprt_at: str = 'N'`
  - `Y` for only final reports
- `pblntf_ty: str | List[str] | None`
  - filing type
- `pblntf_detail_ty: str | List[str] | None`
  - filing detail type
- `corp_cls: str | None`
  - `Y`=KOSPI, `K`=KOSDAQ, `N`=KONEX, `E`=other
- `sort: str = 'date'`
  - `date`, `crp`, `rpt`
- `sort_mth: str = 'desc'`
  - `asc` or `desc`
- `page_no: int = 1`
- `page_count: int = 10`
  - docs describe range `1~100` per page

**Agent default policy**
- always prefer `corp_code`
- set `sort='date'`, `sort_mth='desc'`
- set `last_reprt_at='Y'` when user asks for latest canonical filing only
- date window examples:
  - recent monitoring: last 7–30 days
  - annual analysis: same fiscal year span

**Minimal wrapper shape**
```python
search_filings(
    corp_code=corp_code,
    bgn_de="20260101",
    end_de="20260317",
    last_reprt_at="Y",
    sort="date",
    sort_mth="desc",
    page_no=1,
    page_count=20,
)
```

---

## 3) Filing original download

### `dart_fss.api.filings.download_document(path: str, rcept_no: str) -> str`
Download the original filing document by receipt number and return the saved file path. citeturn129663view0

**Inputs**
- `path`: download directory
- `rcept_no`: filing receipt number

**Agent use**
- fetch raw filing content after `search_filings`
- parse to text / HTML-clean / chunk for LLM summarization

**Recommended post-processing**
1. download by `rcept_no`
2. detect file type
3. strip boilerplate / HTML tags
4. chunk by semantic section
5. store text + metadata (`corp_code`, `rcept_no`, report title, filing date)

---

## 4) Structured “regular report” information

These functions expose structured sections from periodic reports: quarterly, half-year, annual. They generally share the same input signature: `corp_code`, `bsns_year`, `reprt_code`, optional `api_key`. The docs state these data are provided from 2015 onward for these report-info endpoints. citeturn129663view0

### Common inputs
- `corp_code: str`
- `bsns_year: str`
  - 4-digit business year
- `reprt_code: str`
  - `11013` = Q1 report
  - `11012` = half-year report
  - `11014` = Q3 report
  - `11011` = annual report
- `api_key: str | None = None` citeturn129663view0

### High-value endpoints for agents
Only keep the endpoints that materially improve company analysis.

#### Audit / governance
- `accnut_adtor_nm_nd_adt_opinion()`
  - auditor name and audit opinion citeturn129663view0
- `accnut_adtor_non_adt_servc_cncls_sttus()`
  - non-audit service contracts with auditor citeturn129663view0
- `adt_servc_cncls_sttus()`
  - audit service contract status citeturn129663view0

#### Shareholder return / capital / debt
- `alot_matter()`
  - dividend information citeturn129663view0
- `cndl_capl_scrits_nrdmp_blce()`
  - outstanding conditional capital securities balance citeturn129663view0
- `cprnd_nrdmp_blce()`
  - outstanding corporate bonds balance citeturn129663view0

#### Workforce / executives / compensation
- `emp_sttus()`
  - employee status citeturn129663view0
- `exctv_sttus()`
  - executive status citeturn129663view0
- `indvdl_by_pay()`
  - compensation by individual citeturn129663view0

#### Equity / treasury stock
- `stock_totqy_sttus()`
  - total issued shares status citeturn129663view0
- `tesstk_acqs_dsps_sttus()`
  - treasury stock acquisition / disposal status citeturn129663view0

**Agent selection rule**
- ask for these only when the user needs structured governance, dividend, headcount, compensation, or capital-structure detail
- do not call the whole `info.*` surface by default

**Minimal wrapper shape**
```python
accnut_adtor_nm_nd_adt_opinion(
    corp_code=corp_code,
    bsns_year="2025",
    reprt_code="11011",
)
```

---

## 5) Financial statements / XBRL

The Open DART API page groups listed-company financial functions separately: `download_xbrl()`, `fnltt_multi_acnt()`, `fnltt_singl_acnt()`, `fnltt_singl_acnt_all()`, and `xbrl_taxonomy()`. citeturn129663view0

### Priority order for agents
1. `fnltt_singl_acnt_all()`
   - best default when you want a broad structured financial dump
2. `fnltt_singl_acnt()`
   - use when querying one account or a narrow slice
3. `fnltt_multi_acnt()`
   - use when querying several specific accounts
4. `download_xbrl()`
   - use only when raw filing financial package is required
5. `xbrl_taxonomy()`
   - use only for advanced normalization / mapping work citeturn129663view0

**Agent use**
- extract revenue, operating profit, net income, assets, liabilities, equity
- normalize to internal schema for time-series analytics
- join with news sentiment and filing summaries

**Recommendation**
For MVP agent flows, start with `fnltt_singl_acnt_all()` and only add XBRL parsing later. This is an implementation recommendation derived from the API grouping and complexity of the endpoints. citeturn129663view0

---

## 6) Ownership / major shareholders

### `elestock()`
Ownership disclosure summary endpoint listed under shareholding disclosures. citeturn129663view0

### `majorstock()`
Major shareholder disclosure summary endpoint. citeturn129663view0

**Agent use**
- detect controlling-shareholder context
- explain ownership-related filing changes
- augment governance / risk summaries

---

## 7) Minimal agent workflow

## A. Latest filing summarizer
```text
user company name
→ get_corp_code() cache lookup
→ resolve corp_code
→ search_filings(corp_code, recent window, sort=date desc)
→ select latest relevant rcept_no
→ download_document(path, rcept_no)
→ parse text
→ summarize / classify / sentiment score
```

## B. Company analysis workflow
```text
user company name
→ resolve corp_code
→ get_corp_info(corp_code)
→ fnltt_singl_acnt_all(...)
→ search_filings(...)
→ download_document(...)
→ optional: majorstock() / audit opinion / dividend / employee status
→ combine into final analysis object
```

---

## 8) Input normalization rules for the agent

### `corp_code`
- always 8-digit company code
- resolve once, reuse everywhere citeturn129663view0

### `reprt_code`
- annual: `11011`
- half-year: `11012`
- Q1: `11013`
- Q3: `11014` citeturn129663view0

### dates
- format: `YYYYMMDD` for filing search date parameters citeturn129663view0

### `corp_cls`
- `Y`, `K`, `N`, `E` as market class filters when needed citeturn129663view0

---

## 9) What the agent should cache

Cache aggressively:
- result of `get_corp_code()`
- resolved `corp_name -> corp_code`
- downloaded filing text by `rcept_no`
- normalized financial metrics by `(corp_code, year, reprt_code)`

---

## 10) Recommended internal tool names

Map library calls to cleaner tool names:

- `resolve_company` -> `get_corp_code()` + local match
- `get_company_profile` -> `get_corp_info()`
- `search_company_filings` -> `search_filings()`
- `download_filing_original` -> `download_document()`
- `get_financial_statements` -> `fnltt_singl_acnt_all()`
- `get_major_shareholders` -> `majorstock()`
- `get_audit_opinion` -> `accnut_adtor_nm_nd_adt_opinion()`
- `get_dividend_info` -> `alot_matter()`
- `get_employee_status` -> `emp_sttus()`
- `get_executive_status` -> `exctv_sttus()`

---

## 11) Do not over-call these endpoints in MVP

Avoid by default:
- full XBRL taxonomy workflows
- every `info.*` endpoint for every query
- broad searches without `corp_code`

Reason: the docs show a large surface area, but only a subset is necessary for a practical retrieval-and-analysis agent. This is an implementation recommendation, not a direct rule from the docs. The need for `corp_code`, report codes, and narrower endpoint selection is grounded in the documented parameter patterns. citeturn129663view0

---

## 12) Minimal pseudo-implementation contract

```python
class DartAgentTools:
    def resolve_company(self, query: str) -> dict: ...
    def get_company_profile(self, corp_code: str) -> dict: ...
    def search_company_filings(self, corp_code: str, bgn_de: str, end_de: str) -> dict: ...
    def download_filing_original(self, rcept_no: str) -> str: ...
    def get_financial_statements(self, corp_code: str, bsns_year: str, reprt_code: str = "11011") -> dict: ...
    def get_major_shareholders(self, corp_code: str) -> dict: ...
    def get_audit_opinion(self, corp_code: str, bsns_year: str, reprt_code: str) -> dict: ...
```

This contract is not from the docs; it is a practical wrapper layer around the documented endpoints above. The underlying endpoint inventory and parameter conventions come from the Open DART API page. citeturn129663view0
