// static/js/modal_atividade.js

import { configurarFormularioCustos } from "./custos.js";
import { configurarFormularioReceitas } from "./receitas.js";
import { configurarFormularioParticipantes } from "./participantes.js";

function abrirModalNovaAtividade(data) {
  fetch(`/calendario/nova?data=${data}`)
    .then(res => res.text())
    .then(html => {
      document.getElementById("modal-atividade-container").innerHTML = html;
      document.getElementById("modal-atividade").showModal();
      iniciarListenersForm();
      configurarTabsModal();
    });
}

function carregarAtividade(id) {
  fetch(`/calendario/${id}/editar`)
    .then(res => res.text())
    .then(html => {
      document.getElementById("modal-atividade-container").innerHTML = html;
      document.getElementById("modal-atividade").showModal();
      iniciarListenersForm();
      configurarTabsModal();
    });
}

function iniciarListenersForm() {
  const form = document.getElementById("form-atividade");
  if (!form) return;

  form.addEventListener("submit", async function (e) {
    e.preventDefault();
    const formData = new FormData(form);

    const response = await fetch(form.action, {
      method: "POST",
      body: formData
    });

    const result = await response.json();
    if (result.sucesso) {
      document.getElementById("modal-atividade").close();
      const calendar = window.calendar;
      if (calendar) calendar.refetchEvents();
    } else {
      alert("Erro ao salvar atividade");
    }
  });

  const btnExcluir = document.getElementById("btn-excluir");
  if (btnExcluir) {
    btnExcluir.addEventListener("click", async () => {
      const atid = form.querySelector("[name='atid']").value;
      if (confirm("Deseja realmente excluir esta atividade?")) {
        await fetch(`/calendario/${atid}/excluir`, { method: "POST" });
        document.getElementById("modal-atividade").close();
        const calendar = window.calendar;
        if (calendar) calendar.refetchEvents();
      }
    });
  }
}

export function configurarTabsModal() {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const tab = btn.dataset.tab;
      console.log("Tab clicada:", tab);
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('text-[#8B1E3F]', 'border-[#8B1E3F]'));
      btn.classList.add('text-[#8B1E3F]', 'border-[#8B1E3F]');
      document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
      document.getElementById(`tab-${tab}`).classList.remove('hidden');

      const atid = document.querySelector("[name='atid']")?.value;
      console.log("Atividade ID:", atid);

      if (tab === "participantes" && atid) carregarParticipantes(atid);
      if (tab === "custos" && atid) carregarCustos(atid);
      if (tab === "receitas" && atid) carregarReceitas(atid);
    });
  });

  configurarFormularioParticipantes();
  configurarFormularioCustos();
  configurarFormularioReceitas();
}

window.abrirModalNovaAtividade = abrirModalNovaAtividade;
window.carregarAtividade = carregarAtividade;
window.configurarTabsModal = configurarTabsModal;
