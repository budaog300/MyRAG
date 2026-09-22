import type { LucideIcon } from 'lucide-react';

export type NavItem = {
  id: string;
  label: string;
};

export type Capability = {
  id: string;
  icon: LucideIcon;
  title: string;
  description: string;
};

export type DocumentFormat = {
  id: string;
  extension: string;
  name: string;
  description: string;
};

export type ProcessStep = {
  id: string;
  title: string;
  description: string;
};

export type Scenario = {
  id: string;
  icon: LucideIcon;
  title: string;
  description: string;
  exampleQuestion: string;
};

export type ArchitectureNode = {
  id: string;
  icon: LucideIcon;
  title: string;
  short: string;
  description: string;
};

export type PilotStep = {
  id: string;
  title: string;
  description: string;
};

export type FaqItem = {
  id: string;
  question: string;
  answer: string;
};
