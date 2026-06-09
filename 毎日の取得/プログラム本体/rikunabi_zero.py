from playwright.sync_api import sync_playwright
import csv
import time
import sys
import os
from datetime import datetime

# --- カテゴリ・ID・PASSの定義 ---
# 認証情報は credentials.yaml（git管理外）に記載する。
# 新しい環境では credentials.example.yaml をコピーして credentials.yaml を作成してください。
import yaml
_cred_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "credentials.yaml")
try:
    with open(_cred_path, "r", encoding="utf-8") as _f:
        CATEGORY_CONFIG = yaml.safe_load(_f)["rikunabi"]
except FileNotFoundError:
    print("認証情報ファイル credentials.yaml が見つかりません。")
    print("credentials.example.yaml をコピーして credentials.yaml を作成し、ID/PASS を記入してください。")
    sys.exit(1)

def scrape_rikunabi_ats_final(username, password, category_name):
    today_str = datetime.now().strftime('%Y%m%d')
    # Detect sandbox vs local environment
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    output_dir = os.path.join(base_dir, "output", "rikunabi")
    os.makedirs(output_dir, exist_ok=True)
    csv_file = os.path.join(output_dir, f"rikunabi_{category_name}_item_list_{today_str}.csv")
    all_job_data = []
    fieldnames = ["企業名", "求人名", "募集要項ファイル名", "募集要項リンク", "企業からのコメント"]

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            print("ログインページに移動します...")
            page.goto("https://ats.hrtech.rikunabi.com/agent/login", timeout=60000)
            page.wait_for_load_state('networkidle')
            time.sleep(0)

            print("ログイン情報を入力します...")
            try:
                page.fill('input[name="username"]', username)
                time.sleep(0)
                page.fill('input[name="password"]', password)
                time.sleep(0)
                page.click('button[type="submit"]:text(\"ログイン\")')
                print("ログイン後のページが表示されるのを待ちます...")
                page.wait_for_url("https://ats.hrtech.rikunabi.com/agent/upload", timeout=60000)
                page.wait_for_load_state('networkidle')
                time.sleep(0)

                # メンテナンスモーダルを閉じる (JSで強制削除)
                try:
                    modal_overlay = page.locator('.src-shared-components-molecules-Modal-styles_root-uoklK')
                    if modal_overlay.count() > 0:
                        print("メンテナンスモーダルを検出しました。JSで強制削除します...")
                        page.evaluate("""
                            document.querySelectorAll('[class*="Modal-styles_root"]').forEach(el => el.remove());
                            document.querySelectorAll('[class*="Overlay-styles_root"]').forEach(el => el.remove());
                        """)
                        time.sleep(0)
                        print("モーダルを削除しました。")
                except Exception as modal_e:
                    print(f"モーダル処理中: {modal_e}")

            except Exception as e:
                print(f"ログイン処理中にエラーが発生しました: {e}", file=sys.stderr)
                browser.close()
                return

            print("企業リストを取得します...")
            try:
                company_card_selector = '.src-shared-components-organisms-AgentUploadContent-JobOfferTable-styles_body-3bWqR > .src-shared-components-atoms-CollapsibleCard-styles_root-1w1jZ'
                company_cards = page.locator(company_card_selector)

                num_companies = company_cards.count()
                print(f"{num_companies} 件の企業が見つかりました。")

                if num_companies == 0:
                    print("企業が見つかりませんでした。セレクタを確認してください。", file=sys.stderr)
                    browser.close()
                    return

                for i in range(num_companies):
                    current_company_card = company_cards.nth(i)
                    time.sleep(0)

                    company_name_element = current_company_card.locator('.src-shared-components-organisms-AgentUploadContent-JobOfferTable-styles_card-title-axQPv')
                    if company_name_element.count() > 0:
                        company_name = company_name_element.first.text_content().strip()
                        print(f"\n--- 企業: {company_name} ({i+1}/{num_companies}) ---")
                    else:
                        print(f"企業名が見つかりませんでした。", file=sys.stderr)
                        continue

                    try:
                        # モーダル/オーバーレイが再出現していれば削除
                        page.evaluate("""
                            document.querySelectorAll('[class*="Modal-styles_root"], [class*="Overlay-styles_root"]').forEach(el => el.remove());
                        """)
                        time.sleep(0)
                        current_company_card.locator('.src-shared-components-atoms-CollapsibleCard-styles_title-28RzF').first.click(force=True)
                        page.wait_for_timeout(100)
                        time.sleep(0)
                        page.wait_for_load_state('networkidle')

                        # 🌟 追加: 企業展開後に3秒待機
                        print(f"  『{company_name}』の求人一覧を表示後、3秒間待機します...")
                        time.sleep(0)
                    except Exception as e:
                        print(f"  企業 '{company_name}' の展開中にエラーが発生しました: {e}", file=sys.stderr)
                        continue

                    position_record_selector = '.src-shared-components-atoms-CollapsibleCard-styles_content-1BHmD > .src-shared-components-organisms-AgentUploadContent-JobOfferTable-styles_record-2Y2ub'
                    position_records = current_company_card.locator(position_record_selector)

                    num_positions = position_records.count()
                    print(f"  {num_positions} 件の募集ポジションが見つかりました。")

                    for j in range(num_positions):
                        current_position_record = position_records.nth(j)
                        time.sleep(0)

                        position_name_element = current_position_record.locator('.src-shared-components-organisms-AgentUploadContent-JobOfferTable-styles_card-title-axQPv')
                        if position_name_element.count() > 0:
                            position_name = position_name_element.first.text_content().strip()
                            print(f"    --- 求人: {position_name} ({j+1}/{num_positions}) ---")
                        else:
                            print(f"求人名が見つかりませんでした。", file=sys.stderr)
                            continue

                        try:
                            page.evaluate('document.querySelectorAll(\'[class*="Modal-styles_root"], [class*="Overlay-styles_root"]\').forEach(el => el.remove());')
                            current_position_record.locator('.src-shared-components-atoms-CollapsibleCard-styles_title-28RzF').first.click(force=True)
                            page.wait_for_timeout(100)
                            time.sleep(0)
                            page.wait_for_load_state('networkidle')

                            # 🌟 追加: 求人詳細表示後に2秒待機
                            print(f"    『{position_name}』の詳細を表示後、2秒間待機します...")
                            time.sleep(0)
                        except Exception as e:
                            print(f"    求人 '{position_name}' の詳細展開中にエラーが発生しました: {e}", file=sys.stderr)
                            page.wait_for_timeout(100)
                            continue

                        job_offer_link = ""
                        job_offer_filename = ""
                        company_comment = ""

                        try:
                            job_offer_row = current_position_record.locator('.src-shared-components-organisms-AgentUploadContent-JobOfferTable-styles_content-row-2yswS:has-text(\"募集要項\")')
                            job_offer_element = job_offer_row.locator('.src-shared-components-organisms-AgentUploadContent-JobOfferTable-styles_value-cell-uhsxc a.src-shared-components-atoms-FileLink-styles_root-xe4LO')

                            if job_offer_element.count() > 0:
                                job_offer_link = job_offer_element.first.get_attribute('href')
                                job_offer_filename = job_offer_element.first.text_content().strip()
                                print(f"      募集要項ファイル名: {job_offer_filename}")
                                if job_offer_link and job_offer_link.startswith('/'):
                                    base_url = page.url.split('/agent/')[0]
                                    job_offer_link = f"{base_url}{job_offer_link}"
                                print(f"      募集要項リンク: {job_offer_link}")
                            else:
                                print("      募集要項リンクが見つかりませんでした。")

                            comment_row = current_position_record.locator('.src-shared-components-organisms-AgentUploadContent-JobOfferTable-styles_content-row-2yswS:has-text(\"企業からのコメント\")')
                            comment_element = comment_row.locator('.src-shared-components-organisms-AgentUploadContent-JobOfferTable-styles_value-cell-uhsxc')

                            if comment_element.count() > 0:
                                company_comment = comment_element.first.text_content().strip()
                                print(f"      企業からのコメント:\n{company_comment[:100]}...")
                            else:
                                print("      企業からのコメントが見つかりませんでした。")

                        except Exception as e:
                            print(f"    求人 '{position_name}' の詳細情報取得中にエラーが発生しました: {e}", file=sys.stderr)

                        all_job_data.append({
                            "企業名": company_name,
                            "求人名": position_name,
                            "募集要項ファイル名": job_offer_filename,
                            "募集要項リンク": job_offer_link,
                            "企業からのコメント": company_comment
                        })

                        try:
                            current_position_record.locator('.src-shared-components-atoms-CollapsibleCard-styles_title-28RzF').first.click(force=True)
                            page.wait_for_timeout(100)
                            time.sleep(0)
                        except Exception as e:
                            print(f"    求人 '{position_name}' の詳細閉じ中にエラーが発生しました: {e}", file=sys.stderr)

                    try:
                        current_company_card.locator('.src-shared-components-atoms-CollapsibleCard-styles_title-28RzF').first.click(force=True)
                        page.wait_for_timeout(100)
                        time.sleep(0)
                    except Exception as e:
                        print(f"  企業 '{company_name}' のリスト閉じ中にエラーが発生しました: {e}", file=sys.stderr)

            except Exception as e:
                print(f"企業リストの処理中にエラーが発生しました: {e}", file=sys.stderr)

            if all_job_data:
                try:
                    with open(csv_file, 'w', newline='', encoding='utf-8') as output_file:
                        dict_writer = csv.DictWriter(output_file, fieldnames=fieldnames)
                        dict_writer.writeheader()
                        dict_writer.writerows(all_job_data)
                    print(f"\nスクレイピング完了。データは '{csv_file}' に保存されました。")
                except Exception as e:
                    print(f"CSVファイルへの書き込み中にエラーが発生しました: {e}", file=sys.stderr)
            else:
                print("\n取得できるデータがありませんでした。セレクタやウェブサイトの構造を確認してください。")

            browser.close()

    except Exception as e:
        print(f"Playwrightの初期化または実行中にエラーが発生しました: {e}", file=sys.stderr)

# ---- メイン部分 ----
if __name__ == "__main__":
    target_category = sys.argv[1] if len(sys.argv) > 1 else None

    if target_category:
        matched = False
        for config in CATEGORY_CONFIG:
            if config['カテゴリ名'] == target_category:
                print(f"\n====== カテゴリ: {config['カテゴリ名']} ======")
                scrape_rikunabi_ats_final(config["ID"], config["PASS"], config["カテゴリ名"])
                print(f"====== {config['カテゴリ名']} 完了 ======\n")
                matched = True
                break
        if not matched:
            print(f"指定されたカテゴリ '{target_category}' が見つかりません。利用可能カテゴリ:")
            for config in CATEGORY_CONFIG:
                print(f" - {config['カテゴリ名']}")
    else:
        for config in CATEGORY_CONFIG:
            print(f"\n====== カテゴリ: {config['カテゴリ名']} ======")
            scrape_rikunabi_ats_final(config["ID"], config["PASS"], config["カテゴリ名"])
            print(f"====== {config['カテゴリ名']} 完了 ======\n")
            time.sleep(0)
