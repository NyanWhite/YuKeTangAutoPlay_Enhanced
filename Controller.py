'''
Author: LetMeFly
Date: 2024-07-23 16:31:29
LastEditors: LetMeFly
LastEditTime: 2024-07-24 12:42:46
'''
import os

watchList = [
    'https://acgecfd.yuketang.cn/pro/lms/undefined/44371/studycontent',
    'https://acgecfd.yuketang.cn/pro/lms/undefined/44333/studycontent',
    'https://acgecfd.yuketang.cn/pro/lms/undefined/44370/studycontent',
    'https://acgecfd.yuketang.cn/pro/lms/undefined/44372/studycontent',
    'https://acgecfd.yuketang.cn/pro/lms/undefined/44362/studycontent',
    'https://acgecfd.yuketang.cn/pro/lms/undefined/44366/studycontent',
    'https://acgecfd.yuketang.cn/pro/lms/undefined/44360/studycontent',
    'https://acgecfd.yuketang.cn/pro/lms/undefined/44353/studycontent',
    'https://acgecfd.yuketang.cn/pro/lms/undefined/44359/studycontent',
    'https://acgecfd.yuketang.cn/pro/lms/undefined/44321/studycontent',
    'https://acgecfd.yuketang.cn/pro/lms/undefined/44350/studycontent',
    'https://acgecfd.yuketang.cn/pro/lms/undefined/44320/studycontent',
    'https://acgecfd.yuketang.cn/pro/lms/undefined/44355/studycontent',
    'https://acgecfd.yuketang.cn/pro/lms/undefined/44354/studycontent',
    'https://acgecfd.yuketang.cn/pro/lms/undefined/44349/studycontent',
    'https://acgecfd.yuketang.cn/pro/lms/undefined/44345/studycontent',
    'https://acgecfd.yuketang.cn/pro/lms/undefined/44347/studycontent',
    'https://acgecfd.yuketang.cn/pro/lms/undefined/44339/studycontent',
    'https://acgecfd.yuketang.cn/pro/lms/undefined/44313/studycontent',
    'https://acgecfd.yuketang.cn/pro/lms/undefined/44344/studycontent',
    'https://acgecfd.yuketang.cn/pro/lms/undefined/44329/studycontent',
    'https://acgecfd.yuketang.cn/pro/lms/undefined/44328/studycontent',
    'https://acgecfd.yuketang.cn/pro/lms/undefined/44327/studycontent',
    'https://acgecfd.yuketang.cn/pro/lms/undefined/44310/studycontent',
    'https://acgecfd.yuketang.cn/pro/lms/undefined/44318/studycontent',
    'https://acgecfd.yuketang.cn/pro/lms/undefined/44330/studycontent',
    'https://acgecfd.yuketang.cn/pro/lms/undefined/44323/studycontent',
    'https://acgecfd.yuketang.cn/pro/lms/undefined/44315/studycontent',
    'https://acgecfd.yuketang.cn/pro/lms/undefined/44307/studycontent',
    'https://acgecfd.yuketang.cn/pro/lms/undefined/44370/studyconten',

]

for thisUrl in watchList:
    os.system(f'python yuketang.py "{thisUrl}"')
