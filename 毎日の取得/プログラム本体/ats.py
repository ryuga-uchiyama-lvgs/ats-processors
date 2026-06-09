import pandas as pd
import yaml
import datetime
import os
import argparse
from utils.login_direct import login_hrmos, login_talentio, login_jobcan
from utils.scraping import crawl_site, crawl_talentio, crawl_jobcan

def load_config():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ATS クローラー")
    parser.add_argument("--media", type=str, default=None,
                        help="対象媒体: hrmos / talentio / jobcan")
    args = parser.parse_args()

    config = load_config()
    today = datetime.date.today().strftime("%Y-%m-%d")
    # 対象媒体：--media 引数で指定、未指定時はスクリプト内のデフォルト値を使用
    use_media = args.media if args.media else "talentio"  # デフォルト値



    if use_media == "hrmos":
        login_func = login_hrmos
        crawl_func = crawl_site
        login_url = config["login"]["url"]
    elif use_media == "talentio":
        login_func = login_talentio
        crawl_func = crawl_talentio
        login_url = config["login"]["talentio_url"]
    elif use_media == "jobcan":
        login_func = login_jobcan
        crawl_func = crawl_jobcan
        login_url = config["login"]["jobcan_url"] 
    elif use_media == "herp":
        login_func = login_herp
        crawl_func = crawl_herp
        login_url = config["login"]["herp_url"] 
    elif use_media == "rikunabi-hr":
        login_func = login_rikunabi
        crawl_func = crawl_rikunabi
        login_url = config["login"]["rikunabi_url"] 
    elif use_media == "gt":
        login_func = login_gt
        crawl_func = crawl_gt
        login_url = config["login"]["gt_url"] 
    elif use_media == "gt":
        login_func = login_gt
        crawl_func = crawl_gt
        login_url = config["login"]["gt_url"] 
    elif use_media == "gt":
        login_func = login_gt
        crawl_func = crawl_gt
        login_url = config["login"]["gt_url"] 




    print(f"📌 開始媒体: {use_media}")
    print(f"📅 取得日: {today}")
    print(f"🔐 ログインURL: {login_url}")

    output_dir = f"output/{use_media}"
    os.makedirs(output_dir, exist_ok=True)

    for category, creds in config["login"]["accounts"].items():
        print(f"\n=== 🏁 [{category}] ログイン処理開始（{use_media}）===")
        print(f"📨 ID: {creds['email']}")

        try:
            driver = login_func(creds["email"], creds["password"], login_url)
            print(f"✅ ログイン成功：{category}")
        except Exception as e:
            print(f"❌ ログイン失敗：{category} | エラー内容: {e}")
            continue

        filename = f"{output_dir}/{use_media}_{category}_item_list_{today}.csv"
        print(f"📥 クローリング開始: {filename}")
        try:
            crawl_func(driver, today, use_media, filename)
            print(f"📤 クローリング完了: {filename}")
        except Exception as e:
            print(f"⚠️ クローリング中にエラー：{e}")
        finally:
            driver.quit()
            print(f"🧹 ドライバー終了：{category}")