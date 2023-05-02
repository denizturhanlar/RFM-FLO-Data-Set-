#Customer Segmentation with RFM 
###############################################################
# Business Problem
###############################################################
# FLO aims to divide its customer base into segments and devise marketing strategies tailored to each of these segments. 
#To achieve this, customer behaviors will be analyzed and used to create clusters of customers with similar behaviors.

###############################################################
# Story of Data Set 
# The dataset consists of information obtained from the past shopping behaviors of customers who made their last purchases as OmniChannel
#(both online and offline shopper) in 2020 - 2021.

# master_id: Unique customer number
# order_channel : Which channel of the shopping platform is used (Android, ios, Desktop, Mobile, Offline)
# last_order_channel : The channel where the most recent purchase was made
# first_order_date : Date of the customer's first purchase
# last_order_date :  Customer's last purchase date
# last_order_date_online : The date of the last purchase made by the customer on the online platform
# last_order_date_offline : Last shopping date made by the customer on the offline platform
# order_num_total_ever_online : The total number of purchases made by the customer on the online platform
# order_num_total_ever_offline : Total number of purchases made by the customer offline
# customer_value_total_ever_offline : Total fee paid by the customer for offline purchases
# customer_value_total_ever_online : The total fee paid by the customer for their online shopping
# interested_in_categories_12 : List of categories the customer has shopped in the last 12 months

###############################################################
# TASKS
# TASK 1: Data Understanding and Preparing 
# TASK 2: Calculate RFM Metrics 
# TASK 3: Calculate RF ve RFM Scores 
# TASK 4: Identification of RF Scores as Segments
# TASK 5: It's time for action!
# TASK 6: Functionalize the entire process.

###############################################################
# TASK 1: Data Understanding

# let's import the libraries
import pandas as pd
import datetime as dt
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.2f' % x)
pd.set_option('display.width',1000)

# read the csv file and saved a copy
df_ = pd.read_csv("WEEK03/flo_data_20k.csv")
df = df_.copy()
df.head()


# 2. In Data Set
# Make the first 10 observations, Variable names, Size, Descriptive statistics, Null value, Variable types, review.

df.head(10)        #First 10 observations
df.columns         #Variable names
df.shape           #Size
df.describe().T    #Descriptive statistics
df.isnull().sum()  #Null value
df.info()          #Variable types,review

# 3. Omnichannel states that customers shop from both online and offline platforms.
# Create new variables for the total number of purchases and expenditures of each customer.
df["order_num_total"] = df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]
df["customer_value_total"] = df["customer_value_total_ever_offline"] + df["customer_value_total_ever_online"]
df.head()

# 4. Examine the types of variables. Convert the type of variables expressing the date to date.
date_columns = df.columns[df.columns.str.contains("date")]
# we change the type with apply(pd.to_datetime) 
df[date_columns] = df[date_columns].apply(pd.to_datetime)
df.info()

# 5. Look at the distribution of the number of customers in the shopping channels, the total number of products purchased and the total expenditures.
# we do groupby
df.groupby("order_channel").agg({"master_id":"count",
                                 "order_num_total":"sum",
                                 "customer_value_total":"sum"})

# 6. List the top 10 customers who bring the most profit.
#sort_values means sort, ascending = False, goes from large to small
df.sort_values("customer_value_total", ascending=False)[:10]

# 7.List the first 10 customers who have placed the most orders.
df.sort_values("order_num_total", ascending=False)[:10]

# 8. Functionalize the data pre-preparation process.
def data_prep(dataframe):
    dataframe["order_num_total"] = dataframe["order_num_total_ever_online"] + dataframe["order_num_total_ever_offline"]
    dataframe["customer_value_total"] = dataframe["customer_value_total_ever_offline"] + dataframe["customer_value_total_ever_online"]
    date_columns = dataframe.columns[dataframe.columns.str.contains("date")]
    dataframe[date_columns] = dataframe[date_columns].apply(pd.to_datetime)
    return df

###############################################################
# TASK 2: Calculate RFM Metrics
# The date of analysis 2 days after the date of the last purchase in the data set
# we find the deadline using max() the deadline is : 2021-05-30 and is usually thought of as +2 days after the deadline
df["last_order_date"].max()
analysis_date = dt.datetime(2021,6,1)


# a new rfm dataframe with customer_id, recency, frequency and monetary values
rfm = pd.DataFrame()
rfm["customer_id"] = df["master_id"]
rfm["recency"] = (analysis_date - df["last_order_date"]).astype('timedelta64[D]')
rfm["frequency"] = df["order_num_total"]
rfm["monetary"] = df["customer_value_total"]

rfm.head()

###############################################################
# TASK 3:Calculating RF and RFM Scores
# Converting Decency, Frequency and Monetary metrics into scores between 1-5 with the help of qcut and
# Saving these scores as recency_score, frequency_score and monetary_score
rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])  #we need to put a rank in frequency
rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

rfm.head()


# expressing recency_score and frequency_score as a single variable and saving them as RF_SCORE
rfm["RF_SCORE"] = (rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str))


# 3. expressing recency_score and frequency_score and monetary_score as a single variable and saving them as RFM_SCORE
rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str) + rfm['monetary_score'].astype(str))

rfm.head()

rfm[rfm["RF_SCORE"] == '34'].head()
###############################################################
# TASK 4: Identification of RF Scores as Segments
###############################################################

# To make the generated RFM scores more understandable, segment identification and converting RF_SCORE into segments with the help of the defined seg_map
seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

rfm['segment'] = rfm['RF_SCORE'].replace(seg_map, regex=True)


rfm.head()

##################################################
# we could also do it by defining the function
def rf_score(score):
    if score in ('11','12','21','22'):
        return 'hibernating'
    elif score in ('13','14','23','24'):
        return 'at_risk'
    elif score in ('15','25'):
        return 'cant_loose'
    elif score in ('31','32'):
        return 'about_to_sleep'
    elif score in ('33'):
        return 'need_attention'
    elif score in ('34','35','44','45'):
        return 'loyal_customers'
    elif score in ('41'):
        return 'promising'
    elif score in ('51'):
        return 'new_customers'
    elif score in ('42','43','52','53'):
        return 'potantial_loyalists'
    else:
        return 'champions'



rfm["SEGMENT"] = rfm["RF_SCORE"].apply(lambda x: rf_score(x))
rfm.head()

rfm.drop("SEGMENT",axis=1,inplace =True)
###############################################################
# TASK 5: It's time for action!
###############################################################

# 1. Check the recency, frequency and monetary averages of the segments.
rfm[["segment", "recency", "frequency", "monetary"]].groupby("segment").agg(["mean", "count"])

#                          recency       frequency       monetary
#                        mean count      mean count     mean count
# segment
# about_to_sleep       113.79  1629      2.40  1629   359.01  1629
# at_Risk              241.61  3131      4.47  3131   646.61  3131
# cant_loose           235.44  1200     10.70  1200  1474.47  1200
# champions             17.11  1932      8.93  1932  1406.63  1932
# hibernating          247.95  3604      2.39  3604   366.27  3604
# loyal_customers       82.59  3361      8.37  3361  1216.82  3361
# need_attention       113.83   823      3.73   823   562.14   823
# new_customers         17.92   680      2.00   680   339.96   680
# potential_loyalists   37.16  2938      3.30  2938   533.18  2938
# promising             58.92   647      2.00   647   335.67   647


# 2. With the help of RFM analysis, find the customers in the relevant profile for 2 cases and save the customer IDs to the csv.

# a. FLO is incorporating a new women's shoe brand into its structure. The product prices of the brand it includes are above the general customer preferences.
#For this reason, it is desirable to be contacted specifically with the customers in the profile who will be interested in the promotion of the brand and product sales
#These customers were planned to be loyal and female category shoppers. 
#Add the customer id numbers to the csv file yeni_marka_hedef_müşteri_id it as a cvs.

target_segments_customer_ids = rfm[rfm["segment"].isin(["champions","loyal_customers"])]["customer_id"]
cust_ids = df[(df["master_id"].isin(target_segments_customer_ids)) & (df["interested_in_categories_12"].str.contains("KADIN"))]["master_id"]
cust_ids.to_csv("yeni_marka_hedef_müşteri_id_.csv", index=False)
cust_ids.shape



# b. It is planned to discount close to 40% on Men's and children's products.
#Who are one of the good customers in the past who are interested in the categories related to this discount, but who have not shopped for a long time
#and newly arrived customers want to be specifically targeted.
# Download the IDs of the customers in the appropriate profile to the csv file_hedef_muster_ids. save it as csv.

target_segments_customer_ids = rfm[rfm["segment"].isin(["cant_loose","hibernating","new_customers"])]["customer_id"]
cust_ids = df[(df["master_id"].isin(target_segments_customer_ids)) & ((df["interested_in_categories_12"].str.contains("ERKEK"))|(df["interested_in_categories_12"].str.contains("COCUK")))]["master_id"]
cust_ids.to_csv("indirim_hedef_müşteri_ids.csv", index=False)


###############################################################
# BONUS
###############################################################

def create_rfm(dataframe):
    # Preparing the data
    dataframe["order_num_total"] = dataframe["order_num_total_ever_online"] + dataframe["order_num_total_ever_offline"]
    dataframe["customer_value_total"] = dataframe["customer_value_total_ever_offline"] + dataframe["customer_value_total_ever_online"]
    date_columns = dataframe.columns[dataframe.columns.str.contains("date")]
    dataframe[date_columns] = dataframe[date_columns].apply(pd.to_datetime)


    # Calculate the RFM Metrics
    dataframe["last_order_date"].max()  # 2021-05-30
    analysis_date = dt.datetime(2021, 6, 1)
    rfm = pd.DataFrame()
    rfm["customer_id"] = dataframe["master_id"]
    rfm["recency"] = (analysis_date - dataframe["last_order_date"]).astype('timedelta64[D]')
    rfm["frequency"] = dataframe["order_num_total"]
    rfm["monetary"] = dataframe["customer_value_total"]

    # Calculate the RF and RFM Scores 
    rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
    rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
    rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])
    rfm["RF_SCORE"] = (rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str))
    rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str) + rfm['monetary_score'].astype(str))


    # Naming of Segments
    seg_map = {
        r'[1-2][1-2]': 'hibernating',
        r'[1-2][3-4]': 'at_Risk',
        r'[1-2]5': 'cant_loose',
        r'3[1-2]': 'about_to_sleep',
        r'33': 'need_attention',
        r'[3-4][4-5]': 'loyal_customers',
        r'41': 'promising',
        r'51': 'new_customers',
        r'[4-5][2-3]': 'potential_loyalists',
        r'5[4-5]': 'champions'
    }
    rfm['segment'] = rfm['RF_SCORE'].replace(seg_map, regex=True)

    return rfm[["customer_id", "recency","frequency","monetary","RF_SCORE","RFM_SCORE","segment"]]

rfm_df = create_rfm(df)



