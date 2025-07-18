#!/usr/bin/env python3
"""
修复时区问题：将OpenSauce 2025的时间从PDT转换为北京时间
- 会议地点：San Mateo County Event Center, San Francisco Bay Area
- 原时区：Pacific Daylight Time (PDT) = UTC-7
- 目标时区：China Standard Time (CST) = UTC+8
- 时差：北京时间比PDT快15小时
"""

import json
from datetime import datetime, timedelta

def convert_time_to_beijing(time_str, date_str):
    """
    将PDT时间转换为北京时间
    
    Args:
        time_str: 如 "09:30 AM"
        date_str: 如 "July 18, 2025"
    
    Returns:
        tuple: (beijing_time_str, beijing_date_str, is_next_day)
    """
    # 解析时间
    time_obj = datetime.strptime(time_str, "%I:%M %p")
    
    # 解析日期
    date_obj = datetime.strptime(date_str, "%B %d, %Y")
    
    # 合并日期和时间
    pdt_datetime = datetime.combine(date_obj.date(), time_obj.time())
    
    # 转换为北京时间（PDT + 15小时）
    beijing_datetime = pdt_datetime + timedelta(hours=15)
    
    # 检查是否跨天
    is_next_day = beijing_datetime.date() != pdt_datetime.date()
    
    # 格式化输出
    beijing_time_str = beijing_datetime.strftime("%I:%M %p").lstrip('0')
    beijing_date_str = beijing_datetime.strftime("%B %d, %Y")
    
    return beijing_time_str, beijing_date_str, is_next_day

def update_agenda_with_beijing_time():
    """更新日程数据，添加北京时间信息"""
    
    # 读取现有数据
    with open('opensauce_2025_complete_agenda.json', 'r', encoding='utf-8') as f:
        agenda_data = json.load(f)
    
    # 日期映射
    date_mapping = {
        "friday": "July 18, 2025",
        "saturday": "July 19, 2025", 
        "sunday": "July 20, 2025"
    }
    
    # 更新每一天的数据
    for day_key, day_data in agenda_data["days"].items():
        original_date = date_mapping[day_key]
        
        for session in day_data["sessions"]:
            original_time = session["time"]
            
            # 转换时间
            beijing_time, beijing_date, is_next_day = convert_time_to_beijing(original_time, original_date)
            
            # 添加时区信息
            session["time_pdt"] = original_time + " PDT"
            session["time_beijing"] = beijing_time + " CST"
            session["date_pdt"] = original_date
            session["date_beijing"] = beijing_date
            session["timezone_note"] = f"PDT: {original_time} | Beijing: {beijing_time} CST"
            
            if is_next_day:
                session["beijing_next_day"] = True
                session["timezone_note"] += f" (+1 day)"
    
    # 添加时区说明
    agenda_data["timezone_info"] = {
        "original_timezone": "Pacific Daylight Time (PDT, UTC-7)",
        "converted_timezone": "China Standard Time (CST, UTC+8)", 
        "time_difference": "Beijing time is 15 hours ahead of PDT",
        "venue": "San Mateo County Event Center, San Francisco Bay Area",
        "note": "All times are converted for Beijing timezone users"
    }
    
    # 更新抓取时间
    agenda_data["scraped_at"] = datetime.now().isoformat()
    agenda_data["timezone_updated_at"] = datetime.now().isoformat()
    
    # 保存更新后的数据
    with open('opensauce_2025_complete_agenda.json', 'w', encoding='utf-8') as f:
        json.dump(agenda_data, f, ensure_ascii=False, indent=2)
    
    return agenda_data

def update_javascript_with_beijing_time(agenda_data):
    """更新JavaScript文件以支持北京时间"""
    
    # 生成新的JavaScript数据
    js_content = f"""// OpenSauce 2025 Schedule Data with Beijing Time Support
const scheduleDataEmbedded = {json.dumps(agenda_data, ensure_ascii=False, indent=2)};

// 时区转换函数
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
}}

// 全局时区设置
let useBeijingTime = true; // 默认使用北京时间

function toggleTimezone() {{
    useBeijingTime = !useBeijingTime;
    updateDisplayedTimes();
}}

function updateDisplayedTimes() {{
    // 更新页面上显示的时间
    document.querySelectorAll('.session-time').forEach(timeElement => {{
        const session = timeElement.closest('.session-card');
        if (session && session.sessionData) {{
            if (useBeijingTime && session.sessionData.time_beijing) {{
                timeElement.textContent = session.sessionData.time_beijing;
            }} else {{
                timeElement.textContent = session.sessionData.time_pdt || session.sessionData.time;
            }}
        }}
    }});
    
    // 更新时区切换按钮文本
    const toggleButton = document.getElementById('timezone-toggle');
    if (toggleButton) {{
        toggleButton.textContent = useBeijingTime ? '切换到PDT时间' : '切换到北京时间';
    }}
}}"""
    
    # 写入新的data.js文件
    with open('data.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    # 同时更新docs目录
    with open('docs/data.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    with open('docs/opensauce_2025_complete_agenda.json', 'w', encoding='utf-8') as f:
        json.dump(agenda_data, f, ensure_ascii=False, indent=2)

def print_conversion_examples():
    """打印一些转换示例"""
    print("\\n🕐 时区转换示例：")
    print("=" * 50)
    
    examples = [
        ("09:30 AM", "July 18, 2025"),
        ("01:30 PM", "July 18, 2025"), 
        ("05:30 PM", "July 18, 2025"),
        ("10:30 AM", "July 19, 2025"),
        ("05:00 PM", "July 20, 2025")
    ]
    
    for time_str, date_str in examples:
        beijing_time, beijing_date, is_next_day = convert_time_to_beijing(time_str, date_str)
        next_day_note = " (+1天)" if is_next_day else ""
        print(f"PDT: {time_str} {date_str}")
        print(f"北京: {beijing_time} {beijing_date}{next_day_note}")
        print("-" * 30)

if __name__ == "__main__":
    print("🌏 开始修复时区问题...")
    
    # 更新数据
    agenda_data = update_agenda_with_beijing_time()
    
    # 更新JavaScript文件
    update_javascript_with_beijing_time(agenda_data)
    
    print("✅ 时区修复完成！")
    print(f"   - 原时区：Pacific Daylight Time (PDT, UTC-7)")
    print(f"   - 目标时区：China Standard Time (CST, UTC+8)")
    print(f"   - 时差：北京时间比PDT快15小时")
    
    # 显示转换示例
    print_conversion_examples()
    
    print("\\n📁 已更新的文件：")
    print("   - opensauce_2025_complete_agenda.json")
    print("   - data.js")
    print("   - docs/data.js") 
    print("   - docs/opensauce_2025_complete_agenda.json")
