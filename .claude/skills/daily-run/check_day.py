"""今日が実行日かを判定する(土日・祝日・年末年始・夏季休暇は実行しない)。

内閣府の祝日CSVを参照する。出力と終了コード:
  0  RUN <曜日番号 1=月..5=金>
  1  SKIP 土日 / SKIP 祝日 <祝日名> / SKIP 年末年始 / SKIP 夏季休暇
  2  UNKNOWN <理由>(祝日CSVが取得できない・今年分が載っていない)
"""
import datetime
import sys

import requests

CSV_URL = "https://www8.cao.go.jp/chosei/shukujitsu/syukujitsu.csv"

# 一般的な休業期間 (月, 日) の範囲。両端を含む
YEAR_END = ((12, 28), (1, 4))  # 年をまたぐ
SUMMER = ((8, 12), (8, 17))  # お盆

today = datetime.date.today()
if len(sys.argv) > 1:  # 動作確認用: check_day.py 2026-11-03
    today = datetime.date.fromisoformat(sys.argv[1])
dow = today.isoweekday()

if dow >= 6:
    print("SKIP 土日")
    sys.exit(1)

md = (today.month, today.day)
if md >= YEAR_END[0] or md <= YEAR_END[1]:
    print("SKIP 年末年始")
    sys.exit(1)
if SUMMER[0] <= md <= SUMMER[1]:
    print("SKIP 夏季休暇")
    sys.exit(1)

try:
    res = requests.get(CSV_URL, timeout=30)
    res.raise_for_status()
    lines = res.content.decode("shift_jis").splitlines()[1:]
except Exception as e:
    print(f"UNKNOWN 祝日CSVを取得できません: {e}")
    sys.exit(2)

holidays = {}
for line in lines:
    date_str, _, name = line.partition(",")
    try:
        y, m, d = map(int, date_str.split("/"))
    except ValueError:
        continue
    holidays[datetime.date(y, m, d)] = name.strip()

if not any(d.year == today.year for d in holidays):
    print(f"UNKNOWN 祝日CSVに{today.year}年の祝日がありません")
    sys.exit(2)

if today in holidays:
    print(f"SKIP 祝日 {holidays[today]}")
    sys.exit(1)

print(f"RUN {dow}")
