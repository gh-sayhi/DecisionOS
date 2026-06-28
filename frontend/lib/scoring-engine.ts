import type { DecisionPack } from "@/lib/types";

export type ScoringDimensionConfig = {
  key: string;
  label: string;
  weight: number;
};

export type PackScoringModel = {
  framework: string;
  prompt: string;
  dimensions: ScoringDimensionConfig[];
};

export const packScoringModels: Record<DecisionPack, PackScoringModel> = {
  Product: {
    framework: "RICE",
    prompt:
      "Extract user reach, expected impact, evidence confidence, and execution effort. Score each dimension from 0-100, then calculate the weighted RICE decision score.",
    dimensions: [
      { key: "reach", label: "Reach", weight: 0.3 },
      { key: "impact", label: "Impact", weight: 0.3 },
      { key: "confidence", label: "Confidence", weight: 0.2 },
      { key: "effort", label: "Effort", weight: 0.2 }
    ]
  },
  Startup: {
    framework: "Startup Entry Score",
    prompt:
      "Extract market size, problem fit, team fit, timing, and funding readiness. Score each dimension from 0-100, then calculate the weighted startup decision score.",
    dimensions: [
      { key: "market_size", label: "Market Size", weight: 0.25 },
      { key: "problem_fit", label: "Problem Fit", weight: 0.25 },
      { key: "team_fit", label: "Team Fit", weight: 0.2 },
      { key: "timing", label: "Timing", weight: 0.15 },
      { key: "funding", label: "Funding", weight: 0.15 }
    ]
  },
  Marketing: {
    framework: "Growth Allocation Score",
    prompt:
      "Extract channel ROI, audience fit, brand awareness lift, and budget efficiency. Score each dimension from 0-100, then calculate the weighted marketing decision score.",
    dimensions: [
      { key: "channel_roi", label: "Channel ROI", weight: 0.35 },
      { key: "audience_fit", label: "Audience Fit", weight: 0.3 },
      { key: "brand_awareness", label: "Brand Awareness", weight: 0.15 },
      { key: "budget_efficiency", label: "Budget Efficiency", weight: 0.2 }
    ]
  },
  Content: {
    framework: "Content Decision Score",
    prompt:
      "Extract audience intent, format fit, distribution leverage, and production feasibility. Score each dimension from 0-100, then calculate the weighted content decision score.",
    dimensions: [
      { key: "audience_intent", label: "Audience Intent", weight: 0.3 },
      { key: "format_fit", label: "Format Fit", weight: 0.25 },
      { key: "distribution", label: "Distribution", weight: 0.25 },
      { key: "production_feasibility", label: "Production Feasibility", weight: 0.2 }
    ]
  },
  Hiring: {
    framework: "Hiring Decision Score",
    prompt:
      "Extract role urgency, budget fit, market salary pressure, and team capability gap. Score each dimension from 0-100, then calculate the weighted hiring decision score.",
    dimensions: [
      { key: "urgency", label: "Urgency", weight: 0.3 },
      { key: "budget_fit", label: "Budget Fit", weight: 0.25 },
      { key: "market_salary", label: "Market Salary", weight: 0.2 },
      { key: "team_gap", label: "Team Gap", weight: 0.25 }
    ]
  },
  Investment: {
    framework: "Investment Committee Score",
    prompt:
      "Extract risk-return profile, exit probability, market timing, and team quality. Score each dimension from 0-100, then calculate the weighted investment decision score.",
    dimensions: [
      { key: "risk_return", label: "Risk Return", weight: 0.35 },
      { key: "exit_probability", label: "Exit Probability", weight: 0.25 },
      { key: "market_timing", label: "Market Timing", weight: 0.2 },
      { key: "team_quality", label: "Team Quality", weight: 0.2 }
    ]
  },
  Custom: {
    framework: "Strategic Decision Score",
    prompt:
      "Extract strategic fit, evidence quality, reversibility, and execution readiness. Score each dimension from 0-100, then calculate the weighted custom decision score.",
    dimensions: [
      { key: "strategic_fit", label: "Strategic Fit", weight: 0.3 },
      { key: "evidence_quality", label: "Evidence Quality", weight: 0.25 },
      { key: "reversibility", label: "Reversibility", weight: 0.2 },
      { key: "execution_readiness", label: "Execution Readiness", weight: 0.25 }
    ]
  }
};
