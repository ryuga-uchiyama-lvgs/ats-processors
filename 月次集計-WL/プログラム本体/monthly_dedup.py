#!/usr/bin/env python3
"""
月次集計用: 5媒体の最新CSVに対して
1. 英数字・記号の全角→半角統一
2. 特殊記号(★【】！など)の正規化
3. 媒体間での企業名重複削除
4. 各媒体の正規化済みCSV + 全媒体統合企業名一覧を YYYYMMDD_集計 に出力

使い方:
    python3 monthly_dedup.py            # 日付は今日(YYYYMMDD)
    python3 monthly_dedup.py 20260601   # 日付を指定

各媒体フォルダ内の「ファイル名の日付が最新のCSV」を自動で使用する。
スクレイピング実行日とCSVの日付がズレている場合は警告を出す。
(normalize_and_dedup_20260601.py を毎月書き換え不要なよう汎用化したもの)
"""
import csv
import glob
import re
import sys
import unicodedata
import os
from collections import OrderedDict
from datetime import datetime

# ============================================================
# 設定
# ============================================================
BASE = os.path.dirname(os.path.abspath(__file__))
DATE = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y%m%d")

MEDIA_FILES = [
    {
        "name": "atGP",
        "glob": f"{BASE}/atGP/atgp_jobs_*.csv",
        "pattern": r"atgp_jobs_(\d{8})_\d{6}\.csv$",
        "company_col": "companyName",
        "encoding": "utf-8",
    },
    {
        "name": "LITALICO仕事ナビ",
        "glob": f"{BASE}/LITALICO/snabi_jobs_*.csv",
        "pattern": r"snabi_jobs_(\d{8})_\d{6}\.csv$",
        "company_col": "companyInfo",  # companyNameが空なのでcompanyInfoから抽出
        "encoding": "utf-8",
        "extract_company": True,
    },
    {
        "name": "dodaチャレンジ",
        "path": f"{BASE}/doda-challenge/doda-jobs.csv",
        "company_col": "社名",
        "encoding": "utf-8-sig",
    },
    {
        "name": "BABナビ",
        "glob": f"{BASE}/BABNAVI/babnavi_jobs_*.csv",
        "pattern": r"babnavi_jobs_(\d{8})_\d{6}\.csv$",
        "company_col": "company",
        "encoding": "utf-8-sig",
    },
    {
        "name": "マイナビパートナーズ",
        "glob": f"{BASE}/マイナビパートナーズ/mynavi_partners_jobs_*.csv",
        "pattern": r"mynavi_partners_jobs_(\d{8})_\d{6}\.csv$",
        "company_col": "企業名",
        "encoding": "utf-8-sig",
    },
]

OUTPUT_DIR = f"{BASE}/{DATE}_集計"

# 媒体名 -> 出力ファイル名(媒体別CSV)
MEDIA_OUTNAME = {
    "atGP": f"atGP_{DATE}.csv",
    "LITALICO仕事ナビ": f"LITALICO仕事ナビ_{DATE}.csv",
    "dodaチャレンジ": f"dodaチャレンジ_{DATE}.csv",
    "BABナビ": f"BABナビ_{DATE}.csv",
    "マイナビパートナーズ": f"マイナビパートナーズ_{DATE}.csv",
}


def resolve_latest(media: dict) -> str:
    """媒体の入力CSVパスを解決する(globの場合はファイル名の日付が最新のもの)"""
    if "path" in media:
        return media["path"]
    candidates = []
    for p in glob.glob(media["glob"]):
        m = re.search(media["pattern"], os.path.basename(p))
        if m:
            candidates.append((m.group(1), p))
    if not candidates:
        return ""
    candidates.sort()
    file_date, path = candidates[-1]
    if file_date != DATE:
        print(f"[警告] {media['name']}: 最新CSVの日付({file_date})が集計日({DATE})と一致しません → {os.path.basename(path)}")
        print(f"        スクレイピングを実行し忘れていないか確認してください。")
    return path


# ============================================================
# 正規化関数
# ============================================================
def normalize_text(text: str) -> str:
    """全角英数字・記号を半角に変換し、特殊記号を正規化する"""
    if not text:
        return text
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("★", "")
    text = text.replace("☆", "")
    text = text.replace("【", "[")
    text = text.replace("】", "]")
    text = text.replace("　", " ")
    text = text.replace("（", "(")
    text = text.replace("）", ")")
    text = text.replace("：", ":")
    text = text.replace("；", ";")
    text = text.replace("，", ",")
    text = text.replace("．", ".")
    text = text.replace("！", "!")
    text = text.replace("？", "?")
    text = text.replace("～", "~")
    text = text.replace("－", "-")
    text = text.replace("／", "/")
    text = text.replace("＆", "&")
    text = text.replace("＋", "+")
    text = text.replace("＝", "=")
    text = text.replace("＠", "@")
    text = text.replace("％", "%")
    text = text.replace("＃", "#")
    text = text.replace("＄", "$")
    text = text.replace("￥", "\\")
    text = text.replace("｜", "|")
    text = re.sub(r"\s+", " ", text)
    text = text.strip()
    return text


def normalize_company_name(name: str) -> str:
    """企業名の正規化(重複チェック用)"""
    name = normalize_text(name)
    name = name.replace(" ", "")
    name = re.sub(r"\(株\)$", "株式会社", name)
    name = re.sub(r"^\(株\)", "株式会社", name)
    return name


def extract_company_from_info(info: str) -> str:
    """LITALICOのcompanyInfoから企業名を抽出"""
    if not info:
        return ""
    m = re.match(r"^(.+?)の.+?/.+?の障害者雇用求人", info)
    if m:
        return m.group(1)
    parts = info.split("の", 1)
    return parts[0] if parts else info


# ============================================================
# メイン処理
# ============================================================
def main():
    print(f"集計日: {DATE}")
    print(f"出力先: {OUTPUT_DIR}\n")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    all_data = []

    for media in MEDIA_FILES:
        path = resolve_latest(media)
        if not path or not os.path.exists(path):
            print(f"[SKIP] ファイルが見つかりません: {media['name']}")
            continue
        with open(path, "r", encoding=media["encoding"]) as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            rows = list(reader)
        print(f"[読込] {media['name']}: {len(rows)}件 ({os.path.basename(path)})")
        all_data.append({
            "name": media["name"],
            "rows": rows,
            "fieldnames": list(fieldnames),
            "company_col": media["company_col"],
            "path": path,
            "extract_company": media.get("extract_company", False),
        })

    if len(all_data) < len(MEDIA_FILES):
        print("\n[警告] 読み込めなかった媒体があります。全媒体揃ってから再実行してください。")

    # Step 1: 正規化 + 企業名抽出
    print("\n--- Step 1: 英数字・記号の正規化 ---")
    for data in all_data:
        company_col = data["company_col"]
        if data["extract_company"]:
            if "companyName" not in data["fieldnames"]:
                idx = data["fieldnames"].index(company_col)
                data["fieldnames"].insert(idx + 1, "companyName")
        for row in data["rows"]:
            for key in list(row.keys()):
                if row[key]:
                    row[key] = normalize_text(row[key])
            if data["extract_company"]:
                raw_info = row.get(company_col, "")
                row["companyName"] = extract_company_from_info(raw_info)
        if data["extract_company"]:
            companies = set(row.get("companyName", "") for row in data["rows"])
        else:
            companies = set(row.get(company_col, "") for row in data["rows"])
        print(f"  {data['name']}: ユニーク企業数 = {len(companies)}")

    # Step 2: 媒体間の企業名重複削除
    print("\n--- Step 2: 媒体間の企業名重複チェック ---")
    seen_companies = OrderedDict()
    duplicates_removed = {}
    removed_companies_list = []

    for data in all_data:
        duplicates_removed[data["name"]] = 0
        effective_col = "companyName" if data["extract_company"] else data["company_col"]
        filtered_rows = []
        for row in data["rows"]:
            company = row.get(effective_col, "").strip()
            if not company:
                filtered_rows.append(row)
                continue
            norm_company = normalize_company_name(company)
            if norm_company in seen_companies:
                if seen_companies[norm_company] != data["name"]:
                    duplicates_removed[data["name"]] += 1
                    removed_companies_list.append({
                        "企業名(正規化済)": norm_company,
                        "企業名(元表記)": company,
                        "削除元媒体": data["name"],
                        "既出媒体": seen_companies[norm_company],
                    })
                    continue
            else:
                seen_companies[norm_company] = data["name"]
            filtered_rows.append(row)
        removed = len(data["rows"]) - len(filtered_rows)
        data["rows"] = filtered_rows
        if removed > 0:
            print(f"  {data['name']}: {removed}件の重複求人を削除 (他媒体で既出の企業)")

    removed_unique = OrderedDict()
    for item in removed_companies_list:
        key = (item["企業名(正規化済)"], item["削除元媒体"])
        if key not in removed_unique:
            removed_unique[key] = item

    removed_path = os.path.join(OUTPUT_DIR, f"removed_duplicate_companies_{DATE}.csv")
    with open(removed_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["企業名(正規化済)", "企業名(元表記)", "削除元媒体", "既出媒体"])
        writer.writeheader()
        writer.writerows(removed_unique.values())
    print(f"  削除企業一覧: {len(removed_unique)}社 → {os.path.basename(removed_path)}")

    # Step 3: 各媒体の正規化済みCSVを出力
    print("\n--- Step 3: 媒体別CSV出力 ---")
    for data in all_data:
        outname = MEDIA_OUTNAME[data["name"]]
        output_path = os.path.join(OUTPUT_DIR, outname)
        with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=data["fieldnames"], extrasaction="ignore")
            writer.writeheader()
            writer.writerows(data["rows"])
        print(f"  {data['name']}: {len(data['rows'])}件 → {outname}")

    # Step 4: 全媒体統合の企業名一覧を出力
    print("\n--- Step 4: 全媒体統合企業名一覧 ---")
    company_media_map = OrderedDict()
    for data in all_data:
        effective_col = "companyName" if data["extract_company"] else data["company_col"]
        for row in data["rows"]:
            company = row.get(effective_col, "").strip()
            if company:
                norm = normalize_company_name(company)
                if norm not in company_media_map:
                    company_media_map[norm] = set()
                company_media_map[norm].add(data["name"])

    company_list_path = os.path.join(OUTPUT_DIR, f"all_companies_deduped_{DATE}.csv")
    with open(company_list_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["企業名(正規化済)", "掲載媒体数", "掲載媒体"])
        for company, medias in sorted(company_media_map.items()):
            writer.writerow([company, len(medias), " / ".join(sorted(medias))])
    print(f"  ユニーク企業数: {len(company_media_map)} → {os.path.basename(company_list_path)}")

    # サマリ
    print("\n========== サマリ ==========")
    for data in all_data:
        name = data["name"]
        removed = duplicates_removed.get(name, 0)
        print(f"  {name}: {len(data['rows'])}件 (重複削除: {removed}件)")
    print(f"  全媒体ユニーク企業数: {len(company_media_map)}")


if __name__ == "__main__":
    main()
