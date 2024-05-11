# -*- coding: utf-8 -*-
import logging
import re
from phone import Phone
from itertools import groupby
import phonenumbers
from pyhanlp import *
from web.mask.zeelNLP.config.basic.time_nlp.TimeNormalizer import *

__all__ = ['extract_email', 'replace_chinese', 'extract_cellphone', 'extract_cellphone', 'extract_cellphone_location',
           'get_location', 'extract_locations', 'replace_cellphoneNum', 'extract_time', 'extract_name', 'most_common']


class Extractor(object):
    def __init__(self, text):
        self.text = text
        self.seg_list = [(str(t.word), str(t.nature)) for t in HanLP.segment(text)]

    def extract_email(self, text):
        """
        extract all email addresses from texts<string>
        eg: extract_email('我的email是ifee@baidu.com和dsdsd@dsdsd.com,李林的邮箱是eewewe@gmail.com哈哈哈')


        :param: raw_text
        :return: email_addresses_list<list>
        """
        if not text:
            return []
        eng_texts = self.replace_chinese(text)
        eng_texts = eng_texts.replace(' at ', '@').replace(' dot ', '.')
        sep = ',!?:; ，。！？《》、|\\/'
        eng_split_texts = [''.join(g) for k, g in groupby(eng_texts, sep.__contains__) if not k]

        email_pattern = r'^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z_-]+)+$'

        emails = []
        for eng_text in eng_split_texts:
            result = re.match(email_pattern, eng_text, flags=0)
            if result:
                emails.append(result.string)
        return emails

    def extract_ids(self, text):
        """
        extract all ids from texts<string>
        eg: extract_ids('my ids is 150404198812011101 m and dsdsd@dsdsd.com,李林的邮箱是eewewe@gmail.com哈哈哈')


        :param: raw_text
        :return: ids_list<list>

        if text == '':
            return []
        eng_texts = self.replace_chinese(text)
        sep = ',!?:; ：，.。！？《》、|\\/abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        eng_split_texts = [''.join(g) for k, g in groupby(eng_texts, sep.__contains__) if not k]
        eng_split_texts_clean = [ele for ele in eng_split_texts if len(ele) == 18]



        phones = []
        for eng_text in eng_split_texts_clean:
            result = re.match(id_pattern, eng_text, flags=0)
            if result:
                phones.append(result.string.replace('+86', '').replace('-', ''))
        return phones
        """
        if text == '':
            return []
        id_pattern = r'^[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$'
        eng_texts = self.replace_chinese(text)
        sep = ',!?:; ：，.。！？《》、|\\/abcdefghijklmnopqrstuvwyzABCDEFGHIJKLMNOPQRSTUVWYZ'
        # if isinstance(eng_texts, )
        eng_split_texts = [''.join(g) for k, g in groupby(eng_texts, sep.__contains__) if not k or not g]
        eng_split_texts_clean = [ele for ele in eng_split_texts if len(ele) == 18]
        id_list = []
        pattern = re.compile(id_pattern)
        for eng_text in eng_split_texts_clean:
            result = re.match(pattern, eng_text, flags=0)
            if result:
                # if "x" or "X" in result and result.string.endswith("X"):
                id_list.append(result.string)
        return id_list

    def replace_chinese(self, text):
        """
        remove all the chinese characters in text
        eg: replace_chinese('我的email是ifee@baidu.com和dsdsd@dsdsd.com,李林的邮箱是eewewe@gmail.com哈哈哈')


        :param: raw_text
        :return: text_without_chinese<str>
        """
        if text == '':
            return []
        filtrate = re.compile(u'[\u4E00-\u9FA5]')
        text_without_chinese = filtrate.sub(r' ', text)
        return text_without_chinese.strip()

    def extract_cellphone(self, text):
        """
        extract all cell phone numbers from texts<string>
        eg: extract_email('my email address is sldisd@baidu.com and dsdsd@dsdsd.com,李林的邮箱是eewewe@gmail.com哈哈哈')


        :param: raw_text
        :return: email_addresses_list<list>
        """
        phone_pattern = r'\b1[3-9]\d{9}\b'  # 匹配11位数字，以1开头的手机号码
        phone_pattern = r'\b1[3-9]\d{9}'  # 匹配11位数字，以1开头的手机号码

        # 使用正则表达式找到所有匹配的手机号码
        phone_numbers = re.findall(phone_pattern, text)

        # 过滤掉类似 UUID 的字符串
        filtered_phone_numbers = [phone for phone in phone_numbers if len(phone) == 11]

        return filtered_phone_numbers

    def extract_register_numbers(self, text):
        """
            匹配登记号登记号000580649病历号为1785150
        :param text:
        :return:
        """
        registration_number = re.search(r'登记号：(\d+)', text)
        if registration_number:
            return [registration_number.group(1)]
        else:
            return []

    def extract_medical_numbers(self, text):
        """
            匹配登记号登记号000580649病历号为1785150
        :param text:
        :return:
        """
        medical_number = re.search(r'病历号：(\d+)', text) or re.search(r'病案号：(\d+)', text)
        if medical_number:
            return [medical_number.group(1)]
        else:
            return []

    def extract_cellphone_location(self, phoneNum, nation='CHN'):
        """
        extract cellphone number locations according to the given number
        eg: extract_cellphone_location('181000765143',nation=CHN)


        :param: phoneNum<string>, nation<string>
        :return: location<dict>{'phone': '18100065143', 'province': '上海', 'city': '上海', 'zip_code': '200000', 'area_code': '021', 'phone_type': '电信'}

        """
        if nation == 'CHN':
            p = Phone()
            loc_dict = p.find(phoneNum)
        if nation != 'CHN':
            x = phonenumbers.parse(phoneNum, 'GB')
            if phonenumbers.is_possible_number(x):
                loc_dict = x
        # logging.info(loc_dict)
        return loc_dict

    def get_location(self, word_pos_list):
        """

        :param word_pos_list:
        :return:
        """
        addresses = []
        current_address = []
        if word_pos_list == []:
            return []

        for i in range(len(word_pos_list)):
            word, pos = word_pos_list[i]

            if pos == 'ns':  # 地名
                current_address.append(word)

                # 考虑地名的上下文，例如'ns'后面接着的是'q'（量词）或'n'（名词）
                next_word, next_pos = word_pos_list[i + 1] if i + 1 < len(word_pos_list) else (None, None)
                if next_pos in ['q', 'n', 'w', 'vg', 'ns']:
                    current_address.append(next_word)

                # 查找可能的数字信息"nz'), ('嘉', 'b'), ('苑', 'ng"
                j = i + 1
                # while j < len(word_pos_list) and word_pos_list[j][1] in {'m', 'q', 'n', 'nz', 'b', 'ng', 'a', 'v'}:  # 数字或量词
                while j < len(word_pos_list) and word_pos_list[j][1] in {'m', 'q', 'n', 'nz', 'b', 'ng'}:  # 数字或量词
                    current_address.append(word_pos_list[j][0])
                    j += 1

            elif current_address:
                addresses.append(''.join(current_address))
                current_address = []

        # 处理结尾的情况
        if current_address:
            addresses.append(''.join(current_address))

        return addresses

    def chinese_part(self, text):
        seg_list = []
        batch_size = 100  # 每批处理的数据量
        for t in HanLP.segment(text):
            seg_list.append((str(t.word), str(t.nature)))
            if len(seg_list) == batch_size:
                yield seg_list
                seg_list = []
            if seg_list:
                yield seg_list

    def extract_locations(self, text):
        """
        extract locations by from texts
        eg: extract_locations('我家住在陕西省安康市汉滨区。')


        :param: raw_text<string>
        :return: location_list<list> eg: ['陕西省安康市汉滨区', '安康市汉滨区', '汉滨区']

        """
        if text == '':
            return []
        seg_list = self.seg_list
        # location_list = []
        # for seg in self.chinese_part(text):
        #     location_list.extend(self.get_location(seg))
        print(seg_list)
        location_list = self.get_location(seg_list)

        # 过滤无具体门牌号的地址信息
        location_list = [location for location in location_list if self.has_numbers(location)]
        return location_list

    def replace_cellphoneNum(self, text):
        """
        remove cellphone number from texts. If text contains cellphone No., the extract_time will report errors.
        hence, we remove it here.
        eg: extract_locations('我家住在陕西省安康市汉滨区，我的手机号是181-0006-5143。')


        :param: raw_text<string>
        :return: text_without_cellphone<string> eg: '我家住在陕西省安康市汉滨区，我的手机号是。'

        """
        eng_texts = self.replace_chinese(text)
        sep = ',!?:; ：，.。！？《》、|\\/abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        eng_split_texts = [''.join(g) for k, g in groupby(eng_texts, sep.__contains__) if not k]
        eng_split_texts_clean = [ele for ele in eng_split_texts if len(ele) == 11]
        for phone_num in eng_split_texts_clean:
            text = text.replace(phone_num, '')
        return text

    def replace_ids(self, text):
        """
        remove cellphone number from texts. If text contains cellphone No., the extract_time will report errors.
        hence, we remove it here.
        eg: extract_locations('我家住在陕西省安康市汉滨区，我的身份证号是150404198412011312。')


        :param: raw_text<string>
        :return: text_without_ids<string> eg: '我家住在陕西省安康市汉滨区，我的身份证号号是。'

        """
        if text == '':
            return []
        eng_texts = self.replace_chinese(text)
        sep = ',!?:; ：，.。！？《》、|\\/abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        eng_split_texts = [''.join(g) for k, g in groupby(eng_texts, sep.__contains__) if not k]
        eng_split_texts_clean = [ele for ele in eng_split_texts if len(ele) == 18]

        id_pattern = r'^[1-9][0-7]\d{4}((19\d{2}(0[13-9]|1[012])(0[1-9]|[12]\d|30))|(19\d{2}(0[13578]|1[02])31)|(19\d{2}02(0[1-9]|1\d|2[0-8]))|(19([13579][26]|[2468][048]|0[48])0229))\d{3}(\d|X|x)?$'
        ids = []
        for eng_text in eng_split_texts_clean:
            result = re.match(id_pattern, eng_text, flags=0)
            if result:
                ids.append(result.string)

        for phone_num in ids:
            text = text.replace(phone_num, '')
        return text

    def extract_time(self, text):
        """
        extract timestamp from texts
        eg: extract_time('我于2018年1月1日获得1000万美金奖励。')


        :param: raw_text<string>
        :return: time_info<time_dict> eg: {"type": "timestamp", "timestamp": "2018-11-27 11:00:00"}

        """
        if text == '':
            return []
        tmp_text = self.replace_cellphoneNum(text)
        tmp_text = self.replace_ids(tmp_text)
        tn = TimeNormalizer()
        res = tn.parse(target=tmp_text)  # target为待分析语句，timeBase为基准时间默认是当前时间
        return res

    def extract_name(self, text):
        """
        extract chinese names from texts
        eg: extract_time('急寻王龙，短发，王龙，男，丢失发型短发，...如有线索，请迅速与警方联系：19909156745')


        :param: raw_text<string>
        :return: name_list<list> eg: ['王龙', '王龙']

        """
        from web.mask.zeelNLP.constant import medical_name_set, chinese_surnames
        if text == '':
            return []
        seg_list = self.seg_list
        print(seg_list)
        names = set()

        for index, ele_tup in enumerate(seg_list):
            if 'nr' in ele_tup[1]:
                names.add(ele_tup[0])
            if 'nrf' in ele_tup[1]:
                names.add(ele_tup[0])
            if 'a' in ele_tup[1] and len(ele_tup[0]) >= 2:
                names.add((ele_tup[0]))
            if 'ag' in ele_tup[1]:
                next_word, next_pos = seg_list[index + 1] if index + 1 < len(seg_list) else (None, None)
                if next_pos == 'nz':
                    names.add(''.join([ele_tup[0], next_word]))
            if 'tg' in ele_tup[1]:
                next_word, next_pos = seg_list[index + 1] if index + 1 < len(seg_list) else (None, None)
                if next_pos == 'nz':
                    names.add(''.join([ele_tup[0], next_word]))
            if 'ng' in ele_tup[1]:
                next_word, next_pos = seg_list[index + 1] if index + 1 < len(seg_list) else (None, None)
                if next_pos == 'nz' or next_pos == 'vg' or next_pos == 'ns' or next_pos == 'b':
                    names.add(''.join([ele_tup[0], next_word]))
            if 'n' in ele_tup[1]:
                next_word, next_pos = seg_list[index + 1] if index + 1 < len(seg_list) else (None, None)
                if next_pos == 'nz' or next_pos == 'n' or next_pos == 'vg':
                    names.add(''.join([ele_tup[0], next_word]))
            if 'q' in ele_tup[1]:
                next_word, next_pos = seg_list[index + 1] if index + 1 < len(seg_list) else (None, None)
                if next_pos == 'ag':
                    names.add(''.join([ele_tup[0], next_word]))
            if 'd' in ele_tup[1]:
                next_word, next_pos = seg_list[index + 1] if index + 1 < len(seg_list) else (None, None)
                if next_pos == 'x' or next_pos == 'nz':
                    names.add(''.join([ele_tup[0], next_word]))
            if 'vg' in ele_tup[1]:
                next_word, next_pos = seg_list[index + 1] if index + 1 < len(seg_list) else (None, None)
                if next_pos == 'n':
                    names.add(''.join([ele_tup[0], next_word]))
        nnt = self.find_words_between_nnt_and_nz(seg_list)
        if nnt:
            names = names.union(nnt)
        # 构建正则表达式
        pattern = re.compile('|'.join(chinese_surnames))
        results = [r for r in names if
                   re.match(pattern=pattern, string=str(r)) and 1 < len(r) <= 3 and r not in medical_name_set]
        return results

    def most_common(self, content_list):
        """
        return the most common element in a list
        eg: extract_time(['王龙'，'王龙'，'李二狗'])


        :param: content_list<list>
        :return: name<string> eg: '王龙'
        """
        if content_list == []:
            return None
        if len(content_list) == 0:
            return None
        return max(set(content_list), key=content_list.count)

    @staticmethod
    def find_words_between_nnt_and_nz(seg_list):
        nnt_index = [i for i, (word, pos) in enumerate(seg_list) if pos == 'nnt']
        nz_index = [i for i, (word, pos) in enumerate(seg_list) if pos == 'nz']

        result = set()
        if nnt_index and nz_index:
            for nnt_pos in nnt_index:
                nearest_nz = min(nz_index, key=lambda x: abs(x - nnt_pos))
                start = min(nnt_pos, nearest_nz)
                end = max(nnt_pos, nearest_nz)
                words_between = [word for word, pos in seg_list[start + 1:end] if pos != 'w']
                result.add(''.join(words_between))

        return result

    @staticmethod
    def has_numbers(input_string):
        return bool(re.search(r'\d', input_string))


if __name__ == '__main__':

    text = '诊断:1.肺恶性肿瘤IV期PS评分:1分。2,肺继发恶性肿瘤3.颈部淋巴结继发恶性肿瘤4.,肺门淋巴结继发恶性肿瘤5,纵隔淋巴结继发恶性肿瘤6,腔隙性脑梗死医师签名:宗丙丙'
    ex = Extractor(text=text)
    res = ex.extract_name(text=text)
    print(res)