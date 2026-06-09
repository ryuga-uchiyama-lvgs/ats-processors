"""
atGP求人情報スクレイピングスクリプト
prefecture-id.csvから都道府県IDを読み込み、各都道府県の求人情報を取得します。
"""

import asyncio
import csv
import json
from datetime import datetime
from playwright.async_api import async_playwright, Page
import re
from typing import List, Dict, Optional


class AtGPScraper:
    """atGP求人サイトのスクレイパー"""

    BASE_URL = "https://www.atgp.jp/search/top/search_result"

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.results = []

    async def scrape_page(self, page: Page) -> List[Dict]:
        """1ページ分の求人情報を取得"""

        # ポップアップが表示される場合は閉じる
        try:
            close_button = page.locator('button:has-text("閉じる")')
            if await close_button.count() > 0:
                await close_button.click()
                await asyncio.sleep(0.5)
        except Exception:
            pass

        # ページが完全に読み込まれるまで待機
        await page.wait_for_selector('.p-joboffer-list', timeout=10000)

        # JavaScriptで求人情報を抽出
        jobs_data = await page.evaluate("""
            () => {
                const jobOfferList = document.querySelectorAll('.p-joboffer-list');
                const jobs = [];

                jobOfferList.forEach((job) => {
                    try {
                        const tableData = {};
                        const tableRows = job.querySelectorAll('.p-joboffer-list__info__table tr');
                        tableRows.forEach(row => {
                            const th = row.querySelector('th')?.textContent?.trim();
                            const td = row.querySelector('td')?.textContent?.trim().replace(/\\s+/g, ' ');
                            if (th && td) {
                                tableData[th] = td;
                            }
                        });

                        const jobData = {
                            updateDate: job.querySelector('.p-joboffer-list__date_area__date')?.textContent?.trim() || '',
                            isNew: job.querySelector('.p-joboffer-list__date_area__new') ? true : false,
                            title: job.querySelector('.p-joboffer-list__heading-area__heading')?.textContent?.trim() || '',
                            detailUrl: job.querySelector('.jobinfo-title-link')?.getAttribute('href') || '',
                            companyName: (
                                job.querySelector('.jobinfo-sub-title-account-name')?.textContent?.trim() ||
                                job.querySelector('.jobinfo-sub-title-account-name-sp-not-photo')?.textContent?.trim() || ''
                            ),
                            categoryTags: Array.from(job.querySelectorAll('.p-joboffer-list__heading-area__category__list li span'))
                                .map(span => span.textContent?.trim()).filter(t => t),
                            jobType: tableData['職種'] || '',
                            location: tableData['勤務地'] || '',
                            employmentType: tableData['雇用形態'] || '',
                            salary: tableData['給与'] || '',
                            companyPageUrl: job.querySelector('a[href*="company_recruit"]')?.getAttribute('href') || '',
                        };

                        jobs.push(jobData);
                    } catch (e) {
                        console.error('Error parsing job:', e);
                    }
                });

                return jobs;
            }
        """)

        return jobs_data

    async def get_total_pages(self, page: Page) -> int:
        """総ページ数を取得"""
        try:
            # ページネーションから最大ページ番号を取得
            max_page = await page.evaluate("""
                () => {
                    const links = Array.from(document.querySelectorAll('a'));
                    const numberLinks = links.filter(link => {
                        const text = link.textContent?.trim();
                        return text && /^\\d+$/.test(text);
                    });

                    if (numberLinks.length === 0) return 1;

                    const pageNumbers = numberLinks.map(link =>
                        parseInt(link.textContent?.trim() || '0')
                    );

                    return Math.max(...pageNumbers);
                }
            """)

            return max_page if max_page > 0 else 1
        except Exception as e:
            print(f"ページ数の取得に失敗: {e}")
            return 1

    async def scrape_prefecture(self, page: Page, prefecture_id: str, prefecture_name: str) -> List[Dict]:
        """特定の都道府県の求人情報を全ページから取得"""

        print(f"\n{'='*60}")
        print(f"都道府県: {prefecture_name} (ID: {prefecture_id})")
        print(f"{'='*60}")

        all_jobs = []

        # 最初のページにアクセス
        url = f"{self.BASE_URL}?prefectures={prefecture_id}"
        print(f"アクセス中: {url}")

        try:
            await page.goto(url, wait_until='networkidle', timeout=30000)
            await asyncio.sleep(2)

            # 総ページ数を取得
            total_pages = await self.get_total_pages(page)
            print(f"総ページ数: {total_pages}")

            # 各ページをスクレイピング
            for page_num in range(1, total_pages + 1):
                print(f"\nページ {page_num}/{total_pages} を処理中...")

                if page_num > 1:
                    # 2ページ目以降はURLにpage番号を追加
                    page_url = f"{url}&page={page_num}"
                    await page.goto(page_url, wait_until='networkidle', timeout=30000)
                    await asyncio.sleep(2)

                # 求人情報を取得
                jobs = await self.scrape_page(page)

                # 都道府県情報を追加
                for job in jobs:
                    job['prefecture_id'] = prefecture_id
                    job['prefecture_name'] = prefecture_name
                    job['scraped_at'] = datetime.now().isoformat()

                all_jobs.extend(jobs)
                print(f"  取得件数: {len(jobs)}件")

                # リクエスト間隔を設定（サーバーに負荷をかけないため）
                await asyncio.sleep(1)

            print(f"\n{prefecture_name}の取得完了: 合計 {len(all_jobs)}件")

        except Exception as e:
            print(f"エラー: {prefecture_name}のスクレイピング中にエラーが発生: {e}")

        return all_jobs

    async def run(self, prefecture_csv_path: str, output_json_path: str, output_csv_path: str):
        """メイン実行関数"""

        # prefecture-id.csvを読み込む
        prefectures = []
        with open(prefecture_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                prefectures.append({
                    'id': row['prefecture_id'],
                    'name': row['prefecture_name']
                })

        print(f"対象都道府県数: {len(prefectures)}")
        for pref in prefectures:
            print(f"  - {pref['name']} (ID: {pref['id']})")

        # Playwrightを起動
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            page = await context.new_page()

            # 各都道府県の求人情報を取得
            all_results = []
            for pref in prefectures:
                jobs = await self.scrape_prefecture(page, pref['id'], pref['name'])
                all_results.extend(jobs)

            await browser.close()

        # 結果を保存
        print(f"\n{'='*60}")
        print(f"スクレイピング完了: 合計 {len(all_results)}件")
        print(f"{'='*60}")

        # JSON形式で保存
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        print(f"JSONファイルを保存: {output_json_path}")

        # CSV形式で保存
        if all_results:
            with open(output_csv_path, 'w', encoding='utf-8', newline='') as f:
                # すべてのキーを取得
                fieldnames = list(all_results[0].keys())
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for job in all_results:
                    # categoryTagsをカンマ区切りの文字列に変換
                    if 'categoryTags' in job and isinstance(job['categoryTags'], list):
                        job['categoryTags'] = ', '.join(job['categoryTags'])
                    writer.writerow(job)

            print(f"CSVファイルを保存: {output_csv_path}")


async def main():
    """メイン関数"""

    # 設定
    prefecture_csv = 'prefecture-id.csv'
    output_json = f'atgp_jobs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    output_csv = f'atgp_jobs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

    # スクレイパー実行
    scraper = AtGPScraper(headless=True)
    await scraper.run(prefecture_csv, output_json, output_csv)


if __name__ == "__main__":
    print("atGP求人情報スクレイピングを開始します...")
    print(f"開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    asyncio.run(main())

    print(f"\n終了時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("スクレイピングが完了しました。")
