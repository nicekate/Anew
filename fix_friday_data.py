#!/usr/bin/env python3
"""
修复Friday July 18下午的数据
从原始爬取数据中提取完整的Friday下午会议信息
"""

import json
from datetime import datetime

def create_complete_friday_data():
    """创建完整的Friday数据，包括下午的会议"""
    
    complete_friday_sessions = [
        # 上午会议（已有的）
        {
            "time": "09:30 AM",
            "duration": "10 mins",
            "venue": "Industry Stage",
            "title": "WELCOME TO OPEN SAUCE WITH WILLIAM OSMAN",
            "description": "Join the official kickoff of Open Sauce Year 3 with inventor and creator William Osman. This session will offer a quick look at the creator culture that drives innovation, audience connection, and creative business growth.",
            "speakers": ["Jim Louderback", "William Osman"]
        },
        {
            "time": "09:40 AM",
            "duration": "25 mins",
            "venue": "Industry Stage",
            "title": "SCALING CONTENT ACROSS BORDERS",
            "description": "As platforms grow globally, smart creators are discovering opportunity to distribute everywhere. This session lays out the advantages for global content expansion: greater ad revenue, new sponsorship options, and increased audience growth.",
            "speakers": ["Dustin Harris", "Jonny Steel", "Corey Braun"]
        },
        {
            "time": "10:05 AM",
            "duration": "30 mins",
            "venue": "Industry Stage",
            "title": "IF YOUTUBE DIED TOMORROW, WOULD YOUR BUSINESS?",
            "description": "You don't own your followers. And if the algorithm turns on you—or your platform disappears—what happens next? This session explores how creators are future-proofing their business by owning their audiences and monetizing beyond the core social platforms.",
            "speakers": ["Kevin Daigle", "Luria Petrucci", "Brian McManus", "Luke Lafreniere", "Christian Eveleigh"]
        },
        {
            "time": "10:35 AM",
            "duration": "25 mins",
            "venue": "Industry Stage",
            "title": "FIRESIDE CHAT WITH ALEX WELLEN, PRESIDENT QVC",
            "description": "Commerce has entered a bold new era. In this fireside chat, Alex Wellen, President and Chief Growth Officer of QVC Group, joins Jim Louderback to explore how the company is redefining the commerce experience.",
            "speakers": ["Jim Louderback", "Alex Wellen"]
        },
        {
            "time": "11:00 AM",
            "duration": "30 mins",
            "venue": "Industry Stage",
            "title": "FIRESIDE CHAT WITH KEVIN KELLY AND WILLIAM OSMAN",
            "description": "Kevin Kelly helped define digital optimism and shaped how we think about technology, communities, and creativity. In this live podcast recording and fireside chat with maker-creator William Osman, they explore the real meaning behind 1,000 True Fans.",
            "speakers": ["William Osman", "Kevin Kelly"]
        },
        {
            "time": "11:30 AM",
            "duration": "30 mins",
            "venue": "Industry Stage",
            "title": "THE SCIENCE OF MEMES AND THE ART OF RELEVANCE",
            "description": "What do an etymology expert and an engineering creator have in common? Memes. In this surprising and fun session, they explore how meme culture powers both virality and connection.",
            "speakers": ["Adam Aleksic", "Patrick Lacey", "Morgan Sung"]
        },
        {
            "time": "12:20 PM",
            "duration": "30 mins",
            "venue": "Breakout 1",
            "title": "AMA WITH NASA ASTRONAUT MATTHEW DOMINICK",
            "description": "Straight from NASA to our stage, Matthew Dominick answers your boldest, weirdest, and most ambitious space questions - along with talking about what it's like to be a creator in space.",
            "speakers": ["Matthew Dominick"]
        },
        {
            "time": "12:20 PM",
            "duration": "30 mins",
            "venue": "Breakout 2",
            "title": "A DAY IN THE LIFE OF MARK ROBER'S CREATIVE TEAM",
            "description": "Go behind the scenes with Mark Rober's creative team as they share insights into their workflow, problem-solving techniques, and the magic behind their viral projects.",
            "speakers": ["Pojo Riegert", "Jon Marcu"]
        },
        {
            "time": "12:20 PM",
            "duration": "30 mins",
            "venue": "Breakout 3",
            "title": "ROUNDTABLE WITH TYLER CHOU",
            "description": "Got a legal question? Wondering about the law and creators? Bring your questions, thoughts and ideas to this round-table discussion with creator, lawyer, manager and creator advocate Tyler Chou.",
            "speakers": ["Tyler Chou"]
        },
        {
            "time": "01:00 PM",
            "duration": "30 mins",
            "venue": "Industry Stage",
            "title": "YOUTUBE ALGORITHM SECRETS - 2025",
            "description": "YouTube's creator liaison and editor Rene Ritchie and YouTube product manager Todd Beaupre share the deep secrets of success for July 2025, including why the algorithm doesn't hate you, how AI is changing discovery and recommendations.",
            "speakers": ["Todd Beaupré", "Rene Ritchie", "Gwen Miller"]
        },
        {
            "time": "01:30 PM",
            "duration": "25 mins",
            "venue": "Industry Stage",
            "title": "GM'S CREATOR PLAYBOOK",
            "description": "For GM, the road to the future isn't just about EVs and autonomous driving – it's about transforming how they engage with creators and redefine their brand for a digital-first world.",
            "speakers": ["Jessica Wang", "Neil Waller"]
        },
        # 下午会议（缺失的部分）
        {
            "time": "01:55 PM",
            "duration": "30 mins",
            "venue": "Industry Stage",
            "title": "WHAT CREATORS WISH BRANDS KNEW",
            "description": "Brands love working with creators—until they don't. Misaligned expectations, bad briefs, and clunky approval processes can turn a dream deal into a disaster. In this session, top creators pull back the curtain on what brands get wrong (and right) when collaborating with influencers.",
            "speakers": ["Cassandra Bankson", "Monica Khan"]
        },
        {
            "time": "02:25 PM",
            "duration": "25 mins",
            "venue": "Industry Stage",
            "title": "WHAT BRANDS WISH CREATORS KNEW - KAMAL BHANDAL",
            "description": "What makes a creator stand out—or get cut? Kamal Bhandal, SVP of Global Invisalign Brand at Align Technology, shares what brands really look for, what kills a deal, and how creators can position themselves for long-term partnerships.",
            "speakers": ["Kamal Bhandal", "Eric Wei"]
        },
        {
            "time": "02:50 PM",
            "duration": "30 mins",
            "venue": "Industry Stage",
            "title": "THRIVING AS A CREATOR IN THE AGE OF AI",
            "description": "These creators aren't scared of AI, they're adapting and thriving. 3 top creators share how they are integrating AI into their workflows today, and how they plan to differentiate their content from AI-generated slop tomorrow.",
            "speakers": ["YC Sun", "Delia Lazarescu", "Rox Codes"]
        },
        {
            "time": "03:20 PM",
            "duration": "10 mins",
            "venue": "Industry Stage",
            "title": "JOSHUA SCHACHTER ON ANGEL INVESTING",
            "description": "How Creators can Angel Invest",
            "speakers": ["Joshua Schachter"]
        },
        {
            "time": "03:35 PM",
            "duration": "30 mins",
            "venue": "Breakout 1",
            "title": "ROUND TABLE WITH RENE RITCHIE",
            "description": "Join this round table / AMA with Rene Ritchie to talk YouTube algorithms, creating content and really anything on your mind!",
            "speakers": ["Todd Beaupré", "Rene Ritchie"]
        },
        {
            "time": "03:35 PM",
            "duration": "30 mins",
            "venue": "Breakout 2",
            "title": "ROUNDTABLE CONVERSATION: WHAT IS A CREATOR IN THE AGE OF AI",
            "description": "AI is reshaping the creative process. This roundtable offers an interactive forum for creators, marketers and experts to discuss the practical, personal, and ethical questions raised in 'Thriving as a Creator in the Age of AI.'",
            "speakers": ["YC Sun", "Dan Perkel"]
        },
        {
            "time": "03:35 PM",
            "duration": "30 mins",
            "venue": "Breakout 3",
            "title": "ROUND TABLE Q&A: SETTING YOURSELF UP FOR BRAND PARTNERSHIPS SUCCESS",
            "description": "This facilitated discussion brings creators together to unpack the full brand partnerships journey. Whether you're represented or independent, you'll walk through the entire cycle—from strategy to pitch to execution and renewal.",
            "speakers": ["Ben Smith"]
        },
        {
            "time": "04:10 PM",
            "duration": "30 mins",
            "venue": "Industry Stage",
            "title": "EXPLAINING THE UNIVERSE ONE CLICK AT A TIME",
            "description": "From backyard explosions to big-bang theories, science hits different when it's told by creators who love to tinker, test, and ask 'what if?' This session dives into how hands-on creators and lifelong explainers are turning curiosity into content that sticks.",
            "speakers": ["Ian Charnas", "Trace Dominguez"]
        },
        {
            "time": "04:40 PM",
            "duration": "25 mins",
            "venue": "Industry Stage",
            "title": "FROM TECH JOURNALIST TO BRAND INSIDER",
            "description": "Dan Ackerman spent years running major tech sites, including Gizmodo and CNET. Now he's internal editor-in-chief at MicroCenter. What's it like to go from covering the industry to working inside it?",
            "speakers": ["Dan Ackerman", "Michael Reeves"]
        },
        {
            "time": "05:05 PM",
            "duration": "25 mins",
            "venue": "Industry Stage",
            "title": "LIKES DON'T PAY RENT - FIRESIDE CHAT WITH PATREON COO PAIGE FITZGERALD",
            "description": "This fireside chat with Patreon COO Paige Fitzgerald explores how creators are moving beyond ad models and algorithm churn to build real, recurring revenue.",
            "speakers": ["Paige Fitzgerald"]
        },
        {
            "time": "05:30 PM",
            "duration": "30 mins",
            "venue": "Industry Stage",
            "title": "FROM YOUTUBE CLICKBAIT TO REAL ENGINEERING",
            "description": "We're closing out industry day with a conversation with top creators who are pushing the boundaries of internet innovation through hands-on engineering and practical product development.",
            "speakers": ["William Osman"]
        }
    ]
    
    return complete_friday_sessions

def update_agenda_files():
    """更新所有相关的数据文件"""
    
    # 读取现有数据
    with open('opensauce_2025_complete_agenda.json', 'r', encoding='utf-8') as f:
        agenda_data = json.load(f)
    
    # 更新Friday数据
    complete_friday_sessions = create_complete_friday_data()
    agenda_data["days"]["friday"]["sessions"] = complete_friday_sessions
    
    # 更新抓取时间
    agenda_data["scraped_at"] = datetime.now().isoformat()
    
    # 保存更新后的数据
    with open('opensauce_2025_complete_agenda.json', 'w', encoding='utf-8') as f:
        json.dump(agenda_data, f, ensure_ascii=False, indent=2)
    
    # 更新嵌入式数据文件
    update_embedded_data(agenda_data)
    
    print(f"✅ 已修复Friday数据！")
    print(f"   - Friday会议总数: {len(complete_friday_sessions)}")
    print(f"   - 新增下午会议: {len(complete_friday_sessions) - 11}")
    print(f"   - 最后一个会议时间: {complete_friday_sessions[-1]['time']}")

def update_embedded_data(agenda_data):
    """更新data.js中的嵌入式数据"""
    
    # 读取现有的data.js文件
    with open('data.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 生成新的JavaScript数据
    js_data = f"// OpenSauce 2025 Schedule Data\nconst scheduleDataEmbedded = {json.dumps(agenda_data, ensure_ascii=False, indent=2)};"
    
    # 写入新的data.js文件
    with open('data.js', 'w', encoding='utf-8') as f:
        f.write(js_data)
    
    # 同时更新docs目录中的文件
    with open('docs/data.js', 'w', encoding='utf-8') as f:
        f.write(js_data)
    
    with open('docs/opensauce_2025_complete_agenda.json', 'w', encoding='utf-8') as f:
        json.dump(agenda_data, f, ensure_ascii=False, indent=2)
    
    print("✅ 已更新所有数据文件（包括docs目录）")

if __name__ == "__main__":
    update_agenda_files()
