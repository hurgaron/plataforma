console.log("[CUSTOS] script carregado");

export async function carregarCustos(atid) {
  console.log("[CUSTOS] carregando custos para atid:", atid);
  const container = document.getElementById("lista-custos");
  container.innerHTML = `<div class='text-sm text-gray-500 animate-pulse'>🔄 Carregando custos...</div>`;

  try {
    const response = await fetch(`/calendario/${atid}/custos`);
    const html = await response.text();
    container.innerHTML = html;
    console.log("[CUSTOS] HTML carregado com sucesso");
    configurarFormularioCustos();
  } catch (error) {
    console.error("[CUSTOS] Erro ao carregar custos", error);
    container.innerHTML = `<p class='text-sm text-red-500'>❌ Erro ao carregar custos.</p>`;
  }
}

export function configurarFormularioCustos() {
  console.log("[CUSTOS] configurando listeners do formulário de custo...");
  const form = document.getElementById("form-custo");
  const botaoAntigo = form.querySelector("button[type='submit']");

  // Clona o botão e substitui o antigo para remover listeners antigos
  const botao = botaoAntigo.cloneNode(true);
  botaoAntigo.replaceWith(botao);

  botao.addEventListener("click", async (e) => {
    e.preventDefault();
    console.log("[CUSTOS] clique no botão adicionar");

    const atid = document.querySelector("[name='atid']").value;
    const formData = new FormData(form);

    const id = formData.get("id");
    const url = id
      ? `/calendario/custos/${id}/atualizar`
      : `/calendario/${atid}/custos/adicionar`;

    const textoOriginal = botao.innerHTML;
    botao.innerHTML = "⏳ Salvando...";
    botao.disabled = true;

    const response = await fetch(url, {
      method: "POST",
      body: formData
    });

    botao.disabled = false;
    botao.innerHTML = textoOriginal;

    if (response.ok) {
      form.reset();
      const campoId = form.querySelector("[name='id']");
      if (campoId) campoId.remove();
      botao.textContent = "Adicionar";
      carregarCustos(atid);
    } else {
      alert("Erro ao salvar custo.");
    }
  });
}


export async function editarCusto(id) {
  console.log("[CUSTOS] editando custo", id);
  try {
    const response = await fetch(`/calendario/custos/${id}/editar`);
    const custo = await response.json();

    const form = document.getElementById("form-custo");
    form.querySelector("[name='descricao']").value = custo.descricao;
    form.querySelector("[name='quantidade']").value = custo.quantidade;
    form.querySelector("[name='valor_unitario']").value = custo.valor_unitario;
    form.querySelector("[name='tipo_lancamento']").value = custo.tipo_lancamento;
    form.querySelector("[name='tipo']").value = custo.tipo || "";

    let campoId = form.querySelector("[name='id']");
    if (!campoId) {
      campoId = document.createElement("input");
      campoId.type = "hidden";
      campoId.name = "id";
      form.appendChild(campoId);
    }
    campoId.value = custo.id;

    const botao = form.querySelector("button[type='submit']");
    botao.textContent = "Salvar Alterações";
  } catch (error) {
    console.error("Erro ao carregar custo para edição", error);
  }
}

window.editarCusto = editarCusto;
window.removerCusto = async function (id) {
  if (!confirm("Deseja remover este custo?")) return;
  try {
    await fetch(`/calendario/custos/${id}/remover`, { method: "POST" });
    const atid = document.querySelector("[name='atid']")?.value;
    if (atid) carregarCustos(atid);
  } catch (error) {
    alert("Erro ao remover custo.");
  }
};

window.carregarCustos = carregarCustos;
