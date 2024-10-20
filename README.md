# 日本国内における食中毒細菌に関するばく露評価のまとめ
<br />

## 微生物汚染実態データベースの見える化
- [汚染率の可視化システム](https://m7gk8u5qjmoysfsmf5kgqk.streamlit.app) 　([プログラムのソースコード](https://github.com/kento-koyama/risk_st_test))<br>
- [汚染濃度の可視化システム](https://foodcontamiriskapptest-snhhv2zpvszwfmbm6kwhhm.streamlit.app/)　([プログラムのソースコード](https://github.com/junpei05/FoodContamiRisk_AppTest))<br>

## 食中毒細菌に関するばく露評価のDX化に向けた情報整理
ばくろ評価とは、人が摂食する細菌数を推定することである。<br>
国内でのリスク評価を行うためには、日ごろの科学的な知見の集積が必要不可欠である。<br>
このページでは、現状の食中毒汚染実態調査のデータをまとめる。
<br><br>

必要なデータは以下の通りである。
- 国内で集収すべきデータ：汚染実態の定量（汚染率および微生物濃度）、喫食量の定量、温度履歴（流通を含む）
- 海外も視野に入れたデータ：微生物種内の増殖・死滅速度のバラつき

<br>
今後5年かけて、データの構造化を目指す。
<br />



## 1. 食中毒細菌の汚染実態（国内）
汚染実態では食品中の陽性/陰性のみならず、汚染濃度が重要である。<br>
陽性/陰性の割合と汚染濃度のデータの両方を示す。
### 1.1. 陽性/陰性の割合
  **[食中毒細菌汚染実態_汚染率.csv](https://github.com/kento-koyama/food_micro_data_risk/blob/3adb67abbdea7e3d4c62560ac20a3695ca79af55/%E9%A3%9F%E4%B8%AD%E6%AF%92%E7%B4%B0%E8%8F%8C%E6%B1%9A%E6%9F%93%E5%AE%9F%E6%85%8B_%E6%B1%9A%E6%9F%93%E7%8E%87.csv)** に整理
- 2008-2018年度　厚生労働省　[食品中の食中毒菌汚染実態調査](https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/kenkou_iryou/shokuhin/syokuchu/01.html)　（整理済み）
- 2005-2015年度　農林水産省　[食品の安全性に関するサーベイランス・モニタリングの結果【有害微生物】](https://www.maff.go.jp/j/syouan/seisaku/risk_analysis/survei/result_micro.html#kekkasyuu)
- 2009年度　[Campylobacter contamination in retail poultry meats and by-products in Japan: A literature survey](https://www.sciencedirect.com/science/article/pii/S0956713508002247)
- 不確実性の推定のため、総試験数および陽性数が必要となる。
- 国外・国内の差を考慮し、場合によっては地域ごとの差も考慮に入れる。
### 1.2. 汚染濃度 [CFU/g, MPN/g or CFU/cm<sup>2</sup>]
   **[食中毒細菌汚染実態_汚染濃度.csv](https://github.com/kento-koyama/food_micro_data_risk/blob/3adb67abbdea7e3d4c62560ac20a3695ca79af55/%E9%A3%9F%E4%B8%AD%E6%AF%92%E7%B4%B0%E8%8F%8C%E6%B1%9A%E6%9F%93%E5%AE%9F%E6%85%8B_%E6%B1%9A%E6%9F%93%E6%BF%83%E5%BA%A6.csv)** に整理
#### 1.2.1 カンピロバクター　(_Campylobacter jejuni_ / _Campylobacter coli_)
- 2022年度　厚生労働科学研究費（食品の安全確保推進研究事業）「と畜・食鳥処理場におけるHACCP検証手法の確立と食鳥処理工程の高度衛生管理に関する研究」分担研究報告書[「生食用食鳥肉の高度衛生管理に関する研究」](https://mhlw-grants.niph.go.jp/system/files/report_pdf/11.%20%E5%88%86%E6%8B%85%E7%A0%94%E7%A9%B6%E2%91%A5%20p77-97.pdf)
- 2021年度　[と畜検査員及び食鳥検査員による外部検証の実施について（生食発 0528 第6号 令和3年5月31日）](https://www.mhlw.go.jp/content/11130500/000803740.pdf)　（記録済み）
- 2020年度　[食鳥処理場における鶏肉のカンピロバクター汚染の定量調査](https://agriknowledge.affrc.go.jp/RN/2010942163.pdf)　（記録済み）
- 2021年度　厚生労働科学研究費（食品の安全確保推進研究事業）「畜産食品の生物学的ハザードとそのリスクを低減するための研究」分担研究報告書[「鶏肉食品におけるカンピロバクター等の定量的汚染実態に関する研究」](https://mhlw-grants.niph.go.jp/system/files/report_pdf/R3%E6%9C%9D%E5%80%89%E5%88%86%E6%8B%85%E7%A0%94%E7%A9%B6%E5%A0%B1%E5%91%8A%E6%9B%B8.doc__0.pdf)
- 2020年度　厚生労働科学研究費（食品の安全確保推進研究事業）「畜産食品の生物学的ハザードとそのリスクを低減するための研究」分担研究報告書[「鶏肉食品におけるカンピロバクター等の定量的汚染実態に関する研究」](https://mhlw-grants.niph.go.jp/system/files/report_pdf/202024029A-buntan1.pdf)　（記録済み）
- 2019年度　厚生労働科学研究費（食品の安全確保推進研究事業）「畜産食品の生物学的ハザードとそのリスクを低減するための研究」分担研究報告書[「鶏肉食品におけるカンピロバクター等の定量的汚染実態に関する研究」](https://mhlw-grants.niph.go.jp/system/files/2019/193031/201924021A_upload/201924021A0004.pdf)
- 2020-2022年度　[と畜・食鳥処理場におけるHACCP検証方法の確立と食鳥処理工程の高度衛生管理に関する研究](https://mhlw-grants.niph.go.jp/project/165144)
- 2018, 2020年度　[2食鳥処理場におけるブロイラー群および胸肉のカンピロバクターおよびサルモネラ汚染状況と薬剤耐性](https://agriknowledge.affrc.go.jp/RN/2010937017.pdf)　（記録済み）
- 2014-2015年度　[特殊飼料を給与したブロイラーでみられたカンピロバクター低汚染鶏群と偶発的区分処理の潜在的効果](https://agriknowledge.affrc.go.jp/RN/2010902975.pdf)　（記録済み）
- 2014年度　[と畜・食鳥検査における疾病診断の標準化とカンピロバクター等の制御に関する研究](https://mhlw-grants.niph.go.jp/project/24503)
- 2013年度　[ブロイラー鶏群から製造された中抜きと体のカンピロバクター濃度調査](https://www.maff.go.jp/j/syouan/seisaku/kekka/keiniku_cam_13.html)
- 2012年度　[牛胆嚢内胆汁のカンピロバクター汚染と胆汁の生化学的性状](https://warp.ndl.go.jp/info:ndljp/pid/11533510/www.pref.gifu.lg.jp/kurashi/shoku/shokuhin/22513/gakkai-tou-happyou.data/24-13.pdf)
- 2011年度　[食鳥処理工程におけるカンピロバクター等微生物汚染防止低減への取り組みについて](https://warp.ndl.go.jp/info:ndljp/pid/12996857/www.jyuieisei-kgo.jp/topics/sozai/researchextract01_2011.pdf)
- 2010年度　[ブロイラー鶏群から製造された中抜きと体及び鶏肉のカンピロバクター濃度調査](https://warp.ndl.go.jp/info:ndljp/pid/9534028/www.maff.go.jp/j/syouan/seisaku/kekka/keiniku_cam_07.html)
- 2010年度　[鶏肉のカンピロバクター（肉用鶏農場～食鳥処理場）](https://www.maff.go.jp/j/syouan/seisaku/risk_manage/seminar/pdf/siryou2-2_chicken-campylobacter.pdf)
- 2001年度　[MPN法および直接平板塗抹法による市販鶏レバーのカンピロバクターの定量検査](https://www.jstage.jst.go.jp/article/jvma1951/55/7/55_7_447/_pdf/-char/en)
- 2000-2001年度　[鶏肉に起因するカンピロバクター食中毒の予防対策に関する調査研究](https://warp.ndl.go.jp/collections/content/info:ndljp/pid/13046218/mhlw-grants.niph.go.jp/project/3941)
- 2000年度　[市販鶏肉におけるカンピロバクターの定量検査と分離菌株の血清型](https://www.jstage.jst.go.jp/article/jvma1951/57/9/57_9_595/_pdf/-char/ja)
- 1999-2002年度　[国産および輸入鶏肉におけるカンピロバクターの汚染状況](https://agriknowledge.affrc.go.jp/RN/2010671140.pdf)
- 1998-2001年度　[わが国における Ready-to-Eat 水産食品の _Listeria monocytogenes_ 汚染](https://www.jstage.jst.go.jp/article/jsfm1994/20/2/20_2_63/_pdf/-char/ja)
- （参）カナダでの調査：[National Microbiological Baseline Study in Broiler Chicken
December 2012 – December 2013](https://inspection.canada.ca/en/food-safety-industry/food-chemistry-and-microbiology/food-safety-testing-reports-and-journal-articles/december-2012-december-2013)
#### 1.2.2 リステリア (_Listeria monocytogenes_)
- 2024年度　[リステリア](https://www.niid.go.jp/niid/images/lab-manual/kisyo/18_R5_Listeria_Okada.pdf)
- 2022年度　厚生労働科学研究費（食品の安全確保推進研究事業）「と畜・食鳥処理場におけるHACCP検証手法の確立と食鳥処理工程の高度衛生管理に関する研究」分担研究報告書[「と畜場におけるリステリア属菌の汚染実態とリスク管理に関する研究」](https://mhlw-grants.niph.go.jp/system/files/report_pdf/9.%20%E5%88%86%E6%8B%85%E7%A0%94%E7%A9%B6%E2%91%A3%20p64-69.pdf)
- 2018-2022年度　[スプラウトの微生物実態調査の結果（概要）](https://www.maff.go.jp/j/syouan/nouan/kome/k_yasai/attach/pdf/index-7.pdf)　（記録済み）
- 2016年度　[食品からのListeria monocytogenes検出法および定量法の比較](https://www.jstage.jst.go.jp/article/jsfm/33/3/33_155/_pdf)　（記録済み）
- ~2012年度　日本におけるリステリア感染症の状況~（データ確認中）[参考スライド](https://www.fsc.go.jp/fsciis/attachedFile/download?retrievalId=kai20120604bv1&fileId=230), [参考PDF](https://www.fsc.go.jp/sonota/risk_profile/listeriamonocytogenes.pdf)

- 2000-2012年度　[Prevalence and contamination levels of Listeria monocytogenes in ready-to-eat foods in Tokyo, Japan](https://www.jstage.jst.go.jp/article/jvms/advpub/0/advpub_15-0708/_article/-char/ja/)
- 2007年度　[辛子明太子におけるListeria monocytogenesの汚染実態と食品添加物による本菌の制御モデル実験](https://www.jstage.jst.go.jp/article/jsfm/24/3/24_3_122/_pdf)
- 2006年度　宮城県保健環境センター年報　第25号 p45~48 [_Listeria monocytogenes_ による ready-to-eat 食品の汚染実態](https://www.pref.miyagi.jp/documents/1943/617283.pdf)
- 2001年度　[食品由来のリステリア菌の健康被害に関する研究(総括研究報告書)](https://mhlw-grants.niph.go.jp/project/5920)
- 2004-2008 [Risk of Listeria monocytogenes Contamination of Raw Ready-To-Eat Seafood Products Available at Retail Outlets in Japan](https://journals.asm.org/doi/full/10.1128/aem.01456-09)
- 1988-2004 [Overview of Listeria monocytogenes contamination in Japan](https://www.sciencedirect.com/science/article/pii/S0168160503006275#BIB13)
- 1994年度　[リステリア菌によるナチュラルチーズの汚染実態調査（道衛研所報　第44集）](https://www.iph.pref.hokkaido.jp/Kankobutsu/Shoho/annual44/shoho440305.pdf)
- 1990-1991年度　[流通過程における食肉のリステリア汚染状況](https://www.jstage.jst.go.jp/article/jsfm1984/10/3/10_3_139/_pdf)
- 1990年度　[The incidence of Listeria species in retail foods in Japan](https://www.sciencedirect.com/science/article/pii/016816059290009R)
#### 1.2.3 腸管出血性大腸菌 (enterohemorrhagic _Escherichia coli_ :EHEC, 例: O157 など)　
- 2003年度　[夏季における牛の腸管出血性大腸菌O157保菌状況と分離株の薬剤感受性](https://agriknowledge.affrc.go.jp/RN/2010720847.pdf)
- 1998年度　[保育園におけるメロンが原因の腸管出血性大腸菌O157:H7により集団食中毒事例](https://www.pref.chiba.lg.jp/eiken/eiseikenkyuu/kennkyuuhoukoku/documents/22-p31.pdf)　（記録済み）
- 1998年度　[イクラ醤油漬の腸管出血性大腸菌Ｏ157汚染に関する調査－北海道](https://idsc.niid.go.jp/iasr/19/224/dj2242.html)　（登録中）
- 1998年度　[「イクラ」からの腸管出血性大腸菌Ｏ157:H7の検出－神奈川県](https://idsc.niid.go.jp/iasr/19/223/dj2236.html)　（登録中）
- 1997年度　[岩手県盛岡市における対応と課題](https://www.niph.go.jp/journal/data/46-2/199746020009.pdf)
#### 1.2.4 サルモネラ (_Salmonella_ spp., 例: _Salmonella_ Infantis など)
- 2021年度　厚生労働科学研究費（食品の安全確保推進研究事業）「畜産食品の生物学的ハザードとそのリスクを低減するための研究」分担研究報告書[「鶏肉加工製品におけるサルモネラの定量汚染の調査」](https://mhlw-grants.niph.go.jp/system/files/report_pdf/R3%E5%B7%A5%E8%97%A4%E5%88%86%E6%8B%85%E7%A0%94%E7%A9%B6%E5%A0%B1%E5%91%8A%E6%9B%B8.pdf)
- 2020年度　厚生労働科学研究費（食品の安全確保推進研究事業）「畜産食品の生物学的ハザードとそのリスクを低減するための研究」分担研究報告書[「鶏肉加工製品におけるサルモネラ等の定量汚染の調査」](https://mhlw-grants.niph.go.jp/system/files/report_pdf/202024029A-buntan3.pdf)
- 2019年度　厚生労働科学研究費（食品の安全確保推進研究事業）「畜産食品の生物学的ハザードとそのリスクを低減するための研究」分担研究報告書[「鶏肉加工製品におけるサルモネラ等の汚染実態に関する研究」](https://mhlw-grants.niph.go.jp/system/files/2019/193031/201924021A_upload/201924021A0006.pdf)
- 2010年度　[ブロイラー鶏群から製造された中抜きと体及び鶏肉のサルモネラ濃度調査](https://www.maff.go.jp/j/syouan/seisaku/kekka/keiniku/sal/07.html#21222)
## 2. 喫食量（国内）
一人当たり、一食で何をどれだけ食べているのかを推定する必要がある。喫食量の調査は以下で行われている。
- 2006年度　財団法人国際医療情報センター：「食品により媒介される微生物に関する食品健康影響評価に係る情報収集調査」報告書
<br />
<br />

## 3. 温度履歴（国内）
- 原料のさらされる環境の時系列変化を考慮するため、加工前保管・加工・出荷前保管・流通・小売などを考慮に入れる。
- 微生物の増殖・死滅は指数関数的に増減するため、温度履歴の平均値ではなく、温度の経時変化の記録を蓄積することが重要である。

<br />

## 4. 時間経過での細菌集団の増殖・死滅挙動の予測(国際)
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

