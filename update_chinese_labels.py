#!/usr/bin/env python3
"""
更新数据文件中的中文标签
"""

import json

def update_chinese_labels():
    """更新所有标签为中文"""
    
    # 读取现有数据
    with open('opensauce_2025_complete_agenda.json', 'r', encoding='utf-8') as f:
        agenda_data = json.load(f)
    
    # 更新基本信息
    agenda_data["description"] = "创客与创作者的盛会"
    agenda_data["event_dates"] = "2025年7月18-20日"
    agenda_data["location"] = "美国旧金山"
    
    # 更新每天的标题
    day_translations = {
        "friday": {
            "day_name": "周五",
            "date": "2025年7月18日",
            "theme": "产业日"
        },
        "saturday": {
            "day_name": "周六", 
            "date": "2025年7月19日",
            "theme": "创客日"
        },
        "sunday": {
            "day_name": "周日",
            "date": "2025年7月20日", 
            "theme": "创作者日"
        }
    }
    
    # 更新每一天的数据
    for day_key, day_data in agenda_data["days"].items():
        if day_key in day_translations:
            day_data.update(day_translations[day_key])
    
    # 保存更新后的数据
    with open('opensauce_2025_complete_agenda.json', 'w', encoding='utf-8') as f:
        json.dump(agenda_data, f, ensure_ascii=False, indent=2)
    
    # 更新嵌入式数据文件
    update_embedded_data(agenda_data)
    
    print("✅ 已更新中文标签！")
    print("   - 基本信息已中文化")
    print("   - 日期标题已中文化")
    print("   - 主题标题已中文化")

def update_embedded_data(agenda_data):
    """更新data.js中的嵌入式数据"""
    
    # 生成新的JavaScript数据
    js_content = f"""// OpenSauce 2025 Schedule Data with Beijing Time Support
const scheduleDataEmbedded = {json.dumps(agenda_data, ensure_ascii=False, indent=2)};

// 时区转换函数（仅用于数据处理）
function convertToBeiJingTime(timeStr, dateStr) {{
    // 解析PDT时间
    const timeParts = timeStr.match(/(\\d{{1,2}}):(\\d{{2}})\\s*(AM|PM)/i);
    if (!timeParts) return {{ time: timeStr, date: dateStr, isNextDay: false }};
    
    let hours = parseInt(timeParts[1]);
    const minutes = parseInt(timeParts[2]);
    const ampm = timeParts[3].toUpperCase();
    
    // 转换为24小时制
    if (ampm === 'PM' && hours !== 12) hours += 12;
    if (ampm === 'AM' && hours === 12) hours = 0;
    
    // 解析日期
    const dateObj = new Date(dateStr);
    dateObj.setHours(hours, minutes, 0, 0);
    
    // 转换为北京时间（+15小时）
    const beijingTime = new Date(dateObj.getTime() + (15 * 60 * 60 * 1000));
    
    // 格式化时间
    const beijingHours = beijingTime.getHours();
    const beijingMinutes = beijingTime.getMinutes();
    const beijingAmPm = beijingHours >= 12 ? 'PM' : 'AM';
    const displayHours = beijingHours === 0 ? 12 : (beijingHours > 12 ? beijingHours - 12 : beijingHours);
    
    const timeString = `${{displayHours}}:${{beijingMinutes.toString().padStart(2, '0')}} ${{beijingAmPm}}`;
    const dateString = beijingTime.toLocaleDateString('en-US', {{ 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    }});
    
    const isNextDay = beijingTime.toDateString() !== dateObj.toDateString();
    
    return {{
        time: timeString,
        date: dateString,
        isNextDay: isNextDay
    }};
}}"""
    
    # 写入新的data.js文件
    with open('data.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    # 同时更新docs目录
    with open('docs/data.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    with open('docs/opensauce_2025_complete_agenda.json', 'w', encoding='utf-8') as f:
        json.dump(agenda_data, f, ensure_ascii=False, indent=2)
    
    print("✅ 已更新所有数据文件（包括docs目录）")

if __name__ == "__main__":
    update_chinese_labels()
