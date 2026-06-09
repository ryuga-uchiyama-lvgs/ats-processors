
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
def login_talentio(email, password, login_url):
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager

    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')  # デバッグ時OFF
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--disable-extensions')
    options.add_argument('--remote-debugging-port=0')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get(login_url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email")))

    driver.find_element(By.ID, "email").send_keys(email)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    # ✅ ログイン直後に強制で求人一覧に移動
    WebDriverWait(driver, 10).until(EC.url_contains("/candidate_activities"))
    driver.get("https://agent.talentio.com/r/ats/requisitions?sort=updated_at&desc=true")

    return driver

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
    