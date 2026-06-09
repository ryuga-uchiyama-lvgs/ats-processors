import os
import time
import csv
import pandas as pd
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright

# --- 設定 ---
HERP_URLS = [
    ("CRG", "株式会社MIXI", "https://agent.herp.cloud/p/9GvWqB7gFWNUqhRNti-D_WfBSyoLwib2mp2NMuOmGaM"),
    ("CRG", "株式会社ミクシィ", "https://agent.herp.cloud/p/_lXE_wUck7TaeUy53TVzZrZpyRe32v2ved-aua9ELVA"),
    ("CRG", "株式会社10ANTZ", "https://agent.herp.cloud/p/xHMeMdad-FJYGq1AkTojk8er-tcPS0rFEfknowiQd1w"),
    ("CRG", "ソレイユ株式会社", "https://agent.herp.cloud/p/rygOxqdzmFS2Fnoj3nKCzlYW1Gxme1SIz9pzjkF4Eeg"),
    ("CRG", "株式会社Thirdverse", "https://agent.herp.cloud/p/zP2hZgJmekjQI2fRjWxpTCCbS-qWKmXYXtM6wOHMIsI"),
    ("CRG", "株式会社KMS", "https://agent.herp.cloud/p/lakg7DP5eduARs2qY51EmytBVKJ2m8Qs0jeWRAILCrw"),
    ("CRG", "株式会社IRIAM", "https://agent.herp.cloud/p/VdJ2RbY1US8pdZXp7CEu7PH8soyFTvG80KyQLWSRnSA"),
    ("CRG", "株式会社トゥーンクラッカー", "https://agent.herp.cloud/p/NY5WWc2MTxOZIqwzuZ_-WljWjrAtbHhiw0L81hBc2Gk"),
    ("CRG", "株式会社ClaN Entertainment", "https://agent.herp.cloud/p/ierw43kBgZqX2tN1sBs0xbv_lOs--aE0vkGY1k36OAk"),
    ("CRG", "株式会社MIXI", "https://agent.herp.cloud/p/4CXM-rfYxNTTWxVTybZXF09AU6ruyfV5PPG56g2I7Ys"),
    ("CRG", "株式会社flaggs", "https://agent.herp.cloud/p/vEJ6Voj3rtqLFE2jItrY4CYoZaRi82g9HZahL2A-fjs"),
    ("CRG", "株式会社MUGENUP", "https://agent.herp.cloud/p/VKcKxuQnH1JWG2oxCK6CMfdt9ml2XikDJ4G6EitbCyk"),
    ("CRG", "株式会社ディー・エヌ・エー", "https://agent.herp.cloud/p/VdJ2RbY1US8pdZXp7CEu7PH8soyFTvG80KyQLWSRnSA"),
    ("CRG", "株式会社heart relation", "https://agent.herp.cloud/p/VMX0kfqTIciLQOk2iD9NIHD64xBj35uRV8x38AkJKl0"),
    ("CRG", "株式会社アンビリアル", "https://agent.herp.cloud/p/htV9c8tNg0yrYVHz6i8ey7juNU-LS3SPOMK9PxiD7tw"),
    ("CRS", "アライドアーキテクツ株式会社", "https://agent.herp.cloud/p/lu_oXFVUX78fLkaMT_h23FxNCJ9vEY3tnYEiGzB6BI4"),
    ("CRS", "株式会社ネットドリーマーズ", "https://agent.herp.cloud/p/TKoeMZwHZ8dc-CzuIKgoXX3hNtcWNlF8TRkSyQFD8Q0"),
    ("CRS", "Aiロボティクス株式会社", "https://agent.herp.cloud/p/xoaPwG51ad4BRENwU4SgMsNnHWO8D0hWXFnRrXNY23o"),
    ("CRS", "株式会社ディー・エヌ・エー", "https://agent.herp.cloud/p/maqbNwqpdtURIY5VKl-MQOaNljAgmoIV4xXLZvFcABk"),
    ("CRS", "AI inside株式会社", "https://agent.herp.cloud/p/2PWep62sEjxnuOl_K8OcMoB34AplFn92LutTJHsPFjM"),
    ("CRS", "ミイダス株式会社", "https://agent.herp.cloud/p/UZXi7V0lfRiz6CvThdi_WhRdiKiyJF6HUEzjrUHwKRs"),
    ("CRS", "株式会社WiseVine", "https://agent.herp.cloud/p/PJ9Fo6bOjSGa3uvtovpd6fYNGRNUJxVyTPhtUrD_Hyc"),
    ("CRS", "株式会社UPSIDER", "https://agent.herp.cloud/p/ANGw3PykAG8uqqwrfAD63HR_3rMZLdDDKiB8ZeYNcYw"),
    ("CRS", "株式会社スムーズ", "https://agent.herp.cloud/p/oMIEkfIshdLzZmld_4J5lhe1OIxTt88Uc-L0CZ16w70"),
    ("CRS", "アイザック株式会社", "https://agent.herp.cloud/p/4oV_JiYcQc8bvqyvOYRWof_XtWgkajFLobyvSS2ODco/"),
    ("CRS", "株式会社コミチ", "https://agent.herp.cloud/p/jW9slTYSkh96d-T5H8Yqchzc7izrB_koJkz9v1mcZ88/"),
    ("IN", "株式会社ディー・エヌ・エー", "https://agent.herp.cloud/p/VdJ2RbY1US8pdZXp7CEu7PH8soyFTvG80KyQLWSRnSA"),
    ("IN", "株式会社Asobica", "https://agent.herp.cloud/p/U0rSlTG-BAdZq8L1cD6oeSlxi83nG9PmZ_vv9mPFEv8"),
    ("IN", "株式会社WiseVine", "https://agent.herp.cloud/p/h6RS9UHtS66K2W5icK_HvZaKAHW8faEPNx0VdQl9alI"),
    ("IN", "株式会社ＲＥＤ　ＦＲＡＳＣＯ", "https://agent.herp.cloud/p/gaKkj8i0idBA3wA9a8g5usDdxIpb2QDSZYm1s90HgWk/"),
    ("WEB", "株式会社MIXI", "https://agent.herp.cloud/p/4CXM-rfYxNTTWxVTybZXF09AU6ruyfV5PPG56g2I7Ys"),
    ("WEB", "株式会社バニッシュ・スタンダード", "https://agent.herp.cloud/p/M5gHxXgCBTF64YofDl2RIAccFf38bbSCTWvNngVpL_o"),
    ("WEB", "ソレイユ株式会社", "https://agent.herp.cloud/p/nx3gGMmPusKpg_gkl67cjPMmR7631PQaFqD9Mg_fHNo"),
    ("WEB", "株式会社テコテック", "https://agent.herp.cloud/p/AT871K4Krj_HPbwiXRyUMirBhjM7yI4hp5NvXFiPip0"),
    ("WEB", "株式会社ネットドリーマーズ", "https://agent.herp.cloud/p/Qh1bbiUB2jDxqsHvFm3l7CetzyLrtjECsG0RiXpqhbg"),
    ("WEB", "CBcloud株式会社", "https://agent.herp.cloud/p/P19MZUrCaAtP87L6iL28Avy3GgdzrOJ5oIckoMS8Wm4"),
    ("WEB", "株式会社ディー・エヌ・エー", "https://agent.herp.cloud/p/VdJ2RbY1US8pdZXp7CEu7PH8soyFTvG80KyQLWSRnSA/"),
    ("WEB", "AI inside株式会社", "https://agent.herp.cloud/p/2PWep62sEjxnuOl_K8OcMoB34AplFn92LutTJHsPFjM"),
    ("WEB", "株式会社カラダノート", "https://agent.herp.cloud/p/AJWS2dAWjr2c92q7K5f4vJboHp9H3g9CONIeFyLTy2E"),
    ("WEB", "ミイダス株式会社", "https://agent.herp.cloud/p/gchqXNlLVXUPhka2hYdR-549OKQEHwEGXo7ohkn5zIk"),
    ("WEB", "株式会社ティアフォー", "https://agent.herp.cloud/p/LsXuV9EEoaKFLX16_7l2ecFUaI3bJ0kV9PMyJgvXGM8"),
    ("WEB", "株式会社TERASS", "https://agent.herp.cloud/p/sT7WhH7-GGoND8uuFeVypZ_xw-u689562Jz-M-bB8FI"),
    ("WEB", "株式会社WiseVine", "https://agent.herp.cloud/p/qoFZFD2C4FeDUG0frKsw4Psjhu2oka2WMJph_2jiw4E"),
    ("WEB", "株式会社sustenキャピタル・マネジメント", "https://agent.herp.cloud/p/WkDUyiOQkckctZ69zm6h2B87JLssD52PK4WNc0Ryhwg"),
    ("WEB", "Terra Charge株式会社", "https://agent.herp.cloud/p/GEI68q_4cbzRn81AVCwqQKAZYRf78c-bMhyRAlrUdUQ"),
    ("WEB", "Tebiki株式会社", "https://agent.herp.cloud/p/6qLfNsWyJzJanfaJ9C604A_KZeDyZvQUgZXFA4SfC4s"),
    ("WEB", "イチロウ株式会社", "https://agent.herp.cloud/p/TR777EdYmqjor8i3sYOUZRWJkmgbHkbcFTNsp41ygPg"),
    ("WEB", "株式会社UPSIDER", "https://agent.herp.cloud/p/FVqo6AcqSR4-5i4omz5gd9q85oMqvUXUDOxYEM2LsJ8"),
    ("WEB", "株式会社シックスティーパーセント", "https://agent.herp.cloud/p/WKSYqTgMknkm2SqCkhnzsHSw_oVUQpLu1zHsz8uEGSg"),
    ("WEB", "アイザック株式会社", "https://agent.herp.cloud/p/v5PcYbUwLmlbWNoxHTP8wQT9_Gwbf5p0LGXj0XubM5s/"),
    ("WEB", "エンターテイメント株式会社", "https://agent.herp.cloud/p/EP15RWhXDwY0GI36KOs_z3Rhq5oBJYadc7ybGrQqJeo"),
    ("WEB", "株式会社enechain", "https://agent.herp.cloud/p/ey5nESzg2hsNebzDd6-pMAn7zZ0snPYwEmsAwYzrfF0"),
    ("WEB", "AI inside株式会社", "https://agent.herp.cloud/p/cxelGf0pjyk5lxMVIgSijqkgt1RJnJgCo4ZjXVgGvpI"),
    ("WEB", "株式会社エヌエルプラス", "https://agent.herp.cloud/p/cxelGf0pjyk5lxMVIgSijqkgt1RJnJgCo4ZjXVgGvpI"),
    ("WEB", "株式会社ヴァリューズ", "https://agent.herp.cloud/p/lPNOQa5WtlflXjL429M_hUzcAKmvwzPwMW3KzS0q1AA"),
    ("コンサル", "株式会社ジーネクスト", "https://agent.herp.cloud/p/GqI6pA8zbEFdRivrbf0Jh1lM18HeaXEdyjnoIXcia74"),
    ("コンサル", "株式会社クラフトマンソフトウェア", "https://agent.herp.cloud/p/-0nJBmOrP6G_RqlqTmbZlMEhEbBUaMhY9Sms_jI6fgE"),
    ("CRG", "株式会社GNUS", "https://agent.herp.cloud/p/1RRxb7oGfKkxgHKl0bgKpLeAiTYu9OnMgQAI2zjq_MI"),
    ("CRG", "アイザック株式会社", "https://agent.herp.cloud/p/J1trTnR80NJROlZoIZ9jwQ6gfOoJnaUk_9UJCxK4gC8"),
    ("CRG", "株式会社よりそう", "https://agent.herp.cloud/p/K1_18M3EZXDQYOsRMGLHchjXa46PEK_mA_j3vZgh020"),
    ("CRG", "株式会社アカツキゲームス", "https://agent.herp.cloud/p/l9l1QlYaGWKcD1nrGeO7pt9RWNnr7tIIHPUX6-9qsoo"),
    ("CRG", "株式会社Malme", "https://agent.herp.cloud/p/sU8KaIHC41yiiBIj4gEgGs2y3op1o2fchfsfYHEbWhM"),
    ("CRG", "株式会社DeNA Games Tokyo", "https://agent.herp.cloud/p/T1IWvX5FpJEi1ivgiOomyWoWeRhui85oFZgwPayzloU"),
    ("CRS", "株式会社enechain", "https://agent.herp.cloud/p/20Rmu_68gW4uZF81O3JLFlPg0TpvWq5UTA0znS3A2Sc"),
    ("CRS", "株式会社Fivot", "https://agent.herp.cloud/p/23HL1Aa9Alt11HAguamCGztSV21udu-cNUwO-oEsvqQ"),
    ("CRS", "株式会社Algoage", "https://agent.herp.cloud/p/5pJZYDIBXS2MQCwXXRKAi5m32DIL6NR2vTAA09aSYjg"),
    ("CRS", "フラー株式会社", "https://agent.herp.cloud/p/9NTi3ZtBUkVjMXzH62f0ZEsqwGsoJmo3gC8VKXMG-q4"),
    ("CRS", "匠技研工業株式会社", "https://agent.herp.cloud/p/a7aSCKwuZM0bPkhzcWerrgBxrCESVBM5s3HNITe42yU"),
    ("CRS", "株式会社GNUS", "https://agent.herp.cloud/p/ADG_U_-zl1nmylYSi1Ann98JEUzIgrJXgWHoOhJF7Is"),
    ("CRS", "株式会社LegalOn Technologies", "https://agent.herp.cloud/p/AhsfzmbyOEX-nD88cly1vUx_wpCb93VRmj6qmAIKPy0"),
    ("CRS", "テックタッチ株式会社", "https://agent.herp.cloud/p/dv2YvHdt23QgNQshAhaGzQIdmkwIlWKnR1VEsDsWL18"),
    ("CRS", "株式会社TERASS", "https://agent.herp.cloud/p/gMKYRIL6KbO4bW5IStufzAydoCZ0-E4XV1RN01H6BFI"),
    ("CRS", "株式会社heart relation", "https://agent.herp.cloud/p/GvhLc_At27xs0npl9eumCCuBarBTPzawARXbkVZkcqM"),
    ("CRS", "エンターテイメント株式会社", "https://agent.herp.cloud/p/ilexpdiatPw8qAnVx4psvr5HuJGyUpU8fM2Xim0nEcs"),
    ("CRS", "株式会社sustenキャピタル・マネジメント", "https://agent.herp.cloud/p/MOkLxxUF5pw_WGvzmSP9PmNiiUYzC4O89nkWfrJOMkc"),
    ("CRS", "イチロウ株式会社", "https://agent.herp.cloud/p/njt-KN9Ze56PjNBhPjeMcklIlr9TO5Y8NxVKVGBJPcw"),
    ("CRS", "ミチビク株式会社", "https://agent.herp.cloud/p/nM6zqU5bpRf8_aVvV4cqjXl_Y61FInS8HA1ubgfHY8g"),
    ("CRS", "株式会社テコテック", "https://agent.herp.cloud/p/nV7fMTT20pjjWivYGMYTt1ZFGl3tVwV8f_zmRn4NR3w"),
    ("CRS", "Tebiki株式会社", "https://agent.herp.cloud/p/pd6_VV72gSioN6bgoco6InIrzifYzT3497xoM_VJJsw"),
    ("CRS", "株式会社ジーピーオンライン", "https://agent.herp.cloud/p/RGslb1ihCMBV1JYT6rgAUxsFqovQV40TFMNQiKW-Nj8"),
    ("CRS", "株式会社よりそう", "https://agent.herp.cloud/p/RjGtVxX0vjOG2BlGrngeZ2nBY1HhC4n5U6Tbs_c-rDQ/"),
    ("CRS", "株式会社Luup", "https://agent.herp.cloud/p/srLRxYeNU24bU_ihaFZ-NbOjaR0hjW-RRgsDAsgJmvg"),
    ("CRS", "株式会社Malme", "https://agent.herp.cloud/p/StGFh7G-SdfaMFXbqlNnsmqM53-ihGNYbMyO3T0Hpg0"),
    ("CRS", "株式会社ユートニック", "https://agent.herp.cloud/p/UAkNIiIarXN0dQHuUUKIE9XoJ0LBeGna1FRMHmGfOWQ"),
    ("CRS", "株式会社TAPP", "https://agent.herp.cloud/p/uQYLYP4bG3F2g39acQmKx22zjb5XXTPLVM9_9qtwU6U/"),
    ("CRS", "株式会社クロスビット", "https://agent.herp.cloud/p/vTKMiwmainSzcjMfYJH6VrhT9-SoiloEbqgzknnFblg"),
    ("CRS", "株式会社mediba", "https://agent.herp.cloud/p/wKyz9I04zPijU88M_RLr7dBWLIjHhBcLVKQlft8OCNg"),
    ("CRS", "株式会社カラダノート", "https://agent.herp.cloud/p/ybvVrb79Hco8WnFgE8dPl81LPSiiJkMV4TOkVk41qHE/"),
    ("CRS", "ミイダス株式会社", "https://agent.herp.cloud/p/zLbBl-k1XAmZFhhG2p7QSnYFOqTdl9bU7lA9pnITAWw"),
    ("IN", "株式会社よりそう", "https://agent.herp.cloud/p/4py69_Txo_qC5cG2ZbpeoGA3IF_Cxk8EXy8M9tvBFAA"),
    ("IN", "アイザック株式会社", "https://agent.herp.cloud/p/6INvasRKD30WLxiRKJI9jw_4ebifvdBNDiafMQG4IHs/"),
    ("IN", "株式会社ELEMENTS", "https://agent.herp.cloud/p/AljHOsStuCTKUs40wpIEoRWVn9wwYpwr1uIcvTVXXsw"),
    ("IN", "株式会社スムーズ", "https://agent.herp.cloud/p/BrXhrGy2SngAjDskRt2KCbwPk1G5gppFcOuj4HDDpQ8"),
    ("IN", "Ubie株式会社", "https://agent.herp.cloud/p/F8qvCAF_dXO3Xiw_uL8tukKbXr1oLIYI7_E7tev7QiY/"),
    ("IN", "株式会社TERASS", "https://agent.herp.cloud/p/FxQQ52_A7GCHPslcbtD9AlVDqOlIHVBjUT35lOuuHKA/"),
    ("IN", "株式会社ナウキャスト", "https://agent.herp.cloud/p/GEz_4tu5k3GN0L9hbG5TgqvHsBwDW6H0AZgS-wU86-4"),
    ("IN", "株式会社Malme", "https://agent.herp.cloud/p/l49AGye3u68gRe7khijnyLhDHP1az4-5XOm9WBokGf0"),
    ("IN", "匠技研工業株式会社", "https://agent.herp.cloud/p/Li84-_Z4bcFJSR9-7qNlhXbQtQ0baJz-zIe7RbEiQaw"),
    ("IN", "株式会社コミチ", "https://agent.herp.cloud/p/NBDJq5Hcm3CDiZYvIU8UiRRCRmetlRlaB4thSKcchTQ/"),
    ("IN", "株式会社オープンロジ", "https://agent.herp.cloud/p/PLgNOuRiOf5MmPfEdzIGaYkPVPLW4F0LvK3D-GWkRDc"),
    ("IN", "株式会社LegalOn Technologies", "https://agent.herp.cloud/p/QyyZvOnu9sVYAC0zMF10E4KssQ2SHUvCrgNxo3H9xXo"),
    ("IN", "テックタッチ株式会社", "https://agent.herp.cloud/p/rv7qvEphzkjBuA4rWGBCROSKADvl5LMnBBUpdf4EnTg"),
    ("IN", "株式会社クロスビット", "https://agent.herp.cloud/p/sAtlUUw9aZ5rdnMsWBuWUieDvPbyzNeTMGQb4pKNRuY"),
    ("IN", "secondz digital株式会社", "https://agent.herp.cloud/p/u-WReTEzMVdl9ijy44nDPFwctM0csyIBdaoc2-8Cp_8"),
    ("IN", "株式会社シナスタジア", "https://agent.herp.cloud/p/UD9Ep683kVkPuZ_KkWdA7yC-hCn6Pw4bdWAXwmOBCE0"),
    ("IN", "株式会社クラフトマンソフトウェア", "https://agent.herp.cloud/p/XFOei8BtS6eMNKC1f5Pc7Kx-QYpL2PoEnqKcQ35HM-w"),
    ("IN", "株式会社Luup", "https://agent.herp.cloud/p/ztXYm8X8wVmkc5tmVQJe6WQ0v--yxF3UukhB0fHfWKU"),
    ("WEB", "株式会社Luup", "https://agent.herp.cloud/p/0waf5lOUEty5K4AeM3dRF5_UMAM4yVnLOIwi9GuRzdA"),
    ("WEB", "株式会社コドモン", "https://agent.herp.cloud/p/1gQT9BbVmnQM_6M-tS2L-tBzdy9xxWgibGpOYTXBAVs"),
    ("WEB", "FastLabel株式会社", "https://agent.herp.cloud/p/1o2JfyDYdpp2nyKu4iDLm5TjqSZoKKkbh1_cTZhf_8U"),
    ("WEB", "フラー株式会社", "https://agent.herp.cloud/p/4NjdYMzfVDG0mLvVI4IvZJdwRTAnssbEqlHFD7p-510"),
    ("WEB", "株式会社eiicon", "https://agent.herp.cloud/p/5rYDLHTsbSCBANkVBskApzYNLP1fvpBxzbChlGjuImo"),
    ("WEB", "株式会社ELEMENTS", "https://agent.herp.cloud/p/6_E0khKCscJd7r2m6c-b9tWUi0_SKWhNzEmBShYR1OU"),
    ("WEB", "株式会社クロスビット", "https://agent.herp.cloud/p/aNNdjD9BD8Sgob08UwemdlQ_6Ws2Ls8Kx6MB_VfEZKw"),
    ("WEB", "株式会社LegalOn Technologies", "https://agent.herp.cloud/p/aogulTrQ2bC6sFHRu1PlL5ZJivOi7X-J1yRzIK6yrN4"),
    ("WEB", "株式会社スムーズ", "https://agent.herp.cloud/p/BhALyMJPG6CzJLWR1-er99uT7-ymfqsARRGWY0X1iRM"),
    ("WEB", "テックタッチ株式会社", "https://agent.herp.cloud/p/ELA5flzCMTDI2IwcT5av_IN1yLcKCXQQpniniJcI4qQ"),
    ("WEB", "株式会社Insight Edge", "https://agent.herp.cloud/p/gnD37UTjJH9oMDxAhuIbYUIeFpojHrOIWPO0Gr8z5x0"),
    ("WEB", "株式会社シナスタジア", "https://agent.herp.cloud/p/gVFgISG0bwRWvUo8ov3C8p4MpKB9_dsbbq6rjzOy6i4"),
    ("WEB", "株式会社Legalscape", "https://agent.herp.cloud/p/I8W82XSgR3rRUbN6qp1vGDDOpL6WJm2JZyfjLrK15ak"),
    ("WEB", "REHATCH株式会社", "https://agent.herp.cloud/p/J2PSvEhVN8OFURwqzd8m9Y82ehB03YitBltlSI7_8ZE"),
    ("WEB", "株式会社TENTIAL", "https://agent.herp.cloud/p/kg5ENIHDrcBA4qhmaH3e5SoOcJQOjlpBl8P18BMZDIU"),
    ("WEB", "株式会社ナウキャスト", "https://agent.herp.cloud/p/KlW5l5ySxVwpFQxg22HkkTO4HdImuSYmqQqsnTHvJJc"),
    ("WEB", "株式会社Malme", "https://agent.herp.cloud/p/KnbqWfkidKDzFMVsfEIBv5T_-l6f-fFL0Li3uWWxEZ0"),
    ("WEB", "株式会社オープンロジ", "https://agent.herp.cloud/p/lPWcIKV02NBdRGDDqtTq9EwUmTYeOoWdjPc_2xLwtsI"),
    ("WEB", "株式会社Asobica", "https://agent.herp.cloud/p/LTovRDKxseZ3gYPcI0gb5_wbl1phXWkb-L-nw3JsJJA"),
    ("WEB", "株式会社フィックスターズ", "https://agent.herp.cloud/p/lW24bhrIjQjSy40WOKaPgpxGlugHb5y0HgfE9Chjjnk"),
    ("WEB", "株式会社クラフトマンソフトウェア", "https://agent.herp.cloud/p/m9ZRPk40eTWGDVjvdwDZOGZ1M3DBF7U0qTa2PbJ3HnM"),
    ("WEB", "Ubie株式会社", "https://agent.herp.cloud/p/msI_inTUem66lGF7FbRYezoB_gdnT1ixwrYiAthw5KM"),
    ("WEB", "株式会社LITALICO", "https://agent.herp.cloud/p/n45iH6rynpGHbNim3S9EufNeK-y13LziuZvWjKt6law"),
    ("WEB", "株式会社Datachain", "https://agent.herp.cloud/p/n8EXFw_JtjvOXo9c_hq7BDpSpp9PoYI1SAyyl2RSPFs"),
    ("WEB", "株式会社よりそう", "https://agent.herp.cloud/p/NgZR9-9RqyBBEM_0Q00mIXjTkNjgEJfGVDyYLU9efP4"),
    ("WEB", "匠技研工業株式会社", "https://agent.herp.cloud/p/nOM477TZXAdOjNyliN02eDLHdomxj015NL30p2zo-l4"),
    ("WEB", "株式会社Hacobu", "https://agent.herp.cloud/p/nRfvCNWZtw2JnXXtcD5FplWXl2zqe0tzzykOg7i7QLw"),
    ("WEB", "株式会社コミチ", "https://agent.herp.cloud/p/OuZMD5uJR7jBFyedq6LcOHYeSdBXpAYOWXFs9RUI-ow"),
    ("WEB", "株式会社HashPort", "https://agent.herp.cloud/p/ovYtBSx4tvy2Sy7qN1xvaEhe3dJDUCujZKW-_xWGTFk"),
    ("WEB", "株式会社Mediplat", "https://agent.herp.cloud/p/t1f7b0wcG5emEs6DuT7JeulH1Pvq0WPOFOfo8V4fbMo"),
    ("WEB", "株式会社kickflow", "https://agent.herp.cloud/p/t2Qh05txSStwArWpae6AuUzLiVrLQBR2s5BfSTfeJKE/"),
    ("WEB", "株式会社Fivot", "https://agent.herp.cloud/p/wC3N6T8jGqI8hSlQ29VNUR2CBJFk40GfLoU44OPYUiU"),
    ("WEB", "株式会社TAPP", "https://agent.herp.cloud/p/WO6IsA_-3waLuNtvRhDQef5USJFqvYRhjghlmHqLdxE/"),
    ("WEB", "株式会社カラダノート", "https://agent.herp.cloud/p/WX8NeI2Zp4cQ3pmM2NsnbzxIOODWllu7U8RlJjUCxpg/"),
    ("WEB", "株式会社グラファー", "https://agent.herp.cloud/p/Xwg78p1a4_2GfJoROHwbGX53aW4aTy-Gu-b5_SylMnU/"),
    ("WEB", "株式会社GNUS", "https://agent.herp.cloud/p/YtEMb_ClzuXHq6lT3foBYUCvm1nEZ3_QNGKDYhPzhPw"),
    ("WEB", "株式会社キカガク", "https://agent.herp.cloud/p/Z_fjJoykqzorysGWJEdWHpS5OEZAqRCui1ENwix-szo"),
    ("WEB", "SALESCORE株式会社", "https://agent.herp.cloud/p/z-7s1ukbX83T2zP-s9F4JufhdzNcayDdGSXXAYYZSsQ"),
    ("WEB", "ミチビク株式会社", "https://agent.herp.cloud/p/Zf2atdgDraS0CeHIfIcDxzS4VTEx7UIyQvK_qAzMWC8"),
    ("WEB", "株式会社Algoage", "https://agent.herp.cloud/p/zlFMOWmU10RLSB6XwCHRRoHRo0SfYpf6FxDIxNB9Kq0"),
    ("コンサル", "株式会社Malme", "https://agent.herp.cloud/p/5oCb--XUu4iAw8y6DAPaZ60FpUYT-_6klDSM-JvDy0Y"),
    ("コンサル", "株式会社Fivot", "https://agent.herp.cloud/p/7YKHViJjhzyGM_9WFqOiRG8RiTGS400lJdtqd4aqebM"),
    ("コンサル", "株式会社SORAMICHI", "https://agent.herp.cloud/p/CWgXveD5z39pOCyAXN7vz6ob2PzrtTF_R3_0p4PdnBo"),
    ("コンサル", "株式会社TERASS", "https://agent.herp.cloud/p/Esa1cfef5i7TB259txXa6LeElNSP_YSQlDLJGZjagdA"),
    ("コンサル", "株式会社GNUS", "https://agent.herp.cloud/p/jqEn9puCjgMuELWArD7wqKd6Y5jJFlUxbxUnqbnoe_Q"),
    ("コンサル", "株式会社シナスタジア", "https://agent.herp.cloud/p/k05rGcUVonCfdvuh35gaagASqZJIb8n_LQKV0y1ZIoo"),
    ("コンサル", "株式会社テコテック", "https://agent.herp.cloud/p/m9G28BROTdCEO4uJDeJfYgH4bdvL6Jmo_eVm97ArXkQ"),
    ("コンサル", "株式会社ELEMENTS", "https://agent.herp.cloud/p/NdYEZVKmJHD5gJosrEhpuwxkQVV0skE_8Ez_djpg644"),
    ("コンサル", "株式会社Liquid", "https://agent.herp.cloud/p/NdYEZVKmJHD5gJosrEhpuwxkQVV0skE_8Ez_djpg644"),
    ("コンサル", "株式会社Algoage", "https://agent.herp.cloud/p/qGXfJFJFdPCUNw1FzaAZj1iTfzMCUIdMsW09EyZ3GFQ"),
    ("コンサル", "株式会社LegalOn Technologies", "https://agent.herp.cloud/p/qhOSk6J7wp2Fw2QT3VdMQ15n94iffNV60HPbaPaERtA"),
    ("コンサル", "株式会社heart relation", "https://agent.herp.cloud/p/rOs05KQGP8LKqbkwRkZzorMuHB7x_KYMzGEkRJKfMAI"),
    ("コンサル", "株式会社グラファー", "https://agent.herp.cloud/p/TteWNqoAHdgC85Ttl59tcEgsAPrEQYygZJoBqop1CEo/"),
    ("コンサル", "株式会社Datachain", "https://agent.herp.cloud/p/x0u_1OJ6iumjlsmuVT13280QigY_0Bv4uzxNCEy_XUs"),
]

OUTPUT_DIR = "output_herp_jobs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- ユーティリティ関数 ---
def extract_panel_data(section):
    data = {}
    try:
        title = section.query_selector(".titled-panel-content__title").inner_text().strip()
        rows = section.query_selector_all("tr.attributes-table__record")
        for row in rows:
            key = row.query_selector("td.attributes-table__attribute-cell").inner_text().strip()
            val = row.query_selector("td.attributes-table__value-cell").inner_text().strip()
            data[f"{title}_{key}"] = val
    except:
        pass
    return data

# --- 案件名を整形する関数 ---
def clean_job_title(job_title: str, company: str) -> str:
    for space in [" ", "　"]:  # 半角・全角スペース両対応
        target = company + space
        if target in job_title:
            return job_title.replace(target, "", 1)
    return job_title

# --- メイン処理 ---
def scrape_herp():
    from collections import defaultdict
    job_dict = defaultdict(list)
    today = datetime.now().strftime("%Y%m%d")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for category, company, base_url in HERP_URLS:
            print(f"\n▶ カテゴリ: {category} - {company} ({base_url})")
            try:
                page.goto(base_url, timeout=60000)
                page.wait_for_selector(".agent-requisitions-table-list__record", timeout=20000)
                links = page.query_selector_all(".agent-requisitions-table-list__anchor")

                job_links = []
                for a in links:
                    href = a.get_attribute("href")
                    if href:
                        job_links.append("https://agent.herp.cloud" + href)

                for job_url in job_links:
                    try:
                        page.goto(job_url)
                        page.wait_for_selector(".titled-panel-content", timeout=20000)

                        # 案件名取得
                        try:
                            title_elem = page.query_selector(
                                "#application > div > div.layout-toast-collection__content > div > div.page-with-header__header > div > div.page-header__title-and-description > div"
                            )
                            raw_title = title_elem.inner_text().strip() if title_elem else ""
                        except:
                            raw_title = ""

                        # ▼ 案件名から企業名を削除（半角・全角スペース両方対応）
                        cleaned_title = clean_job_title(raw_title, company)

                        sections = page.query_selector_all(".titled-panel-content")

                        job_data = {
                            "カテゴリ": category,
                            "企業名": company,
                            "案件名": cleaned_title,
                            "URL": job_url
                        }

                        for section in sections:
                            job_data.update(extract_panel_data(section))

                        job_dict[category].append(job_data)
                        time.sleep(1.5)

                    except Exception as e:
                        print(f"    ⚠ 詳細ページエラー: {e}")
                        continue

            except Exception as e:
                print(f"    ⚠ 一覧ページエラー: {e}")
                continue

        browser.close()

    # 出力処理（カテゴリ別 + 日付付き）
    for category, jobs in job_dict.items():
        out_df = pd.DataFrame(jobs)
        filename = f"herp-{category}-{today}.csv"
        out_path = os.path.join(OUTPUT_DIR, filename)
        out_df.to_csv(out_path, index=False)
        print(f"✅ 保存完了: {out_path}（{len(out_df)}件）")

if __name__ == "__main__":
    scrape_herp()
