# food_micro_data_risk
<br />

## ばく露評価のDX化に向けた情報整理
ばくろ評価とは、人が摂食する細菌数を推定することである。国内でのリスク評価を行うためには、日ごろのデータ集収が必要である。このページでは、現状のデータとその場所について言及する。
<br><br>

必要なデータは以下の通りである。
- 国内で集収すべきデータ：汚染実態の定量（汚染率および微生物濃度）、喫食量の定量、温度履歴（流通を含む）
- 海外も視野に入れたデータ：微生物種内の増殖・死滅速度のバラつき

<br>
今後5年かけて、データの構造化を目指す。

<br />


## 1. 汚染実態（国内）
汚染実態では食品中の陽性/陰性のみならず、汚染濃度が重要である。陽性/陰性の割合と汚染濃度のデータの両方を示す。
### 1.1. 陽性/陰性の割合
- 2008-2018年度 [食品中の食中毒菌汚染実態調査](https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/kenkou_iryou/shokuhin/syokuchu/01.html)
- 2017年度　[食品安全に関する有害微生物の実態調査の結果集（畜産物）](https://www.maff.go.jp/j/syouan/seisaku/kekka/chikusan.html)
- 2009年度　[Campylobacter contamination in retail poultry meats and by-products in Japan: A literature survey](https://www.sciencedirect.com/science/article/pii/S0956713508002247)
- 不確実性の推定のため、総試験数および陽性数が必要となる。
- 国外・国内の差を考慮し、場合によっては地域ごとの差も考慮に入れる。
### 1.2. 汚染濃度 CFU/g or MPN/g
#### 1.2.1 カンピロバクター
- 2021年度　[と畜検査員及び食鳥検査員による外部検証の実施について（生食発 0528 第6号 令和3年5月31日）](https://www.mhlw.go.jp/content/11130500/000803740.pdf)
- 2014年度　[ブロイラー鶏群から製造された中抜きと体のカンピロバクター濃度調査](https://www.maff.go.jp/j/syouan/seisaku/kekka/keiniku_cam_13.html)
- 2010年度　[鶏肉のカンピロバクター（肉用鶏農場～食鳥処理場）](https://www.maff.go.jp/j/syouan/seisaku/risk_manage/seminar/pdf/siryou2-2_chicken-campylobacter.pdf)
- （参）カナダでの汚染実態調査：[National Microbiological Baseline Study in Broiler Chicken
December 2012 – December 2013](https://inspection.canada.ca/en/food-safety-industry/food-chemistry-and-microbiology/food-safety-testing-reports-and-journal-articles/december-2012-december-2013)
#### 1.2.2 リステリア
- 2001年度　[食品由来のリステリア菌の健康被害に関する研究(総括研究報告書)
](https://mhlw-grants.niph.go.jp/project/5920)
- 1994年度　[リステリア菌によるナチュラルチーズの汚染実態調査（道衛研所報　第44集）](https://www.iph.pref.hokkaido.jp/Kankobutsu/Shoho/annual44/shoho440305.pdf)
#### 1.2.3 腸管出血性大腸菌
- 1998年度　[保育園におけるメロンが原因の腸管出血性大腸菌O157:H7により集団食中毒事例](https://www.pref.chiba.lg.jp/eiken/eiseikenkyuu/kennkyuuhoukoku/documents/22-p31.pdf)
- 1998年度　[イクラ醤油漬の腸管出血性大腸菌Ｏ157汚染に関する調査－北海道](https://idsc.niid.go.jp/iasr/19/224/dj2242.html)
- 1998年度　[「イクラ」からの腸管出血性大腸菌Ｏ157:H7の検出－神奈川県](https://idsc.niid.go.jp/iasr/19/223/dj2236.html)
- 1997年度　[岩手県盛岡市における対応と課題](https://www.niph.go.jp/journal/data/46-2/199746020009.pdf)
<br />

## 2. 喫食量（国内）
一人当たり、一食で何をどれだけ食べているのかを推定する必要がある。喫食量の調査は以下で行われている。
- 2006年度　財団法人国際医療情報センター：「食品により媒介される微生物に関する食品健康影響評価に係る情報収集調査」報告書

<br />

## 3. 温度履歴（国内）
- 原料のさらされる環境の時系列変化を考慮するため、加工前保管・加工・出荷前保管・流通・小売などを考慮に入れる。
- 微生物の増殖・死滅は指数関数的に増減するため、温度履歴の平均値ではなく、温度の経時変化の記録を蓄積することが重要である。

<br />

## 4. 細菌集団の増殖・死滅挙動の評価(国際)
ばく露評価における細菌集団の増殖・死滅を推定する<br>
Combase database　https://www.combase.cc<br>
- 対象の細菌：リステリア、サルモネラ、<br>
- 対象のパラメータ：温度、水分活性、pH<br>

<br />

## 5. 用量反応のDX化に向けた情報整理
摂取された微生物数から感染確率・発症確率を推定するために必要となる情報を集める。
- 食中毒を引き起こす微生物は、ヒトに対する試験ができないことを念頭に置き、データを収集する。
- 摂取された微生物数・微生物濃度のデータを収集するための地盤を形成する必要がある。
- 年齢・性別・遺伝的特徴・細菌叢・その他特異的な特徴によって微生物感染・発症への感受性が異なる可能性がある。併せてデータ収集する必要性がある。
