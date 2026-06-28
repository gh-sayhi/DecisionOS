import type { DecisionPack, FollowUpQuestion } from "@/lib/types";

export const followUpTemplates: Record<DecisionPack, Omit<FollowUpQuestion, "answer">[]> = {
  Product: [
    {
      id: "target_user",
      question: "Who is the exact user segment this decision serves first?",
      context: "This clarifies adoption risk and product scope.",
      type: "textarea"
    },
    {
      id: "user_pain",
      question: "What pain is urgent enough that users would change behavior now?",
      context: "This separates real demand from nice-to-have features.",
      type: "textarea"
    },
    {
      id: "mvp_boundary",
      question: "What must be inside the first version, and what must stay out?",
      context: "This prevents scope expansion before evidence exists.",
      type: "textarea"
    },
    {
      id: "success_signal",
      question: "Which one metric proves the product decision is working?",
      context: "This creates a decision gate for launch or revision.",
      type: "text"
    }
  ],
  Startup: [
    {
      id: "wedge",
      question: "What is the smallest market wedge where you can win first?",
      context: "This checks whether the startup decision has a focused entry point.",
      type: "textarea"
    },
    {
      id: "unfair_advantage",
      question: "What advantage do you have that competitors cannot easily copy?",
      context: "This supports the founder-market and defensibility assessment.",
      type: "textarea"
    },
    {
      id: "runway_gate",
      question: "What proof must exist before spending the next major budget tranche?",
      context: "This aligns execution with runway and financing risk.",
      type: "textarea"
    }
  ],
  Marketing: [
    {
      id: "segment",
      question: "Which segment should receive the first marketing push?",
      context: "This avoids spreading budget across weak audiences.",
      type: "text"
    },
    {
      id: "message",
      question: "What message would make that segment act now?",
      context: "This checks message-market fit.",
      type: "textarea"
    },
    {
      id: "channel",
      question: "Which channel has the strongest evidence of conversion?",
      context: "This grounds the growth decision in measurable behavior.",
      type: "select",
      options: ["Owned", "Paid", "Partner", "Sales-led", "Community", "Other"]
    },
    {
      id: "pipeline_goal",
      question: "What pipeline or revenue result must this campaign produce?",
      context: "This connects the marketing decision to business impact.",
      type: "text"
    }
  ],
  Content: [
    {
      id: "audience",
      question: "Who is the most valuable audience for this content decision?",
      context: "This clarifies audience intent and distribution fit.",
      type: "textarea"
    },
    {
      id: "format",
      question: "Which format gives the best balance of quality, speed, and cost?",
      context: "This keeps the content decision operational rather than abstract.",
      type: "select",
      options: ["Article", "Video", "Newsletter", "Podcast", "Short-form", "Mixed"]
    },
    {
      id: "cadence",
      question: "What cadence can the team sustain without quality drop?",
      context: "This checks production feasibility.",
      type: "text"
    }
  ],
  Hiring: [
    {
      id: "capability_gap",
      question: "What capability gap is blocking the business outcome?",
      context: "This determines whether hiring is the right solution.",
      type: "textarea"
    },
    {
      id: "role_level",
      question: "What seniority level is truly required?",
      context: "This prevents over-hiring or under-scoping the role.",
      type: "select",
      options: ["IC", "Senior IC", "Manager", "Director", "Fractional", "Contractor"]
    },
    {
      id: "ramp_expectation",
      question: "What must this person deliver in the first 90 days?",
      context: "This creates a concrete hiring success gate.",
      type: "textarea"
    },
    {
      id: "alternative",
      question: "Can the gap be solved by redesigning work, contracting, or promoting internally?",
      context: "This compares hiring against lower-risk alternatives.",
      type: "textarea"
    }
  ],
  Investment: [
    {
      id: "investment_thesis",
      question: "What is the investment thesis in one sentence?",
      context: "This separates conviction from narrative.",
      type: "textarea"
    },
    {
      id: "downside",
      question: "What is the most credible downside case?",
      context: "This clarifies risk-adjusted return.",
      type: "textarea"
    },
    {
      id: "liquidity",
      question: "How would this decision affect liquidity or optionality?",
      context: "This checks capital flexibility.",
      type: "textarea"
    },
    {
      id: "exit_gate",
      question: "What condition would make you exit or stop funding this path?",
      context: "This defines loss control before commitment.",
      type: "textarea"
    }
  ],
  Custom: [
    {
      id: "decision_owner",
      question: "Who owns the final decision?",
      context: "This avoids unclear accountability.",
      type: "text"
    },
    {
      id: "irreversible_part",
      question: "Which part of the decision is hardest to reverse?",
      context: "This focuses the risk review.",
      type: "textarea"
    },
    {
      id: "proof_needed",
      question: "What evidence would change the recommendation?",
      context: "This creates a useful validation gate.",
      type: "textarea"
    }
  ]
};
