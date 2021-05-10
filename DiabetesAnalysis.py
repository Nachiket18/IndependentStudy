'''
Created on 09-Mar-2021

@author: Nachiket Deo
'''

import pymonetdb as pm
import pandas as pd
import matplotlib.pyplot as plot
import numpy as np
from sklearn.naive_bayes import ComplementNB,MultinomialNB
from sklearn.preprocessing import StandardScaler
from scipy import float64
from sklearn.metrics import accuracy_score, classification_report
from sklearn.metrics import f1_score
from sklearn import svm
from sklearn.utils import class_weight
from sklearn.neighbors import kneighbors_graph
from src.shortest_path_kernel import shortest_path_kernel 
from grakel.kernels import ShortestPath
from grakel import Graph
from grakel.utils import graph_from_networkx


import networkx as nx

connection = pm.connect(username="monetdb", password="monetdb",
                                    hostname="localhost", database="demo")


cursor = connection.cursor()


def build_kneighbors_graph(data):
        
    A = kneighbors_graph(data,20, mode='distance', include_self=True,metric = 'euclidean',n_jobs = -1)
    A = A.toarray()
    return A

def getDiabetesCausesStatistics():

    sql = 'with diabetes_percentage as ( select ( select count(hdl.seqn) as hdlCount from nhanes_cholesterol_hdl HDL inner join sys.nhanes_glycohemoglobin GLY on (GLY.seqn = HDL.seqn) where direct_hdl_cholesterol < 40 and GLY.glycohemoglobin > 6.5 ) as HDLCount, (select count(ct.seqn) as cotiCount from nhanes_cotinine CT inner join sys.nhanes_glycohemoglobin GLY on(GLY.seqn = CT.seqn) where cotinine > 1and GLY.glycohemoglobin > 6.5 ) as CotiCount ,(select count(LDL.seqn) as ldlCount from nhanes_cholesterol_ldl_triglycerides LDL inner join sys.nhanes_glycohemoglobin GLY on(GLY.seqn = LDL.seqn) where ldl_cholesterol_mg_dl > 130 and GLY.glycohemoglobin > 6.5 ) as ldlCount ,(select count(BP.seqn) as bpCount from nhanes_blood_pressure BP inner join sys.nhanes_glycohemoglobin GLY on(GLY.seqn = BP.seqn) where ((BP.systolic_blood_pres_1_rdg + BP.systolic_blood_pres_2_rdg + BP.systolic_blood_pres_3_rdg)/ 3) > 130 and GLY.glycohemoglobin > 6.5 ) as bpCount ) select * from diabetes_percentage'
    cursor.execute(sql)
    df_diabetes_percentage = pd.DataFrame(cursor.fetchall())
    df_diabetes_percentage.columns = ["HDL_Cholesterol","Nicotine","LDL_Cholesterol","Blood_Pressure"]

    cursor.execute('SELECT COUNT(*) FROM sys.nhanes_glycohemoglobin WHERE glycohemoglobin > 6.5')

    df_diabetes_total_cases = cursor.fetchone()
    df_diabetes_percentage = df_diabetes_percentage.div(df_diabetes_total_cases[0])
    df_diabetes_percentage = df_diabetes_percentage.mul(100)
    
    
    df_diabetes_percentage.plot.bar(rot=0)
    plot.show()

def getDiabetesStatisticsBMI():
    
    sql = 'WITH BMI_percentage AS ( SELECT GLY.seqn,body_mass_index FROM nhanes_glycohemoglobin GLY INNER JOIN nhanes_body_measures BM ON (GLY.seqn = BM.seqn) WHERE GLY.glycohemoglobin > 6.5) SELECT (SELECT COUNT(seqn) from BMI_percentage WHERE body_mass_index < 25) as BMI_25,(SELECT COUNT(seqn) from BMI_percentage WHERE body_mass_index > 25 and body_mass_index < 29) as BMI_29,(SELECT COUNT(seqn) from BMI_percentage WHERE body_mass_index > 29 and body_mass_index < 34) as BMI_34,(SELECT COUNT(seqn) from BMI_percentage WHERE body_mass_index > 34) as BMI_greater_35'
    cursor.execute(sql)
    df_diabetes_bmi = pd.DataFrame(cursor.fetchall())
    
    cursor.execute('SELECT COUNT(*) FROM sys.nhanes_glycohemoglobin WHERE glycohemoglobin > 6.5')

    df_diabetes_total_cases = cursor.fetchone()
    df_diabetes_bmi = df_diabetes_bmi.div(df_diabetes_total_cases[0])
    df_diabetes_bmi = df_diabetes_bmi.mul(100)
    df_diabetes_bmi.columns = ['BMI(<25)','BMI(25-29)','BMI(30-34)','BMI(>35)']
    
    df_diabetes_bmi.plot.bar(rot=0)
    plot.show()

def getDiabetesStatisticsEthnicity():
    
    sql = "WITH BMI_percentage AS ( SELECT GLY.seqn,DM.ridreth1 as Ethnicity FROM nhanes_glycohemoglobin GLY INNER JOIN sys.nhanes_demographics DM ON (GLY.seqn = DM.seqn) WHERE GLY.glycohemoglobin > 6.5) SELECT COUNT(ethnicity) FROM BMI_percentage GROUP BY Ethnicity ORDER BY Ethnicity ASC"
    cursor.execute(sql)
    df_diabetes_ethnicity = pd.DataFrame(cursor.fetchall())
    df_diabetes_ethnicity = df_diabetes_ethnicity.transpose()
    df_diabetes_ethnicity.columns = ['Mexican American','Other Hispanic','Non-Hispanic White','Non-Hispanic Black','Other Race - Including Multi-Racial']
    print(df_diabetes_ethnicity)
    
    cursor.execute('SELECT COUNT(*) FROM sys.nhanes_glycohemoglobin WHERE glycohemoglobin > 6.5')
    
    df_diabetes_total_cases = cursor.fetchone()
    df_diabetes_ethnicity = df_diabetes_ethnicity.div(df_diabetes_total_cases[0])
    df_diabetes_ethnicity = df_diabetes_ethnicity.mul(100)
    
    
    df_diabetes_ethnicity.plot.bar(rot=0)
    plot.show()

def getBayesProbability():
    
    sql_bp = 'WITH naive_bayes_bp AS ( SELECT count(BP.seqn) as BPDiabetesUnion,( SELECT COUNT(seqn) FROM nhanes_blood_pressure  WHERE ((systolic_blood_pres_1_rdg + systolic_blood_pres_2_rdg + systolic_blood_pres_3_rdg)/ 3) > 130) AS TotalHighBPCount, (select COUNT(SEQN) from nhanes_glycohemoglobin  where glycohemoglobin > 6.5) as TotalDiabetesCount,(select COUNT(SEQN) from nhanes_glycohemoglobin) as TotalRecords,(select COUNT(SEQN) from nhanes_blood_pressure)  as TotalBloodPressure FROM nhanes_blood_pressure BP INNER JOIN sys.nhanes_glycohemoglobin GLY on(GLY.seqn = BP.seqn) WHERE ((BP.systolic_blood_pres_1_rdg + BP.systolic_blood_pres_2_rdg + BP.systolic_blood_pres_3_rdg)/ 3) > 130 AND GLY.glycohemoglobin > 6.5 ) select sql_div(sql_mul(sql_div(cast (BPDiabetesUnion as float),cast (TotalDiabetesCount as float)),sql_div(cast (TotalDiabetesCount as float),cast(TotalRecords as float))),sql_div(cast (TotalHighBPCount as float),cast ( TotalBloodPressure as float) )), sql_div(cast (BPDiabetesUnion as float),cast (TotalDiabetesCount as float)) AS P_BP_Diabetes ,sql_div(cast (TotalHighBPCount as float),cast ( TotalBloodPressure as float) ) as P_BP from naive_bayes_bp'
    
    cursor.execute(sql_bp)
    df_diabetes_BP_Naive = pd.DataFrame(cursor.fetchall())
    df_diabetes_BP_Naive.columns = ['High Blood Pressure','P_BP_Diabetes','P_BP']
    
    sql_hdl = 'WITH naive_bayes_hdl as ( select count(hdl.seqn) as HdlDiabetesCount,(select COUNT(SEQN) FROM  nhanes_cholesterol_hdl  where direct_hdl_cholesterol  < 40) AS TotalHDLLowCount,(select COUNT(SEQN) from nhanes_glycohemoglobin  where glycohemoglobin > 6.5) as TotalDiabetesCount,(select COUNT(SEQN) from nhanes_glycohemoglobin) as TotalRecords,(select COUNT(SEQN) from nhanes_cholesterol_hdl) as TotalHDLRecords from nhanes_cholesterol_hdl HDL inner join sys.nhanes_glycohemoglobin GLY on(GLY.seqn = HDL.seqn) where direct_hdl_cholesterol < 40 and GLY.glycohemoglobin > 6.5) select sql_div(sql_mul(sql_div(cast(HdlDiabetesCount as float),cast(TotalDiabetesCount as float)),sql_div(cast (TotalDiabetesCount as float),cast(TotalRecords as float))),sql_div(cast (TotalHDLLowCount as float),cast(TotalHDLRecords as float))),sql_div(cast(HdlDiabetesCount as float),cast(TotalDiabetesCount as float)) as P_BP_Diabetes,sql_div(cast (TotalHDLLowCount as float),cast(TotalHDLRecords as float)) as P_HDL from naive_bayes_hdl'
    cursor.execute(sql_hdl)
    df_diabetes_HDL_Naive = pd.DataFrame(cursor.fetchall())
    df_diabetes_HDL_Naive.columns = ['Low_HDL','P_HDL_Diabetes','P_HDL']
    
    sql_cotinine = 'WITH naive_bayes_nicotine as (select count(ct.seqn) as cotiCount,(SELECT count(seqn) FROM nhanes_cotinine WHERE cotinine >= 1) as TotalHighNicotineCount,(select COUNT(SEQN) from nhanes_glycohemoglobin  where glycohemoglobin > 6.5) as TotalDiabetesCount,(select COUNT(SEQN) from nhanes_glycohemoglobin) as TotalRecords,(select COUNT(SEQN) from nhanes_cotinine ) as TotalNicotine from nhanes_cotinine CT inner join sys.nhanes_glycohemoglobin GLY on(GLY.seqn = CT.seqn)where cotinine >= 1 and GLY.glycohemoglobin > 6.5 ) select sql_div(sql_mul(sql_div(cast(cotiCount as float),cast(TotalDiabetesCount as float)),SQL_DIV(CAST(TotalDiabetesCount as float),cast(TotalRecords as float))),sql_div (cast(TotalHighNicotineCount as float),cast(TotalNicotine as float))),sql_div (cast(cotiCount as float), cast(TotalDiabetesCount as float)) as P_Nicotine_Diabetes,sql_div (cast(cotiCount as float),cast(TotalNicotine as float)) as P_Nicotine from naive_bayes_nicotine'
    
    cursor.execute(sql_cotinine)
    df_diabetes_Nicotine_Naive = pd.DataFrame(cursor.fetchall())
    df_diabetes_Nicotine_Naive.columns = ['High Nicotine', 'P_Nicotine_Diabetes','P_Nicotine']
    
    sql_ldl = 'WITH naive_bayes_ldl as ( select count(LDL.seqn) as CountLDL,(select COUNT(SEQN) from nhanes_glycohemoglobin  where glycohemoglobin > 6.5) as TotalDiabetesCount,(select COUNT(SEQN) from nhanes_glycohemoglobin) as TotalRecords,(select COUNT(SEQN) from nhanes_cholesterol_ldl_triglycerides) as TotalLDLRecords,(select COUNT(SEQN) from nhanes_cholesterol_ldl_triglycerides where ldl_cholesterol_mg_dl > 130) as TotalLDLHighRecords from nhanes_cholesterol_ldl_triglycerides LDL inner join sys.nhanes_glycohemoglobin GLY on(GLY.seqn = LDL.seqn) where ldl_cholesterol_mg_dl > 130 and GLY.glycohemoglobin > 6.5) select sql_div(sql_mul(sql_div(cast(CountLDL as float),cast(TotalDiabetesCount as float)),sql_div (cast(TotalDiabetesCount as float),cast(TotalRecords as float))),sql_div (cast(TotalLDLHighRecords as float),cast(TotalLDLRecords as float))),sql_div(cast(CountLDL as float),cast(TotalDiabetesCount as float)) as P_LDL_Diabetes,sql_div (cast(TotalLDLHighRecords as float),cast(TotalLDLRecords as float)) as P_LDL from naive_bayes_ldl'
    cursor.execute(sql_ldl)
    df_diabetes_LDL_Naive = pd.DataFrame(cursor.fetchall())
    df_diabetes_LDL_Naive.columns = ['High LDL', 'P_LDL_Diabetes','P_LDL']
    
    sql_not_bp = 'WITH naive_bayes_bp AS ( SELECT count(BP.seqn) as BPDiabetesUnion,( SELECT COUNT(seqn) FROM nhanes_blood_pressure  WHERE ((systolic_blood_pres_1_rdg + systolic_blood_pres_2_rdg + systolic_blood_pres_3_rdg)/ 3) < 130) AS TotalHighBPCount, (select COUNT(SEQN) from nhanes_glycohemoglobin  where glycohemoglobin > 6.5) as TotalDiabetesCount,(select COUNT(SEQN) from nhanes_glycohemoglobin) as TotalRecords,(select COUNT(SEQN) from nhanes_blood_pressure)  as TotalBloodPressure FROM nhanes_blood_pressure BP INNER JOIN sys.nhanes_glycohemoglobin GLY on(GLY.seqn = BP.seqn) WHERE ((BP.systolic_blood_pres_1_rdg + BP.systolic_blood_pres_2_rdg + BP.systolic_blood_pres_3_rdg)/ 3) < 130 AND GLY.glycohemoglobin > 6.5 ) select sql_div(sql_mul(sql_div(cast (BPDiabetesUnion as float),cast (TotalDiabetesCount as float)),sql_div(cast (TotalDiabetesCount as float),cast(TotalRecords as float))),sql_div(cast (TotalHighBPCount as float),cast ( TotalBloodPressure as float) )), sql_div(cast (BPDiabetesUnion as float),cast (TotalDiabetesCount as float)) AS P_BP_Diabetes ,sql_div(cast (TotalHighBPCount as float),cast ( TotalBloodPressure as float) ) as P_BP from naive_bayes_bp'
    
    cursor.execute(sql_not_bp)
    df_diabetes_not_BP_Naive = pd.DataFrame(cursor.fetchall())
    df_diabetes_not_BP_Naive.columns = ['Not High Blood Pressure','P_Not_BP_Diabetes','P_Not_BP']
    
    
    sql_not_hdl = 'WITH naive_bayes_hdl as ( select count(hdl.seqn) as HdlDiabetesCount,(select COUNT(SEQN) FROM  nhanes_cholesterol_hdl  where direct_hdl_cholesterol  > 40) AS TotalHDLLowCount,(select COUNT(SEQN) from nhanes_glycohemoglobin  where glycohemoglobin > 6.5) as TotalDiabetesCount,(select COUNT(SEQN) from nhanes_glycohemoglobin) as TotalRecords,(select COUNT(SEQN) from nhanes_cholesterol_hdl) as TotalHDLRecords from nhanes_cholesterol_hdl HDL inner join sys.nhanes_glycohemoglobin GLY on(GLY.seqn = HDL.seqn) where direct_hdl_cholesterol > 40 and GLY.glycohemoglobin > 6.5) select sql_div(sql_mul(sql_div(cast(HdlDiabetesCount as float),cast(TotalDiabetesCount as float)),sql_div(cast (TotalDiabetesCount as float),cast(TotalRecords as float))),sql_div(cast (TotalHDLLowCount as float),cast(TotalHDLRecords as float))),sql_div(cast(HdlDiabetesCount as float),cast(TotalDiabetesCount as float)) as P_BP_Diabetes,sql_div(cast (TotalHDLLowCount as float),cast(TotalHDLRecords as float)) as P_HDL from naive_bayes_hdl'
    
    cursor.execute(sql_not_hdl)
    df_diabetes_not_HDL_Naive = pd.DataFrame(cursor.fetchall())
    df_diabetes_not_HDL_Naive.columns = ['Not Low_HDL','P_Not_HDL_Diabetes','P_Not_HDL']
    
    
    sql_not_ldl = 'WITH naive_bayes_ldl as ( select count(LDL.seqn) as CountLDL,(select COUNT(SEQN) from nhanes_glycohemoglobin  where glycohemoglobin > 6.5) as TotalDiabetesCount,(select COUNT(SEQN) from nhanes_glycohemoglobin) as TotalRecords,(select COUNT(SEQN) from nhanes_cholesterol_ldl_triglycerides) as TotalLDLRecords,(select COUNT(SEQN) from nhanes_cholesterol_ldl_triglycerides where ldl_cholesterol_mg_dl < 130) as TotalLDLHighRecords from nhanes_cholesterol_ldl_triglycerides LDL inner join sys.nhanes_glycohemoglobin GLY on(GLY.seqn = LDL.seqn) where ldl_cholesterol_mg_dl < 130 and GLY.glycohemoglobin > 6.5) select sql_div(sql_mul(sql_div(cast(CountLDL as float),cast(TotalDiabetesCount as float)),sql_div (cast(TotalDiabetesCount as float),cast(TotalRecords as float))),sql_div (cast(TotalLDLHighRecords as float),cast(TotalLDLRecords as float))),sql_div(cast(CountLDL as float),cast(TotalDiabetesCount as float)) as P_LDL_Diabetes,sql_div (cast(TotalLDLHighRecords as float),cast(TotalLDLRecords as float)) as P_LDL,sql_div((cast(TotalDiabetesCount as float)),(cast(TotalRecords as float))) as P_Diabetes from naive_bayes_ldl'
    
    cursor.execute(sql_not_ldl)
    df_diabetes_not_LDL_Naive = pd.DataFrame(cursor.fetchall())
    df_diabetes_not_LDL_Naive.columns = ['Not High LDL', 'P_Not_LDL_Diabetes','P_Not_LDL','P_Diabetes']
    
    sql_not_cotinine = 'WITH naive_bayes_nicotine as (select count(ct.seqn) as cotiCount,(SELECT count(seqn) FROM nhanes_cotinine WHERE cotinine < 1) as TotalHighNicotineCount,(select COUNT(SEQN) from nhanes_glycohemoglobin  where glycohemoglobin > 6.5) as TotalDiabetesCount,(select COUNT(SEQN) from nhanes_glycohemoglobin) as TotalRecords,(select COUNT(SEQN) from nhanes_cotinine ) as TotalNicotine from nhanes_cotinine CT inner join sys.nhanes_glycohemoglobin GLY on(GLY.seqn = CT.seqn)where cotinine < 1 and GLY.glycohemoglobin > 6.5 ) select sql_div(sql_mul(sql_div(cast(cotiCount as float),cast(TotalDiabetesCount as float)),SQL_DIV(CAST(TotalDiabetesCount as float),cast(TotalRecords as float))),sql_div (cast(TotalHighNicotineCount as float),cast(TotalNicotine as float))),sql_div (cast(cotiCount as float), cast(TotalDiabetesCount as float)) as P_Nicotine_Diabetes,sql_div (cast(cotiCount as float),cast(TotalNicotine as float)) as P_Nicotine from naive_bayes_nicotine'
    
    cursor.execute(sql_not_cotinine)
    df_diabetes_not_Nicotine_Naive = pd.DataFrame(cursor.fetchall())
    df_diabetes_not_Nicotine_Naive.columns = ['Not High Nicotine', 'P_Not_Nicotine_Diabetes','P_Not_Nicotine']
    
    df_data_individual_not_naive = pd.DataFrame(df_diabetes_not_BP_Naive['Not High Blood Pressure'])

    
    df_data_individual_not_naive['Not Low_HDL'] = df_diabetes_not_HDL_Naive['Not Low_HDL']
    df_data_individual_not_naive['Not High LDL'] = df_diabetes_not_LDL_Naive['Not High LDL']
    df_data_individual_not_naive['Not High Nicotine'] = df_diabetes_not_Nicotine_Naive['Not High Nicotine'] 
    df_data_individual_not_naive['P_Diabetes'] = df_diabetes_not_LDL_Naive['P_Diabetes']

    df_plot_data_individual_naive = pd.DataFrame(df_diabetes_HDL_Naive['Low_HDL'])    
    
    
    
    df_plot_data_individual_naive['High Blood Pressure'] = df_diabetes_BP_Naive['High Blood Pressure']
    df_plot_data_individual_naive['High Nicotine'] = df_diabetes_Nicotine_Naive['High Nicotine']
    df_plot_data_individual_naive['High LDL'] = df_diabetes_LDL_Naive['High LDL']
    df_plot_data_individual_naive.plot(kind = 'bar',title = 'Diabetes Prediction - Causes (Naive Bayes Probability)',yticks= [0.10,0.20,0.30,0.40,0.50,0.60,0.70])
    plot.show()
    
    
    
    
    ##MultiVariable
    
    sql_diabetes = 'SELECT sql_div(CAST (BP.TotalDiabetesCount as float),CAST(BP.TotalRecords as float)) as ProbabilityDiabetes FROM ( SELECT COUNT(SEQN) as TotalDiabetesCount, (select COUNT(SEQN) from nhanes_glycohemoglobin) as TotalRecords FROM nhanes_glycohemoglobin where glycohemoglobin > 6.5) BP'
    cursor.execute(sql_diabetes)
    df_diabetes = pd.DataFrame(cursor.fetchall())
    df_diabetes.columns = ['DiabetesProbability']
    
    
    
    HighBPLowHDLDiabetes = (df_diabetes_BP_Naive['High Blood Pressure'] * df_diabetes_HDL_Naive['Low_HDL'] * df_diabetes['DiabetesProbability']) / (df_diabetes_HDL_Naive['P_HDL'] * df_diabetes_BP_Naive['P_BP'])
    
    HighBPHighLDLDiabetes = (df_diabetes_BP_Naive['High Blood Pressure'] * df_diabetes_LDL_Naive['High LDL'] * df_diabetes['DiabetesProbability']) / (df_diabetes_LDL_Naive['P_LDL'] * df_diabetes_BP_Naive['P_BP'])
    
    HighBPHighNicotineDiabetes = (df_diabetes_BP_Naive['High Blood Pressure'] * df_diabetes_Nicotine_Naive['High Nicotine'] * df_diabetes['DiabetesProbability']) / (df_diabetes_Nicotine_Naive['P_Nicotine'] * df_diabetes_BP_Naive['P_BP'])
    
    HighLDLowHDLDiabetes = (df_diabetes_HDL_Naive['Low_HDL'] * df_diabetes_LDL_Naive['High LDL'] * df_diabetes['DiabetesProbability']) / (df_diabetes_HDL_Naive['P_HDL'] * df_diabetes_LDL_Naive['P_LDL'])
    
    
    HighBPLowHDLHighLDLDiabetes = (df_diabetes_BP_Naive['High Blood Pressure'] * df_diabetes_HDL_Naive['Low_HDL'] * df_diabetes_LDL_Naive['High LDL'] * df_diabetes['DiabetesProbability']) / (df_diabetes_HDL_Naive['P_HDL'] * df_diabetes_BP_Naive['P_BP'] * df_diabetes_LDL_Naive['P_LDL'])
    
    
    #print(df_diabetes_BP_Naive['High Blood Pressure'] * df_diabetes_HDL_Naive['Low_HDL'] * df_diabetes['DiabetesProbability'])
    
    #print (df_diabetes_HDL_Naive['P_HDL'] * df_diabetes_BP_Naive['P_BP'])
    

    
    df_plot_data_multivariable_naive = pd.DataFrame(HighBPLowHDLDiabetes)
    
    df_plot_data_multivariable_naive.columns = ['HighBP/LowHDL']
    
    df_plot_data_multivariable_naive['HighBP/HighLDL'] = HighBPHighLDLDiabetes
    df_plot_data_multivariable_naive['HighBP/HighNicotine'] = HighBPHighNicotineDiabetes
    df_plot_data_multivariable_naive['HighLDL/LowHDL'] = HighLDLowHDLDiabetes
    df_plot_data_multivariable_naive['HighBP/HighLDL/LowHDL'] = HighBPLowHDLHighLDLDiabetes

    #print(df_plot_data_multivariable_naive)

    df_plot_data_multivariable_naive.plot(kind = 'bar',title = 'Diabetes Prediction - MultipleVariable Causes (Naive Bayes Probability)',yticks= [0.10,0.20,0.30,0.40,0.50,0.60,0.70])    
    #print(df_plot_data_multivariable_naive)
    plot.show()
    
    return df_plot_data_individual_naive,df_data_individual_not_naive,df_diabetes
    
def getAgeDiabetesStatistics():    
    
    sql = 'select COUNT(DEMO_1.SEQN) as Less40 ,COUNT(DEMO_2.SEQN) as Less50 , COUNT(DEMO_3.SEQN) as Less60 , COUNT(DEMO_4.SEQN) as Less70 ,COUNT(DEMO_5.SEQN) as Greater70 from (select SEQN FROM nhanes_glycohemoglobin where glycohemoglobin > 6.5)GLY left join (select SEQN as SEQN from nhanes_demographics  where ridageyr >= 30 and ridageyr <= 40  ) DEMO_1 on (DEMO_1.SEQN = GLY.seqn) left join (select SEQN as SEQN from nhanes_demographics  where ridageyr >= 40 and ridageyr <= 50 ) DEMO_2 on (DEMO_2.SEQN = GLY.seqn ) left join ( select SEQN as SEQN from nhanes_demographics  where ridageyr >= 50 and ridageyr <= 60) DEMO_3 on (DEMO_3.SEQN = GLY.seqn) left join (    select SEQN as SEQN from nhanes_demographics      where ridageyr >= 60 and ridageyr  <=70) DEMO_4 on (DEMO_4.SEQN = GLY.seqn) left join (    select SEQN as SEQN from nhanes_demographics where ridageyr >= 70 ) DEMO_5 on (DEMO_5.SEQN = GLY.seqn)' 
    cursor.execute(sql)
    df_agediabetes = pd.DataFrame(cursor.fetchall())
    
    
    df_agediabetes.columns = ['30-40','40-50','50-60','60-70','70Plus']
    
    #print(df_agediabetes)
    
    df_agediabetes.plot(kind = 'bar',title = 'Age wise Diabetes Distribution',yticks= [10,30,50,100,130,150,200])
    
    #df_agediabetes.plot(kind = 'bar', title = 'Age wise Diabetes Distribution',yticks= [10,30,50,100,130,150,200])
    
    plot.show()

def NaiveBayesClassifierNewData(df_prior_bp,df_prior_hdl,df_prior_ldl,df_prior_cotinine,df_diabetes):

    sql = 'select bp.seqn,(Systolic_Blood_pres_1_rdg + Systolic_Blood_pres_2_rdg + Systolic_Blood_pres_3_rdg)/3 as Blood_Pressure,Direct_HDL_Cholesterol,LDL_cholesterol_mg_dL,Cotinine,Glycohemoglobin,case when Glycohemoglobin > 6.5 then 1when Glycohemoglobin < 6.5 then 0 end as isDiabetic from nhanes_blood_pressure_new bp inner join nhanes_Cholesterol_HDL_new hdl on (bp.seqn = hdl.seqn) inner join nhanes_cholesterol_ldl_triglycerides_new ldl on (cast (hdl.seqn as int) = cast(ldl.seqn as int)) inner join nhanes_Cotinine_new ct on (ldl.seqn = ct.seqn)inner join nhanes_Glycohemoglobin_new GLY on (GLY.seqn = ct.seqn)'    
    cursor.execute(sql)
    df_data_diabetes_new = pd.DataFrame(cursor.fetchall())
    df_data_diabetes_new.columns = ['SEQN','Blood_Pressure','HDL_Cholesterol','LDL_Cholesterol','Cotinine','Glycohemoglobin','isDiabetic']
    
    df_data_classified = pd.DataFrame()
    
    for index, row in df_data_diabetes_new.iterrows():
     
        if row['Blood_Pressure'] > 130:
            bp_prob = df_prior_bp['P_High_BP_Yes']
            bp_prob_not = df_prior_bp['P_High_BP_No']
            
        elif row['Blood_Pressure'] < 130:
            bp_prob = df_prior_bp['P_Low_BP_Yes']
            bp_prob_not = df_prior_bp['P_Low_BP_No']
        
        if row['HDL_Cholesterol'] > 40:
            hdl_prob = df_prior_hdl['P_High_HDL_Yes']
            hdl_prob_not = df_prior_hdl['P_High_HDL_No'] 
        
        else:
            hdl_prob = df_prior_hdl['P_Low_HDL_Yes']
            hdl_prob_not = df_prior_hdl['P_low_HDL_No']
        
        if row['LDL_Cholesterol'] > 130:
            ldl_prob = df_prior_ldl['P_High_LDL_Yes']
            ldl_prob_not = df_prior_ldl['P_High_LDL_No']
        else:
            ldl_prob = df_prior_ldl['P_Low_LDL_Yes']
            ldl_prob_not = df_prior_ldl['P_low_LDL_No']
            
        if row['Cotinine'] > 1:
            cot_prob = df_prior_cotinine['P_High_Cotinine_Yes']
            cot_prob_not = df_prior_cotinine['P_High_Cotinine_No']
        else:
            cot_prob = df_prior_cotinine['P_Low_Cotinine_Yes']
            cot_prob_not = df_prior_cotinine['P_Low_Cotinine_No']
        
        prob_1 = bp_prob * hdl_prob * ldl_prob * cot_prob * df_diabetes['P_Diabetes']
        prob_0 = bp_prob_not * hdl_prob_not * ldl_prob_not * cot_prob_not * df_diabetes['P_Diabetes_No']
        
        prob_x_prime = prob_1 * df_diabetes['P_Diabetes'] + prob_0 * df_diabetes['P_Diabetes_No']
        
        #print(prob_0[0],prob_1[0])
        #print(prob_x_prime[0])
        
        if prob_1[0] != 0 and prob_0[0] != 0:
            
            if (prob_1[0]/prob_x_prime[0]) > (prob_0[0]/prob_x_prime[0]) :
                df_data_classified['SEQN'] = df_data_diabetes_new['SEQN']
                df_data_classified['Actual'] = df_data_diabetes_new['isDiabetic']
                df_data_classified['Predicted'] = 1
            else:
                df_data_classified['SEQN'] = df_data_diabetes_new['SEQN']
                df_data_classified['Actual'] = df_data_diabetes_new['isDiabetic']
                df_data_classified['Predicted'] = 0
        
    df_data_classified.dropna(inplace = True)
    #print("Accuracy using Compliment Naive Bayes",accuracy_score(df_data_classified['Actual'],df_data_classified['Predicted']))
    
    print("Accuracy using Naive Bayes",accuracy_score(df_data_classified['Actual'],df_data_classified['Predicted']))
    
    print("Classification Report")
    print(classification_report(df_data_classified['Actual'], df_data_classified['Predicted'],zero_division = 1))
    
              
    return df_data_classified

def NaiveBayesClassifierNewDataWeighted():
    
    
    sql = 'select bp.seqn,(Systolic_Blood_pres_1_rdg + Systolic_Blood_pres_2_rdg + Systolic_Blood_pres_3_rdg)/3 as Blood_Pressure,Direct_HDL_Cholesterol,LDL_cholesterol_mg_dL,Cotinine,Glycohemoglobin,case when Glycohemoglobin > 6.5 then 1 when Glycohemoglobin < 6.5 then 0 end as isDiabetic from nhanes_blood_pressure bp inner join nhanes_Cholesterol_HDL hdl on (bp.seqn = hdl.seqn) inner join nhanes_cholesterol_ldl_triglycerides ldl on (cast (hdl.seqn as int) = cast(ldl.seqn as int)) inner join nhanes_Cotinine ct on (ldl.seqn = ct.seqn) inner join nhanes_Glycohemoglobin GLY on (GLY.seqn = ct.seqn)'    
    cursor.execute(sql)
    df_data_diabetes_causes = pd.DataFrame(cursor.fetchall())
    
    #df_data_diabetes_causes.replace([np.inf], np.nan, inplace=True)
    
    df_data_diabetes_causes = df_data_diabetes_causes.fillna(df_data_diabetes_causes.mean())
    
    #print(df_data_diabetes_causes)
    
    #print(df_data_diabetes_causes.where(df_data_diabetes_causes < 0).count())
    
    #np_X = df_data_diabetes_causes.to_numpy('float32')
    
    X = df_data_diabetes_causes.iloc[:,[1,2,3,4,5]]
    y = df_data_diabetes_causes.iloc[:, -1].values
    
    y= y.astype('int')
    
    #print(X.where(X < 0).count())
    
    #X[np.isnan(X)] = np.median(X[~np.isnan(X)])
    
#     print(np.any(np.isnan(X)))
#     print(np.all(np.isfinite(X)))
    
    #X = sc.fit_transform(X)
    
    
    classifier = ComplementNB()
    classifier.fit(X, y)
    
    sql_test_data = 'select bp.seqn,(Systolic_Blood_pres_1_rdg + Systolic_Blood_pres_2_rdg + Systolic_Blood_pres_3_rdg)/3 as Blood_Pressure,Direct_HDL_Cholesterol,LDL_cholesterol_mg_dL,Cotinine,Glycohemoglobin,case when Glycohemoglobin > 6.5 then 1 when Glycohemoglobin < 6.5 then 0 end as isDiabetic from nhanes_blood_pressure_new bp inner join nhanes_Cholesterol_HDL_new hdl on (bp.seqn = hdl.seqn) inner join nhanes_cholesterol_ldl_triglycerides_new ldl on (cast (hdl.seqn as int) = cast(ldl.seqn as int)) inner join nhanes_Cotinine_new ct on (ldl.seqn = ct.seqn)inner join nhanes_Glycohemoglobin_new GLY on (GLY.seqn = ct.seqn)'    
    cursor.execute(sql_test_data)
    df_data_diabetes_new = pd.DataFrame(cursor.fetchall())
    df_data_diabetes_new.columns = ['SEQN','Blood_Pressure','HDL_Cholesterol','LDL_Cholesterol','Cotinine','Glycohemoglobin','isDiabetic']
    
    df_data_diabetes_new.replace([np.inf, -np.inf], np.nan, inplace=True)
    df_data_diabetes_new = df_data_diabetes_new.fillna(df_data_diabetes_new.mean())
    
    X_new = df_data_diabetes_new.iloc[:, [1, 2, 3, 4, 5]].values
    Y_true = df_data_diabetes_new.iloc[:,-1].values
    
    Y_true = Y_true.astype('int')
    y_pred  =  classifier.predict(X_new)
    
    #print (y_pred == 1)

    print("Accuracy using Compliment Naive Bayes",accuracy_score(Y_true, y_pred))
    
    print("Classification Report_Compliment")
    print(classification_report(Y_true, y_pred))
    
    classifier_1 = MultinomialNB()
    classifier_1.fit(X, y)
    
    
    Y_predict_Multi = classifier_1.predict(X_new)
    
    #print (Y_predict_Multi == 1)
    
    print("Accuracy using Multinomial Naive Bayes",accuracy_score(Y_true, Y_predict_Multi))
    
    print("Classification Report_Multinomial")
    print (classification_report(Y_true, Y_predict_Multi))
    
    return df_data_diabetes_causes,df_data_diabetes_new
    
def svm_classification(df_data_diabetes_causes,df_data_diabetes_new):
    
    X = df_data_diabetes_causes.iloc[:,[0,1,2,3,4,5]]
    y = df_data_diabetes_causes.iloc[:, -1].values
    
    y= y.astype('int')
    
    #c_w = class_weight.compute_class_weight(class_weight = 'balanced',classes= [0,1],y = y)
    
    clf = svm.SVC(kernel="linear",class_weight = 'balanced')
    clf.fit(X, y)
    
    X_new = df_data_diabetes_new.iloc[:, [0, 1, 2, 3, 4, 5]].values
    Y_true = df_data_diabetes_new.iloc[:,-1].values
    
    Y_true = Y_true.astype('int')
    y_pred  =  clf.predict(X_new)
    
    print("Accuracy using SVM",accuracy_score(Y_true, y_pred))
    
    print("Classification Report - SVM")
    print(classification_report(Y_true, y_pred))


def OsteoporosisNaiveBayes():    
    
    sql = 'SELECT BMD.SEQN,Total_femur_BMD,DM.ridageyr as Age, case when Glycohemoglobin > 6.5 then 1 when Glycohemoglobin < 6.5 then 0 end as isDiabetic,BM.body_mass_index,case when Total_femur_BMD <= 0.64 then 1 when Total_femur_BMD > 0.64  then 0 end as isOsteoporosis FROM sys.nhanes_BMD BMD INNER join nhanes_glycohemoglobin GLY on (BMD.seqn = GLY.seqn) INNER join nhanes_demographics DM on (BMD.seqn = DM.seqn) inner join nhanes_body_measures BM on (BMD.seqn = BM.seqn)'    
    cursor.execute(sql)
    df_data_Osteoporosis_causes = pd.DataFrame(cursor.fetchall())
    
    
    
    df_data_Osteoporosis_causes = df_data_Osteoporosis_causes.fillna(df_data_Osteoporosis_causes.mean())
    
    X = df_data_Osteoporosis_causes.iloc[:,[1,2,3,4]]
    y = df_data_Osteoporosis_causes.iloc[:, -1].values
    
    y= y.astype('int')
    
    classifier = ComplementNB()
    classifier.fit(X, y)
    
    sql_test_data = 'SELECT BMD.SEQN,Total_femur_BMD,DM.ridageyr as Age, case when Glycohemoglobin > 6.5 then 1 when Glycohemoglobin < 6.5 then 0 end as isDiabetic,BM.body_mass_index,case when Total_femur_BMD <= 0.64 then 1 when Total_femur_BMD > 0.64  then 0 end as isOsteoporosis FROM sys.nhanes_BMD_new BMD INNER join nhanes_glycohemoglobin_new GLY on (BMD.seqn = GLY.seqn) INNER join nhanes_demographics DM on (BMD.seqn = DM.seqn) inner join nhanes_body_measures_new BM on (BMD.seqn = BM.seqn)'   
    
    cursor.execute(sql_test_data)
    df_data_Osteoporosis_causes_new = pd.DataFrame(cursor.fetchall())
    #df_data_diabetes_new.columns = ['SEQN','Blood_Pressure','HDL_Cholesterol','LDL_Cholesterol','Cotinine','Glycohemoglobin','isDiabetic']
    
    df_data_Osteoporosis_causes_new.replace([np.inf, -np.inf], np.nan, inplace=True)
    df_data_Osteoporosis_causes_new = df_data_Osteoporosis_causes_new.fillna(df_data_Osteoporosis_causes_new.mean())
    
    X_new = df_data_Osteoporosis_causes_new.iloc[:, [1, 2, 3, 4]].values
    Y_true = df_data_Osteoporosis_causes_new.iloc[:,-1].values
    
    Y_true = Y_true.astype('int')
    y_pred  =  classifier.predict(X_new)
    
    #print (y_pred == 1)

    print("Accuracy using Compliment Naive Bayes",accuracy_score(Y_true, y_pred))
    
    print("Classification Report_Compliment")
    print(classification_report(Y_true, y_pred))
    
    classifier_1 = MultinomialNB()
    classifier_1.fit(X, y)
    
    
    Y_predict_Multi = classifier_1.predict(X_new)
    
    #print (Y_predict_Multi == 1)
    
    print("Accuracy using Multinomial Naive Bayes",accuracy_score(Y_true, Y_predict_Multi))
    
    print("Classification Report_Multinomial")
    print (classification_report(Y_true, Y_predict_Multi))
    
    return df_data_Osteoporosis_causes,df_data_Osteoporosis_causes_new

def OsteoporosisSVM(df_data_Osteoporosis_causes,df_data_Osteoporosis_causes_new):     
    
    X = df_data_Osteoporosis_causes.iloc[:,[1,2,3,4]]
    y = df_data_Osteoporosis_causes.iloc[:, -1].values
    
    y= y.astype('int')
    
    #c_w = class_weight.compute_class_weight(class_weight = 'balanced',classes= [0,1],y = y)
    
    clf = svm.SVC(kernel="linear",class_weight = 'balanced')
    clf.fit(X, y)
    
    X_new = df_data_Osteoporosis_causes_new.iloc[:, [1, 2, 3, 4]].values
    Y_true = df_data_Osteoporosis_causes_new.iloc[:,-1].values
    
    Y_true = Y_true.astype('int')
    y_pred  =  clf.predict(X_new)
    
    print("Accuracy using SVM",accuracy_score(Y_true, y_pred))
    
    print("Classification Report - SVM")
    print(classification_report(Y_true, y_pred))


def OsteoporosisSVMShortestPath(df_data_Osteoporosis_causes,df_data_Osteoporosis_causes_new):     
    
    y = df_data_Osteoporosis_causes.iloc[:, -1].values
    
    y= y.astype('int')
    
    #class_0 = df_data_Osteoporosis_causes[df_data_Osteoporosis_causes[5] == 0]
    #class_1 = df_data_Osteoporosis_causes[df_data_Osteoporosis_causes[5] == 1]
    
    
    #print(type(class_0),type(class_1))
    
    graph_1 = build_kneighbors_graph(df_data_Osteoporosis_causes.iloc[:,[1,2,3,4]])
    #graph_2 = build_kneighbors_graph(class_1.iloc[:,[1,2,3,4]])
    graph_1_up = adj_list_to_matrix(graph_1,6917)
    
    G = Graph(graph_1_up)
    
    gk = ShortestPath(normalize=True)
    K_train = gk.fit_transform(G)
    
    
    clf = svm.SVC(kernel="precomputed",class_weight = 'balanced')
    clf.fit(K_train, y)
    
    Y_true = df_data_Osteoporosis_causes_new.iloc[:,-1].values
    
    Y_true = Y_true.astype('int')
    
    #class_0_test = df_data_Osteoporosis_causes_new[df_data_Osteoporosis_causes_new[5] == 0]
    #class_1_test = df_data_Osteoporosis_causes_new[df_data_Osteoporosis_causes_new[5] == 1]

    
    graph_1_test = build_kneighbors_graph(df_data_Osteoporosis_causes_new.iloc[:,[1,2,3,4]])
    
    graph_2_up = adj_list_to_matrix(graph_1_test,6917)
    
    G_2 = Graph(graph_2_up)
    
    #graph_2_test = build_kneighbors_graph(class_1_test.iloc[:,[1,2,3,4]])
    
    #G1_test = nx.from_numpy_array(graph_1_test)
    #G2_test = nx.from_numpy_array(graph_2_test)
   
    #graph_list_test = [G1_test,G2_test]
    
    #G_test = graph_from_networkx(graph_list_test)
    
    y_pred  =  clf.predict(G_2)
    
    print("Accuracy using SVM",accuracy_score(Y_true, y_pred))
    
    print("Classification Report - SVM")
    print(classification_report(Y_true, y_pred))

def adj_list_to_matrix(adj_list,n):

    adj_matrix = np.nan * np.zeros((n,n))
    print(adj_matrix.shape)
    np.fill_diagonal(adj_matrix,0)

    for j in range(0,len(adj_list)):
        tpl = adj_list[j]
        adj_matrix[tpl[0],tpl[1]] = tpl[2]
        
    print(adj_matrix)
    return adj_matrix
    

def main():
    
    #getDiabetesCausesStatistics()
    #getDiabetesStatisticsBMI()
    #getDiabetesStatisticsEthnicity()
    #df_1,df_2,df_3 = getBayesProbability()
    data_bp = {'P_High_BP_Yes':[0.41],'P_High_BP_No':[0.17],'P_Low_BP_No':[0.67],'P_Low_BP_Yes':[0.43]}
    
    df_prior_bp = pd.DataFrame(data = data_bp,columns = ['P_High_BP_Yes','P_High_BP_No','P_Low_BP_No','P_Low_BP_Yes'])
    #df_prior_bp.columns = ['P_High_BP_Yes','P_High_BP_No','P_Low_BP_No','P_Low_BP_Yes']
    
    #df_prior_bp['P_High_BP_Yes'] = 0.41
#     df_prior_bp['P_High_BP_No'] = 0.17
#     df_prior_bp['P_Low_BP_No'] = 0.67
#     df_prior_bp['P_Low_BP_Yes'] = 0.43
#     
    #df_prior_bp.insert(0.41,0.17,0.67,0.43)
    
    
    data_hdl = {'P_High_HDL_Yes':[0.70],'P_High_HDL_No':[0.15],'P_Low_HDL_Yes':[0.26],'P_low_HDL_No':[0.81]}
    df_prior_hdl = pd.DataFrame(data = data_hdl,columns = ['P_High_HDL_Yes','P_High_HDL_No','P_Low_HDL_Yes','P_low_HDL_No'])
    
    
    data_ldl = {'P_High_LDL_Yes':[0.27],'P_High_LDL_No':[0.25],'P_Low_LDL_Yes':[0.66],'P_low_LDL_No':[0.70]}
    df_prior_ldl = pd.DataFrame(data = data_ldl, columns = ['P_High_LDL_Yes','P_High_LDL_No','P_Low_LDL_Yes','P_low_LDL_No'])


    data_coti = {'P_High_Cotinine_Yes':[0.29],'P_High_Cotinine_No':[0.30],'P_Low_Cotinine_Yes':[0.697],'P_Low_Cotinine_No':[0.690]}
    df_prior_cotinine = pd.DataFrame(data = data_coti,columns = ['P_High_Cotinine_Yes','P_High_Cotinine_No','P_Low_Cotinine_Yes','P_Low_Cotinine_No'])
    
    
    data_diabetes = {'P_Diabetes':[0.0810150631021848],'P_Diabetes_No':[0.9189849368978151]}
    df_diabetes = pd.DataFrame(data = data_diabetes, columns = ['P_Diabetes','P_Diabetes_No'])
    
    
    ##
    ## Type-2 Diabetes Functions 
    ##

    out = NaiveBayesClassifierNewData(df_prior_bp,df_prior_hdl,df_prior_ldl,df_prior_cotinine,df_diabetes)
    #print(out[out['Actual'] == 1])
    df_data_diabetes_causes,df_data_diabetes_new = NaiveBayesClassifierNewDataWeighted()
 
    ##
    ##Osteoporosis Functions 
    ##
    
    #df_data_Osteoporosis_causes,df_data_Osteoporosis_causes_new = OsteoporosisNaiveBayes()
    #OsteoporosisSVMShortestPath(df_data_Osteoporosis_causes,df_data_Osteoporosis_causes_new)
    #OsteoporosisSVM(df_data_Osteoporosis_causes,df_data_Osteoporosis_causes_new)
    
    
    
    
if __name__ == '__main__':
    main() 
