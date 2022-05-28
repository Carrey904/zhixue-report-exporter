from json.decoder import JSONDecodeError
from time import time, sleep
import requests
import sys
import json
import csv

# 准备工作
SCORE_URL = 'https://www.zhixue.com/api-teacher/api/studentScore/getAllSubjectStudentRank'  # 查询成绩的api
EXAMINFO_URL = 'https://www.zhixue.com/api-teacher/api/examInfo'  # 查询具体考试信息的api
EXAMLIST_URL = 'https://www.zhixue.com/api-teacher/api/reportlist'  # 查询最近考试的api
CURRENT_PATH = sys.path[0] + '/'
cookie_parser = lambda c: {msg.split('=')[0].strip(): msg.split('=')[1].strip() for msg in c.split(";")}  # cookie 解析
with open(CURRENT_PATH + 'cookies.txt') as f:
    cookies_raw = f.read()  # 载入 cookies
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://www.zhixue.com/htm-freshreport/',
    'Cookie': cookies_raw}  # 请求头
ms_timestamp = lambda: str(int(time() * 1000))  # 获取毫秒时间戳
s_query_gen = lambda id, i: {'examId': id, 'classId': '', 'lastExamId': '', 'searchValue': '',
                             'direction': '', 'order': '', 'pageIndexInt': str(i), 'electiveTypeCode': '',
                             'version': 'V3', 't': ms_timestamp()}  # 查询字符串生成器(score)
ei_query_gen = lambda id: {'examId': id, 't': ms_timestamp()}  # 查询字符串生成器(exam_info)
el_query_gen = lambda i: {'queryType': 'academicYear', 'termId': '1500000100073166789',
                          'teachingCycleId': '1500000100073166791', 'beginTime': '1628956800000',
                          'endTime': ms_timestamp(), 'pageIndex': i, 't': ms_timestamp()}  # 查询字符串生成器(exam_list)


class Examination:
    def __init__(self, exam_info):
        exam_info = exam_info['data']
        self.id = exam_info['examId']
        self.name = exam_info['examName']
        self.grade_name = exam_info['gradeName']
        self.create_time = exam_info['createDateTime']
        self.subject_names = [msg['name'] for msg in exam_info['subjectCodeList']]

    def __str__(self):
        return f"[{self.grade_name}]{self.name}_{self.id}".replace(' ', '')

    def check_score(self):
        def res_rank_opt(student):
            score_info = student['scoreInfos']
            student_dict = dict()
            student_dict['班级'] = student['className']
            student_dict['学号'] = student['userNum']
            student_dict['姓名'] = student['userName']
            for i in range(len(score_info)):
                student_dict[self.subject_names[i]] = score_info[i]['score']
                student_dict[f"{self.subject_names[i]}班级排名"] = score_info[i]['classRank']
                student_dict[f"{self.subject_names[i]}年级排名"] = score_info[i]['schoolRank']
            return student_dict

        print(f"[INFO] 正在查询{str(self)}。")
        students_score = list()  # 新建成绩空列表
        page_count = 1
        res = json.loads(requests.get(SCORE_URL, params=s_query_gen(self.id, page_count), headers=headers).text)
        for student in res['result']['studentRank']:
            students_score.append(res_rank_opt(student))
        last_page = res['result']['paperInfo']['lastPage']  # 获取总页数
        print(f"[INFO] 第{page_count}页加载完成，共{last_page}页。")
        while page_count < last_page:
            sleep(0.5)  # 延时防止封禁IP
            page_count += 1
            res = json.loads(requests.get(SCORE_URL, params=s_query_gen(self.id, page_count), headers=headers).text)
            for student in res['result']['studentRank']:
                students_score.append(res_rank_opt(student))
            print(f"[INFO] 第{page_count}页加载完成，共{last_page}页。")
        return students_score


def check_examlist(page):
    res = json.loads(requests.get(EXAMLIST_URL, params=el_query_gen(page), headers=headers).text)
    exams = [Examination(msg) for msg in res['result']['reportList']]
    print(f"[INFO] 以下为第 {page} 页考试。")
    [print(f"     {i} - {str(exams[i])}") for i in range(len(exams))]
    return exams

def merge_scores(*scores):
    warned_subjects = ['班级', '学号', '姓名']
    student_scores_dict = dict()
    for msg in scores:
        for student in msg:
            if student['学号'] not in student_scores_dict.keys():
                student_scores_dict[student['学号']] = student
            else:
                for subject in student.keys():
                    if subject not in student_scores_dict[student['学号']].keys():
                        student_scores_dict[student['学号']][subject] = student[subject] # 合并成绩
                    else:
                        if subject not in warned_subjects:
                            print(f"[WARN] {subject}成绩重复！")
    return list(student_scores_dict.values())



# 准备工作结束

try:
    res = json.loads(requests.get(EXAMLIST_URL, params=el_query_gen(1), headers=headers).text)
except JSONDecodeError:
    print('[ERROR] Cookies 过期，请重新获取。')
    sys.exit()
exams = [Examination(msg) for msg in res['result']['reportList']]
e_last_page = res['result']['paperInfo']['lastPage']  # 考试列表页数
e_num = res['result']['paperInfo']['totalCount']  # 考试总数
print(f"[INFO] 查询到{e_last_page}页，共计{e_num}场考试。(时间范围:1615132800000-{ms_timestamp()})")
print(f"[INFO] 以下为第 1 页考试。")
[print(f"     {i} - {str(exams[i])}") for i in range(len(exams))]
print('[INFO] 新功能：不同考试成绩合并。用;隔开多个考试ID。')
user_input = input("[INPUT] 输入你要查询的考试(序号,多场考试用逗号隔开)或页码(例查询第二页则输入p2)\n     >>> ")
while user_input.find('p') == 0: # 判断是否为页码
    e_page = user_input[user_input.find('p') + 1:]
    try:
        if 0 <= int(e_page) <= e_last_page:
            exams = check_examlist(e_page)
        else:
            raise ValueError
    except ValueError:
        print(f"[ERROR] 输入值有误，请重试。")
    user_input = input("[INPUT] 输入你要查询的考试(序号,多场考试用逗号隔开)或页码(例查询第二页则输入p2)\n     >>> ")
exam_indexes = user_input.split(',')
for exam_index in exam_indexes:
    exam_sub_indexes = exam_index.split(';')
    exam_sub_indexes = [int(i) for i in exam_sub_indexes]
    exam_validation = all(0 <= i < len(exams) for i in exam_sub_indexes)
    exam_names = [str(exams[i]) for i in exam_sub_indexes]
    if exam_validation:
        if len(exam_sub_indexes) == 1:
            student_scores = exams[exam_sub_indexes[0]].check_score()
        else:
            student_scores = merge_scores(*[exams[i].check_score() for i in exam_sub_indexes])
    else:
        raise ValueError("输入值有误")
    print("[INFO] 正在导出 .csv 文件")
    if len(exam_names) == 1:
        output_filename = f"{CURRENT_PATH}{exam_names[0]}.csv"
    else:
        print("[INFO] 以下为备选文件名")
        [print(f"     {i} - {str(exam_names[i])}") for i in range(len(exam_names))]
        user_input = input(f"[INFO] 请选择导出文件名(序号)或自定义文件名(custom+名称)。")
        if user_input.find('custom') == 0:
            output_filename = f"{CURRENT_PATH}{user_input[user_input.find('custom') + 6:]}.csv"
        else:
            if 0 <= int(user_input) < len(exam_names):
                output_filename = f"{CURRENT_PATH}{exam_names[int(user_input)]}.csv"
            else:
                raise ValueError("输入值有误")
    with open(output_filename, 'w', encoding='utf-8') as f:
        cw = csv.DictWriter(f, fieldnames=list(student_scores[0].keys()))
        cw.writeheader()
        cw.writerows(student_scores)
    with open(output_filename, encoding='utf-8') as f:
        f_content = f.read().replace('\n\n', '\n')
    with open(output_filename, 'w') as f:
        f.write(f_content)
    print(f"[INFO] .csv 文件导出完毕: {output_filename}")



"""
legacy code

try:
    if user_input.find(';') == -1:
        exam_index = int(user_input)
        if 0 <= exam_index < len(exams):
            current_exam = exams[exam_index]
            student_scores = current_exam.check_score()
            print("[INFO] 正在导出 .csv 文件")
            output_filename = f"{CURRENT_PATH}{str(current_exam)}.csv"
            with open(output_filename, 'w', encoding='utf-8') as f:
                cw = csv.DictWriter(f, fieldnames=list(student_scores[0].keys()))
                cw.writeheader()
                cw.writerows(student_scores)
            with open(output_filename, encoding='utf-8') as f:
                f_content = f.read().replace('\n\n', '\n')
            with open(output_filename, 'w') as f:
                f.write(f_content)
            print(f"[INFO] .csv 文件导出完毕: {output_filename}")
        else:
            raise ValueError
    else:
        exam_indexes = user_input.split(';')
        exam_indexes = [int(i) for i in exam_indexes]
        if all(0 <= i < len(exams) for i in exam_indexes):
            student_scores = merge_scores(*[exams[i].check_score() for i in exam_indexes])
            print("[INFO] 正在导出 .csv 文件")
            output_filename = f"{CURRENT_PATH}all.csv"
            with open(output_filename, 'w', encoding='utf-8') as f:
                cw = csv.DictWriter(f, fieldnames=list(student_scores[0].keys()))
                cw.writeheader()
                cw.writerows(student_scores)
            with open(output_filename, encoding='utf-8') as f:
                f_content = f.read().replace('\n\n', '\n')
            with open(output_filename, 'w') as f:
                f.write(f_content)
            print(f"[INFO] .csv 文件导出完毕: {output_filename}")
        else:
            raise ValueError

except ValueError:
    print(f"[ERROR] 输入值有误。")
"""