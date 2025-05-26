import pandas as pd
import sys
import os

# 添加当前目录到Python路径
sys.path.append('.')

# 导入修复后的函数
from streamlit_app import normalize_item_name, find_best_match

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

if __name__ == "__main__":
    test_item_matching()
    test_edge_cases()
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("💡 建议：在实际使用中，可以通过日志查看匹配情况，")
    print("   并根据实际数据进一步优化匹配算法。") 