import type { DecisionPack, DecisionRequest } from "@/lib/types";

export type DecisionTemplate = {
  id: string;
  title: string;
  pack: DecisionPack;
  summary: string;
  bestFor: string;
  directUrl: string;
  request: DecisionRequest;
};

export const decisionTemplates: DecisionTemplate[] = [
  {
    id: "product-expansion",
    title: "企业 AI 工作台新模块",
    pack: "Product",
    summary: "判断是否上线新产品模块，以及首版范围、资源投入和验证指标。",
    bestFor: "产品路线图、功能优先级、企业客户试点",
    directUrl: "/?template=product-expansion",
    request: {
      title: "是否上线企业 AI 工作台新模块",
      pack: "Product",
      context: "企业客户希望把分散的项目输入快速转化为结构化决策，但本季度工程资源有限，销售团队也需要可演示的新能力。",
      objective: "判断是否在本季度上线聚焦版 AI 工作台模块，并明确发布范围和验证指标。",
      options: ["上线聚焦版 MVP", "等待完整集成后发布", "选择 2 个设计伙伴先试点"],
      constraints: "8 周交付窗口，后端资源有限，必须控制首版范围。",
      budget: 180000,
      timeline: "8 周",
      stakeholders: "产品、工程、销售、客户成功",
      success_metrics: "激活率、周活团队数、首次生成报告时间、试点客户转化率",
      known_risks: "范围过大可能影响质量，并延迟采用证据。"
    }
  },
  {
    id: "market-entry",
    title: "中型企业运营软件市场进入",
    pack: "Startup",
    summary: "评估创业团队是否进入一个新市场，以及应该选择垂直切入还是平台化路径。",
    bestFor: "创业方向、市场进入、融资叙事、冷启动验证",
    directUrl: "/?template=market-entry",
    request: {
      title: "是否进入中型企业运营软件市场",
      pack: "Startup",
      context: "团队观察到中型企业运营负责人存在重复需求，但该市场已有成熟工作流厂商，进入切入点需要更清晰。",
      objective: "判断是否先做垂直切入点，再支持下一轮融资叙事。",
      options: ["选择垂直场景切入", "直接做横向平台", "先用服务方式验证需求"],
      constraints: "距离下一轮融资叙事窗口还有 6 个月，团队需要尽快形成可验证牵引力。",
      budget: 320000,
      timeline: "12 周",
      stakeholders: "创始团队、早期客户、投资人",
      success_metrics: "合格线索、付费试点、实施周期、留存信号",
      known_risks: "市场可能需要更多实施服务，超过团队当前承载能力。"
    }
  },
  {
    id: "campaign-channel",
    title: "企业获客渠道投入选择",
    pack: "Marketing",
    summary: "比较 ABM、伙伴活动和内容增长等渠道，判断下季度预算应投向哪里。",
    bestFor: "营销预算、渠道 ROI、销售协同、增长动作",
    directUrl: "/?template=campaign-channel",
    request: {
      title: "是否加大企业获客渠道投入",
      pack: "Marketing",
      context: "当前自然线索稳定，但企业客户转化不均衡。团队需要在 ABM、伙伴活动和高管内容之间选择下一阶段主投方向。",
      objective: "确定下季度最优获客动作，并把预算集中到可衡量的渠道上。",
      options: ["投放 ABM 定向活动", "举办伙伴联合活动", "加强高管内容和行业观点"],
      constraints: "营销团队较小，销售跟进能力有限，需要一个季度内看到管道结果。",
      budget: 120000,
      timeline: "1 个季度",
      stakeholders: "市场、销售、收入运营、品牌负责人",
      success_metrics: "新增销售线索、会议预约率、机会转化率、单个机会成本",
      known_risks: "品牌活动可能短期不转化，ABM 需要销售团队强配合。"
    }
  },
  {
    id: "content-program",
    title: "专业内容栏目试点",
    pack: "Content",
    summary: "判断是否投入一个连续内容项目，以及先试点、直接做完整季还是先测需求。",
    bestFor: "内容产品、选题判断、分发节奏、商业化验证",
    directUrl: "/?template=content-program",
    request: {
      title: "是否启动专业内容栏目试点",
      pack: "Content",
      context: "团队有一个面向专业人群的内容栏目概念，已有初步受众画像、制作预算、渠道组合和发布节奏，但缺少真实留存信号。",
      objective: "判断是否先投入小规模试点，再决定是否扩展为长期内容项目。",
      options: ["试点 3 期内容", "直接制作完整季度", "先做受众需求测试"],
      constraints: "制作团队精简，发布窗口固定，需要保证品牌安全和内容质量。",
      budget: 90000,
      timeline: "6 周",
      stakeholders: "内容负责人、增长负责人、品牌负责人、财务",
      success_metrics: "完播率、订阅转化、每条内容成本、潜在赞助兴趣",
      known_risks: "创意目标可能超过制作能力，导致更新节奏不稳定。"
    }
  },
  {
    id: "senior-hiring",
    title: "高级平台负责人招聘",
    pack: "Hiring",
    summary: "判断是否现在招聘高级负责人，还是先用顾问或内部负责人过渡。",
    bestFor: "关键岗位、组织缺口、薪酬预算、招聘优先级",
    directUrl: "/?template=senior-hiring",
    request: {
      title: "是否招聘高级平台负责人",
      pack: "Hiring",
      context: "工程团队受架构决策拖慢，但公司也在控制现金消耗。现有团队缺少能跨模块推进平台治理的人。",
      objective: "判断是否立即招聘全职高级负责人，还是采用顾问或内部负责人过渡方案。",
      options: ["招聘高级平台负责人", "使用阶段性顾问", "提拔内部负责人并补充外部辅导"],
      constraints: "预算敏感，架构工作紧急，面试时间有限。",
      budget: 260000,
      timeline: "10 周",
      stakeholders: "CEO、CTO、工程经理、财务",
      success_metrics: "架构决策速度、团队交付吞吐、关键人员留存风险降低",
      known_risks: "过早招聘过高级角色可能增加成本，而组织承接方式还不成熟。"
    }
  },
  {
    id: "capital-allocation",
    title: "新战略资产投资",
    pack: "Investment",
    summary: "评估是否现在投资、分阶段投资，还是等待更好的进入条件。",
    bestFor: "资产配置、风险收益、进入时机、董事会决策",
    directUrl: "/?template=capital-allocation",
    request: {
      title: "是否投资新的战略资产",
      pack: "Investment",
      context: "该资产可能加强长期战略位置，但短期流动性、下行敞口和退出条件需要更明确。",
      objective: "判断现在投入、分阶段投入，还是等待更好的进入条件。",
      options: ["立即投资", "分阶段承诺", "等待更好进入条件"],
      constraints: "需要满足流动性目标、董事会审批，并考虑宏观不确定性。",
      budget: 500000,
      timeline: "30 天",
      stakeholders: "财务、战略、董事会、业务负责人",
      success_metrics: "风险调整回报、战略杠杆、流动性影响、下行保护",
      known_risks: "如果市场条件恶化，机会成本和退出风险可能上升。"
    }
  },
  {
    id: "custom-strategy",
    title: "跨部门战略决策",
    pack: "Custom",
    summary: "用于非标准重大决策，把开放问题转化为明确结论、路径和行动。",
    bestFor: "跨部门议题、资源分配、组织协同、非标准决策",
    directUrl: "/?template=custom-strategy",
    request: {
      title: "是否推进新的跨部门战略项目",
      pack: "Custom",
      context: "领导团队正在讨论一个跨部门战略项目，该项目可能影响预算、人力和多个团队优先级，但当前证据和责任边界仍不够清晰。",
      objective: "把开放问题转化为清晰结论、执行路径和本周行动。",
      options: ["立即推进", "缩小范围后试点", "暂停并补充证据"],
      constraints: "资源有限，跨部门协同成本较高，部分数据仍不完整。",
      budget: 100000,
      timeline: "4 周",
      stakeholders: "业务负责人、财务、运营、用户代表",
      success_metrics: "决策速度、证据质量、执行准备度、风险降低程度",
      known_risks: "如果责任人不清晰，决策可能被反复延迟。"
    }
  }
];

export const decisionTemplateExamples = Object.fromEntries(
  decisionTemplates.map((template) => [template.id, template.request])
) as Record<string, DecisionRequest>;
