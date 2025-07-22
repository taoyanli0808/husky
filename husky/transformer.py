import os
import json
from loguru import logger
from openai import OpenAI
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

logger.add("test_automation.log", rotation="10 MB", retention="7 days")

PROMPT_TEMPLATE = """将自然语言测试用例转换为标准JSON格式，必须严格按照下方示例的JSON结构输出。

操作类型包括：navigate, click, fill, assert_text, screenshot

示例输入（自然语言）：
打开京东首页
在搜索框输入"手机"
点击搜索按钮
验证页面包含"手机排行榜"

示例输出（必须为严格的JSON格式）：
{
  "steps": [
    {"action": "navigate", "url": "https://www.jd.com"},
    {"action": "fill", "selector": "#key", "value": "手机"},
    {"action": "click", "selector": ".button"},
    {"action": "assert_text", "selector": "h1.title", "expected": "手机排行榜"}
  ]
}

当前需要转换为json的测试用例：
"""

def nl_to_script(nl_case):
    try:
        client = OpenAI(
            api_key=os.getenv("API_KEY"),
            base_url="https://api.deepseek.com",
            timeout=30
        )
        
        logger.info("开始转换自然语言测试用例", input=nl_case)
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": PROMPT_TEMPLATE+nl_case}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        logger.debug("收到AI响应", raw_response=content)
        
        data = json.loads(content)
        if not isinstance(data.get("steps"), list):
            raise ValueError("JSON结构缺少steps数组")
            
        logger.success("成功转换测试步骤", step_count=len(data["steps"]))
        return data
        
    except json.JSONDecodeError as e:
        logger.error("JSON解析失败", error=str(e), content=content)
        raise ValueError(f"无效的JSON格式: {str(e)}")
    except Exception as e:
        logger.opt(exception=True).error("转换过程异常")
        raise

def generate_test_script(test_case):
    # try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            logger.info("浏览器实例已创建")

            for idx, step in enumerate(test_case["steps"], 1):
                action = step["action"]
                logger.info(f"执行第{idx}步", action=action)
                
                try:
                    if action == "navigate":
                        page.goto(step["url"])
                        logger.debug("页面跳转完成", url=step["url"])
                    elif action == "click":
                        page.click(step["selector"])
                        logger.debug("点击操作完成", selector=step["selector"])
                    elif action == "fill":
                        page.fill(step["selector"], step["value"])
                        logger.debug("输入完成", selector=step["selector"], value=step["value"])
                    elif action == "assert_text":
                        actual = page.inner_text(step["selector"])
                        assert step["expected"] in actual
                        logger.success("断言通过", expected=step["expected"], actual=actual)
                    elif action == "screenshot":
                        page.screenshot(path=step["path"])
                        logger.info("截图保存成功", path=step["path"])
                        
                    page.wait_for_timeout(500)
                    
                except Exception as e:
                    logger.error("步骤执行异常", step=step, error=str(e))
                    raise

            browser.close()
            logger.success("浏览器正常关闭")
            
    # except Exception as e:
    #     logger.critical("测试执行严重错误", error=str(e))
    #     raise

if __name__ == "__main__":
    logger.info("测试脚本启动")
    
    test_case = """
    打开淘宝首页
    搜索框输入"夏季连衣裙"
    点击搜索按钮
    验证筛选条件中有"包邮"
    对页面进行截图保存为summer_dress.png
    """
    
    # try:
    script = nl_to_script(test_case)
    logger.info(f"testcase: {script}")
    generate_test_script(script)
    logger.success("主流程完成")
    # except Exception as e:
    #     logger.error("主流程异常终止", error=str(e))