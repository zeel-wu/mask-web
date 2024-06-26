# # -*- coding:utf-8 -*-

from pyhanlp import *
CRFnewSegment = HanLP.newSegment("crf")


# 中文人名识别
def demo_chinese_name_recognition(sentences):
    segment = HanLP.newSegment().enableNameRecognize(True);
    for sentence in sentences:
        term_list = segment.seg(sentence)
        print(term_list)
        print([i.word for i in term_list])


sentences = [
    "签约仪式前，秦光荣、李纪恒、仇和等一同会见了参加签约的企业家。",
    "武大靖创世界纪录夺冠，中国代表团平昌首金",
    "区长庄木弟新年致辞",
    "朱立伦：两岸都希望共创双赢 习朱历史会晤在即",
    "陕西首富吴一坚被带走 与令计划妻子有交集",
    "据美国之音电台网站4月28日报道，8岁的凯瑟琳·克罗尔（凤甫娟）和很多华裔美国小朋友一样，小小年纪就开始学小提琴了。她的妈妈是位虎妈么？",
    "凯瑟琳和露西（庐瑞媛），跟她们的哥哥们有一些不同。",
    "王国强、高峰、汪洋、张朝阳光着头、韩寒、小四",
    "张浩和胡健康复员回家了",
    "王总和小丽结婚了",
    "编剧邵钧林和稽道青说",
    "这里有关天培的有关事迹",
    "龚学平等领导说,邓颖超生前杜绝超生",]
demo_chinese_name_recognition(sentences)

print("\n========== 中文人名 基本默认已开启 ==========\n")
print(CRFnewSegment.seg(sentences[0]))
# 中文人名识别
def demo_chinese_name_recognition(sentences):
    segment = HanLP.newSegment().enableNameRecognize(True);
    for sentence in sentences:
        term_list = segment.seg(sentence)
        print(term_list)
        print([i.word for i in term_list])


sentences = [
    "签约仪式前，秦光荣、李纪恒、仇和等一同会见了参加签约的企业家。",
    "武大靖创世界纪录夺冠，中国代表团平昌首金",
    "区长庄木弟新年致辞",
    "朱立伦：两岸都希望共创双赢 习朱历史会晤在即",
    "陕西首富吴一坚被带走 与令计划妻子有交集",
    "据美国之音电台网站4月28日报道，8岁的凯瑟琳·克罗尔（凤甫娟）和很多华裔美国小朋友一样，小小年纪就开始学小提琴了。她的妈妈是位虎妈么？",
    "凯瑟琳和露西（庐瑞媛），跟她们的哥哥们有一些不同。",
    "王国强、高峰、汪洋、张朝阳光着头、韩寒、小四",
    "张浩和胡健康复员回家了",
    "王总和小丽结婚了",
    "编剧邵钧林和稽道青说",
    "这里有关天培的有关事迹",
    "龚学平等领导说,邓颖超生前杜绝超生",]
demo_chinese_name_recognition(sentences)

print("\n========== 中文人名 基本默认已开启 ==========\n")
print(CRFnewSegment.seg(sentences[0]))