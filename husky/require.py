
import re
import json

from husky.pdf import Pdf
from husky.mysql import Mysql


class Require:
    def __init__(self, file, name):
        self._db_ = Mysql()
        self.pdf = Pdf(file)
        self.record = {
            "require_name": name if bool(name) else self._parse_document_name(),
            "summary": self._parse_summary(),
            "content": self.pdf.content,
            "url": name,    # 这里如果有CDN服务，应为CDN地址
            "images": self.pdf.images,    # 这里如果有CDN服务，应为CDN地址
            "version": "0.0.00",
            "owner": "taoyanli0808",
            "completeness": 0.0,
            "testability": 0.0,
            "clarity": 0.0,
            "consistency": 0.0,
            "total_score": 0.0,
            "issues": []
        }


    def _check_completeness(self):
        """完整性检查"""
        required_sections = {"背景", "需求范围", "功能需求", "非功能需求", "验收标准"}
        detected = []
        missing = []
        
        for sect in required_sections:
            if any(s in self.pdf.sections for s in [sect, sect.upper(), sect.lower()]):
                detected.append(sect)
            else:
                missing.append(sect)
                self.record["issues"].append({
                    "type": "missing_section",
                    "detail": f"缺少必要章节：{sect}"
                })
        
        score = len(detected) / len(required_sections) * 20
        return min(round(score, 1), 20)

    def _check_testability(self):
        """可测试性检查"""
        acceptance_text = self.pdf.sections.get("验收标准", "")
        if not acceptance_text:
            self.record["issues"].append({"type": "critical", "detail": "缺失验收标准章节"})
            return 0

        # 查找量化指标
        quantifiers = re.findall(r'(必须|至少|不超过|>|<|=|≥|≤)', acceptance_text)
        quant_score = min(len(quantifiers) * 2, 10)
        
        # 检测测试用例
        test_cases = len(re.findall(r'(测试用例|tc-|case\d+)', acceptance_text, re.IGNORECASE))
        case_score = min(test_cases * 5, 15)
        
        return quant_score + case_score

    def _check_clarity(self):
        """清晰度检查"""
        vague_phrases = {
            '适当的': 2, '必要时': 3, '大致': 2, 
            '可能': 1, '等': 1, 'etc': 3
        }
        
        penalty = 0
        for phrase, weight in vague_phrases.items():
            count = self.pdf.text.count(phrase)
            if count > 0:
                self.record["issues"].append({
                    "type": "vague_phrase",
                    "detail": f"发现模糊表述：'{phrase}'（出现{count}次）"
                })
                penalty += count * weight
        
        return max(25 - penalty, 0)

    def _check_consistency(self):
        """一致性检查"""
        # 提取所有全大写术语（长度3-10）
        terms = re.findall(r'\b[A-Z]{3,10}\b', self.pdf.text.upper())
        term_counts = {}
        
        for term in terms:
            term_counts[term] = term_counts.get(term, 0) + 1
        
        # 检查术语是否定义
        conflict_count = 0
        for term, count in term_counts.items():
            if count > 1 and f"({term})" not in self.pdf.text:
                conflict_count += 1
                self.record["issues"].append({
                    "type": "term_conflict",
                    "detail": f"术语'{term}'未明确定义"
                })
        
        return max(15 - conflict_count*3, 0)
    
    def _parse_document_name(self):
        """从文本解析需求文档名称"""
        # 匹配首个标题格式
        first_header = re.search(r'^([\u4e00-\u9fa5a-zA-Z0-9]{5,20})[ \t]*\n', 
                            self.pdf.text, re.MULTILINE)
        return first_header.group(1).strip() if first_header else "未命名需求"
    
    def _parse_summary(self):
        """解析需求摘要（取前3行有效文本）"""
        summary_lines = []
        for line in self.pdf.text.split('\n'):
            stripped = line.strip()
            if stripped and not re.match(r'^#+', stripped):  # 过滤标题行
                summary_lines.append(stripped)
                if len(summary_lines) >= 3:
                    break
        return ' '.join(summary_lines[:3])

    def evaluate(self):
        scores = {
            "completeness": self._check_completeness(),
            "testability": self._check_testability(),
            "clarity": self._check_clarity(),
            "consistency": self._check_consistency(),
        }

        # 重组issues结构
        categorized_issues = {
            "completeness": [],
            "testability": [],
            "clarity": [],
            "consistency": []
        }
        for issue in self.record["issues"]:
            category_map = {
                "missing_section": "completeness",
                "critical": "testability",
                "vague_phrase": "clarity",
                "term_conflict": "consistency"
            }
            if issue["type"] in category_map:
                categorized_issues[category_map[issue["type"]]].append(issue["detail"])
        
        self.record.update(scores)
        self.record["total_score"] = sum(scores.values())
        self.record["issues"] = categorized_issues
        return self

    def save(self):
        self.record["content"], self.record["images"] = self.pdf.pdf_to_markdown_with_images()
        self._db_.create('require', self.record)


if __name__ == "__main__":
    # 使用示例
    evaluator = Require("test.pdf")
    results = evaluator.evaluate()
    
    print(json.dumps(results, indent=2, ensure_ascii=False))
