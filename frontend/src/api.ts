import type { QuizAnswers } from "./quiz";

const DEFAULT_PROD_API_URL = "https://gerador-de-certificado-3jia.onrender.com";

function resolveApiUrl() {
  const envUrl = import.meta.env.VITE_API_URL;
  if (envUrl) return envUrl;

  return DEFAULT_PROD_API_URL;
}

const API_URL = resolveApiUrl();

export async function issueCertificate(payload: { fullName: string; email: string; answers: QuizAnswers }) {
  let res: Response;
  try {
    res = await fetch(`${API_URL}/api/certificates/issue`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
  } catch {
    throw new Error("Erro de rede: verifique a ligação e tente novamente.");
  }

  const data = (await res.json()) as any;
  if (!res.ok) {
    const message =
      data?.error?.message ||
      (typeof data?.error === "string" ? data.error : null) ||
      "Não foi possível emitir o certificado.";
    const field = data?.field ? ` (${data.field})` : "";
    throw new Error(`${message}${field}`);
  }

  return data as { ok: true; certificateId: string };
}
