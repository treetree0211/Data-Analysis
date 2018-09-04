
# coding: utf-8

# In[1]:


from bs4 import BeautifulSoup
import requests
import pandas as pd
from pandas import Series, DataFrame


# In[2]:


# analysis html table data, return 3 series
def analysis_table(content):
    soup = BeautifulSoup(content, "lxml")    
    tables = soup.find_all('table')
    
    datas = []
    rows = tables[3].findAll('tr')

    for tr in rows:
        cols = tr.findAll('td')

        for td in cols:
            text = td.find(text = True)
            #print text,
            if text is not None:
                datas.append(text)
    
    name = []
    share = []
    value = []

    index = 0

    for item in datas:
        if ('SOLE' in item and index-7>0):
            name.append(datas[index-7])
            share.append(datas[index-3])
            value.append(datas[index-4])

        index += 1
    
    
    name = Series(name)
    name = name.drop(name.index[0])
    share = Series(share)
    share = share.drop(share.index[0])
    value = Series(value)
    value = value.drop(value.index[0])
    
    
    return name,share,value


# In[3]:


# 1. get orginal diagram
orig_url = "https://www.sec.gov/Archives/edgar/data/1510589/000090266417003324/xslForm13F_X01/infotable.xml"


# In[4]:


orig_result = requests.get(orig_url)
c = orig_result.content
# can be called only one time
orig_name, orig_share, orig_value = analysis_table(c)


# In[5]:


# 2. get after1Q data
af1q_url = "https://www.sec.gov/Archives/edgar/data/1510589/000090266417004351/xslForm13F_X01/infotable.xml"
af1g_result = requests.get(af1q_url)
c_q1 = af1g_result.content
# can be called only one time
af1g_name, af1g_share, af1g_value = analysis_table(c_q1)


# In[6]:


# 3. get after2Q data
af2q_url = "https://www.sec.gov/Archives/edgar/data/1510589/000090266418001173/xslForm13F_X01/infotable.xml"
af2g_result = requests.get(af2q_url)
c_q2 = af2g_result.content
# can be called only one time
af2g_name, af2g_share, af2g_value = analysis_table(c_q2)


# In[7]:


# 4. get current data
now_url = "https://www.sec.gov/Archives/edgar/data/1510589/000090266418003164/xslForm13F_X01/infotable.xml"
now_result = requests.get(now_url)
c_now = now_result.content
# can be called only one time
now_name, now_share, now_value = analysis_table(c_now)


# In[61]:


from __future__ import division
# a:old value, b: new value, return string
def quota(a, b):
    if a > b :
        return "(-%.2f%%)" % (((float(a)-float(b))/float(a))*100)
    
    if a == b:
        return "(0.0%)"
    
    if a < b:
        return "(+%.2f%%)" %(((float(b)-float(a))/float(a))*100)


# In[51]:


quota("63","33")


# In[10]:


# map ticker name and share or ticker name and map together
def map_list(name, share):
    
    shares = []
    
    for s in share:
        shares.append(cal_value(s))
        
    dict_ticker = Series(shares, index=name)
    
    return dict_ticker


# In[11]:


# get globale value for [name: share] [name: value] in different quarter
o_share_list = map_list(orig_name, orig_share)
o_value_list = map_list(orig_name, orig_value)

aq1_share_list = map_list(af1g_name, af1g_share)
aq1_value_list = map_list(af1g_name, af1g_value)

aq2_share_list = map_list(af2g_name, af2g_share)
aq2_value_list = map_list(af2g_name, af2g_value)

n_share_list = map_list(now_name, now_share)
n_value_list = map_list(now_name, now_value)


# In[299]:


aq1_share_list.head()


# In[300]:


aq2_share_list.head()


# In[9]:


# conver string to value
def cal_value(value):
    value_list = value.split(',')
    result = ""

    i = 0
    while i < len(value_list):
        result += value_list[i]
        i+=1
    
    return int(result)


# In[281]:


cal_value(af1g_share.get(1))


# In[284]:


# get venture total value
def get_total_value(orig_value):
    
    index1 = 1
    value1 = 0
    for i in orig_value:
        value1 += cal_value(orig_value.get(index1))
        index1 += 1
        
    return value1


# In[285]:


get_total_value(orig_value)


# In[286]:


get_total_value(af1g_value)


# In[287]:


get_total_value(af2g_value)


# In[288]:


get_total_value(now_value)


# In[222]:


sec_report = pd.concat([orig_name, orig_share, orig_value, af1g_name, af1g_share, 
                       af1g_value, af2g_name, af2g_share, af2g_value,now_name,
                       now_share, now_value], axis=1)
sec_report.columns = ['Original Name', 'Original Share', 'Original Value', 
                     'After 1 Quarter Name', 'After 1 Quarter Share', 'After 1 Quarter Value',
                     'After 2 Quarter Name', 'After 2 Quarter Share', 'After 2 Quarter Value',
                     'Current Name', 'Current Share', 'Current Value']


# In[223]:


sec_report


# In[12]:


# creat ticker object
class Ticker(object):
    
    def __init__(self, share, value, s_change, v_change):
        self.share = share
        self.value = value
        self.s_change = s_change
        self.v_change = v_change
        
    def __str__(self):
        # Override to print a readable string presentation of your object
        # below is a dynamic way of doing this without explicity constructing the string manually
        return ', '.join(['{key}={value}'.format(key=key, value=self.__dict__.get(key)) for key in self.__dict__])


# In[62]:


# set global value
ticker_map = {}
#quarters = ["original", "after1q", "after2q", "currrent"]
#get original ticker map   arg: name list, return map
def get_original_map(name, map1, map2):
    
    for n in name:
        share = map1.get(n)
        value = map2.get(n)
    
        single_map = {}
#         series = []
#         series.append(share)
#         series.append(value)
        ticker = Ticker(share = share, value = value, s_change = "New", v_change = "New")
        single_map[0] = ticker
        
        ticker_map[n] = single_map
    
    return ticker_map


# In[63]:


ticker_map = get_original_map(orig_name, o_share_list, o_value_list)


# In[64]:


def assign_ticker(names, shares, values, cur_index):
    for n in names:
        if n in ticker_map:
            i = cur_index - 1
            has_pre = False
            
            while i>=0:
                if i in ticker_map.get(n):
                    pre_share = ticker_map.get(n).get(i).share
                    pre_value = ticker_map.get(n).get(i).value
                    new_share = shares.get(n)
                    new_value = values.get(n)
                    
                    dist_share = quota(pre_share, new_share)
                    dist_value = quota(pre_value, new_value)

                    new_ticker = Ticker(share = new_share, value = new_value, s_change=dist_share, v_change=dist_value)
                    ticker_map.get(n)[cur_index] = new_ticker
                    has_pre = True
                    break
                else:
                    i -= 1
            
            if has_pre == False:
                new_share = shares.get(n)
                new_value = values.get(n)
                
                new_ticker = Ticker(share = new_share, value = new_value, s_change="(new)", v_change="(new)")
                single_map = {}
                single_map[cur_index] = new_ticker
                ticker_map[n] = single_map
            
        else:
            # ticker is a new one
            new_share = shares.get(n)
            new_value = values.get(n)

            new_ticker = Ticker(share = new_share, value = new_value, s_change="(new)", v_change="(new)")
            single_map = {}
            single_map[cur_index] = new_ticker
            ticker_map[n] = single_map


# In[65]:


assign_ticker(af1g_name, aq1_share_list, aq1_value_list, 1)
assign_ticker(af2g_name, aq2_share_list, aq2_value_list, 2)
assign_ticker(now_name, n_share_list, n_value_list, 3)


# In[66]:


dis_name = []
dis_0_share = []
dis_0_value = []
dis_1_share = []
dis_1_value = []
dis_2_share = []
dis_2_value = []
dis_3_share = []
dis_3_value = []


def display_ticker():
   
    for n in sorted(ticker_map):
        dis_name.append(n)
        
        if 0 in ticker_map.get(n):
            share = ticker_map.get(n).get(0).share
            value = ticker_map.get(n).get(0).value
            
            dis_0_share.append(share)
            dis_0_value.append(value)
        else:
            dis_0_share.append("-")
            dis_0_value.append("-")
        
        if 1 in ticker_map.get(n):
            share = ticker_map.get(n).get(1).share
            value = ticker_map.get(n).get(1).value
            
            s_cpt = ticker_map.get(n).get(1).s_change
            v_cpt = ticker_map.get(n).get(1).v_change
            
            dist_s = str(share) + str(s_cpt)
            dist_v = str(value) + str(v_cpt)
            
            dis_1_share.append(dist_s)
            dis_1_value.append(dist_v)
        else:
            dis_1_share.append("-")
            dis_1_value.append("-")
            
        if 2 in ticker_map.get(n):
            share = ticker_map.get(n).get(2).share
            value = ticker_map.get(n).get(2).value
            
            s_cpt = ticker_map.get(n).get(2).s_change
            v_cpt = ticker_map.get(n).get(2).v_change
            
            dist_s = str(share) + str(s_cpt)
            dist_v = str(value) + str(v_cpt)
            
            dis_2_share.append(dist_s)
            dis_2_value.append(dist_v)
        else:
            dis_2_share.append("-")
            dis_2_value.append("-")
            
        if 3 in ticker_map.get(n):
            share = ticker_map.get(n).get(3).share
            value = ticker_map.get(n).get(3).value
            
            s_cpt = ticker_map.get(n).get(3).s_change
            v_cpt = ticker_map.get(n).get(3).v_change
            
            dist_s = str(share) + str(s_cpt)
            dist_v = str(value) + str(v_cpt)
            
            dis_3_share.append(dist_s)
            dis_3_value.append(dist_v)
        else:
            dis_3_share.append("-")
            dis_3_value.append("-")   


# In[67]:


display_ticker()


# In[68]:


dis_name = Series(dis_name)
dis_0_share = Series(dis_0_share)
dis_0_value = Series(dis_0_value)
dis_1_share = Series(dis_1_share)
dis_2_share = Series(dis_2_share)
dis_3_share = Series(dis_3_share)
dis_1_value = Series(dis_1_value)
dis_2_value = Series(dis_2_value)
dis_3_value = Series(dis_3_value)

# display
sec_report = pd.concat([dis_name, dis_0_share, dis_0_value, dis_1_share, dis_1_value, dis_2_share, dis_2_value, dis_3_share, dis_3_value], axis=1)
sec_report.columns = ['Name', 'Original Share', 'Original Value', 
                      'After 1 Quarter Share', 'After 1 Quarter Value',
                      'After 2 Quarter Share', 'After 2 Quarter Value',
                      'Current Share', 'Current Value']


# In[69]:


sec_report

