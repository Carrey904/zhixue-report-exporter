import json

m_stu_list = list() # Modified Student List
with open(r"C:\Users\14116\Desktop\pythonPro\student_stat\output.json") as f:
    stu_list = json.load(f)
for msg in stu_list:
    if msg['Grade'] == '高一':
        t_dict = dict()
        t_dict['班级'] = msg['Grade'] + msg['Class']
        t_dict['姓名'] = msg['Name']
        t_dict['身份证号'] = msg['id']
        m_stu_list.append(t_dict)
with open(r"C:\Users\14116\Desktop\pythonPro\iLearning\students_info.json", 'w') as f:
    json.dump(m_stu_list, f, ensure_ascii=False)
