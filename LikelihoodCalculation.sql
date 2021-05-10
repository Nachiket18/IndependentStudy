
-- Blood Pressure Likelihood 

with diabetes 
AS
(
	select bp.seqn,(Systolic_Blood_pres_1_rdg + Systolic_Blood_pres_2_rdg + Systolic_Blood_pres_3_rdg)/3 as Blood_Pressure,
	Direct_HDL_Cholesterol,
	LDL_cholesterol_mg_dL,
	Cotinine,
	Glycohemoglobin,
	case 
		when Glycohemoglobin >= 6.5 then 1
		when Glycohemoglobin < 6.5 then 0
	end as isDiabetic
from nhanes_blood_pressure_new bp inner join nhanes_Cholesterol_HDL_new hdl on (bp.seqn = hdl.seqn)
inner join nhanes_cholesterol_ldl_triglycerides_new ldl on (cast (hdl.seqn as int) = cast(ldl.seqn as int))
inner join nhanes_Cotinine_new ct on (ldl.seqn = ct.seqn)
inner join nhanes_Glycohemoglobin_new GLY on (GLY.seqn = ct.seqn)
)
select cast ((select COUNT(SEQN) from diabetes where Blood_Pressure < 130 and isDiabetic = 1) as float) /
cast((SELECT COUNT(SEQN) from diabetes where isDiabetic = 1) as float)

GO

with diabetes 
AS
(
	select bp.seqn,(Systolic_Blood_pres_1_rdg + Systolic_Blood_pres_2_rdg + Systolic_Blood_pres_3_rdg)/3 as Blood_Pressure,
	Direct_HDL_Cholesterol,
	LDL_cholesterol_mg_dL,
	Cotinine,
	Glycohemoglobin,
	case 
		when Glycohemoglobin >= 6.5 then 1
		when Glycohemoglobin < 6.5 then 0
	end as isDiabetic
from nhanes_blood_pressure_new bp inner join nhanes_Cholesterol_HDL_new hdl on (bp.seqn = hdl.seqn)
inner join nhanes_cholesterol_ldl_triglycerides_new ldl on (cast (hdl.seqn as int) = cast(ldl.seqn as int))
inner join nhanes_Cotinine_new ct on (ldl.seqn = ct.seqn)
inner join nhanes_Glycohemoglobin_new GLY on (GLY.seqn = ct.seqn)
)
select cast ((select COUNT(SEQN) from diabetes where Blood_Pressure > 130 and isDiabetic = 1) as float) /
cast((SELECT COUNT(SEQN) from diabetes where isDiabetic = 1) as float)

GO




with diabetes 
AS
(
	select bp.seqn,(Systolic_Blood_pres_1_rdg + Systolic_Blood_pres_2_rdg + Systolic_Blood_pres_3_rdg)/3 as Blood_Pressure,
	Direct_HDL_Cholesterol,
	LDL_cholesterol_mg_dL,
	Cotinine,
	Glycohemoglobin,
	case 
		when Glycohemoglobin >= 6.5 then 1
		when Glycohemoglobin < 6.5 then 0
	end as isDiabetic
from nhanes_blood_pressure_new bp inner join nhanes_Cholesterol_HDL_new hdl on (bp.seqn = hdl.seqn)
inner join nhanes_cholesterol_ldl_triglycerides_new ldl on (cast (hdl.seqn as int) = cast(ldl.seqn as int))
inner join nhanes_Cotinine_new ct on (ldl.seqn = ct.seqn)
inner join nhanes_Glycohemoglobin_new GLY on (GLY.seqn = ct.seqn)
)
select cast ((select COUNT(SEQN) from diabetes where Blood_Pressure > 130 and isDiabetic = 0) as float) /
cast((SELECT COUNT(SEQN) from diabetes where isDiabetic = 1) as float)

GO


with diabetes 
AS
(
	select bp.seqn,(Systolic_Blood_pres_1_rdg + Systolic_Blood_pres_2_rdg + Systolic_Blood_pres_3_rdg)/3 as Blood_Pressure,
	Direct_HDL_Cholesterol,
	LDL_cholesterol_mg_dL,
	Cotinine,
	Glycohemoglobin,
	case 
		when Glycohemoglobin >= 6.5 then 1
		when Glycohemoglobin < 6.5 then 0
	end as isDiabetic
from nhanes_blood_pressure_new bp inner join nhanes_Cholesterol_HDL_new hdl on (bp.seqn = hdl.seqn)
inner join nhanes_cholesterol_ldl_triglycerides_new ldl on (cast (hdl.seqn as int) = cast(ldl.seqn as int))
inner join nhanes_Cotinine_new ct on (ldl.seqn = ct.seqn)
inner join nhanes_Glycohemoglobin_new GLY on (GLY.seqn = ct.seqn)
)
select cast ((select COUNT(SEQN) from diabetes where Blood_Pressure < 130 and isDiabetic = 0) as float) /
cast((SELECT COUNT(SEQN) from diabetes where isDiabetic = 1) as float)


-- LDL Cholesterol 

with diabetes 
AS
(
	select bp.seqn,(Systolic_Blood_pres_1_rdg + Systolic_Blood_pres_2_rdg + Systolic_Blood_pres_3_rdg)/3 as Blood_Pressure,
	Direct_HDL_Cholesterol,
	LDL_cholesterol_mg_dL,
	Cotinine,
	Glycohemoglobin,
	case 
		when Glycohemoglobin >= 6.5 then 1
		when Glycohemoglobin < 6.5 then 0
	end as isDiabetic
from nhanes_blood_pressure_new bp inner join nhanes_Cholesterol_HDL_new hdl on (bp.seqn = hdl.seqn)
inner join nhanes_cholesterol_ldl_triglycerides_new ldl on (cast (hdl.seqn as int) = cast(ldl.seqn as int))
inner join nhanes_Cotinine_new ct on (ldl.seqn = ct.seqn)
inner join nhanes_Glycohemoglobin_new GLY on (GLY.seqn = ct.seqn)
)
select cast ((select COUNT(SEQN) from diabetes where LDL_cholesterol_mg_dL < 130 and isDiabetic = 0) as float) /
cast((SELECT COUNT(SEQN) from diabetes where isDiabetic = 0) as float)

GO

with diabetes 
AS
(
	select bp.seqn,(Systolic_Blood_pres_1_rdg + Systolic_Blood_pres_2_rdg + Systolic_Blood_pres_3_rdg)/3 as Blood_Pressure,
	Direct_HDL_Cholesterol,
	LDL_cholesterol_mg_dL,
	Cotinine,
	Glycohemoglobin,
	case 
		when Glycohemoglobin >= 6.5 then 1
		when Glycohemoglobin < 6.5 then 0
	end as isDiabetic
from nhanes_blood_pressure_new bp inner join nhanes_Cholesterol_HDL_new hdl on (bp.seqn = hdl.seqn)
inner join nhanes_cholesterol_ldl_triglycerides_new ldl on (cast (hdl.seqn as int) = cast(ldl.seqn as int))
inner join nhanes_Cotinine_new ct on (ldl.seqn = ct.seqn)
inner join nhanes_Glycohemoglobin_new GLY on (GLY.seqn = ct.seqn)
)
select cast ((select COUNT(SEQN) from diabetes where LDL_cholesterol_mg_dL > 130 and isDiabetic = 0) as float) /
cast((SELECT COUNT(SEQN) from diabetes where isDiabetic = 0) as float)


GO


with diabetes 
AS
(
	select bp.seqn,(Systolic_Blood_pres_1_rdg + Systolic_Blood_pres_2_rdg + Systolic_Blood_pres_3_rdg)/3 as Blood_Pressure,
	Direct_HDL_Cholesterol,
	LDL_cholesterol_mg_dL,
	Cotinine,
	Glycohemoglobin,
	case 
		when Glycohemoglobin >= 6.5 then 1
		when Glycohemoglobin < 6.5 then 0
	end as isDiabetic
from nhanes_blood_pressure_new bp inner join nhanes_Cholesterol_HDL_new hdl on (bp.seqn = hdl.seqn)
inner join nhanes_cholesterol_ldl_triglycerides_new ldl on (cast (hdl.seqn as int) = cast(ldl.seqn as int))
inner join nhanes_Cotinine_new ct on (ldl.seqn = ct.seqn)
inner join nhanes_Glycohemoglobin_new GLY on (GLY.seqn = ct.seqn)
)
select cast ((select COUNT(SEQN) from diabetes where LDL_cholesterol_mg_dL < 130 and isDiabetic = 1) as float) /
cast((SELECT COUNT(SEQN) from diabetes where isDiabetic = 0) as float)

GO


with diabetes 
AS
(
	select bp.seqn,(Systolic_Blood_pres_1_rdg + Systolic_Blood_pres_2_rdg + Systolic_Blood_pres_3_rdg)/3 as Blood_Pressure,
	Direct_HDL_Cholesterol,
	LDL_cholesterol_mg_dL,
	Cotinine,
	Glycohemoglobin,
	case 
		when Glycohemoglobin >= 6.5 then 1
		when Glycohemoglobin < 6.5 then 0
	end as isDiabetic
from nhanes_blood_pressure_new bp inner join nhanes_Cholesterol_HDL_new hdl on (bp.seqn = hdl.seqn)
inner join nhanes_cholesterol_ldl_triglycerides_new ldl on (cast (hdl.seqn as int) = cast(ldl.seqn as int))
inner join nhanes_Cotinine_new ct on (ldl.seqn = ct.seqn)
inner join nhanes_Glycohemoglobin_new GLY on (GLY.seqn = ct.seqn)
)
select cast ((select COUNT(SEQN) from diabetes where LDL_cholesterol_mg_dL > 130 and isDiabetic = 1) as float) /
cast((SELECT COUNT(SEQN) from diabetes where isDiabetic = 0) as float)


-- Cotinine Likelihood 



with diabetes 
AS
(
	select bp.seqn,(Systolic_Blood_pres_1_rdg + Systolic_Blood_pres_2_rdg + Systolic_Blood_pres_3_rdg)/3 as Blood_Pressure,
	Direct_HDL_Cholesterol,
	LDL_cholesterol_mg_dL,
	Cotinine,
	Glycohemoglobin,
	case 
		when Glycohemoglobin >= 6.5 then 1
		when Glycohemoglobin < 6.5 then 0
	end as isDiabetic
from nhanes_blood_pressure_new bp inner join nhanes_Cholesterol_HDL_new hdl on (bp.seqn = hdl.seqn)
inner join nhanes_cholesterol_ldl_triglycerides_new ldl on (cast (hdl.seqn as int) = cast(ldl.seqn as int))
inner join nhanes_Cotinine_new ct on (ldl.seqn = ct.seqn)
inner join nhanes_Glycohemoglobin_new GLY on (GLY.seqn = ct.seqn)
)
select cast ((select COUNT(SEQN) from diabetes where Cotinine < 1 and isDiabetic = 1) as float) /
cast((SELECT COUNT(SEQN) from diabetes where isDiabetic = 1) as float)

GO


with diabetes 
AS
(
	select bp.seqn,(Systolic_Blood_pres_1_rdg + Systolic_Blood_pres_2_rdg + Systolic_Blood_pres_3_rdg)/3 as Blood_Pressure,
	Direct_HDL_Cholesterol,
	LDL_cholesterol_mg_dL,
	Cotinine,
	Glycohemoglobin,
	case 
		when Glycohemoglobin >= 6.5 then 1
		when Glycohemoglobin < 6.5 then 0
	end as isDiabetic
from nhanes_blood_pressure_new bp inner join nhanes_Cholesterol_HDL_new hdl on (bp.seqn = hdl.seqn)
inner join nhanes_cholesterol_ldl_triglycerides_new ldl on (cast (hdl.seqn as int) = cast(ldl.seqn as int))
inner join nhanes_Cotinine_new ct on (ldl.seqn = ct.seqn)
inner join nhanes_Glycohemoglobin_new GLY on (GLY.seqn = ct.seqn)
)
select cast ((select COUNT(SEQN) from diabetes where Cotinine > 1 and isDiabetic = 1) as float) /
cast((SELECT COUNT(SEQN) from diabetes where isDiabetic = 1) as float)

GO


with diabetes 
AS
(
	select bp.seqn,(Systolic_Blood_pres_1_rdg + Systolic_Blood_pres_2_rdg + Systolic_Blood_pres_3_rdg)/3 as Blood_Pressure,
	Direct_HDL_Cholesterol,
	LDL_cholesterol_mg_dL,
	Cotinine,
	Glycohemoglobin,
	case 
		when Glycohemoglobin >= 6.5 then 1
		when Glycohemoglobin < 6.5 then 0
	end as isDiabetic
from nhanes_blood_pressure_new bp inner join nhanes_Cholesterol_HDL_new hdl on (bp.seqn = hdl.seqn)
inner join nhanes_cholesterol_ldl_triglycerides_new ldl on (cast (hdl.seqn as int) = cast(ldl.seqn as int))
inner join nhanes_Cotinine_new ct on (ldl.seqn = ct.seqn)
inner join nhanes_Glycohemoglobin_new GLY on (GLY.seqn = ct.seqn)
)
select cast ((select COUNT(SEQN) from diabetes where Cotinine < 1 and isDiabetic = 0) as float) /
cast((SELECT COUNT(SEQN) from diabetes where isDiabetic = 1) as float)

GO


with diabetes 
AS
(
	select bp.seqn,(Systolic_Blood_pres_1_rdg + Systolic_Blood_pres_2_rdg + Systolic_Blood_pres_3_rdg)/3 as Blood_Pressure,
	Direct_HDL_Cholesterol,
	LDL_cholesterol_mg_dL,
	Cotinine,
	Glycohemoglobin,
	case 
		when Glycohemoglobin >= 6.5 then 1
		when Glycohemoglobin < 6.5 then 0
	end as isDiabetic
from nhanes_blood_pressure_new bp inner join nhanes_Cholesterol_HDL_new hdl on (bp.seqn = hdl.seqn)
inner join nhanes_cholesterol_ldl_triglycerides_new ldl on (cast (hdl.seqn as int) = cast(ldl.seqn as int))
inner join nhanes_Cotinine_new ct on (ldl.seqn = ct.seqn)
inner join nhanes_Glycohemoglobin_new GLY on (GLY.seqn = ct.seqn)
)
select cast ((select COUNT(SEQN) from diabetes where Cotinine > 1 and isDiabetic = 0) as float) /
cast((SELECT COUNT(SEQN) from diabetes where isDiabetic = 1) as float)