from itertools import groupby

import pandas as pd

pd.set_option("display.max_rows", None)
df = pd.read_csv(
    "/home/amorntep/superstore-sales-dashboard/data/superstore.csv", encoding="latin1"
)
df.head(10)
product_name = df["Product Name"].unique()
# NOTE:dtype date
df["Order Date"] = pd.to_datetime(df["Order Date"])
# NOTE: that i knew "9994 rows not null"
# TODO:sales max=22638 min=0.44 need to check with 70 30
# TODO:quantity max=14 min=1
# TODO:discount i think this is percentage max=80% chack why have 80%
# TODO:profit min=-6599 need check
# NOTE:Frist check Customer
df_cus_check = df["Customer ID"].nunique()
print("=" * 20, "First Check", "=" * 20)
print(f" Customer = {df_cus_check}")
df_date_first = df["Order Date"].min()
df_date_last = df["Order Date"].max()
datq_range = df_date_last - df_date_first
print(f"Day one is {df_date_first} ,Last Day is {df_date_last}")
print(f"total : {datq_range.days} Day")
# NOTE:check Sales Quantity Discount Profit Category Sup-Category
sale_sum = df["Sales"].sum()
print(f"Total Sales : {sale_sum:,.2f}")
sale_groupby_day = df.groupby(df["Order Date"].dt.to_period("Y"))["Sales"].nunique()
print(
    f"Sumary \n 2014 : {sale_groupby_day.loc['2014']} \n 2015 : {sale_groupby_day.loc['2015']} \n 2016 : {sale_groupby_day.loc['2016']} \n 2017 : {sale_groupby_day.loc['2017']}"
)
# NOTE:Sales done
# NOTE:ลดความละเอียดเดียวไปดูอีกที่BI
# TODO:Check Quantity
quantity_category = df.groupby("Category")[["Quantity", "Profit", "Discount"]].sum()
print(quantity_category)
top_sale = (
    df.groupby(["Product Name", "Sub-Category"])[["Quantity", "Profit", "Discount"]]
    .sum()
    .sort_values("Profit", ascending=False)
    .head(10)
)
bottle_sale = (
    df.groupby(["Product Name", "Sub-Category"])[["Quantity", "Profit", "Discount"]]
    .sum()
    .sort_values("Profit", ascending=True)
    .head(10)
    .reset_index()
)
print(bottle_sale)

# NOTE:have discount over 1.00 untill profit ติดลบ
# NOTE:ลองหาcorr.
corr_matrix = df[["Sales", "Quantity", "Discount", "Profit"]].corr()
print(corr_matrix)
# NOTE:ตอนนี้ไม่มีcorr
# NOTE:Cluster Sub-Category and profit
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

groupby1 = (
    df.groupby("Sub-Category")[["Sales", "Quantity", "Discount", "Profit"]]
    .sum()
    .reset_index()
)
X = groupby1[["Sales", "Quantity", "Discount", "Profit"]]
x_scaled = StandardScaler().fit_transform(X)
from sklearn.metrics import silhouette_score

silhouette_list = []
k_range = range(2, 11)
for k in k_range:
    kmeans_test = KMeans(n_clusters=k, random_state=42)
    labels = kmeans_test.fit_predict(x_scaled)
    silhouette_list.append(silhouette_score(x_scaled, labels))
best_k = k_range[silhouette_list.index(max(silhouette_list))]

kmeans = KMeans(n_clusters=best_k, random_state=42)

groupby1["cluster"] = kmeans.fit_predict(x_scaled)
print(groupby1.sort_values("cluster"))
# NOTE:Cluter Region
groupby2 = (
    df.groupby("Region")[["Sales", "Quantity", "Discount", "Profit"]]
    .sum()
    .reset_index()
)
X2 = groupby2[["Sales", "Quantity", "Discount", "Profit"]]
x2_scaled = StandardScaler().fit_transform(X2)

silhouette_list = []
k_range = range(2, 4)
for k in k_range:
    kmeans_test = KMeans(n_clusters=k, random_state=42)
    labels = kmeans_test.fit_predict(x2_scaled)
    silhouette_list.append(silhouette_score(x2_scaled, labels))
best_k2 = k_range[silhouette_list.index(max(silhouette_list))]

kmeans = KMeans(n_clusters=best_k2, random_state=42)

groupby2["cluster"] = kmeans.fit_predict(x2_scaled)
print(groupby2.sort_values("cluster"))
# NOTE:เหมือนจะสรุปได้ว่า East , West เป็นกลุ่มใหญ่มีปริมาณและกำลัการซื้อสูงกว่า ในเมืองและภาคใต้
