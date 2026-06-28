from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, model_validator


class CampaignRequest(BaseModel):
    brand: str = Field(..., min_length=1, examples=["Acme AI Notes"])
    budget: float = Field(..., gt=0, examples=[50000])
    goal: str = Field(..., min_length=1, examples=["提升新品认知并获取试用转化"])
    platform: str = Field(..., min_length=1, examples=["douyin"])
    category: str | None = Field(default=None, examples=["tech"])
    audience: str | None = Field(default=None, examples=["一二线城市效率工具用户"])


class Creator(BaseModel):
    id: str
    name: str
    platform: str
    tags: list[str]
    followers: int
    conversion_rate: float
    avg_cpm: float = 60
    risk_flags: list[str] = []


class CreatorInput(BaseModel):
    name: str = Field(..., min_length=1)
    platform: str = Field(..., min_length=1)
    tags: list[str] = []
    followers: int = Field(..., ge=0)
    conversion_rate: float = Field(..., ge=0, le=1)
    avg_cpm: float = Field(default=60, gt=0)
    risk_flags: list[str] = []


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str


class AdminSummary(BaseModel):
    creators: int
    actors: int
    reports: int
    projects: int
    logs: int
    total_followers: int


class ReportFile(BaseModel):
    id: str
    filename: str
    url: str
    size_bytes: int
    created_at: str


class ProjectRecord(BaseModel):
    id: str
    report_id: str
    kind: str
    title: str
    category: str
    platforms: list[str]
    budget: float
    status: str
    score: int | None = None
    pdf_url: str | None = None
    created_at: str
    updated_at: str
    report: dict[str, Any]


class LogEntry(BaseModel):
    id: str
    created_at: str
    level: str
    event: str
    actor: str
    message: str
    metadata: dict[str, str | int | float | bool | None] = {}


class Actor(BaseModel):
    id: str
    name: str
    gender: str
    age_range: str
    location: str
    image_tags: list[str]
    role_tags: list[str]
    genres: list[str]
    fee_min: float
    fee_max: float
    schedule_status: str
    followers: int = 0
    completion_rate: float = 0
    paid_conversion_rate: float = 0
    past_works: list[str] = []
    risk_flags: list[str] = []


class ActorInput(BaseModel):
    name: str = Field(..., min_length=1)
    gender: str = Field(..., min_length=1)
    age_range: str = Field(..., min_length=1)
    location: str = Field(..., min_length=1)
    image_tags: list[str] = []
    role_tags: list[str] = []
    genres: list[str] = []
    fee_min: float = Field(..., ge=0)
    fee_max: float = Field(..., ge=0)
    schedule_status: str = Field(default="available")
    followers: int = Field(default=0, ge=0)
    completion_rate: float = Field(default=0, ge=0, le=1)
    paid_conversion_rate: float = Field(default=0, ge=0, le=1)
    past_works: list[str] = []
    risk_flags: list[str] = []


class DramaProjectRequest(BaseModel):
    title: str = Field(..., min_length=1, examples=["重生后我成了顶流"])
    genre: str = Field(..., min_length=1, examples=["甜宠逆袭"])
    platform: str | None = Field(default=None, examples=["hongguo"])
    platforms: list[str] = Field(default_factory=list, examples=[["hongguo", "douyin"]])
    budget: float = Field(..., gt=0, examples=[300000])
    episodes: int = Field(default=60, ge=1)
    shooting_days: int = Field(default=7, ge=1)
    audience: str | None = Field(default=None)
    monetization: str = Field(default="IAP")
    roles: list[str] = Field(default_factory=lambda: ["女主", "男主"])
    synopsis: str | None = Field(default=None)

    @model_validator(mode="after")
    def normalize_platforms(self) -> "DramaProjectRequest":
        if not self.platforms and self.platform:
            self.platforms = [self.platform]
        if not self.platforms:
            self.platforms = ["hongguo"]
        self.platform = self.platforms[0]
        return self


class MatchedActor(Actor):
    role: str
    match_score: float
    score_reasons: list[str]
    budget_fit: str
    schedule_fit: str


class DramaRoiForecast(BaseModel):
    estimated_views: int
    completion_rate: float
    paid_conversion_rate: float
    estimated_revenue: float
    estimated_profit: float
    estimated_roi: float
    payback_days: str
    assumptions: list[str]


class DramaRiskAssessment(BaseModel):
    level: str
    score: float
    flags: list[str]
    mitigations: list[str]


class CharacterProfile(BaseModel):
    role: str
    name: str
    archetype: str
    desire: str
    conflict: str


class EpisodeOutline(BaseModel):
    episode: int
    title: str
    hook: str
    plot: str
    cliffhanger: str
    paid_point: bool = False


class EpisodeScript(BaseModel):
    episode: int
    title: str
    scenes: list[str]
    dialogue_beats: list[str]
    cliffhanger: str


class ScriptScore(BaseModel):
    hook: int
    character: int
    conflict: int
    payoff: int
    reversal: int
    platform_fit: int
    actor_fit: int
    production_cost: int
    compliance_risk: int
    blockbuster_potential: int
    overall: int
    notes: list[str]


class AdvertisingCreative(BaseModel):
    platform: str
    angle: str
    opening_hook: str
    script: list[str]
    cta: str


class CreativePackage(BaseModel):
    positioning: str
    target_persona: str
    paid_hook_strategy: str
    title_templates: list[str]
    cover_copy: list[str]
    ab_test_angles: list[str]
    platform_notes: list[str]
    creatives: list[AdvertisingCreative]


class ScriptStructureBeat(BaseModel):
    stage: str
    episodes: str
    purpose: str
    must_have: list[str]


class ScriptRevisionItem(BaseModel):
    target: str
    problem: str
    suggestion: str
    example: str


class ScriptDoctorReport(BaseModel):
    structure: list[ScriptStructureBeat]
    content_optimizations: list[str]
    revision_items: list[ScriptRevisionItem]
    dialogue_rewrites: list[str]
    shootable_structure: list[str]


class BenchmarkDrama(BaseModel):
    title: str
    genre_fit: str
    selling_point: str
    opening_hook: str
    paid_hook: str
    production_note: str


class PaidPointPlan(BaseModel):
    episode: int
    trigger: str
    user_emotion: str
    paywall_copy: str
    next_episode_promise: str


class DeliveryAsset(BaseModel):
    name: str
    format: str
    audience: str
    content: list[str]


class CommercialDecisionPack(BaseModel):
    benchmark_summary: str
    benchmarks: list[BenchmarkDrama]
    paid_point_plan: list[PaidPointPlan]
    delivery_assets: list[DeliveryAsset]
    pitch_summary: list[str]
    rollout_checklist: list[str]


class StoryDevelopment(BaseModel):
    logline: str
    core_conflict: str
    relationship_hook: str
    audience_promise: str
    structure_suggestions: list[str]
    characters: list[CharacterProfile]
    episode_outline: list[EpisodeOutline]
    first_3_scripts: list[EpisodeScript]
    first_10_scripts: list[EpisodeScript]
    score: ScriptScore


class DramaReport(BaseModel):
    report_id: str
    title: str
    genre: str
    platform: str
    platforms: list[str]
    budget: float
    roles: list[str]
    actors: list[MatchedActor]
    roi: DramaRoiForecast
    risk: DramaRiskAssessment
    story: StoryDevelopment
    creative_package: CreativePackage
    script_doctor: ScriptDoctorReport
    commercial_pack: CommercialDecisionPack
    recommendations: list[str]
    pdf_url: str
    ppt_url: str | None = None
    docx_url: str | None = None


class MatchedCreator(Creator):
    match_score: float
    score_reasons: list[str]
    estimated_reach: int
    estimated_conversions: int


class ScriptIdea(BaseModel):
    creator_id: str
    hook: str
    structure: list[str]
    cta: str


class RiskAssessment(BaseModel):
    level: str
    score: float
    flags: list[str]
    mitigations: list[str]


class RoiForecast(BaseModel):
    estimated_reach: int
    estimated_conversions: int
    estimated_revenue: float
    estimated_roi: float
    cost_per_conversion: float
    assumptions: list[str]


class CampaignReport(BaseModel):
    report_id: str
    brand: str
    budget: float
    goal: str
    platform: str
    creators: list[MatchedCreator]
    scripts: list[ScriptIdea]
    risk: RiskAssessment
    roi: RoiForecast
    pdf_url: str


class MaterialTestInput(BaseModel):
    name: str = Field(..., min_length=1, examples=["A版-重生打脸标题"])
    title: str = Field(default="")
    cover_copy: str = Field(default="")
    opening_hook: str = Field(default="")
    impressions: int = Field(default=0, ge=0)
    clicks: int = Field(default=0, ge=0)
    three_second_views: int = Field(default=0, ge=0)
    completions: int = Field(default=0, ge=0)
    paid_users: int = Field(default=0, ge=0)
    spend: float = Field(default=0, ge=0)
    revenue: float = Field(default=0, ge=0)


class GrowthReviewRequest(BaseModel):
    project_title: str = Field(..., min_length=1)
    platform: str = Field(default="douyin")
    episode: int = Field(default=1, ge=1)
    tests: list[MaterialTestInput] = Field(default_factory=list)


class MaterialTestResult(BaseModel):
    name: str
    ctr: float
    three_second_rate: float
    completion_rate: float
    paid_rate: float
    roi: float
    status: str
    diagnosis: list[str]
    next_actions: list[str]


class RewriteSuggestion(BaseModel):
    category: str
    target_problem: str
    options: list[str]


class RewriteAssistantPack(BaseModel):
    summary: str = "历史复盘记录未包含改写助手内容，请重新生成复盘以获得改写建议。"
    title_options: list[str] = []
    cover_options: list[str] = []
    opening_recuts: list[str] = []
    paid_point_rewrites: list[str] = []
    suggestions: list[RewriteSuggestion] = []


class GrowthReviewReport(BaseModel):
    project_title: str
    platform: str
    episode: int
    winner: str | None
    overall_diagnosis: list[str]
    test_results: list[MaterialTestResult]
    next_round_plan: list[str]
    rewrite_assistant: RewriteAssistantPack = Field(default_factory=RewriteAssistantPack)


class GrowthReviewRecord(BaseModel):
    id: str
    project_title: str
    platform: str
    episode: int
    winner: str | None
    created_at: str
    request: GrowthReviewRequest
    report: GrowthReviewReport


class ProjectVersionSummary(BaseModel):
    project_id: str
    report_id: str
    version_name: str
    title: str
    category: str
    platforms: list[str]
    budget: float
    score: int | None = None
    pdf_url: str | None = None
    ppt_url: str | None = None
    docx_url: str | None = None
    created_at: str
    updated_at: str


class ProjectWorkspaceGroup(BaseModel):
    title: str
    versions: list[ProjectVersionSummary]
    reviews: list[GrowthReviewRecord]


class ProjectWorkspaceResponse(BaseModel):
    groups: list[ProjectWorkspaceGroup]
