import type { BusinessCase } from "@/lib/types";

export const businessCases: BusinessCase[] = [
  {
    id: "product-notion-ai",
    title: "Notion AI launch",
    company: "Notion",
    year: 2023,
    scenario: "Embedded AI workflows inside an existing workspace.",
    pack: "Product",
    tags: ["ai", "workspace", "productivity", "activation", "collaboration"],
    budget: 300000,
    timeline: "6 months",
    decision: "Add AI as a native workflow layer.",
    outcome: "Strengthened retention and monetization.",
    lesson: "AI features work best when they reduce friction in an already frequent workflow."
  },
  {
    id: "startup-dropbox-mvp",
    title: "Dropbox MVP cold start",
    company: "Dropbox",
    year: 2007,
    scenario: "Validated file sync demand before full product build.",
    pack: "Startup",
    tags: ["mvp", "cold-start", "video", "validation", "demand"],
    budget: 50000,
    timeline: "3 months",
    decision: "Use a demo video to prove demand.",
    outcome: "Waitlist demand validated the thesis.",
    lesson: "Demand can be tested with a clear artifact before heavy build-out."
  },
  {
    id: "marketing-dollar-shave-club",
    title: "Dollar Shave Club viral launch",
    company: "Dollar Shave Club",
    year: 2012,
    scenario: "Used a sharp launch video to create DTC demand.",
    pack: "Marketing",
    tags: ["viral", "dtc", "video", "subscription", "brand"],
    budget: 4500,
    timeline: "1 month",
    decision: "Use humor and a direct value proposition.",
    outcome: "Generated massive awareness and subscriptions.",
    lesson: "A clear wedge and memorable creative can outperform large media spend."
  }
];
