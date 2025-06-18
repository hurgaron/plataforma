// static/js/calendar.js

// ⚠️ NÃO usar import aqui. As funções vêm do window.

document.addEventListener("DOMContentLoaded", function () {
  const calendarEl = document.getElementById("calendar");
  if (!calendarEl || typeof FullCalendar === "undefined") {
    console.error("FullCalendar não está disponível ou #calendar não existe.");
    return;
  }

  let calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: "dayGridMonth",
    locale: "pt-br",
    headerToolbar: {
      left: "prev,next today",
      center: "title",
      right: "dayGridMonth,timeGridWeek,listMonth"
    },
    events: function (fetchInfo, successCallback, failureCallback) {
      const selecionados = Array.from(document.querySelectorAll(".filtro-calendario:checked"))
        .map(cb => cb.value);

      console.log("Filtros selecionados:", selecionados);

      const params = new URLSearchParams();
      selecionados.forEach(val => params.append("calids", val));
      params.append("start", fetchInfo.startStr);
      params.append("end", fetchInfo.endStr);
      const busca = document.getElementById("filtro-busca")?.value || "";
      if (busca) params.append("busca", busca);

      fetch(`/calendario/eventos?${params.toString()}`)
        .then(res => {
          if (!res.ok) throw new Error("Erro ao carregar eventos");
          return res.json();
        })
        .then(data => successCallback(data))
        .catch(err => {
          console.error(err);
          failureCallback(err);
        });
    },
    dateClick: function (info) {
      window.abrirModalNovaAtividade(info.dateStr);
    },
    eventClick: function (info) {
      window.carregarAtividade(info.event.id);
    },
    editable: true,
    eventDrop: function (info) {
      atualizarDataEvento(info.event);
    },
    eventResize: function (info) {
      atualizarDataEvento(info.event);
    },
    eventDidMount: function (info) {
      const { event, el } = info;
      const local = event.extendedProps.local;
      const calendario = event.extendedProps.calendario;

      const textoTooltip = `
${event.title}
${local ? '📍 ' + local : ''}
${calendario ? '📅 ' + calendario : ''}
${event.start && event.end ? '🕒 ' + formatarIntervalo(event.start, event.end) : ''}
      `.trim();

      el.setAttribute("title", textoTooltip);
    }
  });

  calendar.render();
  window.calendar = calendar;

  // Escutador para mudanças nos checkboxes
  document.querySelectorAll(".filtro-calendario").forEach(el => {
    el.addEventListener("change", () => {
      calendar.refetchEvents();
    });

    // Escutador para busca por texto (com proteção)
    setTimeout(() => {
      const filtroBusca = document.getElementById("filtro-busca");
      if (filtroBusca) {
        filtroBusca.addEventListener("input", () => {
          calendar.refetchEvents();
        });
      } else {
        console.warn("Campo #filtro-busca não encontrado no DOM.");
      }
    }, 300);

  });
});

function atualizarDataEvento(event) {
  fetch(`/calendario/${event.id}/atualizar-data`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      start: event.startStr,
      end: event.endStr
    })
  })
    .then(res => {
      if (res.ok) {
        console.log("✅ Evento atualizado com sucesso.");
        // futuro: mostrar toast visual
      } else {
        console.error("❌ Erro ao atualizar data do evento");
        alert("Erro ao mover o evento. Tente novamente.");
      }
    })
    .catch(err => {
      console.error("❌ Erro de rede ao atualizar evento", err);
      alert("Erro ao mover o evento.");
    });
}

function formatarIntervalo(start, end) {
  const inicio = new Date(start).toLocaleString("pt-BR", { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });
  const fim = new Date(end).toLocaleString("pt-BR", { hour: '2-digit', minute: '2-digit' });
  return `${inicio} até ${fim}`;
}
