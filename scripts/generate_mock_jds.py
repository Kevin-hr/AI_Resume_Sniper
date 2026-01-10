import json
import os
import random

def generate_mock_jds(output_dir: str):
    """Generate synthetic JD files."""
    os.makedirs(output_dir, exist_ok=True)
    
    jds = [
        {
            "filename": "jd_java_expert.txt",
            "content": """
职位名称：高级 Java 开发工程师
工作地点：上海/杭州
薪资范围：30k-50k * 15薪

【岗位职责】
1. 负责公司核心业务系统的架构设计、开发和优化；
2. 解决高并发、高可用场景下的技术难题，提升系统稳定性；
3. 指导初中级工程师，进行代码审查，提升团队技术氛围。

【任职要求】
1. 统招本科及以上学历，计算机相关专业，5年以上 Java 开发经验；
2. 精通 Java 基础，熟悉 JVM 原理，精通多线程编程；
3. 熟练掌握 Spring Boot, Spring Cloud, MyBatis 等主流框架；
4. 熟悉 MySQL, Redis, RocketMQ/Kafka 等中间件，有调优经验；
5. 有大型分布式系统、微服务架构设计和落地经验者优先；
6. 具备良好的沟通能力和团队协作精神。
"""
        },
        {
            "filename": "jd_product_manager.txt",
            "content": """
职位名称：资深产品经理 (B端)
工作地点：北京
薪资范围：25k-40k

【岗位职责】
1. 负责公司 SaaS 产品的规划、设计和全生命周期管理；
2. 深入调研客户需求，输出高质量的需求文档 (PRD) 和原型设计；
3. 协调研发、测试、运营等团队，推动产品如期上线；
4. 持续跟踪产品数据，进行迭代优化，提升用户体验和业务价值。

【任职要求】
1. 本科及以上学历，3年以上 B 端产品经理经验；
2. 具备极强的逻辑思维能力和业务抽象能力；
3. 熟练使用 Axure, XMind, Sketch/Figma 等工具；
4. 有 CRM, ERP, HR SaaS 等行业经验者优先；
5. 优秀的跨部门沟通协作能力，抗压能力强。
"""
        },
        {
            "filename": "jd_frontend_lead.txt",
            "content": """
职位名称：前端技术专家
工作地点：深圳
薪资范围：40k-70k

【岗位职责】
1. 负责前端技术体系建设，包括组件库、工程化、性能优化等；
2. 攻克前端技术难点，如复杂可视化、Web 3D、跨端开发等；
3. 带领前端团队，提升代码质量和开发效率。

【任职要求】
1. 5年以上前端开发经验，精通 React 或 Vue 及其生态；
2. 深入理解 Web 标准，熟悉浏览器渲染原理和性能优化；
3. 熟悉 Node.js, Webpack/Vite, TypeScript；
4. 有大型前端项目架构经验，有开源项目贡献者优先。
"""
        }
    ]

    for jd in jds:
        path = os.path.join(output_dir, jd["filename"])
        with open(path, "w", encoding="utf-8") as f:
            f.write(jd["content"].strip())
        print(f"Generated JD: {path}")

if __name__ == "__main__":
    generate_mock_jds(r"c:\Users\52648\Documents\02_baijiahao\AI_Resume_Sniper\tests\fixtures\jds")
