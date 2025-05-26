import pandas as pd

def normalize_item_name(item_name):
    """
    标准化Item Name，用于更好的匹配
    """
    if pd.isna(item_name) or item_name == '':
        return ''
    
    # 转换为字符串并转为大写
    normalized = str(item_name).upper()
    
    # 移除常见的特殊字符和空格
    normalized = normalized.replace(' ', '').replace('-', '').replace('_', '')
    normalized = normalized.replace(',', '.').replace(';', '.')
    
    # 移除常见的后缀
    suffixes_to_remove = ['PARTNO', 'PART', 'NO', 'NUM', 'NUMBER']
    for suffix in suffixes_to_remove:
        if normalized.endswith(suffix):
            normalized = normalized[:-len(suffix)]
    
    return normalized.strip()

def find_best_match(item_name, duty_rates_dict):
    """
    为给定的item_name在duty_rates字典中找到最佳匹配
    """
    if not item_name or pd.isna(item_name):
        return None
    
    normalized_item = normalize_item_name(item_name)
    
    # 首先尝试精确匹配
    if item_name in duty_rates_dict:
        return item_name
    
    # 尝试标准化后的精确匹配
    for duty_item in duty_rates_dict.keys():
        if normalize_item_name(duty_item) == normalized_item:
            return duty_item
    
    # 尝试部分匹配（包含关系）- 改进版本
    best_match = None
    best_score = 0
    
    for duty_item in duty_rates_dict.keys():
        normalized_duty = normalize_item_name(duty_item)
        
        # 计算匹配分数
        score = 0
        
        # 完全包含关系
        if normalized_item in normalized_duty:
            score = len(normalized_item) / len(normalized_duty)
        elif normalized_duty in normalized_item:
            score = len(normalized_duty) / len(normalized_item)
        else:
            # 计算公共子串长度
            common_length = 0
            min_len = min(len(normalized_item), len(normalized_duty))
            for i in range(min_len):
                if normalized_item[i] == normalized_duty[i]:
                    common_length += 1
                else:
                    break
            
            # 如果有足够长的公共前缀，也认为是匹配
            if common_length >= 8:  # 至少8个字符的公共前缀
                score = common_length / max(len(normalized_item), len(normalized_duty))
        
        # 更新最佳匹配
        if score > best_score and score >= 0.7:  # 至少70%的匹配度
            best_score = score
            best_match = duty_item
    
    return best_match

def test_item_matching():
    """测试Item Name匹配功能的改进"""
    
    print("🔍 测试Item Name匹配功能")
    print("=" * 50)
    
    # 模拟税率文件中的Item Name
    duty_rates = {
        'RESISTOR0603.32K1110F0402': {'hsn': '85423900', 'bcd': 10, 'sws': 10, 'igst': 18},
        'CAPACITOR 1206 10UF 25V': {'hsn': '85321000', 'bcd': 7.5, 'sws': 10, 'igst': 18},
        'IC MICROCONTROLLER ARM': {'hsn': '85423100', 'bcd': 0, 'sws': 10, 'igst': 18},
        'CONNECTOR USB TYPE-C': {'hsn': '85366990', 'bcd': 10, 'sws': 10, 'igst': 18},
        'LED 0805 RED': {'hsn': '85414020', 'bcd': 10, 'sws': 10, 'igst': 18}
    }
    
    # 模拟发票中可能出现的Item Name变体
    test_cases = [
        # 精确匹配
        ('RESISTOR0603.32K1110F0402', 'RESISTOR0603.32K1110F0402'),
        
        # 大小写差异
        ('resistor0603.32k1110f0402', 'RESISTOR0603.32K1110F0402'),
        ('Resistor0603.32K1110F0402', 'RESISTOR0603.32K1110F0402'),
        
        # 空格差异
        ('RESISTOR 0603.32K1110F0402', 'RESISTOR0603.32K1110F0402'),
        ('CAPACITOR1206 10UF 25V', 'CAPACITOR 1206 10UF 25V'),
        
        # 特殊字符差异
        ('RESISTOR0603,32K1110F0402', 'RESISTOR0603.32K1110F0402'),
        ('RESISTOR0603;32K1110F0402', 'RESISTOR0603.32K1110F0402'),
        
        # 带有额外后缀的情况
        ('RESISTOR0603.32K1110F0402-PART NO 123', 'RESISTOR0603.32K1110F0402'),
        ('CAPACITOR 1206 10UF 25V PART', 'CAPACITOR 1206 10UF 25V'),
        
        # 部分匹配
        ('IC MICROCONTROLLER', 'IC MICROCONTROLLER ARM'),
        ('CONNECTOR USB', 'CONNECTOR USB TYPE-C'),
        
        # 无匹配的情况
        ('UNKNOWN COMPONENT XYZ', None),
        ('COMPLETELY DIFFERENT ITEM', None),
    ]
    
    print("测试用例:")
    print("-" * 50)
    
    success_count = 0
    total_count = len(test_cases)
    
    for i, (input_item, expected_match) in enumerate(test_cases, 1):
        print(f"\n{i:2d}. 输入: '{input_item}'")
        print(f"    标准化: '{normalize_item_name(input_item)}'")
        
        actual_match = find_best_match(input_item, duty_rates)
        
        if actual_match == expected_match:
            print(f"    ✅ 匹配结果: '{actual_match}' (符合预期)")
            success_count += 1
        else:
            print(f"    ❌ 匹配结果: '{actual_match}' (预期: '{expected_match}')")
        
        if actual_match:
            rates = duty_rates[actual_match]
            print(f"    📊 税率信息: HSN={rates['hsn']}, BCD={rates['bcd']}%, SWS={rates['sws']}%, IGST={rates['igst']}%")
    
    print("\n" + "=" * 50)
    print(f"测试结果: {success_count}/{total_count} 通过 ({success_count/total_count*100:.1f}%)")
    
    if success_count == total_count:
        print("🎉 所有测试用例都通过了！")
    else:
        print("⚠️  部分测试用例失败，需要进一步优化匹配算法")
    
    # 测试标准化函数
    print("\n" + "=" * 50)
    print("🔧 测试标准化函数")
    print("-" * 50)
    
    normalization_tests = [
        ('RESISTOR0603.32K1110F0402', 'RESISTOR0603.32K1110F0402'),
        ('resistor 0603.32k1110f0402', 'RESISTOR0603.32K1110F0402'),
        ('RESISTOR-0603,32K1110F0402', 'RESISTOR0603.32K1110F0402'),
        ('CAPACITOR 1206 10UF 25V PART NO', 'CAPACITOR120610UF25V'),
        ('IC_MICROCONTROLLER-ARM', 'ICMICROCONTROLLERARM'),
    ]
    
    for input_str, expected in normalization_tests:
        result = normalize_item_name(input_str)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{input_str}' -> '{result}' (预期: '{expected}')")

def test_edge_cases():
    """测试边界情况"""
    print("\n" + "=" * 50)
    print("🧪 测试边界情况")
    print("-" * 50)
    
    duty_rates = {'TEST ITEM': {'hsn': '12345', 'bcd': 5, 'sws': 5, 'igst': 18}}
    
    edge_cases = [
        (None, None),
        ('', None),
        ('   ', None),
        (pd.NA, None),
        (123, None),  # 数字类型
    ]
    
    for input_val, expected in edge_cases:
        try:
            result = find_best_match(input_val, duty_rates)
            status = "✅" if result == expected else "❌"
            print(f"{status} 输入: {repr(input_val)} -> 结果: {repr(result)}")
        except Exception as e:
            print(f"❌ 输入: {repr(input_val)} -> 错误: {str(e)}")

def demonstrate_bug_fix():
    """演示bug修复效果"""
    print("\n" + "=" * 50)
    print("🐛 演示Bug修复效果")
    print("-" * 50)
    
    # 模拟您图片中提到的情况
    duty_rates = {
        'RESISTOR0603.32K1110F0402': {'hsn': '85423900', 'bcd': 10, 'sws': 10, 'igst': 18},
        'SOCKET180W4COLUMNS1.25MMBILATERALCARDHOLEALLINCLUSIVE': {'hsn': '85366990', 'bcd': 10, 'sws': 10, 'igst': 18}
    }
    
    # 这些是可能在发票中出现但被错误识别为"new item"的情况
    problematic_cases = [
        'resistor0603.32k1110f0402',  # 大小写问题
        'RESISTOR 0603.32K1110F0402',  # 空格问题
        'RESISTOR0603,32K1110F0402',   # 特殊字符问题
        'SOCKET180W4COLUMNS1.25MMBILATERALCARDHOLEALLINCLUSIVE',  # 完全匹配
        'socket180w4columns1.25mmbilateralcardholeallinclusive',  # 大小写问题
        'SOCKET 180W4COLUMNS 1.25MM BILATERAL CARDHOLEALL INCLUSIVE',  # 空格问题
    ]
    
    print("修复前可能被错误标记为'new item'的情况:")
    print("-" * 30)
    
    for case in problematic_cases:
        match = find_best_match(case, duty_rates)
        if match:
            print(f"✅ '{case}' -> 匹配到: '{match}'")
        else:
            print(f"❌ '{case}' -> 未找到匹配 (会被标记为new item)")

if __name__ == "__main__":
    test_item_matching()
    test_edge_cases()
    demonstrate_bug_fix()
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("💡 建议：在实际使用中，可以通过日志查看匹配情况，")
    print("   并根据实际数据进一步优化匹配算法。") 