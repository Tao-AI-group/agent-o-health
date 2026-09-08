export type Status = "present" | "partial" | "missing" | "not_applicable";

export interface Message {
  id: string;
  role: "assistant" | "user";
  content: string;
  status: string;
  created_at: string;
}

export interface Requirement {
  id: string;
  section: string;
  label: string;
  status: Status;
  required: boolean;
  source: string;
  question: string;
  ontology_term: string;
  value: string | null;
  confidence: number | null;
  review_state: string | null;
  applicability_reason: string | null;
}

export interface Section {
  id: string;
  label: string;
  description: string;
  order: number;
  status: Status;
  counts: Record<string, number>;
  total: number;
}

export interface Completeness {
  requirements: Requirement[];
  sections: Section[];
  dimensions: Array<{ id: string; label: string; weight: number; fraction: number | null; score: number | null }>;
  reporting_completeness_score: number | null;
  score_interpretation: string;
  shacl_conformance: "conformant" | "non_conformant" | "not_yet_validated";
  review_readiness: string;
  unresolved_required_count: number;
  conflict_count: number;
}

export interface Assertion {
  id: string;
  field_id: string;
  predicate_uri: string;
  value: string;
  source_message_id: string | null;
  source_evidence: string;
  confidence: number;
  review_state: string;
  user_confirmed: boolean;
  subject: { id: string; label: string; type_uri: string } | null;
  object_entity: { id: string; label: string; type_uri: string } | null;
}

export interface CardSession {
  id: string;
  name: string;
  intake_mode: string;
  status: string;
  profile: { id: string; uri: string; version: string };
  ontology_snapshot_id: string;
  ontology_snapshot_current: boolean;
  review_readiness: string;
  created_at: string;
  updated_at: string;
  current_question: { id: string; label: string; question: string } | null;
  completeness_summary: { score: number | null; unresolved_required_count: number; shacl_conformance: string };
  messages?: Message[];
  assertions?: Assertion[];
  completeness?: Completeness;
}

export interface ValidationResult {
  id?: string;
  conforms: boolean;
  data_triples: number;
  summary: Record<string, number>;
  results: Array<{ severity: string; focus_node: string; path: string; value: string; message: string; source_shape: string }>;
}
