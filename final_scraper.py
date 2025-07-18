#!/usr/bin/env python3
"""
最终版OpenSauce会议日程爬虫
直接从原始数据中提取结构化信息
"""

import json
import re
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinalOpenSauceScraper:
    def __init__(self):
        self.base_url = "https://opensauce.com/agenda/"
        self.agenda_data = {
            "scraped_at": datetime.now().isoformat(),
            "event_name": "OpenSauce 2025",
            "event_url": self.base_url,
            "event_dates": "July 18-20, 2025",
            "location": "San Francisco, CA",
            "days": {}
        }
    
    async def scrape_agenda(self):
        """主要的爬虫方法"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                logger.info(f"正在访问 {self.base_url}")
                await page.goto(self.base_url, wait_until="networkidle")
                await page.wait_for_timeout(5000)
                
                # 获取页面标题
                title = await page.title()
                logger.info(f"页面标题: {title}")
                
                # 截图以便调试
                await page.screenshot(path="opensauce_page.png")
                logger.info("已保存页面截图")
                
                # 提取所有可见文本内容
                all_text = await page.evaluate('() => document.body.innerText')
                
                # 解析文本内容
                self.parse_text_content(all_text)
                
            except Exception as e:
                logger.error(f"爬取过程中出现错误: {e}")
                raise
            finally:
                await browser.close()
    
    def parse_text_content(self, text_content):
        """解析文本内容"""
        logger.info("开始解析文本内容")
        
        # 将文本按行分割
        lines = text_content.split('\n')
        
        # 查找日程部分
        current_day = None
        current_session = None
        sessions = []
        
        # 定义日期映射
        day_mapping = {
            "FRIDAY": {"name": "Friday", "date": "July 18, 2025"},
            "SATURDAY": {"name": "Saturday", "date": "July 19, 2025"},
            "SUNDAY": {"name": "Sunday", "date": "July 20, 2025"}
        }
        
        # 时间模式
        time_pattern = r'(\d{1,2}:\d{2}\s+[AP]M)'
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # 检查是否是日期标题
            if line in day_mapping:
                if current_day and sessions:
                    self.agenda_data["days"][current_day.lower()] = {
                        "day_name": day_mapping[current_day]["name"],
                        "date": day_mapping[current_day]["date"],
                        "sessions": sessions
                    }
                
                current_day = line
                sessions = []
                logger.info(f"找到日期: {line}")
            
            # 检查是否是时间
            elif re.match(time_pattern, line):
                if current_session:
                    sessions.append(current_session)
                
                current_session = {
                    "time": line,
                    "duration": "",
                    "venue": "",
                    "title": "",
                    "description": "",
                    "speakers": []
                }
                
                # 查找持续时间
                if i + 1 < len(lines) and 'mins' in lines[i + 1]:
                    current_session["duration"] = lines[i + 1].strip()
                    i += 1
                
                # 查找场地
                if i + 1 < len(lines) and ('STAGE' in lines[i + 1] or 'BREAKOUT' in lines[i + 1]):
                    current_session["venue"] = lines[i + 1].strip()
                    i += 1
                
                # 查找标题
                if i + 1 < len(lines):
                    current_session["title"] = lines[i + 1].strip()
                    i += 1
                
                # 查找描述（接下来的几行）
                description_lines = []
                j = i + 1
                while j < len(lines) and j < i + 10:  # 限制查找范围
                    next_line = lines[j].strip()
                    if re.match(time_pattern, next_line) or next_line in day_mapping:
                        break
                    if next_line and len(next_line) > 10:  # 过滤短行
                        description_lines.append(next_line)
                    j += 1
                
                current_session["description"] = ' '.join(description_lines[:3])  # 取前3行作为描述
                
                # 提取演讲者（通常是短行，包含人名）
                speakers = []
                for desc_line in description_lines[3:]:  # 从第4行开始查找演讲者
                    if len(desc_line) < 50 and self.looks_like_name(desc_line):
                        speakers.append(desc_line)
                
                current_session["speakers"] = speakers[:5]  # 最多5个演讲者
            
            i += 1
        
        # 添加最后一个会话和最后一天
        if current_session:
            sessions.append(current_session)
        
        if current_day and sessions:
            self.agenda_data["days"][current_day.lower()] = {
                "day_name": day_mapping[current_day]["name"],
                "date": day_mapping[current_day]["date"],
                "sessions": sessions
            }
        
        # 如果没有找到结构化数据，保存原始文本
        if not self.agenda_data["days"]:
            self.save_raw_text_analysis(text_content)
    
    def looks_like_name(self, text):
        """判断文本是否像人名"""
        # 简单的启发式规则
        if len(text) > 50:
            return False
        
        # 包含大写字母
        if not re.search(r'[A-Z]', text):
            return False
        
        # 不包含常见的非姓名词汇
        exclude_words = ['STAGE', 'BREAKOUT', 'AM', 'PM', 'mins', 'OPEN', 'SAUCE', 'THE', 'AND', 'OR']
        if any(word in text.upper() for word in exclude_words):
            return False
        
        # 包含空格（名字通常有空格）
        if ' ' not in text:
            return False
        
        return True
    
    def save_raw_text_analysis(self, text_content):
        """保存原始文本分析"""
        logger.info("保存原始文本分析")
        
        # 查找所有时间
        time_pattern = r'(\d{1,2}:\d{2}\s+[AP]M)'
        times = re.findall(time_pattern, text_content)
        
        # 查找所有可能的标题（大写文本）
        title_pattern = r'^[A-Z\s]{10,}$'
        lines = text_content.split('\n')
        titles = [line.strip() for line in lines if re.match(title_pattern, line.strip())]
        
        self.agenda_data["raw_analysis"] = {
            "total_lines": len(lines),
            "found_times": times,
            "found_titles": titles[:20],  # 前20个标题
            "sample_content": text_content[:2000]  # 前2000字符
        }
    
    def save_to_json(self, filename="opensauce_agenda_final.json"):
        """保存数据到JSON文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.agenda_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"最终数据已保存到 {filename}")
            
            # 打印统计信息
            total_sessions = sum(
                len(day_data.get("sessions", [])) 
                for day_data in self.agenda_data["days"].values()
            )
            
            logger.info(f"总共提取了 {len(self.agenda_data['days'])} 天的数据")
            logger.info(f"总共提取了 {total_sessions} 个会议项目")
            
            # 打印每天的详细信息
            for day_name, day_data in self.agenda_data["days"].items():
                logger.info(f"{day_name.upper()}: {len(day_data['sessions'])} 个会议")
            
        except Exception as e:
            logger.error(f"保存文件时出错: {e}")
            raise

async def main():
    """主函数"""
    scraper = FinalOpenSauceScraper()
    
    try:
        await scraper.scrape_agenda()
        scraper.save_to_json()
        
        print("✅ 最终爬取完成！数据已保存到 opensauce_agenda_final.json")
        
    except Exception as e:
        logger.error(f"爬取失败: {e}")
        print(f"❌ 爬取失败: {e}")

if __name__ == "__main__":
    asyncio.run(main())
