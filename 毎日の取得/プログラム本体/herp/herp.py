import os
import sys
import time
import csv
import pandas as pd
import yaml
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
    ("CRG", "株式会社GNUS", "https://agent.herp.cloud/p/1RRxb7oGfKkxgHKl0bgKpLeAiTYu9OnMgQAI2zjq_MI"),
    ("CRG", "アイザック株式会社", "https://agent.herp.cloud/p/J1trTnR80NJROlZoIZ9jwQ6gfOoJnaUk_9UJCxK4gC8"),
    ("CRG", "株式会社よりそう", "https://agent.herp.cloud/p/K1_18M3EZXDQYOsRMGLHchjXa46PEK_mA_j3vZgh020"),
    ("CRG", "株式会社アカツキゲームス", "https://agent.herp.cloud/p/l9l1QlYaGWKcD1nrGeO7pt9RWNnr7tIIHPUX6-9qsoo"),
    ("CRG", "株式会社Malme", "https://agent.herp.cloud/p/sU8KaIHC41yiiBIj4gEgGs2y3op1o2fchfsfYHEbWhM"),
    ("CRG", "株式会社DeNA Games Tokyo", "https://agent.herp.cloud/p/T1IWvX5FpJEi1ivgiOomyWoWeRhui85oFZgwPayzloU"),
    ("CRG", "アライドアーキテクツ株式会社", "https://agent.herp.cloud/p/TbA0Ox-oLMtqDpW2yL_YyaWKw86bi4UqdMvPkc-QPyo"),
    ("CRG", "株式会社LIONA", "https://agent.herp.cloud/p/VtTi5DibbzOtOO2XpyYNynYzr9h4n3_TiBMojLvU6lg"),
    ("CRG", "株式会社Diverse", "https://agent.herp.cloud/p/9zJdoQh5HYumk1Fz5x-nBfxiWd43cEuk6Yd54e9FrNU"),
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
    ("CRS", "アイザック株式会社", "https://agent.herp.cloud/p/EDeq7astoV_FS4u1SY0nqptSMKLasVytfiqCHXYn2AQ"),
    ("CRS", "株式会社ELEMENTS", "https://agent.herp.cloud/p/nxbJa5mcURq6DtJpL9zd9HYqmArFvJszYrRq1pq6twA"),
    ("CRS", "株式会社SORAMICHI", "https://agent.herp.cloud/p/jMsaq8TGawQQ-KGYpPZmBV-IhIvlSLza0ZbPaQwWldQ"),
    ("CRS", "株式会社サマリー", "https://agent.herp.cloud/p/1sNM6WyajVz3otogl2xcwBo5PXmDEB2iWmMy-eKtWUA"),
    ("CRS", "株式会社トリビュー", "https://agent.herp.cloud/p/EzLwPOU341im6owCN_8NkwSs2SZqTxucCk9d6r7SA8o"),
    ("CRS", "株式会社STYZ", "https://agent.herp.cloud/p/RA4AfzNcEJEB_VEqjMoGT67hr2oM_6W86HSRQUxKOdA"),
    ("CRS", "ECU株式会社", "https://agent.herp.cloud/p/wlg1uP67njCJ-zc08ri2kGRulu1B8XyvhuEuRHLOnMI"),
    ("IN", "株式会社ディー・エヌ・エー", "https://agent.herp.cloud/p/VdJ2RbY1US8pdZXp7CEu7PH8soyFTvG80KyQLWSRnSA"),
    ("IN", "株式会社Asobica", "https://agent.herp.cloud/p/U0rSlTG-BAdZq8L1cD6oeSlxi83nG9PmZ_vv9mPFEv8"),
    ("IN", "株式会社WiseVine", "https://agent.herp.cloud/p/h6RS9UHtS66K2W5icK_HvZaKAHW8faEPNx0VdQl9alI"),
    ("IN", "株式会社ＲＥＤ　ＦＲＡＳＣＯ", "https://agent.herp.cloud/p/gaKkj8i0idBA3wA9a8g5usDdxIpb2QDSZYm1s90HgWk/"),
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
    ("IN", "株式会社Fivot", "https://agent.herp.cloud/p/Inx-eW4nRWei6KahSByC3nzJFWJOvSVG6db-yab_uKE"),
    ("IN", "株式会社ＲＥＤ　ＦＲＡＳＣＯ", "https://agent.herp.cloud/p/gaKkj8i0idBA3wA9a8g5usDdxIpb2QDSZYm1s90HgWk"),
    ("IN", "株式会社テコテック", "https://agent.herp.cloud/p/x5p8CtW-qafhGjXuge8gYKCJ1Wz_VvSiHHNc-uI_j_w"),
    ("IN", "株式会社Algoage", "https://agent.herp.cloud/p/MzXgvUhfdrlpboNYc7oqmDroJh5G94HlUTcVQO46syc"),
    ("IN", "株式会社SORAMICHI", "https://agent.herp.cloud/p/EVSZZCg7wFbh4aFGdTxQmen5t4GB7Toh-rEf-Wy2XRM"),
    ("IN", "ミイダス株式会社", "https://agent.herp.cloud/p/Iwz7AHUsn2EPkqcsJP7adhVo8j7NOjBkcxNJC0HRU-A"),
    ("IN", "株式会社カウシェ", "https://agent.herp.cloud/p/uF1V8jE158yuOYW3LlFV7yr_Ju0ZGRctvzVrWJbLHCA"),
    ("IN", "株式会社ニーリー", "https://agent.herp.cloud/p/kHhhcc0BZ879M7QiT_AA-1XXPpa06W7s3_1FlKUsXEA"),
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
    ("WEB", "Aiロボティクス株式会社", "https://agent.herp.cloud/p/vyCQDNKMXnfEWk5MAIum-8qrCUToabjUSXVU0TTJ0dc"),
    ("WEB", "アイザック株式会社", "https://agent.herp.cloud/p/v5PcYbUwLmlbWNoxHTP8wQT9_Gwbf5p0LGXj0XubM5s"),
    ("WEB", "株式会社UPSIDER", "https://agent.herp.cloud/p/bAKvfcwbBxaIfDmXQMzPtEL7N4R-pZbZhOYXVbkKZBA"),
    ("WEB", "株式会社Thirdverse", "https://agent.herp.cloud/p/L1o-zCQNEAWlWgFIqzC0QsaXkMywBABODIU-ovIuEmI"),
    ("WEB", "株式会社ユートニック", "https://agent.herp.cloud/p/jJqkRkygtpVyo6jIUHEugLHLY_WXFzVsv-Gm3QBejTM"),
    ("WEB", "EpiMetrix株式会社", "https://agent.herp.cloud/p/iYjl5ViGr70YK4CdEWsC51WNkDYZYHdeWmxaTyp8WWg"),
    ("WEB", "株式会社トリビュー", "https://agent.herp.cloud/p/5rr-1tLQds0yRj5BG6z4TTtJT4HyO87W4cwPEi44OBA"),
    ("WEB", "株式会社カウシェ", "https://agent.herp.cloud/p/PvhgHdARCGP7UK4ofY_qzrJ_cPHWswBNQqwd2oC-3NY"),
    ("WEB", "株式会社カケハシ", "https://agent.herp.cloud/p/bjCa0APLdgNKul-zCK1LPt3gC4cZIuE_mtXeojrzbi0"),
    ("WEB", "LRM株式会社", "https://agent.herp.cloud/p/eRZlEPKXj1ftcnPK4rLrvIeeAtC-sz5mkl1Hdwaey0Q"),
    ("WEB", "株式会社スピークバディ", "https://agent.herp.cloud/p/EvAFzYKP8fbqNYSrQG44cFlbFJrp67dG1bilVJGQPlo"),
    ("WEB", "株式会社FUTUREMIND", "https://agent.herp.cloud/p/9KUgP8_XUZJiCYlL_wud6Izk1Ft0og3vamGI1Bg3l98"),
    ("WEB", "株式会社Helpfeel", "https://agent.herp.cloud/p/xbcYmWgnpCNn5PqvkbTa16Gsod2aV8CXmC7GqLPCubQ"),
    ("WEB", "株式会社HERP", "https://agent.herp.cloud/p/bQWyWh-u6A3qbO3yyVZMSzk8pEGNBLGVmJ2rC8aNIcU"),
    ("WEB", "株式会社InsightX", "https://agent.herp.cloud/p/z0D1E6p5_sBiRQ4iy2V_fhZg0iJQcIkZSjpcKkj5pZU"),
    ("WEB", "ECU株式会社", "https://agent.herp.cloud/p/nEESbI1LPvmcwoEUZAZi46eRfGbelgvtXkeUgfgzgpg"),
    ("WEB", "株式会社メディカルノート", "https://agent.herp.cloud/p/YWdU_LNJMlGThDfmUfACR4fw2M4KCGdYt1-6qSC83yw"),
    ("WEB", "株式会社スタンバイ", "https://agent.herp.cloud/p/XRtQEHQ15Y7gGWvjv5jkzKjQaL3-Ppiim4Yi29nmf64"),
    ("WEB", "ColorSing株式会社", "https://agent.herp.cloud/p/ZJwCQZM_UlLaM1NIHya66QxDAqs7jMmSvp1g-kXYISQ"),
    ("コンサル", "株式会社ジーネクスト", "https://agent.herp.cloud/p/GqI6pA8zbEFdRivrbf0Jh1lM18HeaXEdyjnoIXcia74"),
    ("コンサル", "株式会社クラフトマンソフトウェア", "https://agent.herp.cloud/p/-0nJBmOrP6G_RqlqTmbZlMEhEbBUaMhY9Sms_jI6fgE"),
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
    ("コンサル", "株式会社TERASS", "https://agent.herp.cloud/p/STs0JYBVfyQZeAI76oHekYiDYKhQkAgL7xhZABEpNXk"),
    ("コンサル", "株式会社HashPort", "https://agent.herp.cloud/p/GrahJe8Qt8j9jhxuUxQcHUWbwb6dMRVKaIabM4q9Vno"),
    ("コンサル", "ミイダス株式会社", "https://agent.herp.cloud/p/_55SijjosnDlJ6lyq5D40ikN-yQLRJGzWoPmUaxYkww"),
    ("コンサル", "千株式会社", "https://agent.herp.cloud/p/uO56EIJOc1FyJuHG9ZCSzvCMmCNKquv5he8CZgwaTj4"),
]

OUTPUT_DIR = "output_herp_jobs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 全カテゴリ（HERP_URLS に出てくる順）。カテゴリ指定の検証にも使う
ALL_CATEGORIES = ["CRG", "CRS", "IN", "WEB", "コンサル"]
# コマンドラインや環境変数で書かれがちな別表記を吸収する（config.yaml / password.txt の列名も含む）
CATEGORY_INPUT_ALIAS = {"IN_DS": "IN", "IN/DS": "IN", "in": "IN", "web": "WEB", "crs": "CRS", "crg": "CRG"}

# ブラウザ画面を出すか。既定は出さない（headless）。
# 画面を見たいとき（デバッグ・ログイン失敗の切り分け）は HERP_SHOW_BROWSER=1 を付けて実行する。
SHOW_BROWSER = os.environ.get("HERP_SHOW_BROWSER", "0").lower() in ("1", "true", "yes")

# HERP_URLSのカテゴリ名とpassword.txtの列名の対応（表記が違うものだけ）
CATEGORY_ALIAS = {"IN": "IN/DS"}

# --- ログイン情報を読む ---
# 2026/9/4: 置き場を ../config.yaml（HRMOS/Talentio/JobCan と同じファイル）に統合した。
# HERP のログイン ID/PASS は各カテゴリの ATS アカウントと同一なので、別ファイルを持つ理由がない。
# 旧 herp/password.txt（タブ区切り）はまだ残っている環境向けのフォールバックとして読む。
CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"
PASSWORD_TXT_PATH = Path(__file__).parent / "password.txt"
# config.yaml の accounts キー → HERP_URLS のカテゴリ名
CONFIG_KEY_TO_CATEGORY = {"WEB": "WEB", "IN_DS": "IN", "CRS": "CRS", "CRG": "CRG", "コンサル": "コンサル"}


def load_credentials_from_config(path=CONFIG_PATH):
    """../config.yaml の login.accounts から {カテゴリ: (email, password)} を返す。無ければ {}。"""
    if not path.exists():
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            accounts = (yaml.safe_load(f) or {}).get("login", {}).get("accounts", {}) or {}
    except Exception as e:
        print(f"⚠ config.yaml 読み込み失敗: {e}")
        return {}
    creds = {}
    for key, acc in accounts.items():
        cat = CONFIG_KEY_TO_CATEGORY.get(key)
        if cat and acc and acc.get("email") and acc.get("password"):
            creds[cat] = (acc["email"], acc["password"])
    return creds


def load_credentials_from_password_txt(path=PASSWORD_TXT_PATH):
    """旧形式 herp/password.txt（タブ区切り）から {カテゴリ: (email, password)} を返す。無ければ {}。"""
    if not path.exists():
        return {}
    creds = {}
    try:
        with open(path, encoding="utf-8") as f:
            rows = list(csv.reader(f, delimiter="\t"))
        table = {row[0]: row[1:] for row in rows}
        for i, cat in enumerate(table["カテゴリ"]):
            cat = CATEGORY_INPUT_ALIAS.get(cat, cat)
            if cat in ALL_CATEGORIES:
                creds[cat] = (table["ID"][i], table["リクナビ以外PASS"][i])
    except Exception as e:
        print(f"⚠ password.txt読み込み失敗: {e}")
    return creds


def load_credentials():
    creds = load_credentials_from_config()
    if creds:
        print(f"🔑 ログイン情報: {CONFIG_PATH.name} から {len(creds)} カテゴリ分を読み込みました")
        return creds
    creds = load_credentials_from_password_txt()
    if creds:
        print(f"🔑 ログイン情報: {PASSWORD_TXT_PATH.name}（旧形式）から {len(creds)} カテゴリ分を読み込みました。"
              f" ../config.yaml への移行を推奨します")
        return creds
    print(f"⚠ ログイン情報が見つかりません（{CONFIG_PATH} / {PASSWORD_TXT_PATH}）→ 未ログインで実行します。"
          f" 2026/8/5 以降は未ログインだと求人を取得できません")
    return {}


# --- HERP Hire for Agentsにログインする（Auth0） ---
# 2026/8/5以降はログインしないと求人が閲覧できない。
# 失敗してもFalseを返すだけで処理は続行する（8/4まではモーダル回避で取得可能）
def login_herp(page, base_url, email, password):
    try:
        page.goto(base_url, timeout=60000)
        link = page.query_selector(".ats-header__authorize-link")
        if link is None or "ログアウト" in (link.inner_text() or ""):
            return True  # すでにログイン済み
        link.click()
        page.wait_for_selector("input[name=email]", timeout=30000)
        page.fill("input[name=email]", email)
        page.fill("input[name=password]", password)
        page.click("button[type=submit]")
        # ログイン成功するとAuth0から元のページへ戻り、ヘッダーが「ログアウト」表示になる
        # （求人0件の企業ページもあるため、一覧テーブルの出現では判定しない）
        page.wait_for_selector("text=ログアウト", timeout=45000)
        return True
    except Exception as e:
        print(f"    ⚠ ログイン失敗 ({email}): {e}")
        return False

# --- 招待一覧から「いま開ける企業URL」を取る ---
# HERPは2026/8/5以降、推薦URLがエージェントアカウントに紐づくようになった。
# ハードコードした HERP_URLS は招待の失効・追加に追従できず、古いURLを叩くと
# 「認可されませんでした」になる（2026/8/10 実測: 202件中169件が該当）。
# ログイン後のホーム /p/invitations にそのアカウントの有効な招待が全部並ぶので、
# 毎回そこから取り直す。これでURLリストのメンテナンス自体が不要になる。
INVITATIONS_URL = "https://agent.herp.cloud/p/invitations"


def fetch_invitations(page):
    """招待一覧ページから [(企業名, 推薦URL), ...] を返す。失敗時は空リスト。"""
    try:
        page.goto(INVITATIONS_URL, timeout=60000)
        page.wait_for_selector('a[href^="/p/"]', timeout=30000)
        page.wait_for_timeout(2000)  # 一覧の描画待ち
        # クラス名はビルド毎に変わるハッシュなので使わない。
        # 「招待日」を含む div の直前の div が企業名、という構造で辿る。
        return page.evaluate("""() => {
            const out = [];
            for (const a of document.querySelectorAll('a[href^="/p/"]')) {
                const href = a.getAttribute('href') || '';
                if (!/^\\/p\\/[A-Za-z0-9_-]{20,}\\/?$/.test(href)) continue;
                const divs = [...a.querySelectorAll('div')]
                    .map(d => (d.innerText || '').trim()).filter(Boolean);
                let name = '';
                const i = divs.findIndex(t => t.startsWith('招待日'));
                if (i > 0) name = divs[i - 1];
                else if (divs.length) name = divs[0];
                out.push([name, 'https://agent.herp.cloud' + href]);
            }
            return out;
        }""")
    except Exception as e:
        print(f"    ⚠ 招待一覧の取得に失敗: {e}")
        return []


# --- ユーティリティ関数 ---
# 2026/8/12〜17の間にHERPがTailwindへ移行し、attributes-table__* のクラスが消えた。
# （旧: tr.attributes-table__record / td.attributes-table__attribute-cell）
# パネル見出し .titled-panel-content__title は生きているので、テーブルは
# 「td 2つ = 見出し/値」という構造で拾う。旧クラスが復活しても動くよう両対応にする。
def extract_panel_data(section):
    data = {}
    title_elem = section.query_selector(".titled-panel-content__title")
    if title_elem is None:
        return data
    title = title_elem.inner_text().strip()

    rows = section.query_selector_all("tr.attributes-table__record")  # 旧記法
    if rows:
        for row in rows:
            key_cell = row.query_selector("td.attributes-table__attribute-cell")
            val_cell = row.query_selector("td.attributes-table__value-cell")
            if key_cell is None or val_cell is None:
                continue
            key = key_cell.inner_text().strip()
            if key:
                data[f"{title}_{key}"] = val_cell.inner_text().strip()
        return data

    for row in section.query_selector_all("table tr"):  # 新記法
        cells = row.query_selector_all("td")
        if len(cells) < 2:
            continue
        key = cells[0].inner_text().strip()
        if key:
            data[f"{title}_{key}"] = cells[1].inner_text().strip()
    return data

# --- ログイン必須化の告知モーダルを閉じてから目的の要素を待つ ---
# 2026/8/5のHERPログイン必須化に伴い、告知モーダルが表示されている間は
# ページ本体が描画されずセレクタが見つからないため、先にモーダルを閉じる
def wait_with_notice_dismiss(page, selector, timeout=20000):
    try:
        page.wait_for_selector(selector, timeout=5000)
        return
    except Exception:
        pass
    dismiss_btn = page.query_selector("text=一時的に非表示にする")
    if dismiss_btn:
        dismiss_btn.click()
    page.wait_for_selector(selector, timeout=timeout)

# --- 案件名を整形する関数 ---
def clean_job_title(job_title: str, company: str) -> str:
    for space in [" ", "　"]:  # 半角・全角スペース両対応
        target = company + space
        if target in job_title:
            return job_title.replace(target, "", 1)
    return job_title

# --- 保存と検算 ---
# 2026/8/17: HERP側のDOM変更でパースが全滅したのに、警告ゼロ・「✅ 保存完了」で
# 案件名も詳細25列も空のCSVを納品してしまった。同じ壊れ方を黙って通さないための検算。
BASE_COLS = ["カテゴリ", "企業名", "案件名", "URL"]


def save_category(category, jobs, today):
    """カテゴリ単位でCSVを書き、健全性を検算する。問題があれば理由のリストを返す。"""
    out_df = pd.DataFrame(jobs)
    out_path = os.path.join(OUTPUT_DIR, f"herp-{category}-{today}.csv")
    out_df.to_csv(out_path, index=False)

    problems = []
    n = len(out_df)
    if n == 0:
        problems.append("0件（1件も取得できていない）")
    else:
        blank_title = sum(1 for t in out_df["案件名"] if not str(t).strip())
        if blank_title:
            problems.append(f"案件名が空: {blank_title}/{n}件")
        detail_cols = [c for c in out_df.columns if c not in BASE_COLS]
        if not detail_cols:
            problems.append("詳細列が1つも取れていない（基本情報・企業情報が丸ごと欠落）")
        elif "基本情報_仕事概要" in out_df.columns:
            filled = sum(1 for v in out_df["基本情報_仕事概要"] if str(v).strip() and str(v) != "nan")
            if filled < n * 0.5:
                problems.append(f"基本情報_仕事概要の充足率が低い: {filled}/{n}件")

    mark = "⚠" if problems else "✅"
    print(f"{mark} 保存完了: {out_path}（{n}件 / {len(out_df.columns)}列）")
    for msg in problems:
        print(f"   🔴 {msg}")
    return problems


# --- メイン処理 ---
def scrape_herp(categories=None):
    from collections import defaultdict
    job_dict = defaultdict(list)
    problems_by_category = {}
    today = datetime.now().strftime("%Y%m%d")

    creds = load_credentials()

    # カテゴリごとにアカウントが異なるため、カテゴリ単位でまとめて処理する
    urls_by_category = defaultdict(list)
    for category, company, base_url in HERP_URLS:
        urls_by_category[category].append((company, base_url))
    # カテゴリ指定があればそれだけ回す（中断からの再開・1カテゴリだけの取り直し用）。
    # 2026/9/4 まではこれが無く、途中で止まると全5カテゴリ約2時間のやり直しになっていた。
    if categories:
        urls_by_category = {c: urls_by_category[c] for c in ALL_CATEGORIES if c in categories}
    print(f"▶ 対象カテゴリ: {' / '.join(urls_by_category.keys())}"
          f"{'' if SHOW_BROWSER else '（ブラウザ画面は表示しません。HERP_SHOW_BROWSER=1 で表示）'}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not SHOW_BROWSER)

        for category, entries in urls_by_category.items():
            context = browser.new_context()
            page = context.new_page()

            # creds のキーは両ローダーとも正規名（IN など）。旧列名 IN/DS はフォールバックで見る
            # （2026/9/7: ここが IN/DS 固定だったため config.yaml 移行後に IN だけ未ログイン→0件になった）
            email, password = creds.get(category) or creds.get(CATEGORY_ALIAS.get(category, category), (None, None))
            if email:
                # ⚠️ ログインの起点にカテゴリ1社目の招待URLを使ってはいけない。
                #    そのURLが別アカウント宛だとHERPが強制ログアウトし、
                #    「ログイン失敗」に見える（2026/8/10: IN・WEBがこれで空振り）。
                #    中立な入口 /p/invitations からログインすれば5アカウント全て通る。
                # 起動直後は goto が about:blank に割り込まれてログインを取りこぼすことがある。
                # 長時間実行でここを外すとカテゴリ丸ごと空振りするので2回まで試す。
                logged_in = login_herp(page, INVITATIONS_URL, email, password)
                if not logged_in:
                    print(f"    ↻ ログインを再試行します ({category})")
                    time.sleep(5)
                    logged_in = login_herp(page, INVITATIONS_URL, email, password)

                if logged_in:
                    print(f"\n✔ ログイン成功: {category} ({email})")
                    # 招待一覧から最新の有効URLを取り直す（取れたらそちらを優先）
                    inv = fetch_invitations(page)
                    if inv:
                        # 招待一覧のURLは末尾スラッシュ付き、ハードコードは無しのことがある。
                        # 正規化せずに比較すると全件「新規」に見えてしまう
                        before = {u.rstrip("/") for _, u in entries}
                        after = {u.rstrip("/") for _, u in inv}
                        print(f"  📋 招待一覧: {len(inv)}社 "
                              f"(ハードコード {len(entries)}社 / 新規 +{len(after - before)} / 失効 -{len(before - after)})")
                        entries = [(n, u) for n, u in inv]
                    else:
                        print(f"  ⚠ 招待一覧が取れなかったため、ハードコードの {len(entries)}社で続行します")
                else:
                    print(f"\n⚠ {category}: 未ログインのまま続行します")
            else:
                print(f"\n⚠ {category}: config.yaml / password.txt に認証情報が無いため未ログインで続行します（2026/8/5 以降は0件になります）")

            for company, base_url in entries:
                print(f"\n▶ カテゴリ: {category} - {company} ({base_url})")
                try:
                    page.goto(base_url, timeout=60000)
                    try:
                        wait_with_notice_dismiss(page, ".agent-requisitions-table-list__record")
                    except Exception:
                        # 掲載0件の企業は一覧テーブル自体が存在しない
                        if page.query_selector("text=推薦いただける職種がありません"):
                            print("    ℹ 掲載中の職種なし（0件）")
                            continue
                        # 企業側で推薦URLが無効化されているケース
                        if page.query_selector("text=このURLは無効になっています"):
                            print("    ⚠ URLが無効化されています（企業側での再発行が必要）")
                            continue
                        # ページ単位でログイン必須化されている場合、そのページのログインリンクを
                        # 踏んで再認可する（Auth0セッションが生きていれば再入力なしで通る）
                        if page.query_selector("text=ログイン・ユーザー登録をお願いします"):
                            link = page.query_selector(".ats-header__authorize-link")
                            if link:
                                link.click()
                                try:
                                    page.wait_for_selector(".agent-requisitions-table-list__record", timeout=20000)
                                except Exception:
                                    if page.query_selector("text=推薦いただける職種がありません"):
                                        print("    ℹ 掲載中の職種なし（0件）")
                                    else:
                                        print("    ⚠ 認可されませんでした（別アカウント宛の招待URLの可能性。要再発行）")
                                    continue
                            else:
                                print("    ⚠ ログイン必須ページで認可できませんでした")
                                continue
                        else:
                            raise
                    links = page.query_selector_all(".agent-requisitions-table-list__anchor")

                    job_links = []
                    for a in links:
                        href = a.get_attribute("href")
                        if href:
                            job_links.append("https://agent.herp.cloud" + href)

                    for job_url in job_links:
                        try:
                            page.goto(job_url)
                            wait_with_notice_dismiss(page, ".titled-panel-content")

                            # 案件名取得
                            # 見出しのDOMはTailwind移行でクラスが総入れ替えになり（2026/8/17に全空欄化）、
                            # ビルド毎に変わるユーティリティクラスは当てにできない。
                            # <title> が "案件名 - 企業名 - HERP Hire" で安定しているのでそこから取る。
                            cleaned_title = ""
                            try:
                                page_title = (page.title() or "").strip()
                                if page_title.endswith(" - HERP Hire"):
                                    cleaned_title = page_title.rsplit(" - ", 2)[0].strip()
                            except Exception:
                                pass

                            if not cleaned_title:  # 旧DOMへのフォールバック
                                title_elem = page.query_selector(
                                    "#application > div > div.layout-toast-collection__content > div > div.page-with-header__header > div > div.page-header__title-and-description > div"
                                )
                                raw_title = title_elem.inner_text().strip() if title_elem else ""
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

            # カテゴリが終わるたびに書き出す。
            # 最後にまとめて書く作りだと途中停止で全損する（2026/8/10に2回データを失った）。
            problems_by_category[category] = save_category(category, job_dict[category], today)

            context.close()

        browser.close()

    # 検算のまとめ。1カテゴリでも異常なら異常終了させ、「黙って空のCSVを納品」を防ぐ
    ng = {c: p for c, p in problems_by_category.items() if p}
    print("\n" + "=" * 60)
    if ng:
        print("🔴 検算NG — このデータは納品しないでください")
        for category, msgs in ng.items():
            print(f"  [{category}] " + " / ".join(msgs))
        print("=" * 60)
        sys.exit(1)
    print("✅ 検算OK — 対象カテゴリすべてで案件名・詳細列が取れています")
    for category in problems_by_category:
        print(f"  [{category}] {len(job_dict[category])}件 → {OUTPUT_DIR}/herp-{category}-{today}.csv")
    print("=" * 60)


def parse_categories(argv):
    """コマンドライン引数（例: `python herp.py CRS WEB`）または環境変数 HERP_CATEGORIES（カンマ区切り）
    からカテゴリ集合を作る。指定なしなら None（＝全カテゴリ）。不正な名前は止める（黙って全件回さない）。"""
    raw = [a for a in argv if a.strip()]
    if not raw and os.environ.get("HERP_CATEGORIES"):
        raw = [x for x in os.environ["HERP_CATEGORIES"].replace("、", ",").split(",") if x.strip()]
    if not raw:
        return None
    cats = []
    for r in raw:
        c = CATEGORY_INPUT_ALIAS.get(r.strip(), r.strip())
        if c not in ALL_CATEGORIES:
            print(f"🔴 不明なカテゴリ: {r}（使えるのは {' / '.join(ALL_CATEGORIES)}。IN_DS は IN と同じ）")
            sys.exit(2)
        if c not in cats:
            cats.append(c)
    return cats


if __name__ == "__main__":
    scrape_herp(parse_categories(sys.argv[1:]))
