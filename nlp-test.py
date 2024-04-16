def extract_address_with_number(tagged_list):
    address_info = []
    current_address = ""
    current_number = ""

    for word, tag in tagged_list:
        if tag in ['ns', 'nz', 'n']:  # 地名、名词
            current_address += word
        elif tag == 'm':  # 数字（门牌号）
            current_number += word
        elif current_address:  # 如果当前地址不为空
            if current_number:
                current_address += current_number
                current_number = ""
            address_info.append(current_address)
            current_address = ""

    if current_address:  # 处理最后一个地址
        if current_number:
            current_address += current_number
        address_info.append(current_address)

    return address_info

# 给定的标记列表
