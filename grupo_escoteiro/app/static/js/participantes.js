// static/js/participantes.js

export async function carregarParticipantes(atid) {
  const container = document.getElementById("lista-participantes");
  container.innerHTML = `<div class='text-sm text-gray-500 animate-pulse'>🔄 Carregando participantes...</div>`;

  try {
    const response = await fetch(`/calendario/${atid}/participantes`);
    const html = await response.text();
    container.innerHTML = html;
  } catch (error) {
    container.innerHTML = `<p class='text-sm text-red-500'>❌ Erro ao carregar participantes.</p>`;
  }
}

export function configurarFormularioParticipantes() {
  const form = document.getElementById("form-participante");
  const tipoSelect = document.getElementById("tipo-participante");
  const pessoaSelect = document.getElementById("pessoa-participante");
  const atid = document.querySelector("[name='atid']")?.value;

  if (!form || !tipoSelect || !pessoaSelect || !atid) return;

  tipoSelect.addEventListener("change", async () => {
    const tipo = tipoSelect.value;
    try {
      const response = await fetch(`/api/${tipo}s/lista`);
      const pessoas = await response.json();

      pessoaSelect.innerHTML = "<option value=''>Selecione</option>";
      const lista = document.getElementById("lista-pessoas");
      lista.innerHTML = "";

      if (Array.isArray(pessoas)) {
        pessoas.forEach(p => {
          const option = document.createElement("option");
          option.value = p.nome;
          option.dataset.id = p.id;
          lista.appendChild(option);
        });
      }
    } catch (error) {
      console.error("Erro ao carregar pessoas:", error);
    }
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(form);
    const botao = form.querySelector("button[type='submit']");
    const textoOriginal = botao.innerHTML;
    botao.disabled = true;
    botao.innerHTML = "⏳ Salvando...";

    const id = formData.get("id");
    const url = id
      ? `/calendario/participantes/${id}/atualizar`
      : `/calendario/${atid}/participantes/adicionar`;

    const response = await fetch(url, {
      method: "POST",
      body: formData
    });

    botao.disabled = false;
    botao.innerHTML = textoOriginal;

    if (response.ok) {
      form.reset();
      document.getElementById("participante-id").value = "";
      botao.textContent = "Adicionar";
      carregarParticipantes(atid);
    } else {
      alert("Erro ao salvar participante.");
    }
  });
}

export async function editarParticipante(id) {
  try {
    const response = await fetch(`/calendario/participantes/${id}/editar`);
    const p = await response.json();

    document.getElementById("tipo-participante").value = p.tipo;
    await carregarPessoasPorTipo(p.tipo, p.pessoa_id, p.nome);

    document.getElementById("participante-id").value = p.id;
    const btn = document.querySelector("#form-participante button[type='submit']");
    btn.textContent = "Salvar Alterações";
  } catch (err) {
    alert("Erro ao carregar participante para edição.");
  }
}

async function carregarPessoasPorTipo(tipo, pessoa_id, nome) {
  const pessoaSelect = document.getElementById("pessoa-participante");
  const lista = document.getElementById("lista-pessoas");

  lista.innerHTML = "";
  const option = document.createElement("option");
  option.value = nome;
  lista.appendChild(option);

  pessoaSelect.value = nome;
  document.getElementById("pessoa-id").value = pessoa_id;
}

export async function removerParticipante(id) {
  if (!confirm("Deseja remover este participante?")) return;
  const atid = document.querySelector("[name='atid']")?.value;
  try {
    await fetch(`/calendario/participantes/${id}/remover`, { method: "POST" });
    if (atid) carregarParticipantes(atid);
  } catch (error) {
    alert("Erro ao remover participante.");
  }
}

window.carregarParticipantes = carregarParticipantes;
window.editarParticipante = editarParticipante;
