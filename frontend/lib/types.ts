export type CampaignRequest = {
  brand: string;
  budget: number;
  goal: string;
  platform: string;
  category?: string;
  audience?: string;
};

export type DecisionPack = "Product" | "Startup" | "Marketing" | "Content" | "Hiring" | "Investment" | "Custom";

export type DecisionRequest = {
  title: string;
  pack: DecisionPack;
  language?: "en" | "zh";
  context: string;
  objective: string;
  options: string[];
  constraints: string;
  budget: number;
  timeline: string;
  stakeholders: string;
  success_metrics: string;
  known_risks: string;
};

export type FollowUpQuestion = {
  id: string;
  question: string;
  context: string;
  type: "text" | "textarea" | "select" | "multiselect";
  options?: string[];
  answer?: string;
};

export type FollowUpSession = {
  decisionId: string;
  questions: FollowUpQuestion[];
  status: "pending" | "answering" | "completed";
};

export type ActionItem = {
  day: string;
  task: string;
  owner: string;
  duration: string;
  priority: "High" | "Medium" | "Low" | "高" | "中" | "低" | string;
};

export type ScoringDimension = {
  key: string;
  label: string;
  weight: number;
  score: number;
  reason: string;
};

export type ScoringSummary = {
  pack: DecisionPack;
  framework: string;
  prompt: string;
  extracted_signals: string[];
  dimensions: ScoringDimension[];
  total_score: number;
  recommendation: string;
};

export type FeedbackChange = {
  section: string;
  before: string;
  after: string;
  reason: string;
};

export type BusinessCase = {
  id: string;
  title: string;
  company: string;
  year: number;
  scenario: string;
  pack: DecisionPack;
  tags: string[];
  budget: number;
  timeline: string;
  decision: string;
  outcome: string;
  lesson: string;
  source?: string;
};

export type MatchedBusinessCase = BusinessCase & {
  similarity: number;
};

export type DecisionReport = {
  report_id: string;
  created_at: string;
  pack: DecisionPack;
  executive_summary: string;
  decision_verdict: string;
  core_value: string[];
  benchmark: string[];
  risk_matrix: Array<{
    risk: string;
    likelihood: string;
    impact: string;
    mitigation: string;
  }>;
  execution_plan: string[];
  budget: string[];
  timeline: Array<{
    phase: string;
    window: string;
    output: string;
  }>;
  next_actions: string[];
  action_items: ActionItem[];
  scoring_summary: ScoringSummary;
  reference_cases: MatchedBusinessCase[];
  reasoning_timeline: Array<{
    label: string;
    focus: string;
    signal: string;
    status: string;
  }>;
};

export type MatchedCreator = {
  id: string;
  name: string;
  platform: string;
  tags: string[];
  followers: number;
  conversion_rate: number;
  match_score: number;
  score_reasons: string[];
  estimated_reach: number;
  estimated_conversions: number;
};

export type CreatorInput = {
  name: string;
  platform: string;
  tags: string[];
  followers: number;
  conversion_rate: number;
  avg_cpm: number;
  risk_flags: string[];
};

export type Creator = CreatorInput & {
  id: string;
};

export type ActorInput = {
  name: string;
  gender: string;
  age_range: string;
  location: string;
  image_tags: string[];
  role_tags: string[];
  genres: string[];
  fee_min: number;
  fee_max: number;
  schedule_status: string;
  followers: number;
  completion_rate: number;
  paid_conversion_rate: number;
  past_works: string[];
  risk_flags: string[];
};

export type Actor = ActorInput & {
  id: string;
};

export type AdminSummary = {
  creators: number;
  actors: number;
  reports: number;
  projects: number;
  logs: number;
  total_followers: number;
};

export type ReportFile = {
  id: string;
  filename: string;
  url: string;
  size_bytes: number;
  created_at: string;
};

export type LogEntry = {
  id: string;
  created_at: string;
  level: string;
  event: string;
  actor: string;
  message: string;
  metadata: Record<string, string | number | boolean | null>;
};

export type ProjectRecord = {
  id: string;
  report_id: string;
  kind: "brand" | "drama" | string;
  title: string;
  category: string;
  platforms: string[];
  budget: number;
  status: string;
  score?: number | null;
  pdf_url?: string | null;
  created_at: string;
  updated_at: string;
  report: Record<string, unknown>;
};

export type ScriptIdea = {
  creator_id: string;
  hook: string;
  structure: string[];
  cta: string;
};

export type CampaignReport = {
  report_id: string;
  brand: string;
  budget: number;
  goal: string;
  platform: string;
  creators: MatchedCreator[];
  scripts: ScriptIdea[];
  risk: {
    level: string;
    score: number;
    flags: string[];
    mitigations: string[];
  };
  roi: {
    estimated_reach: number;
    estimated_conversions: number;
    estimated_revenue: number;
    estimated_roi: number;
    cost_per_conversion: number;
    assumptions: string[];
  };
  pdf_url: string;
};

export type DramaProjectRequest = {
  title: string;
  genre: string;
  platform?: string;
  platforms: string[];
  budget: number;
  episodes: number;
  shooting_days: number;
  audience?: string;
  monetization: string;
  roles: string[];
  synopsis?: string;
};

export type MatchedActor = Actor & {
  role: string;
  match_score: number;
  score_reasons: string[];
  budget_fit: string;
  schedule_fit: string;
};

export type DramaReport = {
  report_id: string;
  title: string;
  genre: string;
  platform: string;
  platforms: string[];
  budget: number;
  roles: string[];
  actors: MatchedActor[];
  roi: {
    estimated_views: number;
    completion_rate: number;
    paid_conversion_rate: number;
    estimated_revenue: number;
    estimated_profit: number;
    estimated_roi: number;
    payback_days: string;
    assumptions: string[];
  };
  risk: {
    level: string;
    score: number;
    flags: string[];
    mitigations: string[];
  };
  story: {
    logline: string;
    core_conflict: string;
    relationship_hook: string;
    audience_promise: string;
    structure_suggestions: string[];
    characters: Array<{
      role: string;
      name: string;
      archetype: string;
      desire: string;
      conflict: string;
    }>;
    episode_outline: Array<{
      episode: number;
      title: string;
      hook: string;
      plot: string;
      cliffhanger: string;
      paid_point: boolean;
    }>;
    first_3_scripts: Array<{
      episode: number;
      title: string;
      scenes: string[];
      dialogue_beats: string[];
      cliffhanger: string;
    }>;
    first_10_scripts: Array<{
      episode: number;
      title: string;
      scenes: string[];
      dialogue_beats: string[];
      cliffhanger: string;
    }>;
    score: {
      hook: number;
      character: number;
      conflict: number;
      payoff: number;
      reversal: number;
      platform_fit: number;
      actor_fit: number;
      production_cost: number;
      compliance_risk: number;
      blockbuster_potential: number;
      overall: number;
      notes: string[];
    };
  };
  creative_package: {
    positioning: string;
    target_persona: string;
    paid_hook_strategy: string;
    title_templates: string[];
    cover_copy: string[];
    ab_test_angles: string[];
    platform_notes: string[];
    creatives: Array<{
      platform: string;
      angle: string;
      opening_hook: string;
      script: string[];
      cta: string;
    }>;
  };
  script_doctor: {
    structure: Array<{
      stage: string;
      episodes: string;
      purpose: string;
      must_have: string[];
    }>;
    content_optimizations: string[];
    revision_items: Array<{
      target: string;
      problem: string;
      suggestion: string;
      example: string;
    }>;
    dialogue_rewrites: string[];
    shootable_structure: string[];
  };
  commercial_pack: {
    benchmark_summary: string;
    benchmarks: Array<{
      title: string;
      genre_fit: string;
      selling_point: string;
      opening_hook: string;
      paid_hook: string;
      production_note: string;
    }>;
    paid_point_plan: Array<{
      episode: number;
      trigger: string;
      user_emotion: string;
      paywall_copy: string;
      next_episode_promise: string;
    }>;
    delivery_assets: Array<{
      name: string;
      format: string;
      audience: string;
      content: string[];
    }>;
    pitch_summary: string[];
    rollout_checklist: string[];
  };
  recommendations: string[];
  pdf_url: string;
  ppt_url?: string | null;
  docx_url?: string | null;
};

export type MaterialTestInput = {
  name: string;
  title: string;
  cover_copy: string;
  opening_hook: string;
  impressions: number;
  clicks: number;
  three_second_views: number;
  completions: number;
  paid_users: number;
  spend: number;
  revenue: number;
};

export type GrowthReviewRequest = {
  project_title: string;
  platform: string;
  episode: number;
  tests: MaterialTestInput[];
};

export type GrowthReviewReport = {
  project_title: string;
  platform: string;
  episode: number;
  winner?: string | null;
  overall_diagnosis: string[];
  test_results: Array<{
    name: string;
    ctr: number;
    three_second_rate: number;
    completion_rate: number;
    paid_rate: number;
    roi: number;
    status: string;
    diagnosis: string[];
    next_actions: string[];
  }>;
  next_round_plan: string[];
  rewrite_assistant: {
    summary: string;
    title_options: string[];
    cover_options: string[];
    opening_recuts: string[];
    paid_point_rewrites: string[];
    suggestions: Array<{
      category: string;
      target_problem: string;
      options: string[];
    }>;
  };
};

export type GrowthReviewRecord = {
  id: string;
  project_title: string;
  platform: string;
  episode: number;
  winner?: string | null;
  created_at: string;
  request: GrowthReviewRequest;
  report: GrowthReviewReport;
};

export type ProjectVersionSummary = {
  project_id: string;
  report_id: string;
  version_name: string;
  title: string;
  category: string;
  platforms: string[];
  budget: number;
  score?: number | null;
  pdf_url?: string | null;
  ppt_url?: string | null;
  docx_url?: string | null;
  created_at: string;
  updated_at: string;
};

export type ProjectWorkspaceGroup = {
  title: string;
  versions: ProjectVersionSummary[];
  reviews: GrowthReviewRecord[];
};

export type ProjectWorkspaceResponse = {
  groups: ProjectWorkspaceGroup[];
};
