export type QuizAnswers = {
  orador: string;
  moderador: string;
  parceiros: string[];
  tema: string;
};

export const PARTNERS = ["TI360", "NexMind", "LinkUp"] as const;

export const DEFAULT_ANSWERS: QuizAnswers = {
  orador: "",
  moderador: "",
  parceiros: [],
  tema: ""
};

