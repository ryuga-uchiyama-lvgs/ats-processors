import pandas as pd
import csv
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

def crawl_site(driver, date_str, media_name, filename):
    results = []
    company_links = driver.find_elements(By.CSS_SELECTOR, "a[href^='/agent/corporates/']")

    for company_link in company_links:
        try:
            company_name = company_link.find_element(By.CSS_SELECTOR, "span.normal").text.strip()
            href = company_link.get_attribute("href")
            driver.execute_script("window.open(arguments[0]);", href)
            driver.switch_to.window(driver.window_handles[1])
            time.sleep(2)

            job_elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='/jobs/'] span.normal")
            for job in job_elements:
                job_title = job.text.strip()
                parent = job.find_element(By.XPATH, "./ancestor::a[1]")
                job_url = parent.get_attribute("href")

                results.append({
                    "取得日": date_str,
                    "媒体名": media_name,
                    "会社名": company_name,
                    "求人ページ用": job_url,
                    "募集職種": job_title,
                    "求人カテゴリ": "",
                    "雇用形態": "",
                    "募集人数": "",
                    "概要・業務内容": "",
                    "必須スキル・経験": "",
                    "歓迎スキル・経験": "",
                    "求める人物像": "",
                    "勤務時間": "",
                    "休日・休暇": "",
                    "想定給与": ""
                })

            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        except Exception as e:
            print(f"❌ {company_name} | エラー: {e}")
            continue

    pd.DataFrame(results).to_csv(filename, index=False)
    print(f"✅ [hrmos] 出力完了: {filename}")


def crawl_talentio(driver, date_str, media_name, filename):
    results = []

    while True:
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table tr.table__row--hoverable"))
            )
            print("📄 正しい求人行の描画を検知")
        except:
            print("❌ 求人行が見つかりません")
            break

        rows = driver.find_elements(By.CSS_SELECTOR, "table tr.table__row--hoverable")
        print(f"🔍 正常行数: {len(rows)}")

        for row in rows:
            try:
                cols = row.find_elements(By.TAG_NAME, "td")
                job_title = cols[2].text.strip() if len(cols) > 2 else ""
                company = cols[3].text.strip() if len(cols) > 3 else ""

                results.append({
                    "取得日": date_str,
                    "媒体名": media_name,
                    "会社名": company,
                    "求人名": job_title
                })
            except Exception as e:
                print(f"❌ 行取得失敗: {e}")
                continue

        # 次ページが押せるか確認
        # (2025年10月にTalentio側の構造変更あり: a[aria-label] → アイコン入りbutton)
        try:
            next_btn = driver.find_element(
                By.XPATH,
                '//ul[contains(@class,"pagination__paginator")]'
                '//i[contains(@class,"fa-angle-right")]/ancestor::button[1]'
            )
            parent_li = next_btn.find_element(By.XPATH, './ancestor::li[1]')
            if "pagination__item--disabled" in parent_li.get_attribute("class") or next_btn.get_attribute("disabled"):
                print("⏹ 最終ページに到達しました")
                break
            else:
                print("➡️ 次ページへ遷移")
                driver.execute_script("arguments[0].click();", next_btn)
                time.sleep(2)
        except Exception as e:
            print(f"⛔ ページネーションのクリック失敗: {e}")
            break


    pd.DataFrame(results).to_csv(filename, index=False)
    print(f"✅ [talentio] 出力完了: {filename}")

def get_job_list(driver):
    from selenium.webdriver.common.by import By
    import time
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    job_elements = driver.find_elements(By.CSS_SELECTOR, ".p-jobOffer__NameInTable")
    job_list = []
    for job_el in job_elements:
        job_title = job_el.text.strip()
        job_el.click()
        time.sleep(1)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "p-personalInfo__table"))
        )
        job_url = driver.current_url
        job_list.append((job_title, job_url))
        driver.back()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "p-jobOffer__NameInTable"))
        )
    return job_list

import csv
import time
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

FIELDS_MAP = {
    # 会社名はあとで企業切替時の値をセット
    "求人ページ用": None,  # URLは詳細遷移時に取得
    "募集職種": "管理用求人名",
    "求人カテゴリ": "求人カテゴリ",
    "雇用形態": "雇用形態",
    "募集人数": "定員(募集人数)",
    "概要・業務内容": "募集要項",
    "必須スキル・経験": "必須スキル・経験",
    "歓迎スキル・経験": "歓迎スキル・経験",
    "求める人物像": "求める人物像",
    "勤務時間": "勤務時間",
    "休日・休暇": "休日・休暇",
    "想定給与": "想定給与",
}

CSV_COLUMNS = [
    "取得日", "媒体名", "会社名", "求人ページ用", "募集職種", "求人カテゴリ", "雇用形態",
    "募集人数", "概要・業務内容", "必須スキル・経験", "歓迎スキル・経験", "求める人物像",
    "勤務時間", "休日・休暇", "想定給与"
]

def extract_jobcan_details(driver, fields):
    from selenium.webdriver.common.by import By
    details = {}
    for col_name, th_label in fields.items():
        if th_label is None:
            continue
        value = ""
        try:
            value = driver.find_element(
                By.XPATH, f'//th[text()="{th_label}"]/following-sibling::td/pre'
            ).text.strip()
        except Exception:
            try:
                value = driver.find_element(
                    By.XPATH, f'//th[text()="{th_label}"]/following-sibling::td'
                ).text.strip()
            except Exception:
                value = ""
        details[col_name] = value
    return details

def crawl_jobcan(driver, today, media_name, filename):
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(CSV_COLUMNS)

        select_elem = Select(driver.find_element(By.ID, "change_agent_client"))
        companies = [
            (option.get_attribute("value"), option.text.strip())
            for option in select_elem.options
            if option.get_attribute("value")
        ]

        for idx, (value, company_name) in enumerate(companies):
            try:
                print(f"\n🏢 [{idx+1}/{len(companies)}] 企業切替: {company_name}")
                select_elem = Select(driver.find_element(By.ID, "change_agent_client"))
                select_elem.select_by_value(value)
                time.sleep(2)

                driver.get("https://ats.jobcan.jp/job_offers")
                print(f"  🌐 現在URL: {driver.current_url}")
                time.sleep(3)

                try:
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "p.p-jobOffer__NameInTable"))
                    )
                except Exception as e:
                    print(f"  ⏰ [WARN] 求人リスト要素が15秒以内に見つかりません: {e}")

                job_elements = driver.find_elements(By.CSS_SELECTOR, "p.p-jobOffer__NameInTable")
                print(f"  🔎 求人数: {len(job_elements)}")

                if not job_elements:
                    print(f"  🛑 求人が見つかりません（企業: {company_name}）")
                    continue

                # ページネーション含めて全求人取得
                while True:
                    job_elements = driver.find_elements(By.CSS_SELECTOR, "p.p-jobOffer__NameInTable")
                    for index in range(len(job_elements)):
                        try:
                            job_elements = driver.find_elements(By.CSS_SELECTOR, "p.p-jobOffer__NameInTable")
                            job = job_elements[index]
                            driver.execute_script("arguments[0].click();", job)
                            time.sleep(2)

                            details = extract_jobcan_details(driver, FIELDS_MAP)
                            row = [
                                today,                # 取得日
                                media_name,           # 媒体名
                                company_name,         # 会社名（企業切替名をそのまま入れる！）
                                driver.current_url,   # 求人ページ用
                                details.get("募集職種", ""),
                                details.get("求人カテゴリ", ""),
                                details.get("雇用形態", ""),
                                details.get("募集人数", ""),
                                details.get("概要・業務内容", ""),
                                details.get("必須スキル・経験", ""),
                                details.get("歓迎スキル・経験", ""),
                                details.get("求める人物像", ""),
                                details.get("勤務時間", ""),
                                details.get("休日・休暇", ""),
                                details.get("想定給与", ""),
                            ]
                            writer.writerow(row)
                            print(f"    ✅ {details.get('募集職種', '(No Name)')} 取得")

                            driver.back()
                            time.sleep(2)
                        except Exception as e:
                            print(f"    ⚠️ 求人詳細取得エラー: {e}")
                            try:
                                driver.back()
                                time.sleep(2)
                            except Exception:
                                pass
                            continue

                    try:
                        next_button = driver.find_element(By.CSS_SELECTOR, 'a[aria-label="Next"]')
                        aria_hidden = next_button.get_attribute("aria-hidden")
                        if aria_hidden == "true":
                            print("  ⏹ 最終ページに到達")
                            break
                        else:
                            driver.execute_script("arguments[0].click();", next_button)
                            time.sleep(3)
                    except Exception:
                        print("  ⛔ ページネーション終了またはエラー")
                        break

            except Exception as e:
                print(f"❌ {company_name} 切替時エラー: {e}")
                time.sleep(2)
                continue
