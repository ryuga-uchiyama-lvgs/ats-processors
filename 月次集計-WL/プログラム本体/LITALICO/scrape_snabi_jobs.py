"""
LITALICO Snabi 求人情報スクレイピングスクリプト

このスクリプトは https://snabi.jp/ から複数の都道府県の求人情報を取得します。
対応都道府県: 東京、神奈川、千葉、埼玉、愛知、大阪、福岡
"""

import asyncio
import json
from typing import List, Dict
from playwright.async_api import async_playwright, Page
import csv
from datetime import datetime

# 対象の都道府県とそのID
PREFECTURES = {
    "東京": "13",
    "神奈川": "14",
    "千葉": "12",
    "埼玉": "11",
    "愛知": "23",
    "大阪": "27",
    "福岡": "40"
}


async def extract_job_data(page: Page, prefecture_name: str) -> List[Dict]:
    """
    現在のページから全ての求人情報を抽出します。

    Args:
        prefecture_name: 都道府県名

    Returns:
        求人情報の辞書のリスト
    """
    jobs = await page.evaluate("""
        () => {
            // カードコンテナを選択（旧: a[href*="/recruitments/"] は今は「詳細を見る」ボタンのみ）
            const cards = document.querySelectorAll('div.chakra-linkbox');
            const jobs = [];

            cards.forEach(card => {
                // 求人詳細ページへのリンクを取得
                const linkEl = card.querySelector('a.chakra-linkbox__overlay');
                if (!linkEl) return;
                const href = linkEl.href;
                if (!href.includes('/recruitments/') || href.includes('/recruitment_inquiries/')) return;

                // 職種セクションを取得
                const jobDescSection = Array.from(card.querySelectorAll('.chakra-stack.css-k7bpxb')).find(
                    section => section.querySelector('.css-1rmgsnc')?.textContent.trim() === '職種'
                );
                const jobDescription = jobDescSection?.querySelector('.css-1nh8hoj p')?.textContent?.trim()
                    || jobDescSection?.querySelector('.css-1nh8hoj')?.textContent?.trim() || '';

                // 給与セクションを取得
                const salarySection = Array.from(card.querySelectorAll('.chakra-stack.css-k7bpxb')).find(
                    section => section.querySelector('.css-1rmgsnc')?.textContent.trim() === '給与'
                );
                const salary = salarySection?.querySelector('.css-1nh8hoj')?.textContent?.trim() || '';

                // 勤務地セクションを取得
                const locationSection = Array.from(card.querySelectorAll('.chakra-stack.css-k7bpxb')).find(
                    section => section.querySelector('.css-1rmgsnc')?.textContent.trim() === '勤務地'
                );
                const location = locationSection?.querySelector('.css-1nh8hoj')?.textContent?.trim() || '';

                // 合理的配慮タグを取得（旧: .css-1nuruzl → 新: .css-l3st5b）
                const accommodationTags = Array.from(card.querySelectorAll('.css-l3st5b')).map(tag => tag.textContent.trim());

                jobs.push({
                    href: href,
                    id: href.split('/').pop(),
                    employmentType: card.querySelector('.css-1fj1db0')?.textContent?.trim() || '',
                    title: card.querySelector('div.css-1voz26z')?.textContent?.trim() || '',
                    companyInfo: card.querySelector('h2')?.textContent?.trim() || '',
                    jobDescription: jobDescription,
                    salary: salary,
                    location: location,
                    accommodationTags: accommodationTags
                });
            });

            return jobs;
        }
    """)

    # 都道府県名を各求人に追加
    for job in jobs:
        job['prefecture'] = prefecture_name

    return jobs


async def get_total_pages(page: Page) -> int:
    """
    全ページ数を取得します。

    Returns:
        総ページ数
    """
    pagination_info = await page.evaluate("""
        () => {
            const paginationLinks = Array.from(document.querySelectorAll('a[href*="page="]'));
            const pageNumbers = paginationLinks
                .map(link => {
                    const match = link.href.match(/page=(\\d+)/);
                    return match ? parseInt(match[1]) : 0;
                })
                .filter(num => num > 0);

            return pageNumbers.length > 0 ? Math.max(...pageNumbers) : 1;
        }
    """)

    return pagination_info


async def _goto_or_raise(page: Page, url: str):
    """指定URLに遷移し、HTTPエラー時は例外を投げる。"""
    response = await page.goto(url, wait_until="domcontentloaded")
    if response is not None and response.status >= 400:
        raise RuntimeError(
            f"HTTP {response.status} を受信しました ({url})。"
            "WAFブロックの可能性があります（User-Agent等を確認してください）。"
        )


async def scrape_prefecture_jobs(context, prefecture_name: str, prefecture_id: str) -> List[Dict]:
    """
    指定した都道府県の全ページから求人情報をスクレイピングします。

    Args:
        context: PlaywrightのBrowserContextインスタンス
        prefecture_name: 都道府県名
        prefecture_id: 都道府県ID

    Returns:
        全ての求人情報のリスト
    """
    all_jobs = []
    base_url = f"https://snabi.jp/recruitments/prefecture-{prefecture_id}"

    page = await context.new_page()

    print(f"\n【{prefecture_name}】アクセス中: {base_url}")
    await _goto_or_raise(page, base_url)
    await page.wait_for_timeout(4000)  # ページの読み込みを待つ

    # 総ページ数を取得
    total_pages = await get_total_pages(page)
    print(f"  総ページ数: {total_pages}")

    # 各ページをスクレイピング
    for page_num in range(1, total_pages + 1):
        url = f"{base_url}?page={page_num}"
        print(f"  ページ {page_num}/{total_pages} を処理中...")

        if page_num > 1:
            await _goto_or_raise(page, url)
            await page.wait_for_timeout(4000)

        # 求人情報を抽出
        jobs = await extract_job_data(page, prefecture_name)
        all_jobs.extend(jobs)
        print(f"    {len(jobs)} 件の求人を取得しました（{prefecture_name}累計: {len(all_jobs)} 件）")

    await page.close()
    return all_jobs


async def scrape_all_prefectures() -> Dict[str, List[Dict]]:
    """
    全ての対象都道府県から求人情報をスクレイピングします。

    Returns:
        都道府県名をキーとした求人情報の辞書
    """
    all_prefecture_jobs = {}

    # CloudFront WAFがheadlessのデフォルトUA(HeadlessChrome)を弾くため、
    # 通常のChrome UAを偽装する必要がある。
    user_agent = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )

    async with async_playwright() as p:
        # ブラウザを起動
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=user_agent,
            locale="ja-JP",
            viewport={"width": 1280, "height": 800},
        )

        # 各都道府県をスクレイピング
        for prefecture_name, prefecture_id in PREFECTURES.items():
            jobs = await scrape_prefecture_jobs(context, prefecture_name, prefecture_id)
            all_prefecture_jobs[prefecture_name] = jobs
            print(f"\n【{prefecture_name}】完了: {len(jobs)} 件の求人を取得")

        await context.close()
        await browser.close()

    return all_prefecture_jobs


def save_to_json(jobs: List[Dict], filename: str = None):
    """
    求人情報をJSONファイルに保存します。

    Args:
        jobs: 求人情報のリスト
        filename: 保存先のファイル名（デフォルト: snabi_jobs_YYYYMMDD_HHMMSS.json）
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"snabi_jobs_{timestamp}.json"

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)

    print(f"\nJSONファイルを保存しました: {filename}")


def save_to_csv(jobs: List[Dict], filename: str = None):
    """
    求人情報をCSVファイルに保存します。

    Args:
        jobs: 求人情報のリスト
        filename: 保存先のファイル名（デフォルト: snabi_jobs_YYYYMMDD_HHMMSS.csv）
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"snabi_jobs_{timestamp}.csv"

    if not jobs:
        print("保存する求人情報がありません")
        return

    # CSVのフィールド名
    fieldnames = [
        'id', 'prefecture', 'href', 'employmentType', 'title', 'companyName', 'companyInfo',
        'jobDescription', 'salary', 'location', 'accommodationTags'
    ]

    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for job in jobs:
            # accommodationTagsをカンマ区切りの文字列に変換
            job_copy = job.copy()
            if isinstance(job_copy.get('accommodationTags'), list):
                job_copy['accommodationTags'] = ', '.join(job_copy['accommodationTags'])
            writer.writerow(job_copy)

    print(f"CSVファイルを保存しました: {filename}")


async def main():
    """
    メイン処理
    """
    print("=" * 70)
    print("LITALICO Snabi 求人情報スクレイピング")
    print("=" * 70)
    print(f"対象都道府県: {', '.join(PREFECTURES.keys())}")
    print("=" * 70)

    # 全都道府県の求人情報をスクレイピング
    all_prefecture_jobs = await scrape_all_prefectures()

    # 統合データを作成
    all_jobs = []
    for prefecture_name, jobs in all_prefecture_jobs.items():
        all_jobs.extend(jobs)

    print("\n" + "=" * 70)
    print(f"スクレイピング完了！")
    print("=" * 70)
    print(f"総取得求人数: {len(all_jobs)} 件")
    print()
    print("【都道府県別内訳】")
    for prefecture_name, jobs in all_prefecture_jobs.items():
        print(f"  {prefecture_name}: {len(jobs)} 件")
    print("=" * 70)

    # 統合JSONファイルに保存
    save_to_json(all_jobs)

    # 統合CSVファイルに保存
    save_to_csv(all_jobs)

    # 都道府県別にも保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    for prefecture_name, jobs in all_prefecture_jobs.items():
        if jobs:
            save_to_json(jobs, f"snabi_jobs_{prefecture_name}_{timestamp}.json")
            save_to_csv(jobs, f"snabi_jobs_{prefecture_name}_{timestamp}.csv")

    # サンプルデータを表示
    if all_jobs:
        print("\n最初の求人情報（サンプル）:")
        print("-" * 70)
        sample = all_jobs[0]
        for key, value in sample.items():
            if key == 'accommodationTags' and isinstance(value, list):
                print(f"{key}: {', '.join(value[:3])}..." if len(value) > 3 else f"{key}: {', '.join(value)}")
            else:
                display_value = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                print(f"{key}: {display_value}")


if __name__ == "__main__":
    asyncio.run(main())
