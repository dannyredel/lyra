import React, { useState, useEffect } from "react";
import { Sidebar, DemoBanner } from "./ui.jsx";
import Home from "./Home.jsx";
import StudyCase from "./StudyCase.jsx";
import Registry from "./Registry.jsx";
import Scorecard from "./Scorecard.jsx";
import NewExperiment from "./NewExperiment.jsx";
import Metrics from "./Metrics.jsx";
import Decisions from "./Decisions.jsx";
import Health from "./Health.jsx";
import { api } from "./api.js";

export default function ChassisApp() {
  const [mode, setMode] = useState(null);
  const [data, setData] = useState(null);
  const [section, setSection] = useState("home");
  const [selected, setSelected] = useState(null);
  const [liveDetail, setLiveDetail] = useState(null);
  const [creating, setCreating] = useState(false);
  const [createTemplate, setCreateTemplate] = useState(null);
  const [selectedCase, setSelectedCase] = useState(null);
  const [bannerOff, setBannerOff] = useState(false);

  const withTimeout = (p, ms) =>
    Promise.race([p, new Promise((_, rej) => setTimeout(() => rej(new Error("timeout")), ms))]);

  const loadList = async () => {
    try {
      const r = await withTimeout(api.list(), 15000);
      setMode("live");
      setData({ experiments: r.experiments, meta: { ...r.meta, fdr: r.fdr } });
    } catch {
      const s = await fetch(import.meta.env.BASE_URL + "data/chassis.json").then((x) => x.json());
      setMode("static");
      setData({ experiments: s.experiments, meta: s.meta, scorecards: s.scorecards });
    }
  };
  useEffect(() => { loadList(); }, []);

  const nav = (key) => {
    setSection(key); setSelected(null); setLiveDetail(null); setCreating(false);
    setCreateTemplate(null); setSelectedCase(null);
  };

  const open = async (id) => {
    setSection("experiments"); setCreating(false); setSelectedCase(null); setSelected(id); setLiveDetail(null);
    if (mode === "live") { try { setLiveDetail(await api.get(id)); } catch {} }
  };

  const startCreate = (template = null) => {
    setSection("experiments"); setSelectedCase(null); setSelected(null);
    setCreateTemplate(template); setCreating(true);
  };

  const onCreate = async (spec) => {
    if (mode === "live") {
      const created = await api.create(spec); await loadList(); setCreating(false); setCreateTemplate(null); open(created.id);
    } else {
      setData({ ...data, experiments: [spec.__row, ...data.experiments] });
      setCreating(false); setCreateTemplate(null); setSelected(spec.__row.id);
    }
  };

  const onTransition = async (id, to_state, extra) => {
    if (mode !== "live") return;
    await api.transition(id, to_state, extra); await loadList(); open(id);
  };

  if (!data) {
    return (
      <div className="app">
        <Sidebar section="home" onNav={() => {}} />
        <main className="main">
          <div className="skel" style={{ height: 168, borderRadius: 18, marginBottom: 30 }} />
          <div className="case-grid">{Array.from({ length: 6 }, (_, i) => <div key={i} className="skel" style={{ height: 178 }} />)}</div>
        </main>
      </div>
    );
  }

  const row = selected && data.experiments.find((e) => e.id === selected);
  const detail = !row ? null
    : mode === "live" ? (liveDetail && liveDetail.id === selected ? { ...row, ...liveDetail } : row)
    : (data.scorecards?.[selected] ? { ...row, ...data.scorecards[selected] } : row);

  let content;
  if (section === "home") {
    content = selectedCase
      ? <StudyCase id={selectedCase} onBack={() => setSelectedCase(null)} onViewLive={open} onCreate={startCreate} />
      : <Home experiments={data.experiments} onOpenCase={setSelectedCase} onNew={() => startCreate()} />;
  } else if (section === "experiments") {
    content = creating
      ? <NewExperiment mode={mode} template={createTemplate} onBack={() => nav("experiments")} onCreate={onCreate} />
      : detail
        ? <Scorecard data={detail} mode={mode} onBack={() => nav("experiments")} onTransition={(to, extra) => onTransition(selected, to, extra)} />
        : <Registry experiments={data.experiments} meta={data.meta} onSelect={open} onNew={() => startCreate()} />;
  } else if (section === "metrics") {
    content = <Metrics experiments={data.experiments} />;
  } else if (section === "decisions") {
    content = <Decisions experiments={data.experiments} onSelect={open} />;
  } else {
    content = <Health experiments={data.experiments} />;
  }

  return (
    <div className="app">
      <Sidebar section={section} onNav={nav} mode={mode} />
      <main className="main">
        {mode === "static" && !bannerOff && section !== "home" && <DemoBanner onClose={() => setBannerOff(true)} />}
        {content}
      </main>
    </div>
  );
}
