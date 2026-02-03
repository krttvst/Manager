import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getAgentSettings, updateAgentSettings } from "../api/agentSettings.js";
import { useAuth } from "../state/auth.jsx";

const TONE_TEMPLATE =
  "Я хочу составить подробное описание tone of voice для своей компании. Это описание будет использоваться, чтобы автоматически генерировать посты в Телеграм на основе статей и новостей из блога. Посты должны будут выглядеть так, как будто их написал собственный SMM-менеджер моей компании. Создай такое описание tone of voice на базе постов моей компании в Телеграм. Первый пост: [вставьте ваши данные]. Второй пост: [вставьте ваши данные]. Третий пост: [вставьте ваши данные].";

const STYLE_OPTIONS = [
  "формальный",
  "неформальный",
  "убедительный",
  "описательный",
  "научный",
  "повествовательный"
];

const FORMAT_OPTIONS = ["статья", "рецепт", "обзор", "гид", "интервью", "новости", "анализ"];

function buildToneText(values) {
  let idx = 0;
  return TONE_TEMPLATE.replace(/\[[^\]]*]/g, () => `[${values[idx++] || "вставьте ваши данные"}]`);
}

function extractBracketValues(text) {
  const matches = text.match(/\[[^\]]*]/g);
  return matches ? matches.map((m) => m.slice(1, -1)) : [];
}

function isTemplateCompatible(text) {
  const stripped = text.replace(/\[[^\]]*]/g, "[]");
  const templateStripped = TONE_TEMPLATE.replace(/\[[^\]]*]/g, "[]");
  return stripped === templateStripped;
}

export default function AgentSettings() {
  const { id } = useParams();
  const { token } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [length, setLength] = useState(400);
  const [style, setStyle] = useState("формальный");
  const [format, setFormat] = useState("статья");
  const [temperature, setTemperature] = useState(0.4);
  const [extra, setExtra] = useState("");
  const [toneValues, setToneValues] = useState([
    "вставьте ваши данные",
    "вставьте ваши данные",
    "вставьте ваши данные"
  ]);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);

  const settingsQuery = useQuery({
    queryKey: ["agent-settings", { channelId: id }],
    queryFn: () => getAgentSettings(token, id),
    enabled: Boolean(token && id)
  });

  useEffect(() => {
    if (!settingsQuery.data) return;
    const data = settingsQuery.data;
    setLength(data.length ?? 400);
    setStyle(data.style ?? "формальный");
    setFormat(data.format ?? "статья");
    setTemperature(data.temperature ?? 0.4);
    setExtra(data.extra ?? "");
    setToneValues(data.tone_values ?? ["вставьте ваши данные", "вставьте ваши данные", "вставьте ваши данные"]);
  }, [settingsQuery.data]);

  const saveMutation = useMutation({
    mutationFn: (payload) => updateAgentSettings(token, id, payload),
    onSuccess: (data) => {
      queryClient.setQueryData(["agent-settings", { channelId: id }], data);
      if (data) {
        setLength(data.length ?? 400);
        setStyle(data.style ?? "формальный");
        setFormat(data.format ?? "статья");
        setTemperature(data.temperature ?? 0.4);
        setExtra(data.extra ?? "");
        setToneValues(
          data.tone_values ?? ["вставьте ваши данные", "вставьте ваши данные", "вставьте ваши данные"]
        );
      }
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    },
    onError: (err) => setError(err.message)
  });

  const toneText = useMemo(() => buildToneText(toneValues), [toneValues]);

  function handleToneChange(event) {
    const next = event.target.value;
    if (!isTemplateCompatible(next)) return;
    const values = extractBracketValues(next);
    setToneValues(values.length ? values : toneValues);
  }

  async function handleSave() {
    setError("");
    await saveMutation.mutateAsync({
      length,
      style,
      format,
      temperature,
      extra,
      tone_text: toneText,
      tone_values: toneValues
    });
  }

  return (
    <section className="agent-settings-page">
      <div className="page-header">
        <div>
          <h1>Настройка агента</h1>
          <p className="muted">Сохраняйте параметры для генерации предложений и контента.</p>
        </div>
        <button className="ghost-dark" onClick={() => navigate(-1)}>
          Назад
        </button>
      </div>

      <div className="panel modal-wide modal-comfort">
        <div className="form-grid">
          <div className="form-card">
            <div className="form-card-title">Длина текста</div>
            <input
              type="range"
              min={100}
              max={4000}
              value={length}
              onChange={(e) => setLength(Number(e.target.value))}
            />
            <div className="hint">{length} символов</div>
          </div>

          <div className="form-card">
            <div className="form-card-title">Температура</div>
            <input
              type="range"
              min={0}
              max={1}
              step={0.01}
              value={temperature}
              onChange={(e) => setTemperature(Number(e.target.value))}
            />
            <div className="hint">От предсказуемости к разнообразию</div>
          </div>

          <div className="form-card">
            <div className="form-card-title">Стиль письма</div>
            <select value={style} onChange={(e) => setStyle(e.target.value)}>
              {STYLE_OPTIONS.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>

          <div className="form-card">
            <div className="form-card-title">Формат контента</div>
            <select value={format} onChange={(e) => setFormat(e.target.value)}>
              {FORMAT_OPTIONS.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="modal-form">
          <label>
            Дополнительно
            <textarea
              rows={4}
              value={extra}
              onChange={(e) => setExtra(e.target.value)}
              placeholder="Промпты, инструкции и т.д."
            />
          </label>

          <label>
            Настройка Tone Of Voice
            <textarea rows={6} value={toneText} onChange={handleToneChange} />
            <div className="hint">Можно редактировать только слова в квадратных скобках.</div>
          </label>

          <div className="placeholder-card">
            <div className="label">База знаний</div>
            <div className="muted">Раздел в разработке.</div>
          </div>
        </div>
      </div>

      {error && <div className="error">{error}</div>}
      {saved && <div className="hint">Настройки сохранены.</div>}

      <div className="actions">
        <button className="primary" onClick={handleSave} disabled={saveMutation.isPending}>
          {saveMutation.isPending ? "Сохранение..." : "Сохранить"}
        </button>
      </div>
    </section>
  );
}
