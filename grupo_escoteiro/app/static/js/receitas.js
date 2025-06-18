// static/js/receitas.js

console.log("[RECEITAS] script carregado");

export function configurarFormularioReceitas() {
  console.log("[RECEITAS] configurando listeners do formulário de receita...");

  const form = document.getElementById("form-receita");
  if (!form) return;

  const btn = form.querySelector("button[type='submit']");
  btn.addEventListener("click", async (e) => {
    e.preventDefault();
    console.log("[RECEITAS] clique no botão adicionar/editar");

    const formData = new FormData(form);
    const atid = document.querySelector("[name='atid']")?.value;
    const receitaId = formData.get("id");

    const url = receitaId
      ? `/calendario/receitas/${receitaId}/atualizar`
      : `/calendario/${atid}/receitas/adicionar`;

    const textoOriginal = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = "⏳ Salvando...";

    const response = await fetch(url, {
      method: "POST",
      body: formData
    });

    btn.disabled = false;
    btn.innerHTML = textoOriginal;

    if (response.ok) {
      console.log("[RECEITAS] receita salva com sucesso");
      form.reset();
      form.querySelector("[name='id']")?.remove();
      await carregarReceitas(atid);
    } else {
      alert("Erro ao salvar receita");
    }
  });
}

export async function carregarReceitas(atid) {
  console.log("[RECEITAS] carregando receitas para atid:", atid);
  const container = document.getElementById("lista-receitas");
  container.innerHTML = `<div class='text-sm text-gray-500 animate-pulse'>🔄 Carregando receitas...</div>`;

  try {
    const response = await fetch(`/calendario/${atid}/receitas`);
    const html = await response.text();
    container.innerHTML = html;
    console.log("[RECEITAS] HTML carregado com sucesso");

    document.querySelectorAll(".editar-receita").forEach(btn => {
      btn.addEventListener("click", () => {
        const receita = JSON.parse(btn.dataset.receita);
        const form = document.getElementById("form-receita");
        form.querySelector("[name='descricao']").value = receita.descricao;
        form.querySelector("[name='quantidade']").value = receita.quantidade;
        form.querySelector("[name='valor_unitario']").value = receita.valor_unitario;
        form.querySelector("[name='tipo_lancamento']").value = receita.tipo_lancamento;
        form.querySelector("[name='tipo']").value = receita.tipo || "";

        let hiddenId = form.querySelector("[name='id']");
        if (!hiddenId) {
          hiddenId = document.createElement("input");
          hiddenId.type = "hidden";
          hiddenId.name = "id";
          form.appendChild(hiddenId);
        }
        hiddenId.value = receita.id;
      });
    });
  } catch (error) {
    container.innerHTML = `<p class='text-sm text-red-500'>❌ Erro ao carregar receitas.</p>`;
  }
}

window.removerReceita = async function (id) {
  if (!confirm("Deseja remover esta receita?")) return;
  try {
    await fetch(`/calendario/receitas/${id}/remover`, { method: "POST" });
    const atid = document.querySelector("[name='atid']")?.value;
    if (atid) carregarReceitas(atid);
  } catch (error) {
    alert("Erro ao remover receita.");
  }
};

window.carregarReceitas = carregarReceitas;

export async function editarReceita(id) {
  try {
    const response = await fetch(`/calendario/receitas/${id}/editar`);
    const receita = await response.json();

    const form = document.getElementById("form-receita");
    form.querySelector("[name='descricao']").value = receita.descricao;
    form.querySelector("[name='quantidade']").value = receita.quantidade;
    form.querySelector("[name='valor_unitario']").value = receita.valor_unitario;
    form.querySelector("[name='tipo_lancamento']").value = receita.tipo_lancamento;
    form.querySelector("[name='tipo']").value = receita.tipo || "";

    let hiddenId = form.querySelector("[name='id']");
    if (!hiddenId) {
      hiddenId = document.createElement("input");
      hiddenId.type = "hidden";
      hiddenId.name = "id";
      form.appendChild(hiddenId);
    }
    hiddenId.value = receita.id;

    const botao = form.querySelector("button[type='submit']");
    if (botao) botao.textContent = "Salvar Alterações";
  } catch (error) {
    console.error("Erro ao carregar receita para edição", error);
  }
}

window.editarReceita = editarReceita;
