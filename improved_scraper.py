#!/usr/bin/env python3
"""
改进的OpenSauce会议日程爬虫
更好地解析和结构化数据
"""

import json
import re
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImprovedOpenSauceScraper:
    def __init__(self):
        self.base_url = "https://opensauce.com/agenda/"
        self.agenda_data = {
            "scraped_at": datetime.now().isoformat(),
            "event_name": "OpenSauce 2025",
            "event_url": self.base_url,
            "event_dates": "July 18-20, 2025",
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
                await page.wait_for_timeout(3000)
                
                # 获取页面标题
                title = await page.title()
                logger.info(f"页面标题: {title}")
                
                # 提取三天的日程数据
                await self.extract_all_days_data(page)
                
            except Exception as e:
                logger.error(f"爬取过程中出现错误: {e}")
                raise
            finally:
                await browser.close()
    
    async def extract_all_days_data(self, page):
        """提取所有三天的数据"""
        days = ["FRIDAY", "SATURDAY", "SUNDAY"]
        
        for day in days:
            try:
                # 点击对应的日期标签
                day_tab = await page.query_selector(f'text="{day}"')
                if day_tab:
                    await day_tab.click()
                    await page.wait_for_timeout(2000)
                    
                    logger.info(f"正在提取 {day} 的数据")
                    
                    # 获取页面内容
                    content = await page.content()
                    
                    # 解析当天的会议数据
                    day_data = self.parse_day_content(content, day)
                    
                    if day_data:
                        self.agenda_data["days"][day.lower()] = day_data
                        logger.info(f"{day}: 提取了 {len(day_data['sessions'])} 个会议项目")
                    
            except Exception as e:
                logger.error(f"提取 {day} 数据时出错: {e}")
                continue
    
    def parse_day_content(self, html_content, day_name):
        """解析单天的内容"""
        day_data = {
            "day_name": day_name,
            "date": self.get_date_for_day(day_name),
            "sessions": []
        }
        
        # 使用正则表达式提取会议信息
        # 匹配时间、地点、标题和描述的模式
        session_pattern = r'(\d{2}:\d{2}\s+[AP]M)\s*\n\s*\((\d+)\s+mins\)\s*\n\s*([A-Z\s]+STAGE|BREAKOUT\s+\d+)\s*\n\s*([^\n]+)\s*\n\s*(.*?)(?=\d{2}:\d{2}\s+[AP]M|\Z)'
        
        matches = re.findall(session_pattern, html_content, re.DOTALL | re.MULTILINE)
        
        for match in matches:
            time, duration, venue, title, description = match
            
            # 清理和格式化数据
            session = {
                "time": time.strip(),
                "duration_minutes": int(duration),
                "venue": venue.strip(),
                "title": title.strip(),
                "description": self.clean_description(description),
                "speakers": self.extract_speakers(description)
            }
            
            day_data["sessions"].append(session)
        
        # 如果正则表达式没有匹配到，尝试备用方法
        if not day_data["sessions"]:
            day_data["sessions"] = self.parse_fallback_method(html_content)
        
        return day_data
    
    def clean_description(self, description):
        """清理描述文本"""
        # 移除多余的空白字符
        description = re.sub(r'\s+', ' ', description.strip())
        
        # 移除演讲者姓名（通常在描述末尾）
        lines = description.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not self.is_speaker_name(line):
                cleaned_lines.append(line)
        
        return ' '.join(cleaned_lines)
    
    def extract_speakers(self, description):
        """从描述中提取演讲者姓名"""
        speakers = []
        lines = description.split('\n')
        
        for line in lines:
            line = line.strip()
            if self.is_speaker_name(line):
                speakers.append(line)
        
        return speakers
    
    def is_speaker_name(self, text):
        """判断是否为演讲者姓名"""
        # 简单的启发式规则：短文本，包含大写字母，不包含常见的描述词汇
        if len(text) > 50:
            return False
        
        if not re.search(r'[A-Z]', text):
            return False
        
        # 排除常见的非姓名文本
        exclude_words = ['STAGE', 'BREAKOUT', 'AM', 'PM', 'mins', 'OPEN', 'SAUCE']
        if any(word in text.upper() for word in exclude_words):
            return False
        
        return True
    
    def parse_fallback_method(self, html_content):
        """备用解析方法"""
        sessions = []
        
        # 查找所有时间模式
        time_pattern = r'(\d{1,2}:\d{2}\s+[AP]M)'
        times = re.findall(time_pattern, html_content)
        
        for i, time in enumerate(times[:10]):  # 限制数量
            session = {
                "time": time,
                "duration_minutes": 30,  # 默认时长
                "venue": "TBD",
                "title": f"Session {i+1}",
                "description": "Details to be extracted",
                "speakers": []
            }
            sessions.append(session)
        
        return sessions
    
    def get_date_for_day(self, day_name):
        """获取具体日期"""
        dates = {
            "FRIDAY": "July 18, 2025",
            "SATURDAY": "July 19, 2025", 
            "SUNDAY": "July 20, 2025"
        }
        return dates.get(day_name, "TBD")
    
    def save_to_json(self, filename="opensauce_agenda_improved.json"):
        """保存数据到JSON文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.agenda_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"改进的数据已保存到 {filename}")
            
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
    scraper = ImprovedOpenSauceScraper()
    
    try:
        await scraper.scrape_agenda()
        scraper.save_to_json()
        
        print("✅ 改进的爬取完成！数据已保存到 opensauce_agenda_improved.json")
        
    except Exception as e:
        logger.error(f"爬取失败: {e}")
        print(f"❌ 爬取失败: {e}")

if __name__ == "__main__":
    asyncio.run(main())
