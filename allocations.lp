\* Staff_Observation_Assignment_Problem *\
Minimize
OBJ: max_workload
Subject To
Consecutive_Hours_(staff_1,_observation_10,_time_0)_Constraint:
 Assignments_(1,_10,_0) + Assignments_(1,_10,_1) <= 2
Consecutive_Hours_(staff_1,_observation_10,_time_1)_Constraint:
 Assignments_(1,_10,_0) + Assignments_(1,_10,_1) + Assignments_(1,_10,_2) <= 2
Consecutive_Hours_(staff_1,_observation_10,_time_2)_Constraint:
 Assignments_(1,_10,_1) + Assignments_(1,_10,_2) + Assignments_(1,_10,_3) <= 2
Consecutive_Hours_(staff_1,_observation_10,_time_3)_Constraint:
 Assignments_(1,_10,_2) + Assignments_(1,_10,_3) + Assignments_(1,_10,_4) <= 2
Consecutive_Hours_(staff_1,_observation_10,_time_4)_Constraint:
 Assignments_(1,_10,_3) + Assignments_(1,_10,_4) + Assignments_(1,_10,_5) <= 2
Consecutive_Hours_(staff_2,_observation_10,_time_0)_Constraint:
 Assignments_(2,_10,_0) + Assignments_(2,_10,_1) <= 2
Consecutive_Hours_(staff_2,_observation_10,_time_1)_Constraint:
 Assignments_(2,_10,_0) + Assignments_(2,_10,_1) + Assignments_(2,_10,_2) <= 2
Consecutive_Hours_(staff_2,_observation_10,_time_2)_Constraint:
 Assignments_(2,_10,_1) + Assignments_(2,_10,_2) + Assignments_(2,_10,_3) <= 2
Consecutive_Hours_(staff_2,_observation_10,_time_3)_Constraint:
 Assignments_(2,_10,_2) + Assignments_(2,_10,_3) + Assignments_(2,_10,_4) <= 2
Consecutive_Hours_(staff_2,_observation_10,_time_4)_Constraint:
 Assignments_(2,_10,_3) + Assignments_(2,_10,_4) + Assignments_(2,_10,_5) <= 2
Consecutive_Hours_(staff_3,_observation_10,_time_0)_Constraint:
 Assignments_(3,_10,_0) + Assignments_(3,_10,_1) <= 2
Consecutive_Hours_(staff_3,_observation_10,_time_1)_Constraint:
 Assignments_(3,_10,_0) + Assignments_(3,_10,_1) + Assignments_(3,_10,_2) <= 2
Consecutive_Hours_(staff_3,_observation_10,_time_2)_Constraint:
 Assignments_(3,_10,_1) + Assignments_(3,_10,_2) + Assignments_(3,_10,_3) <= 2
Consecutive_Hours_(staff_3,_observation_10,_time_3)_Constraint:
 Assignments_(3,_10,_2) + Assignments_(3,_10,_3) + Assignments_(3,_10,_4) <= 2
Consecutive_Hours_(staff_3,_observation_10,_time_4)_Constraint:
 Assignments_(3,_10,_3) + Assignments_(3,_10,_4) + Assignments_(3,_10,_5) <= 2
Max_Workload_Constraint_Staff_1: Assignments_(1,_10,_0)
 + Assignments_(1,_10,_1) + Assignments_(1,_10,_2) + Assignments_(1,_10,_3)
 + Assignments_(1,_10,_4) + Assignments_(1,_10,_5) - max_workload <= 0
Max_Workload_Constraint_Staff_2: Assignments_(2,_10,_0)
 + Assignments_(2,_10,_1) + Assignments_(2,_10,_2) + Assignments_(2,_10,_3)
 + Assignments_(2,_10,_4) + Assignments_(2,_10,_5) - max_workload <= 0
Max_Workload_Constraint_Staff_3: Assignments_(3,_10,_0)
 + Assignments_(3,_10,_1) + Assignments_(3,_10,_2) + Assignments_(3,_10,_3)
 + Assignments_(3,_10,_4) + Assignments_(3,_10,_5) - max_workload <= 0
Minimum_Break_(staff_1,_time_3)_Constraint: Assignments_(1,_10,_2)
 + Assignments_(1,_10,_3) <= 1
Minimum_Break_(staff_1,_time_4)_Constraint: Assignments_(1,_10,_3)
 + Assignments_(1,_10,_4) <= 1
Minimum_Break_(staff_1,_time_5)_Constraint: Assignments_(1,_10,_4)
 + Assignments_(1,_10,_5) <= 1
Minimum_Break_(staff_2,_time_3)_Constraint: Assignments_(2,_10,_2)
 + Assignments_(2,_10,_3) <= 1
Minimum_Break_(staff_2,_time_4)_Constraint: Assignments_(2,_10,_3)
 + Assignments_(2,_10,_4) <= 1
Minimum_Break_(staff_2,_time_5)_Constraint: Assignments_(2,_10,_4)
 + Assignments_(2,_10,_5) <= 1
Minimum_Break_(staff_3,_time_3)_Constraint: Assignments_(3,_10,_2)
 + Assignments_(3,_10,_3) <= 1
Minimum_Break_(staff_3,_time_4)_Constraint: Assignments_(3,_10,_3)
 + Assignments_(3,_10,_4) <= 1
Minimum_Break_(staff_3,_time_5)_Constraint: Assignments_(3,_10,_4)
 + Assignments_(3,_10,_5) <= 1
Observation_Level_1_(observation_10,_time_0)_Constraint:
 Assignments_(1,_10,_0) + Assignments_(2,_10,_0) + Assignments_(3,_10,_0) = 1
Observation_Level_1_(observation_10,_time_1)_Constraint:
 Assignments_(1,_10,_1) + Assignments_(2,_10,_1) + Assignments_(3,_10,_1) = 1
Observation_Level_1_(observation_10,_time_10)_Constraint:
 Assignments_(1,_10,_10) + Assignments_(2,_10,_10) + Assignments_(3,_10,_10)
 = 1
Observation_Level_1_(observation_10,_time_11)_Constraint:
 Assignments_(1,_10,_11) + Assignments_(2,_10,_11) + Assignments_(3,_10,_11)
 = 1
Observation_Level_1_(observation_10,_time_2)_Constraint:
 Assignments_(1,_10,_2) + Assignments_(2,_10,_2) + Assignments_(3,_10,_2) = 1
Observation_Level_1_(observation_10,_time_3)_Constraint:
 Assignments_(1,_10,_3) + Assignments_(2,_10,_3) + Assignments_(3,_10,_3) = 1
Observation_Level_1_(observation_10,_time_4)_Constraint:
 Assignments_(1,_10,_4) + Assignments_(2,_10,_4) + Assignments_(3,_10,_4) = 1
Observation_Level_1_(observation_10,_time_5)_Constraint:
 Assignments_(1,_10,_5) + Assignments_(2,_10,_5) + Assignments_(3,_10,_5) = 1
Observation_Level_1_(observation_10,_time_6)_Constraint:
 Assignments_(1,_10,_6) + Assignments_(2,_10,_6) + Assignments_(3,_10,_6) = 1
Observation_Level_1_(observation_10,_time_7)_Constraint:
 Assignments_(1,_10,_7) + Assignments_(2,_10,_7) + Assignments_(3,_10,_7) = 1
Observation_Level_1_(observation_10,_time_8)_Constraint:
 Assignments_(1,_10,_8) + Assignments_(2,_10,_8) + Assignments_(3,_10,_8) = 1
Observation_Level_1_(observation_10,_time_9)_Constraint:
 Assignments_(1,_10,_9) + Assignments_(2,_10,_9) + Assignments_(3,_10,_9) = 1
Staff_Row_Constraint_(staff_1,_time_0)_Constraint: Assignments_(1,_10,_0) <= 1
Staff_Row_Constraint_(staff_1,_time_1)_Constraint: Assignments_(1,_10,_1) <= 1
Staff_Row_Constraint_(staff_1,_time_10)_Constraint: Assignments_(1,_10,_10)
 <= 1
Staff_Row_Constraint_(staff_1,_time_11)_Constraint: Assignments_(1,_10,_11)
 <= 1
Staff_Row_Constraint_(staff_1,_time_2)_Constraint: Assignments_(1,_10,_2) <= 1
Staff_Row_Constraint_(staff_1,_time_3)_Constraint: Assignments_(1,_10,_3) <= 1
Staff_Row_Constraint_(staff_1,_time_4)_Constraint: Assignments_(1,_10,_4) <= 1
Staff_Row_Constraint_(staff_1,_time_5)_Constraint: Assignments_(1,_10,_5) <= 1
Staff_Row_Constraint_(staff_1,_time_6)_Constraint: Assignments_(1,_10,_6) <= 1
Staff_Row_Constraint_(staff_1,_time_7)_Constraint: Assignments_(1,_10,_7) <= 1
Staff_Row_Constraint_(staff_1,_time_8)_Constraint: Assignments_(1,_10,_8) <= 1
Staff_Row_Constraint_(staff_1,_time_9)_Constraint: Assignments_(1,_10,_9) <= 1
Staff_Row_Constraint_(staff_2,_time_0)_Constraint: Assignments_(2,_10,_0) <= 1
Staff_Row_Constraint_(staff_2,_time_1)_Constraint: Assignments_(2,_10,_1) <= 1
Staff_Row_Constraint_(staff_2,_time_10)_Constraint: Assignments_(2,_10,_10)
 <= 1
Staff_Row_Constraint_(staff_2,_time_11)_Constraint: Assignments_(2,_10,_11)
 <= 1
Staff_Row_Constraint_(staff_2,_time_2)_Constraint: Assignments_(2,_10,_2) <= 1
Staff_Row_Constraint_(staff_2,_time_3)_Constraint: Assignments_(2,_10,_3) <= 1
Staff_Row_Constraint_(staff_2,_time_4)_Constraint: Assignments_(2,_10,_4) <= 1
Staff_Row_Constraint_(staff_2,_time_5)_Constraint: Assignments_(2,_10,_5) <= 1
Staff_Row_Constraint_(staff_2,_time_6)_Constraint: Assignments_(2,_10,_6) <= 1
Staff_Row_Constraint_(staff_2,_time_7)_Constraint: Assignments_(2,_10,_7) <= 1
Staff_Row_Constraint_(staff_2,_time_8)_Constraint: Assignments_(2,_10,_8) <= 1
Staff_Row_Constraint_(staff_2,_time_9)_Constraint: Assignments_(2,_10,_9) <= 1
Staff_Row_Constraint_(staff_3,_time_0)_Constraint: Assignments_(3,_10,_0) <= 1
Staff_Row_Constraint_(staff_3,_time_1)_Constraint: Assignments_(3,_10,_1) <= 1
Staff_Row_Constraint_(staff_3,_time_10)_Constraint: Assignments_(3,_10,_10)
 <= 1
Staff_Row_Constraint_(staff_3,_time_11)_Constraint: Assignments_(3,_10,_11)
 <= 1
Staff_Row_Constraint_(staff_3,_time_2)_Constraint: Assignments_(3,_10,_2) <= 1
Staff_Row_Constraint_(staff_3,_time_3)_Constraint: Assignments_(3,_10,_3) <= 1
Staff_Row_Constraint_(staff_3,_time_4)_Constraint: Assignments_(3,_10,_4) <= 1
Staff_Row_Constraint_(staff_3,_time_5)_Constraint: Assignments_(3,_10,_5) <= 1
Staff_Row_Constraint_(staff_3,_time_6)_Constraint: Assignments_(3,_10,_6) <= 1
Staff_Row_Constraint_(staff_3,_time_7)_Constraint: Assignments_(3,_10,_7) <= 1
Staff_Row_Constraint_(staff_3,_time_8)_Constraint: Assignments_(3,_10,_8) <= 1
Staff_Row_Constraint_(staff_3,_time_9)_Constraint: Assignments_(3,_10,_9) <= 1
Staff_Time_Availability_(staff_1,_observation_10,_time_10)_Constraint:
 Assignments_(1,_10,_10) = 0
Staff_Time_Availability_(staff_1,_observation_10,_time_11)_Constraint:
 Assignments_(1,_10,_11) = 0
Staff_Time_Availability_(staff_1,_observation_10,_time_6)_Constraint:
 Assignments_(1,_10,_6) = 0
Staff_Time_Availability_(staff_1,_observation_10,_time_7)_Constraint:
 Assignments_(1,_10,_7) = 0
Staff_Time_Availability_(staff_1,_observation_10,_time_8)_Constraint:
 Assignments_(1,_10,_8) = 0
Staff_Time_Availability_(staff_1,_observation_10,_time_9)_Constraint:
 Assignments_(1,_10,_9) = 0
Staff_Time_Availability_(staff_2,_observation_10,_time_10)_Constraint:
 Assignments_(2,_10,_10) = 0
Staff_Time_Availability_(staff_2,_observation_10,_time_11)_Constraint:
 Assignments_(2,_10,_11) = 0
Staff_Time_Availability_(staff_2,_observation_10,_time_6)_Constraint:
 Assignments_(2,_10,_6) = 0
Staff_Time_Availability_(staff_2,_observation_10,_time_7)_Constraint:
 Assignments_(2,_10,_7) = 0
Staff_Time_Availability_(staff_2,_observation_10,_time_8)_Constraint:
 Assignments_(2,_10,_8) = 0
Staff_Time_Availability_(staff_2,_observation_10,_time_9)_Constraint:
 Assignments_(2,_10,_9) = 0
Staff_Time_Availability_(staff_3,_observation_10,_time_10)_Constraint:
 Assignments_(3,_10,_10) = 0
Staff_Time_Availability_(staff_3,_observation_10,_time_11)_Constraint:
 Assignments_(3,_10,_11) = 0
Staff_Time_Availability_(staff_3,_observation_10,_time_6)_Constraint:
 Assignments_(3,_10,_6) = 0
Staff_Time_Availability_(staff_3,_observation_10,_time_7)_Constraint:
 Assignments_(3,_10,_7) = 0
Staff_Time_Availability_(staff_3,_observation_10,_time_8)_Constraint:
 Assignments_(3,_10,_8) = 0
Staff_Time_Availability_(staff_3,_observation_10,_time_9)_Constraint:
 Assignments_(3,_10,_9) = 0
Binaries
Assignments_(1,_10,_0)
Assignments_(1,_10,_1)
Assignments_(1,_10,_10)
Assignments_(1,_10,_11)
Assignments_(1,_10,_2)
Assignments_(1,_10,_3)
Assignments_(1,_10,_4)
Assignments_(1,_10,_5)
Assignments_(1,_10,_6)
Assignments_(1,_10,_7)
Assignments_(1,_10,_8)
Assignments_(1,_10,_9)
Assignments_(2,_10,_0)
Assignments_(2,_10,_1)
Assignments_(2,_10,_10)
Assignments_(2,_10,_11)
Assignments_(2,_10,_2)
Assignments_(2,_10,_3)
Assignments_(2,_10,_4)
Assignments_(2,_10,_5)
Assignments_(2,_10,_6)
Assignments_(2,_10,_7)
Assignments_(2,_10,_8)
Assignments_(2,_10,_9)
Assignments_(3,_10,_0)
Assignments_(3,_10,_1)
Assignments_(3,_10,_10)
Assignments_(3,_10,_11)
Assignments_(3,_10,_2)
Assignments_(3,_10,_3)
Assignments_(3,_10,_4)
Assignments_(3,_10,_5)
Assignments_(3,_10,_6)
Assignments_(3,_10,_7)
Assignments_(3,_10,_8)
Assignments_(3,_10,_9)
End
