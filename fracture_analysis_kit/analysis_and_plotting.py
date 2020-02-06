import resources.analysis_main as analysis_main

# Analysis name
analysis_name = "nikke"

# Input directories
branchdirs = [
    r"Data/Valmis_data_08082019/Detailed_branches_and_nodes",
    r"Data/Valmis_data_08082019/20m_branches_and_nodes",
    r"Data/Valmis_data_08082019/LiDAR_branches_and_nodes",
]
tracedirs = [
    r"Data/Valmis_data_08082019/Detailed_traces",
    r"Data/Valmis_data_08082019/20m_traces",
    r"Data/Valmis_data_08082019/LiDAR_traces",
]
nodedirs = [
    r"Data/Valmis_data_08082019/Detailed_branches_and_nodes",
    r"Data/Valmis_data_08082019/20m_branches_and_nodes",
    r"Data/Valmis_data_08082019/LiDAR_branches_and_nodes",
]
areadirs = [
    r"Data/Valmis_data_08082019/Detailed_areas",
    r"Data/Valmis_data_08082019/20m_areas",
    r"Data/Valmis_data_08082019/LiDAR_areas",
]

# Input codes
codes = ["KB", "KL", "Hastholmen", "Loviisa"]

# Assign cut-offs
cut_offs_branches = [[0.9, 0.9], [0.9, 0.9], [0.95], [0.95]]
cut_offs_traces = [[0.99, 0.95], [0.99, 0.97], [0.95], [0.97]]

# Assign sets
set_list = [(45, 90), (125, 170), (171, 15)]

analysis_main.analyze_data(analysis_name, branchdirs, tracedirs, nodedirs, areadirs, codes, cut_offs_branches,
                           cut_offs_traces, set_list)

# Assign length distributions for predictions
predict_with = [
    ["KB_20m", "KL_20m", "Hastholmen_LiDAR"],
    ["Hastholmen_LiDAR", "Loviisa_LiDAR"],
]

analysis_main.plot_data(analysis_name, predict_with)
