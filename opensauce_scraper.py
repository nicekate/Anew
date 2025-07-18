#!/usr/bin/env python3
"""
OpenSauce 会议日程爬虫
获取 https://opensauce.com/agenda/ 的完整三天日程信息
"""

import json
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OpenSauceScraper:
    def __init__(self):
        self.base_url = "https://opensauce.com/agenda/"
        self.agenda_data = {
            "scraped_at": datetime.now().isoformat(),
            "event_name": "OpenSauce",
            "event_url": self.base_url,
            "days": {}
        }
    
    async def scrape_agenda(self):
        """主要的爬虫方法"""
        async with async_playwright() as p:
            # 启动浏览器
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                logger.info(f"正在访问 {self.base_url}")
                await page.goto(self.base_url, wait_until="networkidle")
                
                # 等待页面加载完成
                await page.wait_for_timeout(3000)
                
                # 获取页面标题
                title = await page.title()
                logger.info(f"页面标题: {title}")
                
                # 查找日程标签页或日期选择器
                await self.extract_agenda_data(page)
                
            except Exception as e:
                logger.error(f"爬取过程中出现错误: {e}")
                raise
            finally:
                await browser.close()
    
    async def extract_agenda_data(self, page):
        """提取日程数据"""
        try:
            # 首先尝试查找日期标签页
            day_tabs = await page.query_selector_all('[role="tab"], .tab, .day-tab, [data-day], .agenda-day')
            
            if day_tabs:
                logger.info(f"找到 {len(day_tabs)} 个日期标签页")
                await self.extract_from_tabs(page, day_tabs)
            else:
                # 如果没有标签页，尝试查找所有日程内容
                logger.info("未找到日期标签页，尝试提取所有可见内容")
                await self.extract_all_visible_content(page)
                
        except Exception as e:
            logger.error(f"提取数据时出错: {e}")
            # 作为备用方案，获取页面的所有文本内容
            await self.extract_fallback_content(page)
    
    async def extract_from_tabs(self, page, day_tabs):
        """从标签页中提取数据"""
        for i, tab in enumerate(day_tabs):
            try:
                # 点击标签页
                await tab.click()
                await page.wait_for_timeout(2000)
                
                # 获取标签页文本
                tab_text = await tab.inner_text()
                logger.info(f"处理标签页: {tab_text}")
                
                # 提取当前标签页的内容
                day_data = await self.extract_day_content(page, tab_text)
                
                if day_data:
                    self.agenda_data["days"][f"day_{i+1}_{tab_text}"] = day_data
                    
            except Exception as e:
                logger.error(f"处理标签页 {i} 时出错: {e}")
                continue
    
    async def extract_day_content(self, page, day_name):
        """提取单天的日程内容"""
        day_data = {
            "day_name": day_name,
            "sessions": []
        }
        
        # 查找会议议程项目
        session_selectors = [
            '.session', '.agenda-item', '.schedule-item', 
            '.event-item', '[data-session]', '.talk',
            '.presentation', '.workshop'
        ]
        
        sessions = []
        for selector in session_selectors:
            found_sessions = await page.query_selector_all(selector)
            if found_sessions:
                sessions = found_sessions
                logger.info(f"使用选择器 '{selector}' 找到 {len(sessions)} 个会议项目")
                break
        
        if not sessions:
            # 如果没有找到特定的会议项目，尝试查找包含时间的元素
            time_elements = await page.query_selector_all('*:has-text(":")') 
            sessions = time_elements[:20]  # 限制数量避免过多无关内容
            logger.info(f"通过时间模式找到 {len(sessions)} 个可能的会议项目")
        
        for session in sessions:
            try:
                session_data = await self.extract_session_data(session)
                if session_data:
                    day_data["sessions"].append(session_data)
            except Exception as e:
                logger.error(f"提取会议项目数据时出错: {e}")
                continue
        
        return day_data
    
    async def extract_session_data(self, session_element):
        """提取单个会议的详细信息"""
        try:
            # 获取会议的所有文本内容
            full_text = await session_element.inner_text()
            
            if not full_text.strip():
                return None
            
            session_data = {
                "full_text": full_text.strip(),
                "time": "",
                "title": "",
                "speaker": "",
                "description": "",
                "location": ""
            }
            
            # 尝试提取时间信息
            time_element = await session_element.query_selector('.time, .schedule-time, [data-time]')
            if time_element:
                session_data["time"] = await time_element.inner_text()
            
            # 尝试提取标题
            title_element = await session_element.query_selector('h1, h2, h3, h4, .title, .session-title, .talk-title')
            if title_element:
                session_data["title"] = await title_element.inner_text()
            
            # 尝试提取演讲者信息
            speaker_element = await session_element.query_selector('.speaker, .presenter, .author, .by')
            if speaker_element:
                session_data["speaker"] = await speaker_element.inner_text()
            
            # 尝试提取描述
            desc_element = await session_element.query_selector('.description, .abstract, .summary, p')
            if desc_element:
                session_data["description"] = await desc_element.inner_text()
            
            # 尝试提取地点
            location_element = await session_element.query_selector('.location, .room, .venue')
            if location_element:
                session_data["location"] = await location_element.inner_text()
            
            return session_data
            
        except Exception as e:
            logger.error(f"提取会议详细信息时出错: {e}")
            return None
    
    async def extract_all_visible_content(self, page):
        """提取所有可见内容作为备用方案"""
        try:
            # 获取页面的主要内容区域
            content_selectors = ['main', '.content', '.agenda', '.schedule', 'body']
            
            for selector in content_selectors:
                content_element = await page.query_selector(selector)
                if content_element:
                    content_text = await content_element.inner_text()
                    
                    self.agenda_data["days"]["all_content"] = {
                        "day_name": "All Visible Content",
                        "raw_content": content_text,
                        "extracted_at": datetime.now().isoformat()
                    }
                    
                    logger.info(f"提取了 {len(content_text)} 字符的内容")
                    break
                    
        except Exception as e:
            logger.error(f"提取所有内容时出错: {e}")
    
    async def extract_fallback_content(self, page):
        """最后的备用方案：获取页面HTML"""
        try:
            html_content = await page.content()
            
            self.agenda_data["days"]["fallback_html"] = {
                "day_name": "Fallback HTML Content",
                "html_content": html_content,
                "extracted_at": datetime.now().isoformat()
            }
            
            logger.info("已保存HTML内容作为备用")
            
        except Exception as e:
            logger.error(f"获取HTML内容时出错: {e}")
    
    def save_to_json(self, filename="opensauce_agenda.json"):
        """保存数据到JSON文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.agenda_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"数据已保存到 {filename}")
            
            # 打印统计信息
            total_sessions = sum(
                len(day_data.get("sessions", [])) 
                for day_data in self.agenda_data["days"].values()
                if isinstance(day_data, dict) and "sessions" in day_data
            )
            
            logger.info(f"总共提取了 {len(self.agenda_data['days'])} 天的数据")
            logger.info(f"总共提取了 {total_sessions} 个会议项目")
            
        except Exception as e:
            logger.error(f"保存文件时出错: {e}")
            raise

async def main():
    """主函数"""
    scraper = OpenSauceScraper()
    
    try:
        await scraper.scrape_agenda()
        scraper.save_to_json()
        
        print("✅ 爬取完成！数据已保存到 opensauce_agenda.json")
        
    except Exception as e:
        logger.error(f"爬取失败: {e}")
        print(f"❌ 爬取失败: {e}")

if __name__ == "__main__":
    asyncio.run(main())
