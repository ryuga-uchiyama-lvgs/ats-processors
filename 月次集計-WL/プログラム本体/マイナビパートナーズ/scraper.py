#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
マイナビパートナーズ 求人情報スクレイピングスクリプト
"""

import csv
import time
import random
from datetime import datetime
from playwright.sync_api import sync_playwright

# ===== 設定（先頭で定義） =====
BASE_URL = "https://mpt-shoukai.mynavi.jp/recruit"
OUTPUT_FILE = f"mynavi_partners_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
MAX_RETRIES = 3
WAIT_MIN = 1
WAIT_MAX = 5

# セレクタ定義
SELECTORS = {
    'job_card': '.entry-box',
    'job_no': '.label-offer',
    'status': '.label-recruit',
    'title': 'h2',
    'company': '.company-name',
    'tags': '.tag-list li',
    'detail_link': 'a[href*="/recruit/"]',
    'dl_elements': 'dl',
    'dt': 'dt',
    'dd': 'dd',
    'next_button': 'a:has-text("次へ")',
}

# 出力カラム
CSV_COLUMNS = [
    '求人No',
    '募集ステータス',
    '求人タイトル',
    '企業名',
    'タグ',
    '勤務地',
    '給与',
    '募集ポジション',
    '勤務時間',
    '雇用形態',
    '詳細URL'
]


def random_wait():
    """ランダムなwait時間を設定"""
    wait_time = random.uniform(WAIT_MIN, WAIT_MAX)
    print(f"  待機中... ({wait_time:.1f}秒)")
    time.sleep(wait_time)


def parse_job_card(card):
    """求人カードから情報を抽出"""
    job = {}

    try:
        # 求人No
        job_no_elem = card.query_selector(SELECTORS['job_no'])
        job['求人No'] = job_no_elem.text_content().strip() if job_no_elem else ''

        # 募集ステータス
        status_elem = card.query_selector(SELECTORS['status'])
        job['募集ステータス'] = status_elem.text_content().strip() if status_elem else ''

        # 求人タイトル
        title_elem = card.query_selector(SELECTORS['title'])
        job['求人タイトル'] = title_elem.text_content().strip() if title_elem else ''

        # 企業名
        company_elem = card.query_selector(SELECTORS['company'])
        job['企業名'] = company_elem.text_content().strip() if company_elem else '社名非公開'

        # タグ
        tag_elems = card.query_selector_all(SELECTORS['tags'])
        tags = [tag.text_content().strip() for tag in tag_elems]
        job['タグ'] = ', '.join(tags) if tags else ''

        # 詳細情報（dl/dt/dd構造）
        job['勤務地'] = ''
        job['給与'] = ''
        job['募集ポジション'] = ''
        job['勤務時間'] = ''
        job['雇用形態'] = ''

        dl_elements = card.query_selector_all(SELECTORS['dl_elements'])
        for dl in dl_elements:
            dt = dl.query_selector(SELECTORS['dt'])
            dd = dl.query_selector(SELECTORS['dd'])

            if dt and dd:
                label = dt.text_content().strip()
                value = ' '.join(dd.text_content().strip().split())

                if label == '勤務地':
                    job['勤務地'] = value
                elif label == '給与':
                    job['給与'] = value
                elif label == '募集ポジション':
                    job['募集ポジション'] = value
                elif label == '勤務時間':
                    job['勤務時間'] = value
                elif label == '雇用形態':
                    job['雇用形態'] = value

        # 詳細URL
        detail_links = card.query_selector_all('a')
        for link in detail_links:
            href = link.get_attribute('href')
            if href and '/recruit/' in href and '/company/' not in href and '/entry/' not in href and '/favorite/' not in href:
                if href.startswith('https://'):
                    job['詳細URL'] = href
                else:
                    job['詳細URL'] = f'https://mpt-shoukai.mynavi.jp{href}'
                break

        return job

    except Exception as e:
        print(f"  ⚠ カード解析エラー: {e}")
        return None


def scrape_page(page, page_num):
    """1ページ分の求人情報を取得"""
    print(f"ページ {page_num} を処理中...")

    jobs = []

    try:
        # ページが完全に読み込まれるまで待機
        page.wait_for_selector(SELECTORS['job_card'], timeout=30000)
        random_wait()

        # 求人カードを全て取得
        job_cards = page.query_selector_all(SELECTORS['job_card'])
        print(f"  {len(job_cards)} 件の求人を発見")

        # 各カードから情報を抽出
        for i, card in enumerate(job_cards, 1):
            job = parse_job_card(card)
            if job:
                jobs.append(job)
                print(f"  [{i}/{len(job_cards)}] {job.get('求人No', 'N/A')} - {job.get('求人タイトル', 'N/A')[:50]}")

        return jobs, True

    except Exception as e:
        print(f"  ✗ ページ処理エラー: {e}")
        return jobs, False


def scrape():
    """メイン処理"""
    print("=" * 80)
    print("マイナビパートナーズ 求人情報スクレイピング開始")
    print("=" * 80)
    print(f"対象URL: {BASE_URL}")
    print(f"出力ファイル: {OUTPUT_FILE}")
    print()

    all_jobs = []

    with sync_playwright() as p:
        # ブラウザ起動（ヘッドレスモード）
        print("ブラウザを起動中...")
        browser = p.chromium.launch(headless=True)

        # コンテキスト作成（User-Agent設定）
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        page = context.new_page()

        try:
            # 最初のページにアクセス
            print(f"アクセス中: {BASE_URL}")
            page.goto(BASE_URL, wait_until='domcontentloaded', timeout=60000)
            random_wait()

            page_num = 1

            while True:
                # 現在のページをスクレイピング
                jobs, success = scrape_page(page, page_num)

                if not success:
                    print(f"⚠ ページ {page_num} の処理に失敗しました")
                    break

                all_jobs.extend(jobs)
                print(f"✓ ページ {page_num} 完了: {len(jobs)} 件取得（累計: {len(all_jobs)} 件）")
                print()

                # 次へボタンを探す
                try:
                    next_button = page.query_selector(SELECTORS['next_button'])
                    if next_button and next_button.is_visible():
                        print("次のページへ移動中...")
                        next_button.click()
                        page_num += 1
                        random_wait()
                    else:
                        print("✓ 全ページの取得が完了しました")
                        break
                except Exception as e:
                    print(f"次ページ移動エラー（最終ページと判断）: {e}")
                    break

        except Exception as e:
            print(f"✗ スクレイピングエラー: {e}")

        finally:
            print("ブラウザを終了中...")
            browser.close()

    # CSV出力
    print()
    print("=" * 80)
    print(f"CSV出力中: {OUTPUT_FILE}")
    print("=" * 80)

    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            writer.writerows(all_jobs)

        print(f"✓ 完了: {len(all_jobs)} 件の求人情報を {OUTPUT_FILE} に保存しました")

    except Exception as e:
        print(f"✗ CSV出力エラー: {e}")

    print()
    print("=" * 80)
    print("スクレイピング完了")
    print("=" * 80)


if __name__ == '__main__':
    scrape()
