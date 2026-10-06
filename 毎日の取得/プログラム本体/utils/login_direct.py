
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import time

def login_hrmos(email, password, login_url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--disable-extensions')
    options.add_argument('--remote-debugging-port=0')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get(login_url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email")))

    driver.find_element(By.NAME, "email").send_keys(email)
    driver.find_element(By.NAME, "password").send_keys(password)
    time.sleep(1)

    login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    driver.execute_script("arguments[0].scrollIntoView(true);", login_button)
    time.sleep(0.3)
    driver.execute_script("arguments[0].click();", login_button)

    # ✅ ログイン成功確認（例：企業一覧リンクが表示されるまで待つ）
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href^='/agent/corporates/']"))
        )
        print("✅ ログイン成功")
    except TimeoutException:
        print("❌ ログイン失敗または画面遷移が未完了")
        driver.save_screenshot("login_failed.png")
        raise

    return driver
def login_talentio(email, password, login_url, max_retries=3):
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import (
        ElementNotInteractableException, TimeoutException, StaleElementReferenceException,
    )
    from webdriver_manager.chrome import ChromeDriverManager
    import os, time, datetime

    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')  # デバッグ時OFF
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--disable-extensions')
    options.add_argument('--remote-debugging-port=0')
    options.add_argument('--window-size=1280,900')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    last_err = None
    for attempt in range(1, max_retries + 1):
        try:
            driver.get(login_url)
            wait = WebDriverWait(driver, 20)
            # presence だけだと描画前に send_keys して element not interactable になるので
            # 可視化・クリック可能まで待つ
            email_el = wait.until(EC.visibility_of_element_located((By.ID, "email")))
            pw_el = wait.until(EC.visibility_of_element_located((By.ID, "password")))
            email_el.clear()
            email_el.send_keys(email)
            pw_el.clear()
            pw_el.send_keys(password)
            btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
            btn.click()

            # ✅ ログイン直後に強制で求人一覧に移動
            WebDriverWait(driver, 20).until(EC.url_contains("/candidate_activities"))
            driver.get("https://agent.talentio.com/r/ats/requisitions?sort=updated_at&desc=true")
            return driver

        except (ElementNotInteractableException, TimeoutException, StaleElementReferenceException) as e:
            last_err = e
            os.makedirs("logs", exist_ok=True)
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            shot = f"logs/talentio_login_fail_{ts}_try{attempt}.png"
            try:
                driver.save_screenshot(shot)
            except Exception:
                shot = "(スクショ保存失敗)"
            print(f"⚠️ talentio ログイン試行 {attempt}/{max_retries} 失敗: {type(e).__name__}: "
                  f"{str(e).splitlines()[0]} | url={driver.current_url} | screenshot={shot}")
            time.sleep(3 * attempt)

    driver.quit()
    raise last_err

def login_jobcan(email, password, login_url):
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import WebDriverException, TimeoutException

    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument("--start-maximized")
        # options.add_argument("--headless")  # 必要なら有効化

        driver = webdriver.Chrome(options=options)
        driver.get(login_url)

        # email入力を待機
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "agent_email"))
        )
        driver.find_element(By.ID, "agent_email").send_keys(email)

        # password入力を待機
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "agent_password"))
        )
        driver.find_element(By.ID, "agent_password").send_keys(password)

        # ログインボタン押下（name="commit"）
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "commit"))
        )
        driver.find_element(By.NAME, "commit").click()

        # 遷移後のページの何かを待機（例：ダッシュボードが開くなど）
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".l-sidebar"))
        )

        return driver

    except TimeoutException as e:
        print("⏱️ 要素の読み込みに時間がかかりすぎました:", e)
        driver.quit()
        raise e

    except WebDriverException as e:
        print("🛑 WebDriverエラー発生:", e)
        driver.quit()
        raise e
    