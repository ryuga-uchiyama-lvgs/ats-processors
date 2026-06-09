import asyncio
import csv
import json
from datetime import datetime
from playwright.async_api import async_playwright
import re


class BabNaviScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.all_jobs = []

    async def scrape_page(self, page):
        """現在のページから全ての求人情報を取得"""
        await page.wait_for_selector('.mod-jobResultBox', timeout=10000)

        jobs = await page.evaluate('''() => {
            const jobBoxes = document.querySelectorAll('.mod-jobResultBox');
            const results = [];

            jobBoxes.forEach(jobBox => {
                // タイトルとURL
                const titleElement = jobBox.querySelector('h2.mod-h1 a');
                const title = titleElement?.textContent?.trim() || '';
                const jobUrl = titleElement?.href || '';

                // 会社名
                const company = jobBox.querySelector('.job-excerpt-wrap p.job-excerpt a')?.textContent?.trim() || '';

                // 画像URL
                const image = jobBox.querySelector('.job-photo img')?.src || '';

                // タグ/アイコン
                const icons = Array.from(jobBox.querySelectorAll('.mod-iconSearchKey span.icon')).map(
                    icon => icon.textContent?.trim()
                ).filter(Boolean);

                // テーブルデータ
                const tableRows = jobBox.querySelectorAll('table.mod-table2 tr');
                const tableData = {};
                tableRows.forEach(row => {
                    const th = row.querySelector('th')?.textContent?.trim();
                    const td = row.querySelector('td')?.textContent?.trim();
                    if (th && td) {
                        tableData[th] = td;
                    }
                });

                results.push({
                    title,
                    jobUrl,
                    company,
                    image,
                    icons,
                    ...tableData
                });
            });

            return results;
        }''')

        return jobs

    async def check_next_page(self, page):
        """次のページが存在するかチェック"""
        next_button = await page.query_selector('.mod-pagination .next a')
        if next_button:
            next_url = await next_button.get_attribute('href')
            return next_url
        return None

    async def scrape_all_pages(self):
        """全ページをスクレイピング"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            current_url = self.base_url
            page_number = 1

            while current_url:
                print(f"ページ {page_number} をスクレイピング中: {current_url}")

                # ページに移動
                await page.goto(current_url, wait_until='networkidle', timeout=60000)

                # ページから求人情報を取得
                jobs = await self.scrape_page(page)
                self.all_jobs.extend(jobs)

                print(f"  {len(jobs)} 件の求人を取得しました（合計: {len(self.all_jobs)} 件）")

                # 次のページをチェック
                next_url = await self.check_next_page(page)

                if next_url:
                    # 相対URLを絶対URLに変換
                    if next_url.startswith('/'):
                        base = 'https://bab-navi.dandi.co.jp'
                        current_url = base + next_url
                    else:
                        current_url = next_url
                    page_number += 1

                    # サーバーへの負荷を軽減するため少し待つ
                    await asyncio.sleep(1)
                else:
                    print("次のページが見つかりません。スクレイピング完了。")
                    break

            await browser.close()

        return self.all_jobs

    def save_to_csv(self, filename=None):
        """CSVファイルに保存"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'babnavi_jobs_{timestamp}.csv'

        if not self.all_jobs:
            print("保存するデータがありません。")
            return

        # すべてのキーを取得（全ての求人情報から）
        all_keys = set()
        for job in self.all_jobs:
            # iconsは配列なので特別扱い
            job_keys = {k for k in job.keys() if k != 'icons'}
            all_keys.update(job_keys)

        # iconsは最後に追加
        fieldnames = ['title', 'jobUrl', 'company', 'image']
        for key in sorted(all_keys):
            if key not in fieldnames:
                fieldnames.append(key)
        fieldnames.append('icons')

        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for job in self.all_jobs:
                # iconsを文字列に変換
                job_copy = job.copy()
                if 'icons' in job_copy:
                    job_copy['icons'] = ', '.join(job_copy['icons'])
                writer.writerow(job_copy)

        print(f"\nCSVファイルに保存しました: {filename}")
        print(f"合計 {len(self.all_jobs)} 件の求人情報")

    def save_to_json(self, filename=None):
        """JSONファイルに保存"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'babnavi_jobs_{timestamp}.json'

        if not self.all_jobs:
            print("保存するデータがありません。")
            return

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.all_jobs, f, ensure_ascii=False, indent=2)

        print(f"\nJSONファイルに保存しました: {filename}")
        print(f"合計 {len(self.all_jobs)} 件の求人情報")


async def main():
    # スクレイピング対象のURL
    base_url = 'https://bab-navi.dandi.co.jp/zenkoku/PC13,14,12,11,23,27,40'

    # スクレイパーのインスタンスを作成
    scraper = BabNaviScraper(base_url)

    # 全ページをスクレイピング
    print("スクレイピングを開始します...")
    await scraper.scrape_all_pages()

    # 結果を保存
    scraper.save_to_csv()
    scraper.save_to_json()


if __name__ == '__main__':
    asyncio.run(main())
