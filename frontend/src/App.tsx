import { useMemo, useState } from "react";
import { DEFAULT_ANSWERS, PARTNERS, type QuizAnswers } from "./quiz";
import { issueCertificate } from "./api";

type Step = "gate" | "quiz" | "form" | "done";

export function App() {
  const [step, setStep] = useState<Step>("gate");
  const [answers, setAnswers] = useState<QuizAnswers>(DEFAULT_ANSWERS);
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [certificateId, setCertificateId] = useState<string | null>(null);

  const stepLabel = useMemo(() => {
    if (step === "gate") return "Início";
    if (step === "quiz") return "1/2 • Perguntas";
    if (step === "form") return "2/2 • Dados";
    return "Concluído";
  }, [step]);

  function togglePartner(partner: string) {
    setAnswers((prev) => {
      const exists = prev.parceiros.includes(partner);
      return {
        ...prev,
        parceiros: exists ? prev.parceiros.filter((p) => p !== partner) : [...prev.parceiros, partner]
      };
    });
  }

  async function onNextFromQuiz(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (!answers.orador.trim() || !answers.moderador.trim() || !answers.tema.trim()) {
      setError("Preencha todas as respostas.");
      return;
    }
    if (answers.parceiros.length !== PARTNERS.length) {
      setError("Selecione todos os parceiros da PADE.");
      return;
    }

    setStep("form");
  }

  async function onIssue(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      const result = await issueCertificate({ fullName, email, answers });
      setCertificateId(result.certificateId);
      setStep("done");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro inesperado.");
    } finally {
      setBusy(false);
    }
  }

  function reset() {
    setStep("gate");
    setAnswers(DEFAULT_ANSWERS);
    setFullName("");
    setEmail("");
    setError(null);
    setBusy(false);
    setCertificateId(null);
  }

  return (
    <div className="container">
      <div className="header">
        <div className="brand">
          <h1>PADE • Emissão de Certificados</h1>
          <p>Responda às perguntas e receba o certificado por email.</p>
        </div>
        <div className="step">
          <span className="pill" />
          {stepLabel}
        </div>
      </div>

      <div className="card">
        {step === "gate" && (
          <div className="landing">
            <div className="landingGrid">
              <div className="landingCopy">
                <div className="kicker">Certificado de participação</div>
                <h2 className="landingTitle">Obtenha o seu certificado em minutos</h2>
                <p className="landingLead">
                  Responda às perguntas de validação, informe o seu nome completo e receba o PDF no seu email.
                </p>

                <div className="landingSteps">
                  <div className="stepCard">
                    <div className="stepNum">1</div>
                    <div>
                      <div className="stepHead">Validar participação</div>
                      <div className="stepSub">4 perguntas rápidas</div>
                    </div>
                  </div>
                  <div className="stepCard">
                    <div className="stepNum">2</div>
                    <div>
                      <div className="stepHead">Dados do certificado</div>
                      <div className="stepSub">Nome + email</div>
                    </div>
                  </div>
                  <div className="stepCard">
                    <div className="stepNum">3</div>
                    <div>
                      <div className="stepHead">Envio automático</div>
                      <div className="stepSub">PDF direto no Gmail</div>
                    </div>
                  </div>
                </div>

                <div className="actions actionsCenter">
                  <button className="primary ctaButton" type="button" onClick={() => setStep("quiz")}>
                    Obter certificado
                  </button>
                </div>

                <div className="finePrint">Se não receber o email, verifique a pasta de spam.</div>
              </div>
            </div>
          </div>
        )}

        {step === "quiz" && (
          <form onSubmit={onNextFromQuiz} className="row">
            <div className="sectionHead">
              <h2>Perguntas de validação</h2>
              <p>Os dados abaixo devem bater com o que você viu na actividade.</p>
            </div>
            <div>
              <label>1) Quem foi o Orador principal?</label>
              <input value={answers.orador} onChange={(e) => setAnswers({ ...answers, orador: e.target.value })} type="text" />
            </div>

            <div>
              <label>2) Quem foi o moderador da actividade?</label>
              <input value={answers.moderador} onChange={(e) => setAnswers({ ...answers, moderador: e.target.value })} type="text" />
            </div>

            <div>
              <label>3) Quais são os parceiros da PADE? (múltiplas escolhas)</label>
              <div className="choices">
                {PARTNERS.map((partner) => (
                  <label key={partner} className="choice">
                    <input
                      type="checkbox"
                      checked={answers.parceiros.includes(partner)}
                      onChange={() => togglePartner(partner)}
                    />
                    {partner}
                  </label>
                ))}
              </div>
            </div>

            <div>
              <label>4) Qual foi o tema da actividade?</label>
              <textarea value={answers.tema} onChange={(e) => setAnswers({ ...answers, tema: e.target.value })} />
            </div>

            <div className="actions actionsSplit">
              <button className="primary" type="submit">
                Continuar
              </button>
              <button className="secondary" type="button" onClick={() => setStep("gate")}>
                Voltar
              </button>
            </div>

            {error && <div className="error">{error}</div>}
          </form>
        )}

        {step === "form" && (
          <form onSubmit={onIssue} className="row">
            <div>
              <label>Nome completo (como deve aparecer no certificado)</label>
              <input value={fullName} onChange={(e) => setFullName(e.target.value)} type="text" />
            </div>

            <div>
              <label>Email (Gmail recomendado para testes)</label>
              <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" />
            </div>

            <div className="actions">
              <button type="button" onClick={() => setStep("quiz")} disabled={busy}>
                Voltar
              </button>
              <button className="primary" type="submit" disabled={busy}>
                {busy ? "A enviar..." : "Emitir e enviar"}
              </button>
            </div>

            {error && <div className="error">{error}</div>}
          </form>
        )}

        {step === "done" && (
          <div className="row">
            <div>
              <h2 style={{ margin: 0, fontSize: 18 }}>Certificado enviado</h2>
              <p style={{ margin: "8px 0 0", color: "var(--muted)" }}>
                Verifique a sua caixa de entrada (e spam). Código: <strong>{certificateId}</strong>
              </p>
            </div>
            <div className="actions">
              <button className="primary" type="button" onClick={reset}>
                Emitir outro
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
