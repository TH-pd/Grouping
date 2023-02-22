# -*- coding: utf-8 -*-
import glob
import re
import os
import itertools
import copy

class GROUPING():
    #   メンバー一覧の取得
    def __init__(self):
        self.grade_member = {}
        self.member = []
        self.log    = []
        self.cnt_member = 0
        self.ver = 0
        self.next_group = []
        self.next_error = None
        self.next_max   = None
        self.next_min   = [-1, 0]

    def set_member(self, text_path):
        group = None
        with open(text_path, 'r', encoding='UTF-8') as f:
            lines = [x.replace('\n', '') for x in f.readlines()]
            for line in lines:
                if line[0] == '・':
                    self.grade_member[line[1:]] = []
                    group = line[1:]
                else:
                    self.grade_member[group].append(line)
                    self.member.append(line)
                    self.cnt_member += 1
    
    #ログから過去の振り分けを入手、二次元配列に格納
    def set_log(self, log_dir):
        for _ in range(self.cnt_member):
            self.log.append([0]*self.cnt_member)
        log_files = [p for p in glob.glob(log_dir + os.sep + '*') if re.search('\d+\.txt', p)]
        self.ver  = len(log_files) + 1
        for fn in log_files:
            with open(fn, 'r', encoding = 'UTF-8') as f:
                lines = [x.replace('\n', '') for x in f.readlines()]
                lines.append('')
                group_member = []
                for line in lines:
                    if (len(line) == 0):
                        for i in group_member:
                            for j in group_member:
                                if (i != j):
                                    self.log[i][j] += 1
                        group_member = []
                            
                    elif (line not in self.member):
                        print(f'{line}はメンバーに登録されていません')

                    else:
                        group_member.append(self.member.index(line))

    def check_sum(self, group):
        l    = len(self.member)
        group2 = list(set(range(l)) - set(group))
        if (abs(len(group) - len(group2)) > 1):
            return
        _sum = 0
        cnt  = {}
        count = 0
        for i in range(l - 1):
            for j in range(i + 1, l):
                if ([k for k, v in self.grade_member.items() if self.member[i] in v] == [k for k, v in self.grade_member.items() if self.member[j] in v] and len([k for k, v in self.grade_member.items() if self.member[j] in v]) == 1 and len(self.grade_member[[k for k, v in self.grade_member.items() if self.member[j] in v][0]]) <= 2):
                    continue
                s = self.log[i][j] + (((i in group and j in group) or (i in group2 and j in group2)))
                if (s not in cnt.keys()):
                    cnt[s] = 1
                else:
                    cnt[s] += 1
                _sum += s
                count += 1

        avg   = _sum / count
        error = 0
        for i in cnt:
            if (i == 0):
                continue
            error += cnt[i] * ((avg - i) * (avg - i))
        _max, _min = max(cnt.keys()), min(cnt.keys())
        if self.next_max == None:
            self.next_error = error
            self.next_max = _max
            self.next_min = [_min, cnt[_min]]
            del(self.next_group)
            self.next_group = copy.deepcopy(group)
        elif (self.next_min[0] < _min or (self.next_min[0] == _min and self.next_min[1] > cnt[_min])):
            self.next_error = error
            self.next_max = _max
            self.next_min = [_min, cnt[_min]]
            del(self.next_group)
            self.next_group = copy.deepcopy(group)
        elif (self.next_min[0] == _min and self.next_min[1] == cnt[_min] and self.next_max > _max):
            self.next_error = error
            self.next_max = _max
            del(self.next_group)
            self.next_group = copy.deepcopy(group)
        elif (self.next_min[0] == _min and self.next_min[1] == cnt[_min] and self.next_max == _max and self.next_error > error):
            self.next_error = error
            del(self.next_group)
            self.next_group = copy.deepcopy(group)
        
    def _for(self, pattern, group):
        if (len(pattern) == 0):
            self.check_sum(group)
            del(pattern)
            del(group)
            return
        pat = pattern.pop(0)
        for p in pat:
            self._for(copy.deepcopy(pattern), group + list(p))
        del(group)
        del(pattern)

    def grouping(self):
        pattern = []
        for x in self.grade_member:
            l = list(itertools.combinations(self.grade_member[x], int(len(self.grade_member[x])/2)))
            if (len(self.grade_member[x]) % 2 == 1):
                l += list(itertools.combinations(self.grade_member[x], 1+int(len(self.grade_member[x])/2)))
            l = [[self.member.index(n) for n in y] for y in l]
            pattern.append(l)

        group = []
        self._for(pattern, group)
        print(self.next_min)

    def next_save(self, log_dir):
        array = copy.deepcopy(self.log)
        group2 = list(set(range(len(self.member))) - set(self.next_group))
        for i in self.next_group:
            for j in self.next_group:
                if (i != j):
                    array[i][j] += 1
        for i in group2:
            for j in group2:
                if (i != j):
                    array[i][j] += 1

        #   出力
        with open(log_dir + os.sep + str(self.ver) + '.txt', 'w', encoding = 'UTF-8') as f:
            for x in self.next_group:
                f.write(self.member[x] + '\n')
            f.write('\n')
            for x in group2:
                f.write(self.member[x] + '\n')

        #   配列をcsv形式で保存
        with open(log_dir + os.sep + str(self.ver) + '.csv', 'w') as f:
            f.write(','+','.join(self.member) + '\n')
            for m, x in zip(self.member, array):
                f.write(m + ',' + ','.join([str(i) for i in x]) + '\n')
        del(array)
        del(group2)

    #   2次元配列をcsv形式で出力
    def save_csv(self, log_dir):
        with open(log_dir + os.sep + str(self.ver-1) + '.csv', 'w') as f:
            f.write(','+','.join(self.member) + '\n')
            for m, x in zip(self.member, self.log):
                f.write(m + ',' + ','.join([str(i) for i in x]) + '\n')

if __name__ == '__main__':
    PATH = os.path.dirname(__file__)
    group = GROUPING()
    group.set_member(PATH + os.sep + 'Data' + os.sep + 'members.txt')
    group.set_log(PATH + os.sep + 'log')
    #group.save_csv(PATH + os.sep + 'log')
    group.grouping()
    group.next_save(PATH + os.sep + 'log')
